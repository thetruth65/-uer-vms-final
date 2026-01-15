export interface VoterRegistrationData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'MALE' | 'FEMALE' | 'OTHER';
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  pincode: string;
  phone_number?: string;
  email?: string;
  photo?: File;
}

export interface RegistrationStep {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

export interface RegistrationResponse {
  voter_id: string;
  status: string;
  message: string;
  blockchain_transaction_id: string;
  steps_completed: string[];
}

export interface VoterStatus {
  voter_id: string;
  name: string;
  status: string;
  current_state: string;
  is_voted: boolean;
  can_vote: boolean;
  registration_date: string;
  last_updated: string;
}

export interface TransferRequest {
  voter_id: string;
  from_state: string;
  to_state: string;
  new_address_line1: string;
  new_address_line2?: string;
  new_city: string;
  new_pincode: string;
}

export interface BlockchainBlock {
  block_number: number;
  transaction_id: string;
  voter_id: string;
  event_type: string;
  owner_state: string;
  data_hash: string;
  timestamp: string;
}

export interface DashboardStats {
  total_voters: number;
  active_voters: number;
  voted_voters: number;
  total_blockchain_blocks: number;
  recent_registrations: Array<{
    voter_id: string;
    name: string;
    registered_at: string;
  }>;
  recent_blockchain_events: Array<{
    transaction_id: string;
    event_type: string;
    voter_id: string;
    timestamp: string;
  }>;
}