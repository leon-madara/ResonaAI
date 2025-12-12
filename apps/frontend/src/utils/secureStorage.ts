/**
 * Secure IndexedDB Storage
 * Encrypts data before storing in IndexedDB
 * For offline-first encrypted data storage
 */

import { encrypt, decrypt, encryptObject, decryptObject, EncryptedData } from './encryption';

const DB_NAME = 'ResonaSecureDB';
const DB_VERSION = 1;

// Store names
const STORES = {
  MESSAGES: 'encrypted_messages',
  CONVERSATIONS: 'encrypted_conversations',
  USER_DATA: 'encrypted_user_data',
  SYNC_QUEUE: 'sync_queue',
};

/**
 * Initialize the secure IndexedDB database
 */
export async function initSecureStorage(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => {
      reject(new Error('Failed to open IndexedDB'));
    };

    request.onsuccess = () => {
      resolve(request.result);
    };

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      // Encrypted messages store
      if (!db.objectStoreNames.contains(STORES.MESSAGES)) {
        const messageStore = db.createObjectStore(STORES.MESSAGES, { keyPath: 'id' });
        messageStore.createIndex('conversationId', 'conversationId', { unique: false });
        messageStore.createIndex('timestamp', 'timestamp', { unique: false });
      }

      // Encrypted conversations store
      if (!db.objectStoreNames.contains(STORES.CONVERSATIONS)) {
        const convStore = db.createObjectStore(STORES.CONVERSATIONS, { keyPath: 'id' });
        convStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
      }

      // Encrypted user data store
      if (!db.objectStoreNames.contains(STORES.USER_DATA)) {
        db.createObjectStore(STORES.USER_DATA, { keyPath: 'key' });
      }

      // Sync queue store (for offline actions)
      if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
        const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, {
          keyPath: 'id',
          autoIncrement: true,
        });
        syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        syncStore.createIndex('status', 'status', { unique: false });
      }
    };
  });
}

/**
 * Get database connection
 */
async function getDB(): Promise<IDBDatabase> {
  return initSecureStorage();
}

/**
 * Secure Storage class for encrypted IndexedDB operations
 */
export class SecureStorage {
  private encryptionKey: string;

  constructor(encryptionKey: string) {
    this.encryptionKey = encryptionKey;
  }

