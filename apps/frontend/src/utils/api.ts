/**
 * API helpers for the web app.
 *
 * Purpose:
 * - Centralize API base URL selection (dev/prod)
 * - Avoid sprinkling hardcoded `/api/...` proxy paths across the app
 */
export function getApiBaseUrl(): string {
  // CRA exposes env vars prefixed with REACT_APP_*
  const envUrl = process.env.REACT_APP_API_BASE_URL;
  if (envUrl && envUrl.trim().length > 0) return envUrl.trim().replace(/\/+$/, '');

  // Default to local API gateway
  return 'http://localhost:8000';
}

export function getAuthHeader(token: string | null | undefined): Record<string, string> {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function readJsonOrText(response: Response): Promise<any> {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return await response.json();
  return await response.text();
}

/**
 * API utility functions for frontend pages
 */

// Data Export API
export interface ExportRequest {
  user_id: string;
  format?: 'json' | 'csv';
  encrypt?: boolean;
  include_conversations?: boolean;
  include_emotions?: boolean;
  include_consents?: boolean;
  include_baselines?: boolean;
  include_sessions?: boolean;
}

export interface ExportResponse {
  request_id: string;
  status: string;
  message: string;
  expires_at?: string;
}

export async function exportUserData(
  token: string | null,
  request: ExportRequest
): Promise<ExportResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/data-management/export/request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify({
      user_id: request.user_id,
      format: request.format || 'json',
      encrypt: request.encrypt !== false,
      include_conversations: request.include_conversations !== false,
      include_emotions: request.include_emotions !== false,
      include_consents: request.include_consents !== false,
      include_baselines: request.include_baselines !== false,
      include_sessions: request.include_sessions !== false,
    }),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Export request failed');
  }

  return await response.json();
}

// Dissonance Detector API
export interface DissonanceAnalysisRequest {
  transcript: string;
  voice_emotion: {
    emotion: string;
    confidence: number;
  };
  session_id?: string;
  user_id?: string;
  timestamp?: string;
}

export interface DissonanceAnalysisResponse {
  dissonance_level: 'low' | 'medium' | 'high';
  dissonance_score: number;
  stated_emotion: string;
  actual_emotion: string;
  interpretation: string;
  risk_level: string;
  confidence: number;
  timestamp: string;
  details: {
    sentiment_score: number;
    emotion_score: number;
    gap: number;
    normalized_gap: number;
  };
}

export async function analyzeDissonance(
  token: string | null,
  request: DissonanceAnalysisRequest
): Promise<DissonanceAnalysisResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/dissonance-detector/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to analyze dissonance');
  }

  return await response.json();
}

// Baseline Tracker API - Update Baseline
export interface BaselineUpdateRequest {
  user_id: string;
  voice_features?: {
    pitch_mean: number;
    pitch_std: number;
    energy_mean: number;
    energy_std: number;
    speech_rate?: number;
    pause_frequency?: number;
    duration?: number;
  };
  emotion_data?: {
    emotion: string;
    confidence: number;
  };
  session_id?: string;
}

export interface BaselineUpdateResponse {
  user_id: string;
  voice_fingerprint?: {
    user_id: string;
    features: {
      pitch_mean: number;
      pitch_std: number;
      energy_mean: number;
      energy_std: number;
      speech_rate: number;
      pause_frequency: number;
    };
    confidence: number;
    calculated_at: string;
  };
  emotion_baseline?: {
    user_id: string;
    emotion_distribution: Record<string, number>;
    average_confidence: number;
    dominant_emotion: string;
    baseline_period_days: number;
    sample_count: number;
    calculated_at: string;
  };
  deviation_score?: number;
  deviation_detected: boolean;
  message: string;
}

export async function updateBaseline(
  token: string | null,
  request: BaselineUpdateRequest
): Promise<BaselineUpdateResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/baseline-tracker/baseline/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to update baseline');
  }

  return await response.json();
}

// Baseline Tracker API - Check Deviation
export interface DeviationCheckRequest {
  user_id: string;
  voice_features?: {
    pitch_mean: number;
    pitch_std: number;
    energy_mean: number;
    energy_std: number;
    speech_rate?: number;
    pause_frequency?: number;
    duration?: number;
  };
  emotion_data?: {
    emotion: string;
    confidence: number;
  };
  session_id?: string;
}

