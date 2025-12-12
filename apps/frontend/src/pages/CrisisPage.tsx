import React from 'react';
import { Phone, MessageCircle, Globe, Heart, AlertTriangle } from 'lucide-react';
import './CrisisPage.css';

const CrisisPage: React.FC = () => {
  const emergencyContacts = [
    {
      name: 'Kenya Mental Health Helpline',
      phone: '+254 800 723 333',
      available: '24/7',
    },
    {
      name: 'Uganda Mental Health Helpline',
      phone: '+256 800 200 600',
      available: '24/7',
    },
    {
      name: 'Tanzania Mental Health Helpline',
      phone: '+255 800 111 222',
      available: '24/7',
    },
  ];

  const resources = [
    {
      title: 'Immediate Help',
      description: 'If you are in immediate danger, please call emergency services',
      action: 'Call 999',
      urgent: true,
    },
    {
      title: 'Crisis Text Line',
      description: 'Text with a trained crisis counselor',
      action: 'Text HOME to 741741',
      urgent: false,
    },
    {
      title: 'Safety Planning',
      description: 'Create a safety plan for difficult moments',
      action: 'Learn More',
      urgent: false,
    },
  ];

  return (
    <div className="crisis-page">
      <div className="crisis-hero">
        <AlertTriangle className="w-12 h-12 text-red-600 dark:text-red-400 mb-4" />
        <h1 className="crisis-title">Crisis Support</h1>
        <p className="crisis-subtitle">
          You are not alone. Help is available 24/7.
        </p>
      </div>

      <div className="crisis-content">
        <div className="crisis-section urgent">
          <h2 className="section-title">
            <Phone className="w-6 h-6" />
            Emergency Contacts
          </h2>
          <div className="contacts-list">
            {emergencyContacts.map((contact, index) => (
              <div key={index} className="contact-card">
                <div className="contact-info">
                  <h3 className="contact-name">{contact.name}</h3>
                  <p className="contact-phone">{contact.phone}</p>
                  <p className="contact-available">Available: {contact.available}</p>
                </div>
                <a
                  href={`tel:${contact.phone.replace(/\s/g, '')}`}
                  className="contact-button"
                >
                  <Phone className="w-5 h-5" />
                  Call Now
                </a>
              </div>
            ))}
          </div>
        </div>

        <div className="crisis-section">
          <h2 className="section-title">
            <Heart className="w-6 h-6" />
            Resources & Support
          </h2>
          <div className="resources-grid">
            {resources.map((resource, index) => (
              <div
                key={index}
                className={`resource-card ${resource.urgent ? 'urgent' : ''}`}
              >
                <h3 className="resource-title">{resource.title}</h3>
                <p className="resource-description">{resource.description}</p>
                <button className="resource-button">
                  {resource.action}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="crisis-section">
          <h2 className="section-title">
            <Globe className="w-6 h-6" />
            Additional Resources
          </h2>
          <div className="additional-resources">
            <div className="resource-item">
              <MessageCircle className="w-5 h-5" />
              <div>
                <h4>Online Support Groups</h4>
                <p>Connect with others who understand what you're going through</p>
              </div>
            </div>
            <div className="resource-item">
              <Heart className="w-5 h-5" />
              <div>
                <h4>Self-Care Resources</h4>
                <p>Tools and techniques to help you manage difficult moments</p>
              </div>
            </div>
          </div>
        </div>

        <div className="crisis-footer">
          <p className="crisis-message">
            Remember: It's okay to ask for help. Reaching out is a sign of strength, not weakness.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CrisisPage;

