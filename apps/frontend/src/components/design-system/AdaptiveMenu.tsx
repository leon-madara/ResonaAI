/**
 * AdaptiveMenu Component
 * 
 * Navigation that reorganizes based on usage and needs.
 * Part of the ResonaAI Design System.
 */

import React, { useState } from 'react';
import { Menu, X, Home, MessageCircle, HelpCircle, Settings, User } from 'lucide-react';
import './AdaptiveMenu.css';

export interface AdaptiveMenuProps {
  items: Array<{
    id: string;
    label: string;
    icon: string;
    usageCount: number;
    priority: number;
    visible: boolean;
    isNew?: boolean;
    badge?: string;
  }>;
  layout: 'bottom' | 'sidebar' | 'hamburger';
  isCrisisMode?: boolean;
  onItemClick?: (itemId: string) => void;
}

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  home: Home,
  chat: MessageCircle,
  help: HelpCircle,
  settings: Settings,
  profile: User,
};

export const AdaptiveMenu: React.FC<AdaptiveMenuProps> = ({
  items,
  layout,
  isCrisisMode = false,
  onItemClick,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Filter and sort items
  const visibleItems = items
    .filter(item => item.visible)
    .sort((a, b) => {
      // In crisis mode, prioritize by priority field
      if (isCrisisMode) {
        return b.priority - a.priority;
      }
      // Otherwise, sort by usage count
      return b.usageCount - a.usageCount;
    });

  // In crisis mode, only show critical items
  const displayedItems = isCrisisMode
    ? visibleItems.filter(item => item.priority >= 8)
    : visibleItems;

  const handleItemClick = (itemId: string) => {
    onItemClick?.(itemId);
    if (layout === 'hamburger') {
      setIsOpen(false);
    }
  };

  if (layout === 'hamburger') {
    return (
      <div className="adaptive-menu adaptive-menu--hamburger">
        <button
          className="adaptive-menu__toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="adaptive-menu__toggle-icon" /> : <Menu className="adaptive-menu__toggle-icon" />}
        </button>

        {isOpen && (
          <div className="adaptive-menu__dropdown">
            {displayedItems.map((item) => {
              const Icon = ICON_MAP[item.icon] || Home;
              return (
                <button
                  key={item.id}
                  className="adaptive-menu__item"
                  onClick={() => handleItemClick(item.id)}
                >
                  <Icon className="adaptive-menu__item-icon" />
                  <span className="adaptive-menu__item-label">{item.label}</span>
                  {item.isNew && (
                    <span className="adaptive-menu__item-badge adaptive-menu__item-badge--new">New</span>
                  )}
                  {item.badge && (
                    <span className="adaptive-menu__item-badge">{item.badge}</span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  if (layout === 'sidebar') {
    return (
      <nav className="adaptive-menu adaptive-menu--sidebar">
        <ul className="adaptive-menu__list">
          {displayedItems.map((item) => {
            const Icon = ICON_MAP[item.icon] || Home;
            return (
              <li key={item.id} className="adaptive-menu__list-item">
                <button
                  className="adaptive-menu__item"
                  onClick={() => handleItemClick(item.id)}
                >
                  <Icon className="adaptive-menu__item-icon" />
                  <span className="adaptive-menu__item-label">{item.label}</span>
                  {item.isNew && (
                    <span className="adaptive-menu__item-badge adaptive-menu__item-badge--new">New</span>
                  )}
                  {item.badge && (
                    <span className="adaptive-menu__item-badge">{item.badge}</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>
    );
  }

  // Bottom layout (default)
  return (
    <nav className="adaptive-menu adaptive-menu--bottom">
      <ul className="adaptive-menu__list">
        {displayedItems.map((item) => {
          const Icon = ICON_MAP[item.icon] || Home;
          return (
            <li key={item.id} className="adaptive-menu__list-item">
              <button
                className="adaptive-menu__item"
                onClick={() => handleItemClick(item.id)}
                aria-label={item.label}
              >
                <Icon className="adaptive-menu__item-icon" />
                <span className="adaptive-menu__item-label">{item.label}</span>
                {item.isNew && (
                  <span className="adaptive-menu__item-badge adaptive-menu__item-badge--new">New</span>
                )}
                {item.badge && (
                  <span className="adaptive-menu__item-badge">{item.badge}</span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default AdaptiveMenu;

