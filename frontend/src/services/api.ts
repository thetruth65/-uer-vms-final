import axios from 'axios';
import type { 
  VoterRegistrationData, 
  RegistrationResponse,
  VoterStatus,
  TransferRequest,
  DashboardStats,
  BlockchainBlock 
} from '../types';

const API_BASE_STATE_A = import.meta.env.VITE_BACKEND_STATE_A_URL || 'http://localhost:8001';
const API_BASE_STATE_B = import.meta.env.VITE_BACKEND_STATE_B_URL || 'http://localhost:8002';

// Helper to get API base URL by state
const getApiBase = (stateId: string) => {
  return stateId === 'STATE_A' ? API_BASE_STATE_A : API_BASE_STATE_B;
};

export const api = {
  // Registration
  registerVoter: async (data: VoterRegistrationData, stateId: string): Promise<RegistrationResponse> => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value);
      }
    });

    const response = await axios.post(
      `${getApiBase(stateId)}/api/registration/register`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  },

  // Get voter status
  getVoterStatus: async (voterId: string, stateId: string): Promise<VoterStatus> => {
    const response = await axios.get(
      `${getApiBase(stateId)}/api/registration/status/${voterId}`
    );
    return response.data;
  },

  // Transfer voter
  transferVoter: async (data: TransferRequest): Promise<any> => {
    // Transfer request goes to the destination state
    const response = await axios.post(
      `${getApiBase(data.to_state)}/api/transfer/transfer`,
      data
    );
    return response.data;
  },

  // Vote
  castVote: async (voterId: string, pollingBoothId: string, photo: File, stateId: string): Promise<any> => {
    const formData = new FormData();
    formData.append('voter_id', voterId);
    formData.append('polling_booth_id', pollingBoothId);
    formData.append('photo', photo);

    const response = await axios.post(
      `${getApiBase(stateId)}/api/voting/vote`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    );
    return response.data;
  },

  // Check voting eligibility
  checkEligibility: async (voterId: string, stateId: string): Promise<any> => {
    const response = await axios.get(
      `${getApiBase(stateId)}/api/voting/eligibility/${voterId}`
    );
    return response.data;
  },

  // Admin - Dashboard stats
  getDashboardStats: async (stateId: string): Promise<DashboardStats> => {
    const response = await axios.get(
      `${getApiBase(stateId)}/api/admin/dashboard`
    );
    return response.data;
  },

  // Admin - Blockchain explorer
  getBlockchainBlocks: async (stateId: string, skip = 0, limit = 20): Promise<{ total_blocks: number; blocks: BlockchainBlock[] }> => {
    const response = await axios.get(
      `${getApiBase(stateId)}/api/admin/blockchain/explorer?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Admin - Audit logs
  getAuditLogs: async (stateId: string, skip = 0, limit = 50): Promise<any> => {
    const response = await axios.get(
      `${getApiBase(stateId)}/api/admin/audit-logs?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // [NEW] Integrity Functions
  checkIntegrity: async (stateId: string): Promise<any[]> => {
    const response = await axios.post(`${getApiBase(stateId)}/api/admin/run-integrity-check`);
    return response.data;
  },

  simulateHack: async (voterId: string, stateId: string): Promise<any> => {
    const response = await axios.post(`${getApiBase(stateId)}/api/admin/simulate-hack/${voterId}`);
    return response.data;
  }
};