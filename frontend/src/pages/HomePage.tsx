import React from 'react';
import { Link } from 'react-router-dom';
import { UserPlus, ArrowLeftRight, Vote, Shield, Zap, Globe } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      icon: Shield,
      title: 'Blockchain Security',
      description: 'Immutable records with cryptographic verification'
    },
    {
      icon: Zap,
      title: 'Instant Transfer',
      description: 'Seamless inter-state voter mobility'
    },
    {
      icon: Globe,
      title: 'Nationwide Lock',
      description: 'Prevent double voting across all states'
    }
  ];
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Unified Electoral Roll & Voter Mobility System
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          A blockchain-based hybrid architecture solving India's electoral challenges 
          with seamless inter-state voter mobility and tamper-proof verification.
        </p>
        
        <div className="flex justify-center gap-4">
          <Link to="/register" className="btn-primary inline-flex items-center">
            <UserPlus className="w-5 h-5 mr-2" />
            Register as Voter
          </Link>
          <Link to="/admin" className="btn-secondary inline-flex items-center">
            View Dashboard
          </Link>
        </div>
      </div>
      
      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {features.map((feature, index) => (
          <div key={index} className="card text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <feature.icon className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
      </div>
      
      {/* Action Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <Link to="/register" className="card hover:shadow-xl transition-shadow cursor-pointer group">
          <UserPlus className="w-12 h-12 text-blue-600 mb-4 group-hover:scale-110 transition-transform" />
          <h3 className="text-2xl font-bold mb-2">Register</h3>
          <p className="text-gray-600">
            New voter registration with AI-powered duplicate detection
          </p>
        </Link>
        
        <Link to="/transfer" className="card hover:shadow-xl transition-shadow cursor-pointer group">
          <ArrowLeftRight className="w-12 h-12 text-green-600 mb-4 group-hover:scale-110 transition-transform" />
          <h3 className="text-2xl font-bold mb-2">Transfer</h3>
          <p className="text-gray-600">
            Transfer voter registration between states seamlessly
          </p>
        </Link>
        
        <Link to="/vote" className="card hover:shadow-xl transition-shadow cursor-pointer group">
          <Vote className="w-12 h-12 text-purple-600 mb-4 group-hover:scale-110 transition-transform" />
          <h3 className="text-2xl font-bold mb-2">Vote</h3>
          <p className="text-gray-600">
            Cast your vote with biometric verification
          </p>
        </Link>
      </div>
      
      {/* Stats Section */}
      <div className="mt-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-white">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">2</div>
            <div className="text-blue-100">States Connected</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">100%</div>
            <div className="text-blue-100">Blockchain Secured</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">&lt;2s</div>
            <div className="text-blue-100">Transfer Time</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">0</div>
            <div className="text-blue-100">Duplicate Votes</div>
          </div>
        </div>
      </div>
    </div>
  );
}