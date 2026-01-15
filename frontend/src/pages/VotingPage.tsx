import React, { useState } from 'react';
import { Vote, Upload, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function VotingPage() {
  const [voterId, setVoterId] = useState('');
  const [pollingBoothId, setPollingBoothId] = useState('BOOTH_001');
  const [selectedState, setSelectedState] = useState('STATE_A');
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState('');
  
  const [isChecking, setIsChecking] = useState(false);
  const [isVoting, setIsVoting] = useState(false);
  const [eligibility, setEligibility] = useState<any>(null);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transactionId, setTransactionId] = useState('');
  
  const checkEligibility = async () => {
    setError(null);
    setIsChecking(true);
    
    try {
      const result = await api.checkEligibility(voterId, selectedState);
      setEligibility(result);
      if (!result.eligible) {
        setError(result.reason);
      }
    } catch (err: any) {
      setError('Failed to check eligibility');
    } finally {
      setIsChecking(false);
    }
  };
  
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => setPhotoPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };
  
  const handleVote = async () => {
    if (!photo) {
      setError('Please upload your photo for biometric verification');
      return;
    }
    
    setIsVoting(true);
    setError(null);
    
    try {
      const response = await api.castVote(voterId, pollingBoothId, photo, selectedState);
      setTransactionId(response.blockchain_transaction_id);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Voting failed');
    } finally {
      setIsVoting(false);
    }
  };
  
  if (success) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="card text-center">
          <CheckCircle className="w-20 h-20 text-green-600 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Vote Recorded!</h2>
          <p className="text-gray-600 mb-6">
            Your vote has been securely recorded on the blockchain
          </p>
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <div className="text-sm text-gray-600 mb-1">Transaction ID</div>
            <div className="font-mono text-sm text-blue-600">{transactionId}</div>
          </div>
          <Shield className="w-12 h-12 text-blue-600 mx-auto mb-4" />
          <p className="text-sm text-gray-600">
            Your voter ID is now locked nationwide. You cannot vote again in this election.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="card">
        <div className="flex items-center mb-6">
          <Vote className="w-8 h-8 text-purple-600 mr-3" />
          <div>
            <h1 className="text-3xl font-bold">Cast Your Vote</h1>
            <p className="text-gray-600">Biometric verification required</p>
          </div>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
            <p className="text-red-700">{error}</p>
          </div>
        )}
        
        {eligibility?.eligible && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">✓ Eligible to vote</p>
            <p className="text-green-700 text-sm mt-1">
              {eligibility.name} - {eligibility.state}
            </p>
          </div>
        )}
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Polling State</label>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="input-field"
            >
              <option value="STATE_A">Maharashtra</option>
              <option value="STATE_B">Karnataka</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Voter ID</label>
            <input
              type="text"
              value={voterId}
              onChange={(e) => setVoterId(e.target.value)}
              className="input-field"
            />
          </div>
          
          <button
            onClick={checkEligibility}
            className="btn-secondary w-full"
            disabled={!voterId || isChecking}
          >
            {isChecking ? 'Checking...' : 'Check Eligibility'}
          </button>
          
          {eligibility?.eligible && (
            <>
              <div>
                <label className="block text-sm font-medium mb-2">Polling Booth</label>
                <select
                  value={pollingBoothId}
                  onChange={(e) => setPollingBoothId(e.target.value)}
                  className="input-field"
                >
                  <option value="BOOTH_001">Booth 001 - Central School</option>
                  <option value="BOOTH_002">Booth 002 - Community Hall</option>
                  <option value="BOOTH_003">Booth 003 - Municipal Office</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Upload Photo for Biometric Verification
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  {photoPreview ? (
                    <div>
                      <img src={photoPreview} alt="Preview" className="w-32 h-32 object-cover rounded-lg mx-auto mb-4" />
                      <button onClick={() => {
                        setPhoto(null);
                        setPhotoPreview('');
                      }} className="text-sm text-red-600">Remove</button>
                    </div>
                  ) : (
                    <label className="cursor-pointer">
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <span className="btn-secondary inline-block">Upload Photo</span>
                      <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    </label>
                  )}
                </div>
              </div>
              
              {isVoting && <LoadingSpinner message="Verifying biometrics and recording vote..." />}
              
              <button
                onClick={handleVote}
                className="btn-primary w-full"
                disabled={!photo || isVoting}
              >
                Cast Vote
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}