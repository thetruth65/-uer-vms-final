// frontend/src/components/Admin/AttackModal.tsx
import React, { useState, useEffect } from 'react';
import { X, Terminal, Database, ShieldAlert, Lock, AlertTriangle } from 'lucide-react';
import { api } from '../../services/api';

interface AttackModalProps {
  isOpen: boolean;
  onClose: () => void;
  voterId: string;
  stateId: string;
  onAttackComplete: () => void;
}

export default function AttackModal({ isOpen, onClose, voterId, stateId, onAttackComplete }: AttackModalProps) {
  const [step, setStep] = useState<'IDLE' | 'INJECTING' | 'DETECTED'>('IDLE');
  const [logs, setLogs] = useState<string[]>([]);
  const [hashes, setHashes] = useState<{ chain: string; local: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      startSimulation();
    } else {
      setStep('IDLE');
      setLogs([]);
      setHashes(null);
    }
  }, [isOpen]);

  const addLog = (msg: string) => setLogs(prev => [...prev, msg]);

  const startSimulation = async () => {
    setStep('INJECTING');
    addLog("> Initializing SQL Injection sequence...");
    
    setTimeout(() => addLog("> Bypassing API Gateway security layer..."), 800);
    setTimeout(() => addLog("> Accessing 'voters' table directly via Root..."), 1600);
    
    try {
      setTimeout(async () => {
        addLog(`> UPDATE voters SET address = 'HACKED' WHERE id = '${voterId.substring(0,8)}...'`);
        
        // 1. Perform Hack
        await api.simulateHack(voterId, stateId);
        
        addLog("> SQL Update Successful. Data integrity corrupted.");
        addLog("> Triggering System Integrity Check...");
        
        // 2. Run Audit to fetch the new Mismatched Hashes
        const audit = await api.checkIntegrity(stateId);
        
        // 3. Find the specific record
        const record = audit.find((r: any) => r.voter_id === voterId);
        
        if (record) {
            setHashes({
                chain: record.chain_hash || "Error fetching chain",
                local: record.local_hash || "Error calculating local"
            });
            setStep('DETECTED');
            onAttackComplete(); 
        } else {
            addLog("> Error: Could not verify hack status.");
        }
      }, 2500);
    } catch (e) {
      addLog("> Error: Simulation failed.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-gray-900 text-white rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden border border-red-500/30">
        
        {/* Header */}
        <div className="bg-gray-800 px-6 py-4 flex justify-between items-center border-b border-gray-700">
          <div className="flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-red-500" />
            <span className="font-mono font-bold text-red-400">ATTACK SIMULATION TERMINAL</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          
          {/* Terminal View */}
          <div className="bg-black rounded-lg p-4 font-mono text-xs md:text-sm h-40 overflow-y-auto border border-gray-800 shadow-inner">
            {logs.map((log, i) => (
              <div key={i} className="mb-1 text-green-400">
                <span className="text-gray-500 mr-2">{new Date().toLocaleTimeString()}</span>
                {log}
              </div>
            ))}
            {step === 'INJECTING' && (
              <div className="animate-pulse text-green-400">_</div>
            )}
          </div>

          {/* Visualization Area */}
          {step === 'DETECTED' && hashes && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 mb-4 flex items-center justify-center space-x-3">
                <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
                <div>
                  <h3 className="text-lg font-bold text-red-400">TAMPERING DETECTED</h3>
                  <p className="text-red-200 text-sm">Cryptographic Signature Mismatch</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Blockchain Truth */}
                <div className="bg-gray-800 p-4 rounded-lg border border-green-500/50 relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-green-500 text-black text-xs font-bold px-2 py-1">IMMUTABLE</div>
                  <div className="flex items-center mb-2 text-green-400">
                    <Lock className="w-4 h-4 mr-2" />
                    <span className="font-bold text-sm">BLOCKCHAIN RECORD</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-1">Expected Hash:</div>
                  <div className="font-mono text-green-400 text-xs break-all bg-black p-2 rounded border border-green-900">
                    {hashes.chain}
                  </div>
                </div>

                {/* Corrupted DB */}
                <div className="bg-gray-800 p-4 rounded-lg border border-red-500/50 relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold px-2 py-1">CORRUPTED</div>
                  <div className="flex items-center mb-2 text-red-400">
                    <Database className="w-4 h-4 mr-2" />
                    <span className="font-bold text-sm">LOCAL SQL DATABASE</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-1">Actual Hash:</div>
                  <div className="font-mono text-red-400 text-xs break-all bg-black p-2 rounded border border-red-900">
                    {hashes.local}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-800 px-6 py-4 flex justify-end">
          {step === 'DETECTED' ? (
            <button onClick={onClose} className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-medium transition-colors">
              Close Investigation
            </button>
          ) : (
            <div className="text-gray-500 text-sm italic">Simulating attack in progress...</div>
          )}
        </div>
      </div>
    </div>
  );
}