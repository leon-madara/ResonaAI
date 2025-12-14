import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Lock, Heart, Loader2, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './RegisterPage.css';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  // Enhanced email validation
  const validateEmail = (emailValue: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailValue) {
      setEmailError('');
      return false;
    }
    if (!emailRegex.test(emailValue)) {
      setEmailError('Please enter a valid email address');
      return false;
    }
    const domain = emailValue.split('@')[1];
    if (domain && (domain.startsWith('.') || domain.endsWith('.') || !domain.includes('.'))) {
      setEmailError('Please enter a valid email domain');
      return false;
    }
    setEmailError('');
    return true;
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    if (value) {
      validateEmail(value);
    } else {
      setEmailError('');
    }
  };

  // Enhanced password strength calculation
  const passwordStrength = (pwd: string) => {
    const checks = {
      length: pwd.length >= 8,
      lowercase: /[a-z]/.test(pwd),
      uppercase: /[A-Z]/.test(pwd),
      number: /\d/.test(pwd),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
    };
    
    if (pwd.length === 0) return { strength: 0, label: '', color: '', checks };

    let score = 0;
    if (checks.length) score++;
    if (checks.lowercase) score++;
    if (checks.uppercase) score++;
    if (checks.number) score++;
    if (checks.special) score++;

    let strength = 0;
    let label = '';
    let color = '';

    if (pwd.length < 6) {
      strength = 1;
      label = 'Very Weak';
      color = '#ef4444';
    } else if (score <= 2) {
      strength = 1;
      label = 'Weak';
      color = '#f59e0b';
    } else if (score <= 3) {
      strength = 2;
      label = 'Fair';
      color = '#3b82f6';
    } else if (score <= 4) {
      strength = 3;
      label = 'Good';
      color = '#10b981';
    } else {
      strength = 4;
      label = 'Strong';
      color = '#059669';
    }

    return { strength, label, color, checks };
  };

  const strength = passwordStrength(password);

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    if (value && value.length < 6) {
      setPasswordError('Password must be at least 6 characters');
    } else {
      setPasswordError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (!validateEmail(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    if (strength.strength < 2) {
      toast.error('Please choose a stronger password');
      return;
    }

    if (!consentAccepted) {
      toast.error('Please accept the terms and privacy policy');
      return;
    }

    setIsLoading(true);
    try {
      await register(email, password, '1.0');
      navigate('/consent');
    } catch (error) {
      // Error is already handled in AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Heart className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <h1 className="text-3xl font-bold">ResonaAI</h1>
          </div>
          <h2 className="text-2xl font-semibold text-center mb-2">Create your account</h2>
          <p className="text-gray-600 dark:text-gray-400 text-center">
            Start your mental health journey today
          </p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              <Mail className="w-4 h-4" />
              Email
            </label>
            <div className="input-wrapper">
              <input
                id="email"
                type="email"
                value={email}
                onChange={handleEmailChange}
                onBlur={() => email && validateEmail(email)}
                className={`form-input ${emailError ? 'error' : email && !emailError ? 'valid' : ''}`}
                placeholder="your.email@example.com"
                required
                disabled={isLoading}
                aria-invalid={!!emailError}
                aria-describedby={emailError ? 'email-error' : undefined}
              />
              {email && !emailError && (
                <CheckCircle className="input-icon valid-icon" />
              )}
              {emailError && (
                <AlertCircle className="input-icon error-icon" />
              )}
            </div>
            {emailError && (
              <span id="email-error" className="error-message" role="alert">
                {emailError}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              <Lock className="w-4 h-4" />
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={handlePasswordChange}
              className={`form-input ${passwordError ? 'error' : ''}`}
              placeholder="Create a password"
              required
              disabled={isLoading}
              aria-invalid={!!passwordError}
              aria-describedby={passwordError ? 'password-error' : undefined}
            />
            {passwordError && (
              <span id="password-error" className="error-message" role="alert">
                {passwordError}
              </span>
            )}
            {password && (
              <div className="password-strength">
                <div className="strength-bar">
                  <div
                    className={`strength-fill strength-${strength.strength}`}
                    style={{ 
                      width: `${(strength.strength / 4) * 100}%`,
                      backgroundColor: strength.color
                    }}
                  />
                </div>
                <span className="strength-label" style={{ color: strength.color }}>
                  {strength.label}
                </span>
              </div>
            )}
            {password && (
              <div className="password-requirements">
                <div className={`requirement ${strength.checks.length ? 'met' : ''}`}>
                  {strength.checks.length ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  <span>At least 8 characters</span>
                </div>
                <div className={`requirement ${strength.checks.lowercase ? 'met' : ''}`}>
                  {strength.checks.lowercase ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  <span>Lowercase letter</span>
                </div>
                <div className={`requirement ${strength.checks.uppercase ? 'met' : ''}`}>
                  {strength.checks.uppercase ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  <span>Uppercase letter</span>
                </div>
                <div className={`requirement ${strength.checks.number ? 'met' : ''}`}>
                  {strength.checks.number ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  <span>Number</span>
                </div>
                <div className={`requirement ${strength.checks.special ? 'met' : ''}`}>
                  {strength.checks.special ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  <span>Special character</span>
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              <Lock className="w-4 h-4" />
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="form-input"
              placeholder="Confirm your password"
              required
              disabled={isLoading}
            />
            {confirmPassword && password === confirmPassword && (
              <div className="password-match">
                <CheckCircle className="w-4 h-4" />
                Passwords match
              </div>
            )}
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={consentAccepted}
                onChange={(e) => setConsentAccepted(e.target.checked)}
                disabled={isLoading}
                className="checkbox"
              />
              <span>
                I agree to the{' '}
                <Link to="/consent" className="link">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/consent" className="link">
                  Privacy Policy
                </Link>
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading || !!emailError || !!passwordError || strength.strength < 2}
            className="register-button"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className="social-login">
          <div className="social-divider">
            <span>Or sign up with</span>
          </div>
          <div className="social-buttons">
            <button
              type="button"
              className="social-button"
              disabled={isLoading}
              onClick={() => toast('Social registration coming soon')}
            >
              <svg className="social-icon" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>
            <button
              type="button"
              className="social-button"
              disabled={isLoading}
              onClick={() => toast('Social registration coming soon')}
            >
              <svg className="social-icon" viewBox="0 0 24 24" fill="#1877F2">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
          </div>
        </div>

        <div className="register-footer">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

