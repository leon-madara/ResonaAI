import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast } from 'react-hot-toast';

interface OfflineContextType {
  isOnline: boolean;
  isOfflineMode: boolean;
  syncQueue: SyncItem[];
  addToSyncQueue: (item: SyncItem) => void;
  processSyncQueue: () => Promise<void>;
  clearSyncQueue: () => void;
}

interface SyncItem {
  id: string;
  type: 'message' | 'emotion' | 'profile_update';
  data: any;
  timestamp: Date;
  retryCount: number;
}

const OfflineContext = createContext<OfflineContextType | undefined>(undefined);

interface OfflineProviderProps {
  children: ReactNode;
}

export const OfflineProvider: React.FC<OfflineProviderProps> = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const [syncQueue, setSyncQueue] = useState<SyncItem[]>([]);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setIsOfflineMode(false);
      toast.success('Connection restored');
      processSyncQueue();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsOfflineMode(true);
      toast.error('You are offline. Data will sync when connection is restored.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load sync queue from localStorage
    const storedQueue = localStorage.getItem('syncQueue');
    if (storedQueue) {
      try {
        const queue = JSON.parse(storedQueue).map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
        setSyncQueue(queue);
      } catch (error) {
        console.error('Failed to load sync queue:', error);
      }
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const addToSyncQueue = (item: Omit<SyncItem, 'id' | 'timestamp' | 'retryCount'>) => {
    const syncItem: SyncItem = {
      ...item,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      retryCount: 0
    };

    setSyncQueue(prev => {
      const updated = [...prev, syncItem];
      localStorage.setItem('syncQueue', JSON.stringify(updated));
      return updated;
    });

    if (isOnline) {
      processSyncQueue();
    }
  };

  const processSyncQueue = async () => {
    if (!isOnline || syncQueue.length === 0) return;

    const itemsToProcess = [...syncQueue];
    const processedItems: SyncItem[] = [];
    const failedItems: SyncItem[] = [];

    for (const item of itemsToProcess) {
      try {
        await processSyncItem(item);
        processedItems.push(item);
      } catch (error) {
        console.error('Failed to sync item:', error);
        
        if (item.retryCount < 3) {
          failedItems.push({
            ...item,
            retryCount: item.retryCount + 1
          });
        } else {
          console.error('Max retries exceeded for item:', item);
          // Could show a notification to user about failed sync
        }
      }
    }

    // Update sync queue
    setSyncQueue(failedItems);
    localStorage.setItem('syncQueue', JSON.stringify(failedItems));

    if (processedItems.length > 0) {
      toast.success(`Synced ${processedItems.length} items`);
    }
  };

  const processSyncItem = async (item: SyncItem): Promise<void> => {
    switch (item.type) {
      case 'message':
        await fetch('/api/conversation/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(item.data)
        });
        break;
      
      case 'emotion':
        await fetch('/api/emotion/track', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(item.data)
        });
        break;
      
      case 'profile_update':
        await fetch('/api/user/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(item.data)
        });
        break;
      
      default:
        throw new Error(`Unknown sync item type: ${item.type}`);
    }
  };

  const clearSyncQueue = () => {
    setSyncQueue([]);
    localStorage.removeItem('syncQueue');
  };

  const value: OfflineContextType = {
    isOnline,
    isOfflineMode,
    syncQueue,
    addToSyncQueue,
    processSyncQueue,
    clearSyncQueue,
  };

  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
};

export const useOffline = (): OfflineContextType => {
  const context = useContext(OfflineContext);
  if (context === undefined) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
};
