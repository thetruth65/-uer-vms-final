import React, { useState } from 'react';
import { ArrowLeftRight, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function TransferPage() {
  const [voterId, setVoterId] = useState('');
  const [fromState, setFromState] = useState('STATE_A');
  const [toState, setToState] = useState('STATE_B');
  const [newAddress, setNewAddress] = useState({
    address_line1: '',
    address_line2: '',
    city: '',
    pincode: ''
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transactionId, setTransactionId] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsProcessing(true);
    
    try {
      const response = await api.transferVoter({
        voter_id: voterId,
        from_state: fromState,
        to_state: toState,
        new_address_line1: newAddress.address_line1,
        new_address_line2: newAddress.address_line2,
        new_city: newAddress.city,
        new_pincode: newAddress.pincode
      });
      
      setTransactionId(response.blockchain_transaction_id);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Transfer failed');
    } finally {
      setIsProcessing(false);
    }
  };
  
  if (success) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="card text-center">
          <CheckCircle className="w-20 h-20 text-green-600 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Transfer Successful!</h2>
          <p className="text-gray-600 mb-6">
            Voter has been transferred from {fromState === 'STATE_A' ? 'Maharashtra' : 'Karnataka'} to {toState === 'STATE_A' ? 'Maharashtra' : 'Karnataka'}
          </p>
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <div className="text-sm text-gray-600 mb-1">Transaction ID</div>
            <div className="font-mono text-sm text-blue-600">{transactionId}</div>
          </div>
          <button onClick={() => {
            setSuccess(false);
            setVoterId('');
            setNewAddress({
              address_line1: '',
              address_line2: '',
              city: '',
              pincode: ''
            });
          }} className="btn-primary">
            Transfer Another Voter
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="card">
        <div className="flex items-center mb-6">
          <ArrowLeftRight className="w-8 h-8 text-green-600 mr-3" />
          <div>
            <h1 className="text-3xl font-bold">Voter Transfer</h1>
            <p className="text-gray-600">Transfer voter registration between states</p>
          </div>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
            <p className="text-red-700">{error}</p>
          </div>
        )}
        
        {isProcessing && <LoadingSpinner message="Processing transfer via blockchain..." />}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Voter ID</label>
            <input
              type="text"
              value={voterId}
              onChange={(e) => setVoterId(e.target.value)}
              className="input-field"
              required
            />
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">From State</label>
              <select
                value={fromState}
                onChange={(e) => setFromState(e.target.value)}
                className="input-field"
              >
                <option value="STATE_A">Maharashtra</option>
                <option value="STATE_B">Karnataka</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">To State</label>
              <select
                value={toState}
                onChange={(e) => setToState(e.target.value)}
                className="input-field"
              >
                <option value="STATE_A">Maharashtra</option>
                <option value="STATE_B">Karnataka</option>
              </select>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">New Address</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Address Line 1"
                value={newAddress.address_line1}
                onChange={(e) => setNewAddress({...newAddress, address_line1: e.target.value})}
                className="input-field"
                required
              />
              <input
                type="text"
                placeholder="Address Line 2"
                value={newAddress.address_line2}
                onChange={(e) => setNewAddress({...newAddress, address_line2: e.target.value})}
                className="input-field"
              />
              <div className="grid md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="City"
                  value={newAddress.city}
                  onChange={(e) => setNewAddress({...newAddress, city: e.target.value})}
                  className="input-field"
                  required
                />
                <input
                  type="text"
                  placeholder="Pincode"
                  value={newAddress.pincode}
                  onChange={(e) => setNewAddress({...newAddress, pincode: e.target.value})}
                  className="input-field"
                  maxLength={6}
                  required
                />
              </div>
            </div>
          </div>
          
          <button type="submit" className="btn-primary w-full" disabled={isProcessing}>
            Transfer Voter
          </button>
        </form>
      </div>
    </div>
  );
}