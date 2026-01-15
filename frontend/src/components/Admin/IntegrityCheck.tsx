// frontend/src/components/Admin/IntegrityCheck.tsx
import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, RefreshCw, Lock, Skull, ServerCrash } from 'lucide-react';
import { api } from '../../services/api';
import AttackModal from './AttackModal';

interface IntegrityResult {
  voter_id: string;
  name: string;
  status: string;
  details: string;
  hash_mismatch: boolean;
  local_hash?: string; 
  chain_hash?: string;
}

export default function IntegrityCheck({ stateId }: { stateId: string }) {
  const [results, setResults] = useState<IntegrityResult[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedVoterId, setSelectedVoterId] = useState('');

  const runAudit = async () => {
    setLoading(true);
    try {
      const data = await api.checkIntegrity(stateId);
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openAttackSimulation = (voterId: string) => {
    setSelectedVoterId(voterId);
    setIsModalOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'SECURE': return 'bg-green-100 text-green-800 border-green-200';
      case 'SIMULATED_TAMPERING': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'SERVICE_FAILED': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-red-100 text-red-800 border-red-200'; // Real Tampering
    }
  };

  return (
    <>
      <div className="card mt-8 border-t-4 border-blue-600">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center text-gray-900">
              <ShieldCheck className="w-8 h-8 mr-3 text-blue-600" />
              Blockchain Integrity Audit
            </h2>
            <p className="text-gray-600 mt-1">
              Cryptographically verify SQL database against the Immutable Ledger.
            </p>
          </div>
          <button 
            onClick={runAudit} 
            disabled={loading}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Verifying Hashes...' : 'Run Full Audit'}
          </button>
        </div>

        {results.length > 0 && (
          <div className="space-y-3">
            {results.map((res) => {
              const isBad = res.status !== 'SECURE';
              const isSimulated = res.status === 'SIMULATED_TAMPERING';
              
              return (
                <div 
                  key={res.voter_id} 
                  className={`p-4 rounded-lg border-l-4 flex flex-col md:flex-row justify-between items-center transition-all ${
                    isBad ? 'bg-red-50 border-red-500' : 'bg-green-50 border-green-500'
                  } ${isSimulated ? 'bg-orange-50 border-orange-500' : ''}`}
                >
                  <div className="flex-1 w-full">
                    <div className="flex items-center mb-2">
                      {res.status === 'SERVICE_FAILED' ? (
                        <ServerCrash className="w-5 h-5 text-gray-600 mr-2" />
                      ) : isBad ? (
                        <AlertTriangle className={`w-5 h-5 mr-2 ${isSimulated ? 'text-orange-600' : 'text-red-600'}`} />
                      ) : (
                        <Lock className="w-5 h-5 text-green-600 mr-2" />
                      )}
                      
                      <span className="font-mono font-bold text-gray-800 mr-2">{res.voter_id}</span>
                      <span className="text-gray-500">|</span>
                      <span className="font-medium ml-2">{res.name}</span>
                    </div>
                    
                    {/* HASH DISPLAY */}
                    {isBad && res.status !== 'SERVICE_FAILED' && (
                      <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono bg-white/60 p-2 rounded">
                          <div className="text-red-700">
                              <span className="font-bold">SQL Hash (Corrupted):</span><br/>
                              {res.local_hash ? res.local_hash : "Generating..."}
                          </div>
                          <div className="text-green-700">
                              <span className="font-bold">Blockchain Hash (Original):</span><br/>
                              {res.chain_hash ? res.chain_hash : "Fetching..."}
                          </div>
                      </div>
                    )}
                    
                    <p className="text-sm mt-1 text-gray-600">{res.details}</p>
                  </div>
                  
                  <div className="flex items-center space-x-4 mt-4 md:mt-0 ml-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusColor(res.status)}`}>
                      {res.status.replace('_', ' ')}
                    </span>

                    {/* Attack Button (Only for Secure rows) */}
                    {res.status === 'SECURE' && (
                      <button
                        onClick={() => openAttackSimulation(res.voter_id)}
                        className="flex items-center px-3 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded border border-red-200 transition-colors"
                      >
                        <Skull className="w-3 h-3 mr-1" />
                        Simulate Attack
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <AttackModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        voterId={selectedVoterId}
        stateId={stateId}
        onAttackComplete={runAudit}
      />
    </>
  );
}