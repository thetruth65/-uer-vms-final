import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import StepIndicator from '../components/Registration/StepIndicator';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { api } from '../services/api';
import type { VoterRegistrationData } from '../types';

const registrationSteps = [
  { id: 1, title: 'Personal Details', description: 'Basic information' },
  { id: 2, title: 'Photo Upload', description: 'Face capture' },
  { id: 3, title: 'AI Verification', description: 'Duplicate check' },
  { id: 4, title: 'Blockchain', description: 'Immutable record' },
  { id: 5, title: 'Complete', description: 'Registration done' }
];

export default function RegistrationPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [voterId, setVoterId] = useState<string>('');
  
  const [formData, setFormData] = useState<VoterRegistrationData>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'MALE',
    address_line1: '',
    address_line2: '',
    city: '',
    state: 'Maharashtra',
    pincode: '',
    phone_number: '',
    email: '',
  });
  
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');
  const [selectedState, setSelectedState] = useState('STATE_A');
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const validateForm = (): boolean => {
    if (!formData.first_name || !formData.last_name) {
      setError('Please enter your full name');
      return false;
    }
    
    if (!formData.date_of_birth) {
      setError('Please enter your date of birth');
      return false;
    }
    
    if (!formData.address_line1 || !formData.city || !formData.pincode) {
      setError('Please complete your address');
      return false;
    }
    
    if (!/^\d{6}$/.test(formData.pincode)) {
      setError('Pincode must be 6 digits');
      return false;
    }
    
    if (!photoFile) {
      setError('Please upload your photo');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!validateForm()) {
      return;
    }
    
    setIsProcessing(true);
    setCurrentStep(1);
    
    try {
      // Simulate step-by-step process with visual feedback
      
      // Step 1: Personal Details
      setProcessingMessage('Validating personal details...');
      setCurrentStep(1);
      await new Promise(resolve => setTimeout(resolve, 800));
      setCompletedSteps([1]);
      
      // Step 2: Photo Upload
      setProcessingMessage('Uploading photo...');
      setCurrentStep(2);
      await new Promise(resolve => setTimeout(resolve, 800));
      setCompletedSteps([1, 2]);
      
      // Step 3: AI Verification
      setProcessingMessage('Running AI duplicate detection...');
      setCurrentStep(3);
      
      const registrationData = {
        ...formData,
        photo: photoFile!
      };
      
      const response = await api.registerVoter(registrationData, selectedState);
      
      setCompletedSteps([1, 2, 3]);
      
      // Step 4: Blockchain
      setProcessingMessage('Recording on blockchain...');
      setCurrentStep(4);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCompletedSteps([1, 2, 3, 4]);
      
      // Step 5: Complete
      setProcessingMessage('Registration complete!');
      setCurrentStep(5);
      setCompletedSteps([1, 2, 3, 4, 5]);
      
      setVoterId(response.voter_id);
      setSuccess(true);
      
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.response?.data?.detail || 'Registration failed. Please try again.');
      setCurrentStep(1);
      setCompletedSteps([]);
    } finally {
      setIsProcessing(false);
      setProcessingMessage('');
    }
  };
  
  if (success) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="card text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Registration Successful!
          </h2>
          
          <p className="text-gray-600 mb-6">
            Your voter registration has been completed and recorded on the blockchain.
          </p>
          
          <div className="bg-blue-50 rounded-lg p-6 mb-6">
            <div className="text-sm text-gray-600 mb-2">Your Voter ID</div>
            <div className="text-2xl font-mono font-bold text-blue-600">{voterId}</div>
          </div>
          
          <div className="text-left bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="font-semibold mb-3">Completed Steps:</h3>
            <ul className="space-y-2">
              {registrationSteps.slice(0, -1).map(step => (
                <li key={step.id} className="flex items-center text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                  {step.title} - {step.description}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate('/')}
              className="btn-primary"
            >
              Back to Home
            </button>
            <button
              onClick={() => {
                setSuccess(false);
                setFormData({
                  first_name: '',
                  last_name: '',
                  date_of_birth: '',
                  gender: 'MALE',
                  address_line1: '',
                  address_line2: '',
                  city: '',
                  state: 'Maharashtra',
                  pincode: '',
                  phone_number: '',
                  email: '',
                });
                setPhotoFile(null);
                setPhotoPreview('');
                setCompletedSteps([]);
                setCurrentStep(1);
              }}
              className="btn-secondary"
            >
              Register Another Voter
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="card">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Voter Registration
        </h1>
        <p className="text-gray-600 mb-8">
          Register as a new voter with AI-powered duplicate detection and blockchain verification
        </p>
        
        {/* State Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Registration State
          </label>
          <select
            value={selectedState}
            onChange={(e) => {
              setSelectedState(e.target.value);
              setFormData(prev => ({
                ...prev,
                state: e.target.value === 'STATE_A' ? 'Maharashtra' : 'Karnataka'
              }));
            }}
            className="input-field"
          >
            <option value="STATE_A">Maharashtra (State A)</option>
            <option value="STATE_B">Karnataka (State B)</option>
          </select>
        </div>
        
        {isProcessing && (
          <div className="mb-8">
            <StepIndicator
              steps={registrationSteps}
              currentStep={currentStep}
              completedSteps={completedSteps}
            />
            <LoadingSpinner message={processingMessage} />
          </div>
        )}
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Registration Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Details */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Personal Details</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date of Birth *
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleInputChange}
                  className="input-field"
                  max={new Date(new Date().setFullYear(new Date().getFullYear() - 18)).toISOString().split('T')[0]}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender *
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="input-field"
                  required
                >
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Address */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Address</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address Line 1 *
                </label>
                <input
                  type="text"
                  name="address_line1"
                  value={formData.address_line1}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="House no., Street"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address Line 2
                </label>
                <input
                  type="text"
                  name="address_line2"
                  value={formData.address_line2}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="Landmark, Area"
                />
              </div>
              
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City *
                  </label>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    className="input-field"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State *
                  </label>
                  <input
                    type="text"
                    name="state"
                    value={formData.state}
                    className="input-field bg-gray-100"
                    readOnly
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pincode *
                  </label>
                  <input
                    type="text"
                    name="pincode"
                    value={formData.pincode}
                    onChange={handleInputChange}
                    className="input-field"
                    maxLength={6}
                    pattern="\d{6}"
                    required
                  />
                </div>
              </div>
            </div>
          </div>
          
          {/* Contact */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Contact Information</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="input-field"
                  maxLength={10}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input-field"
                />
              </div>
            </div>
          </div>
          
          {/* Photo Upload */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Photo Upload *</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {photoPreview ? (
                <div className="flex flex-col items-center">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-48 h-48 object-cover rounded-lg mb-4"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setPhotoFile(null);
                      setPhotoPreview('');
                    }}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove Photo
                  </button>
                </div>
              ) : (
                <div>
                  <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <label className="cursor-pointer">
                    <span className="btn-primary inline-flex items-center">
                      <Upload className="w-5 h-5 mr-2" />
                      Upload Photo
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoUpload}
                      className="hidden"
                      required
                    />
                  </label>
                  <p className="text-sm text-gray-500 mt-2">
                    Clear face photo required for AI verification
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {/* Submit Button */}
          <div className="flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn-secondary"
              disabled={isProcessing}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Register Voter'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}