export interface DeviationCheckResponse {
  user_id: string;
  deviation_type: string;
  deviation_score: number;
  baseline_value: any;
  current_value: any;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

export async function checkDeviation(
  token: string | null,
  request: DeviationCheckRequest
): Promise<DeviationCheckResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/baseline-tracker/baseline/check-deviation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to check deviation');
  }

  return await response.json();
}

// Account Deletion API
export interface DeletionRequest {
  user_id: string;
  reason?: string;
  immediate?: boolean;
}

export interface DeletionResponse {
  request_id: string;
  status: string;
  message: string;
  scheduled_deletion_date?: string;
  grace_period_days?: number;
}

export async function requestAccountDeletion(
  token: string | null,
  request: DeletionRequest
): Promise<DeletionResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/data-management/deletion/request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify({
      user_id: request.user_id,
      reason: request.reason || 'User requested account deletion',
      immediate: request.immediate || false,
    }),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Deletion request failed');
  }

  return await response.json();
}

// User Settings API
export interface UserSettings {
  language?: string;
  theme?: string;
  notifications?: {
    email?: boolean;
    push?: boolean;
    reminders?: boolean;
  };
}

export async function getUserSettings(
  token: string | null,
  user_id: string
): Promise<UserSettings> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/users/${user_id}/settings`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      // Return default settings if not found
      return {};
    }
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to get user settings');
  }

  return await response.json();
}

export async function saveUserSettings(
  token: string | null,
  user_id: string,
  settings: UserSettings
): Promise<UserSettings> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/users/${user_id}/settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(settings),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to save user settings');
  }

  return await response.json();
}

// Consent Management API
export interface ConsentRecord {
  consent_id: string;
  user_id: string;
  consent_type: string;
  granted: boolean;
  consent_version: string;
  granted_at?: string;
  revoked_at?: string;
  ip_address?: string;
  user_agent?: string;
}

export async function getConsents(
  token: string | null
): Promise<ConsentRecord[]> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/consent-management/consents`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to get consents');
  }

  return await response.json();
}

export interface ConsentUpdateRequest {
  consent_type: string;
  granted: boolean;
  consent_version: string;
}

export async function updateConsent(
  token: string | null,
  request: ConsentUpdateRequest
): Promise<ConsentRecord> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/consent-management/consents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to update consent');
  }

  return await response.json();
}

export async function revokeConsent(
  token: string | null,
  consent_type: string
): Promise<ConsentRecord> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/consent-management/consents/${consent_type}/revoke`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to revoke consent');
  }

  return await response.json();
}

// Session History API
export interface ConversationSession {
  session_id: string;
  user_id: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
  primary_emotion?: string;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
}

export async function getSessionHistory(
  token: string | null,
  user_id: string
): Promise<ConversationSession[]> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/conversations/${user_id}/sessions`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      return [];
    }
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to get session history');
  }

  return await response.json();
}

// Voice Baseline API
export interface VoiceBaseline {
  user_id: string;
  voice_fingerprint?: {
    user_id: string;
    features: {
      pitch_mean: number;
      pitch_std: number;
      energy_mean: number;
      energy_std: number;
      speech_rate: number;
      pause_frequency: number;
    };
    confidence: number;
    calculated_at: string;
  };
  emotion_baseline?: {
    user_id: string;
    emotion_distribution: Record<string, number>;
    average_confidence: number;
    dominant_emotion: string;
    baseline_period_days: number;
    sample_count: number;
    calculated_at: string;
  };
  deviation_history?: Array<{
    deviation_type: string;
    deviation_score: number;
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export async function getVoiceBaseline(
  token: string | null,
  user_id: string
): Promise<VoiceBaseline> {
  const apiBaseUrl = getApiBaseUrl();
  const response = await fetch(`${apiBaseUrl}/baseline-tracker/baseline/${user_id}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      // Return empty baseline if not found
      return { user_id };
    }
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to get voice baseline');
  }

  return await response.json();
}
