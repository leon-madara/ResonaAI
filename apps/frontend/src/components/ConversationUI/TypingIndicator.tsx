import React from 'react';
import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import './TypingIndicator.css';

const TypingIndicator: React.FC = () => {
  return (
    <motion.div
      className="typing-indicator"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      <div className="typing-avatar">
        <Bot className="w-5 h-5" />
      </div>
      
      <div className="typing-content">
        <div className="typing-bubble">
          <div className="typing-dots">
            <motion.span
              className="dot"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
            />
            <motion.span
              className="dot"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
            />
            <motion.span
              className="dot"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
            />
          </div>
        </div>
        <div className="typing-label">AI is thinking...</div>
      </div>
    </motion.div>
  );
};

export default TypingIndicator;
