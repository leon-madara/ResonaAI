/**
 * PersonalizedResources Component
 * 
 * Resources filtered to user's specific patterns and cultural context.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import { ExternalLink, BookOpen, Users, Heart } from 'lucide-react';
import './PersonalizedResources.css';

export interface PersonalizedResourcesProps {
  resources: Array<{
    id: string;
    title: string;
    type: 'article' | 'support_group' | 'guide' | 'video';
    reason: string;
    url?: string;
    location?: string;
  }>;
  filters: {
    mentalHealthNeeds: string[];
    culturalContext: string;
    triggers: string[];
    coping: string[];
  };
  maxItems?: number;
  showReason?: boolean;
  onResourceClick?: (resourceId: string) => void;
}

const RESOURCE_ICONS = {
  article: BookOpen,
  support_group: Users,
  guide: BookOpen,
  video: Heart,
};

const RESOURCE_EMOJIS = {
  article: '📄',
  support_group: '👥',
  guide: '📚',
  video: '🎥',
};

export const PersonalizedResources: React.FC<PersonalizedResourcesProps> = ({
  resources,
  filters,
  maxItems = 5,
  showReason = true,
  onResourceClick,
}) => {
  const displayedResources = resources.slice(0, maxItems);

  if (displayedResources.length === 0) {
    return null;
  }

  const getContextLabel = () => {
    const contexts: Record<string, string> = {
      kenya: 'Kenya',
      uganda: 'Uganda',
      tanzania: 'Tanzania',
      rwanda: 'Rwanda',
      east_africa: 'East Africa',
    };
    return contexts[filters.culturalContext] || filters.culturalContext;
  };

  const handleResourceClick = (resourceId: string) => {
    onResourceClick?.(resourceId);
  };

  return (
    <div className="personalized-resources">
      <div className="personalized-resources__header">
        <span className="personalized-resources__icon">📚</span>
        <h3 className="personalized-resources__title">Resources Chosen for You</h3>
      </div>

      <div className="personalized-resources__content">
        <p className="personalized-resources__intro">
          Based on what we've learned about your journey, these might help:
        </p>

        <ul className="personalized-resources__list">
          {displayedResources.map((resource) => {
            const Icon = RESOURCE_ICONS[resource.type] || BookOpen;
            const emoji = RESOURCE_EMOJIS[resource.type] || '📄';

            return (
              <li key={resource.id} className="personalized-resources__item">
                <div className="personalized-resources__item-header">
                  <span className="personalized-resources__item-emoji">{emoji}</span>
                  <div className="personalized-resources__item-title-section">
                    <h4 className="personalized-resources__item-title">{resource.title}</h4>
                    {resource.location && (
                      <span className="personalized-resources__item-location">
                        ({resource.location})
                      </span>
                    )}
                  </div>
                </div>

                {showReason && resource.reason && (
                  <p className="personalized-resources__item-reason">
                    → {resource.reason}
                  </p>
                )}

                <div className="personalized-resources__item-actions">
                  {resource.url ? (
                    <a
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="personalized-resources__item-link"
                      onClick={() => handleResourceClick(resource.id)}
                    >
                      {resource.type === 'support_group' ? 'Find Groups' : 'Read More'}
                      <ExternalLink className="personalized-resources__link-icon" />
                    </a>
                  ) : (
                    <button
                      className="personalized-resources__item-button"
                      onClick={() => handleResourceClick(resource.id)}
                    >
                      Learn More
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>

        {resources.length > maxItems && (
          <p className="personalized-resources__footer">
            {resources.length - maxItems} more resources available
          </p>
        )}
      </div>
    </div>
  );
};

export default PersonalizedResources;

