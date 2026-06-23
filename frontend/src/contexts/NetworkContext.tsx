import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { ALL_STATES, StateConfig } from '../config/states';

interface NetworkContextType {
  activeStates: StateConfig[];
  isScanning: boolean;
  refreshNetwork: () => Promise<void>;
  getStateUrl: (stateId: string) => string;
}

const NetworkContext = createContext<NetworkContextType>({
  activeStates: [],
  isScanning: true,
  refreshNetwork: async () => {},
  getStateUrl: () => '',
});

export const useNetwork = () => useContext(NetworkContext);

export const NetworkProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeStates, setActiveStates] = useState<StateConfig[]>([]);
  const [isScanning, setIsScanning] = useState(true);

  const scanNetwork = async () => {
    setIsScanning(true);
    const discoveredStates: StateConfig[] = [];
    
    // Determine URLs to scan
    let urlsToScan: string[] = [];
    // If user provided a comma-separated list of URLs in .env (e.g. for Prod/Docker/K8s)
    if (import.meta.env.VITE_NODE_URLS) {
      urlsToScan = import.meta.env.VITE_NODE_URLS.split(',').map((s: string) => s.trim());
    } else {
      // Local testing auto-discovery: Scan ports 8000, 8002... up to 8054 (max 28 states)
      for (let i = 0; i < 28; i++) {
        urlsToScan.push(`http://127.0.0.1:${8000 + (i * 2)}`);
      }
    }

    // Ping all nodes simultaneously
    const promises = urlsToScan.map(async (url) => {
      try {
        // Fast timeout since it's local network auto-discovery
        const response = await axios.get(`${url}/`, { timeout: 1500 });
        if (response.data && response.data.status === 'operational') {
          discoveredStates.push({
            id: response.data.state_id,
            name: response.data.state,
            port: parseInt(url.split(':').pop() || '0'),
            url: url
          });
        }
      } catch (err) {
        // Node is offline/not started - completely expected
      }
    });

    await Promise.allSettled(promises);
    
    // Sort to maintain consistent ordering in UI
    discoveredStates.sort((a, b) => a.port - b.port);
    setActiveStates(discoveredStates);
    
    // Dynamically update the global ALL_STATES cache for offline resolution
    if (discoveredStates.length > 0) {
      import('../config/states').then(m => m.updateAllStates(discoveredStates));
    }
    
    setIsScanning(false);
  };

  useEffect(() => {
    scanNetwork();
    // Optional: Re-scan every 30 seconds to simulate real-time Service Mesh
    const interval = setInterval(scanNetwork, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStateUrl = (stateId: string) => {
    const state = activeStates.find(s => s.id === stateId) || ALL_STATES.find(s => s.id === stateId);
    return state ? state.url : 'http://127.0.0.1:8000';
  };

  return (
    <NetworkContext.Provider value={{ activeStates, isScanning, refreshNetwork: scanNetwork, getStateUrl }}>
      {children}
    </NetworkContext.Provider>
  );
};
