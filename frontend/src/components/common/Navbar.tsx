import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Vote, UserPlus, ArrowLeftRight, LayoutDashboard, Home } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/register', label: 'Register', icon: UserPlus },
    { path: '/transfer', label: 'Transfer', icon: ArrowLeftRight },
    { path: '/vote', label: 'Vote', icon: Vote },
    { path: '/admin', label: 'Admin', icon: LayoutDashboard },
  ];
  
  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Vote className="w-8 h-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">
              UER-VMS
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center px-4 py-2 rounded-lg transition-all ${
                  isActive(path)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5 mr-2" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
