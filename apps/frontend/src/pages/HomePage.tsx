import React from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Heart, TrendingUp, Shield, Globe } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { CulturalGreeting } from '../components/design-system';
import './HomePage.css';

const HomePage: React.FC = () => {
  const { user } = useAuth();
  
  // Determine time of day
  const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' | 'night' => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 22) return 'evening';
    return 'night';
  };

  return (
    <div className="home-page">
      <div className="home-hero">
        <CulturalGreeting
          language="english"
          timeOfDay={getTimeOfDay()}
          mood="warm"
          userName={user?.email?.split('@')[0]}
        />
        <p className="home-subtitle">
          Your voice-first mental health companion for East Africa
        </p>
        <Link to="/chat" className="home-cta">
          <MessageSquare className="w-5 h-5" />
          Start a Conversation
        </Link>
      </div>

      <div className="home-features">
        <div className="feature-card">
          <div className="feature-icon">
            <Heart className="w-6 h-6" />
          </div>
          <h3 className="feature-title">Empathetic AI</h3>
          <p className="feature-description">
            Our AI understands cultural context and provides culturally-sensitive support
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">
            <Shield className="w-6 h-6" />
          </div>
          <h3 className="feature-title">Privacy First</h3>
          <p className="feature-description">
            Your conversations are encrypted and stored securely in East Africa
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h3 className="feature-title">Track Progress</h3>
          <p className="feature-description">
            Monitor your emotional well-being over time with personalized insights
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">
            <Globe className="w-6 h-6" />
          </div>
          <h3 className="feature-title">Offline Support</h3>
          <p className="feature-description">
            Continue your journey even without internet connectivity
          </p>
        </div>
      </div>

      <div className="home-quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/chat" className="action-card">
            <MessageSquare className="w-6 h-6" />
            <span>New Conversation</span>
          </Link>
          <Link to="/profile" className="action-card">
            <Heart className="w-6 h-6" />
            <span>View Profile</span>
          </Link>
          <Link to="/settings" className="action-card">
            <Shield className="w-6 h-6" />
            <span>Settings</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;