  /**
   * Store encrypted message
   */
  async storeMessage(
    id: string,
    conversationId: string,
    content: string,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    const db = await getDB();

    const encryptedContent = await encrypt(content, this.encryptionKey);
    const encryptedMetadata = metadata
      ? await encryptObject(metadata, this.encryptionKey)
      : null;

    const record = {
      id,
      conversationId,
      encryptedContent,
      encryptedMetadata,
      timestamp: Date.now(),
    };

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.MESSAGES], 'readwrite');
      const store = transaction.objectStore(STORES.MESSAGES);
      const request = store.put(record);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(new Error('Failed to store message'));
    });
  }

  /**
   * Retrieve and decrypt message
   */
  async getMessage(id: string): Promise<DecryptedMessage | null> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.MESSAGES], 'readonly');
      const store = transaction.objectStore(STORES.MESSAGES);
      const request = store.get(id);

      request.onsuccess = async () => {
        const record = request.result;
        if (!record) {
          resolve(null);
          return;
        }

        try {
          const content = await decrypt(record.encryptedContent, this.encryptionKey);
          const metadata = record.encryptedMetadata
            ? await decryptObject<Record<string, unknown>>(
                record.encryptedMetadata,
                this.encryptionKey
              )
            : null;

          resolve({
            id: record.id,
            conversationId: record.conversationId,
            content,
            metadata,
            timestamp: record.timestamp,
          });
        } catch (error) {
          reject(new Error('Failed to decrypt message'));
        }
      };

      request.onerror = () => reject(new Error('Failed to retrieve message'));
    });
  }

  /**
   * Get all messages for a conversation
   */
  async getConversationMessages(conversationId: string): Promise<DecryptedMessage[]> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.MESSAGES], 'readonly');
      const store = transaction.objectStore(STORES.MESSAGES);
      const index = store.index('conversationId');
      const request = index.getAll(conversationId);

      request.onsuccess = async () => {
        const records = request.result;
        const messages: DecryptedMessage[] = [];

        for (const record of records) {
          try {
            const content = await decrypt(record.encryptedContent, this.encryptionKey);
            const metadata = record.encryptedMetadata
              ? await decryptObject<Record<string, unknown>>(
                  record.encryptedMetadata,
                  this.encryptionKey
                )
              : null;

            messages.push({
              id: record.id,
              conversationId: record.conversationId,
              content,
              metadata,
              timestamp: record.timestamp,
            });
          } catch {
            // Skip messages that fail to decrypt
            console.warn(`Failed to decrypt message ${record.id}`);
          }
        }

        // Sort by timestamp
        messages.sort((a, b) => a.timestamp - b.timestamp);
        resolve(messages);
      };

      request.onerror = () => reject(new Error('Failed to retrieve messages'));
    });
  }

  /**
   * Store encrypted user data
   */
  async storeUserData(key: string, data: unknown): Promise<void> {
    const db = await getDB();

    const encryptedData = await encryptObject(data, this.encryptionKey);

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.USER_DATA], 'readwrite');
      const store = transaction.objectStore(STORES.USER_DATA);
      const request = store.put({
        key,
        encryptedData,
        timestamp: Date.now(),
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(new Error('Failed to store user data'));
    });
  }

  /**
   * Retrieve and decrypt user data
   */
  async getUserData<T>(key: string): Promise<T | null> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.USER_DATA], 'readonly');
      const store = transaction.objectStore(STORES.USER_DATA);
      const request = store.get(key);

      request.onsuccess = async () => {
        const record = request.result;
        if (!record) {
          resolve(null);
          return;
        }

        try {
          const data = await decryptObject<T>(record.encryptedData, this.encryptionKey);
          resolve(data);
        } catch {
          reject(new Error('Failed to decrypt user data'));
        }
      };

      request.onerror = () => reject(new Error('Failed to retrieve user data'));
    });
  }

  /**
   * Delete message
   */
  async deleteMessage(id: string): Promise<void> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.MESSAGES], 'readwrite');
      const store = transaction.objectStore(STORES.MESSAGES);
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(new Error('Failed to delete message'));
    });
  }

  /**
   * Clear all data (for logout or data deletion)
   */
  async clearAllData(): Promise<void> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction(
        [STORES.MESSAGES, STORES.CONVERSATIONS, STORES.USER_DATA],
        'readwrite'
      );

      transaction.objectStore(STORES.MESSAGES).clear();
      transaction.objectStore(STORES.CONVERSATIONS).clear();
      transaction.objectStore(STORES.USER_DATA).clear();

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(new Error('Failed to clear data'));
    });
  }

  /**
   * Add action to sync queue (for offline support)
   */
  async addToSyncQueue(action: SyncAction): Promise<void> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);

      const record = {
        ...action,
        timestamp: Date.now(),
        status: 'pending',
      };

      const request = store.add(record);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(new Error('Failed to add to sync queue'));
    });
  }

  /**
   * Get pending sync actions
   */
  async getPendingSyncActions(): Promise<SyncAction[]> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.SYNC_QUEUE], 'readonly');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      const index = store.index('status');
      const request = index.getAll('pending');

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(new Error('Failed to get sync queue'));
    });
  }

  /**
   * Mark sync action as completed
   */
  async completeSyncAction(id: number): Promise<void> {
    const db = await getDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(new Error('Failed to complete sync action'));
    });
  }
}

// Types

export interface DecryptedMessage {
  id: string;
  conversationId: string;
  content: string;
  metadata: Record<string, unknown> | null;
  timestamp: number;
}

export interface SyncAction {
  id?: number;
  type: 'create_message' | 'update_message' | 'delete_message' | 'create_conversation';
  payload: unknown;
  timestamp?: number;
  status?: 'pending' | 'completed' | 'failed';
}

/**
 * Create a SecureStorage instance with the user's encryption key
 */
export function createSecureStorage(encryptionKey: string): SecureStorage {
  return new SecureStorage(encryptionKey);
}

/**
 * Delete the entire database (for complete data wipe)
 */
export async function deleteSecureDatabase(): Promise<void> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.deleteDatabase(DB_NAME);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(new Error('Failed to delete database'));
    request.onblocked = () => {
      console.warn('Database deletion blocked - close all other tabs');
    };
  });
}

