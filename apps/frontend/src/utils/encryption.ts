/**
 * Client-Side Encryption Utility
 * Uses Web Crypto API for secure encryption in the browser
 * Implements AES-GCM encryption with key derivation from password
 */

// Encryption configuration
const ENCRYPTION_ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits for AES-GCM
const SALT_LENGTH = 16;
const PBKDF2_ITERATIONS = 100000;

/**
 * Generate a random salt
 */
export function generateSalt(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
}

/**
 * Generate a random initialization vector
 */
export function generateIV(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(IV_LENGTH));
}

/**
 * Derive an encryption key from a password using PBKDF2
 * @param password User's password
 * @param salt Random salt
 * @returns CryptoKey for AES-GCM encryption
 */
export async function deriveKey(
  password: string,
  salt: Uint8Array
): Promise<CryptoKey> {
  // Import password as key material
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
    'PBKDF2',
    false,
    ['deriveKey']
  );

  // Derive AES key using PBKDF2
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256',
    },
    keyMaterial,
    {
      name: ENCRYPTION_ALGORITHM,
      length: KEY_LENGTH,
    },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt data using AES-GCM
 * @param plaintext Data to encrypt
 * @param password Password for key derivation
 * @returns Object containing encrypted data, salt, and IV
 */
export async function encrypt(
  plaintext: string,
  password: string
): Promise<EncryptedData> {
  const salt = generateSalt();
  const iv = generateIV();
  const key = await deriveKey(password, salt);

  const encodedData = new TextEncoder().encode(plaintext);

  const ciphertext = await crypto.subtle.encrypt(
    {
      name: ENCRYPTION_ALGORITHM,
      iv: iv,
    },
    key,
    encodedData
  );

  return {
    ciphertext: arrayBufferToBase64(ciphertext),
    salt: arrayBufferToBase64(salt),
    iv: arrayBufferToBase64(iv),
    algorithm: ENCRYPTION_ALGORITHM,
    timestamp: Date.now(),
  };
}

/**
 * Decrypt data using AES-GCM
 * @param encryptedData Encrypted data object
 * @param password Password for key derivation
 * @returns Decrypted plaintext
 */
export async function decrypt(
  encryptedData: EncryptedData,
  password: string
): Promise<string> {
  const salt = base64ToArrayBuffer(encryptedData.salt);
  const iv = base64ToArrayBuffer(encryptedData.iv);
  const ciphertext = base64ToArrayBuffer(encryptedData.ciphertext);

  const key = await deriveKey(password, new Uint8Array(salt));

  const decrypted = await crypto.subtle.decrypt(
    {
      name: ENCRYPTION_ALGORITHM,
      iv: new Uint8Array(iv),
    },
    key,
    ciphertext
  );

  return new TextDecoder().decode(decrypted);
}

/**
 * Encrypt an object
 * @param data Object to encrypt
 * @param password Password for key derivation
 * @returns Encrypted data
 */
export async function encryptObject<T>(
  data: T,
  password: string
): Promise<EncryptedData> {
  const jsonString = JSON.stringify(data);
  return encrypt(jsonString, password);
}

/**
 * Decrypt an object
 * @param encryptedData Encrypted data
 * @param password Password for key derivation
 * @returns Decrypted object
 */
export async function decryptObject<T>(
  encryptedData: EncryptedData,
  password: string
): Promise<T> {
  const jsonString = await decrypt(encryptedData, password);
  return JSON.parse(jsonString) as T;
}

/**
 * Generate a random encryption key (for session keys)
 * @returns Base64-encoded random key
 */
export async function generateRandomKey(): Promise<string> {
  const key = await crypto.subtle.generateKey(
    {
      name: ENCRYPTION_ALGORITHM,
      length: KEY_LENGTH,
    },
    true,
    ['encrypt', 'decrypt']
  );

  const exported = await crypto.subtle.exportKey('raw', key);
  return arrayBufferToBase64(exported);
}

/**
 * Hash data using SHA-256
 * @param data Data to hash
 * @returns Base64-encoded hash
 */
export async function hash(data: string): Promise<string> {
  const encoded = new TextEncoder().encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
  return arrayBufferToBase64(hashBuffer);
}

// Utility functions

/**
 * Convert ArrayBuffer to Base64 string
 */
export function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Convert Base64 string to ArrayBuffer
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

// Types

export interface EncryptedData {
  ciphertext: string; // Base64-encoded encrypted data
  salt: string; // Base64-encoded salt
  iv: string; // Base64-encoded initialization vector
  algorithm: string; // Encryption algorithm used
  timestamp: number; // Encryption timestamp
}

export interface EncryptedMessage {
  id: string;
  encryptedContent: EncryptedData;
  conversationId: string;
  createdAt: string;
}

