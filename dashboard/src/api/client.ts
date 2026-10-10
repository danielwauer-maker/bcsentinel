export type TenantSession = {
  tenantId: string;
  sessionToken?: string;
  apiToken?: string;
  preferredLanguage?: string;
};

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

export async function apiRequest<T>(path: string, session: TenantSession, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');

  if (session.sessionToken) {
    headers.set('Authorization', `Bearer ${session.sessionToken}`);
  } else if (session.apiToken) {
    // Legacy/machine-runtime compatibility. Production dashboard hosts should
    // exchange the machine credential for a short-lived session token first.
    headers.set('X-Tenant-Id', session.tenantId);
    headers.set('X-Api-Token', session.apiToken);
  } else {
    throw new ApiError(401, 'No tenant session credential is available.');
  }

  if (session.preferredLanguage) headers.set('X-Preferred-Language', session.preferredLanguage);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const response = await fetch(`${baseUrl}${path}`, { ...init, headers, credentials: 'omit' });
  if (!response.ok) {
    const safeMessage = response.status === 403 ? 'Access denied.' : response.status === 404 ? 'Resource not found.' : 'The request could not be completed.';
    throw new ApiError(response.status, safeMessage);
  }
  return response.json() as Promise<T>;
}
