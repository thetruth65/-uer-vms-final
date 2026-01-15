import React, { useState, useEffect } from 'react';
import { BarChart3, Users, Vote, Database } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import IntegrityCheck from '../components/Admin/IntegrityCheck';

export default function AdminDashboard() {
  const [selectedState, setSelectedState] = useState('STATE_A');
  const [stats, setStats] = useState<any>(null);
  const [blocks, setBlocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadData();
  }, [selectedState]);
  
  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, blocksData] = await Promise.all([
        api.getDashboardStats(selectedState),
        api.getBlockchainBlocks(selectedState, 0, 20)
      ]);
      setStats(statsData);
      setBlocks(blocksData.blocks || []);
    } catch (err) {
      console.error('Failed to load data', err);
      // Fallback to prevent crash
      setStats({
        total_voters: 0,
        active_voters: 0,
        voted_voters: 0,
        total_blockchain_blocks: 0
      });
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading Dashboard...</div>;
  }

  // Safety check: If stats is still null for some reason, don't render
  if (!stats) return <div className="p-8">Error loading dashboard stats. Check Backend connection.</div>;
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="input-field w-auto"
        >
          <option value="STATE_A">Maharashtra</option>
          <option value="STATE_B">Karnataka</option>
        </select>
      </div>
      
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <Users className="w-8 h-8 text-blue-600 mb-2" />
          <div className="text-3xl font-bold">{stats.total_voters}</div>
          <div className="text-gray-600">Total Voters</div>
        </div>
        <div className="card">
          <Vote className="w-8 h-8 text-green-600 mb-2" />
          <div className="text-3xl font-bold">{stats.active_voters}</div>
          <div className="text-gray-600">Active Voters</div>
        </div>
        <div className="card">
          <BarChart3 className="w-8 h-8 text-purple-600 mb-2" />
          <div className="text-3xl font-bold">{stats.voted_voters}</div>
          <div className="text-gray-600">Voted</div>
        </div>
        <div className="card">
          <Database className="w-8 h-8 text-indigo-600 mb-2" />
          <div className="text-3xl font-bold">{stats.total_blockchain_blocks}</div>
          <div className="text-gray-600">Blockchain Blocks</div>
        </div>
      </div>

      <div className="card mb-8">
        <h2 className="text-2xl font-bold mb-4">Real-Time Blockchain Ledger</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Block #</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Voter ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Owner State</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {blocks.length > 0 ? blocks.map((block) => (
                <tr key={block.block_number + block.timestamp}>
                  <td className="px-4 py-3 text-sm font-mono text-blue-600 font-bold">{block.block_number}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={block.event_type} />
                  </td>
                  <td className="px-4 py-3 text-sm font-mono">{block.voter_id ? block.voter_id.substring(0, 8) + '...' : '-'}</td>
                  <td className="px-4 py-3 text-sm">{block.owner_state}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(block.timestamp * 1000).toLocaleString()}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">No blocks found on the chain yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <IntegrityCheck stateId={selectedState} />
    </div>
  );
}