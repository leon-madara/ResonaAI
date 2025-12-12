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


