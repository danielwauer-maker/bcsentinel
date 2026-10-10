export type TenantSession = {
  tenantId: string;
  sessionToken?: string;
  apiToken?: string;
  accountSessionToken?: string;
  preferredLanguage?: string;
  tenantLabel?: string;
  role?: string;
  userEmail?: string;
};

export type AccountTenantSummary = {
  tenant_id: string;
  environment_name: string;
  role: string;
  membership_status: string;
  tenant_status: string;
  current_plan: string;
  license_status: string;
};

export type AccountTenantListResponse = {
  user_identity_id: number;
  tenants: AccountTenantSummary[];
};

export type TenantSwitchResponse = {
  tenant_id: string;
  session_token: string;
  token_type: string;
  expires_in_seconds: number;
  scope: string;
  role: string;
  user_identity_id: number;
};

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const safeMessage = response.status === 401
      ? 'Authentication required.'
      : response.status === 403
        ? 'Access denied.'
        : response.status === 404
          ? 'Resource not found.'
          : 'The request could not be completed.';
    throw new ApiError(response.status, safeMessage);
  }
  return response.json() as Promise<T>;
}

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
  return parseResponse<T>(response);
}

export async function accountRequest<T>(path: string, accountSessionToken: string, init: RequestInit = {}): Promise<T> {
  const token = accountSessionToken.trim();
  if (!token) throw new ApiError(401, 'No account session credential is available.');
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers, credentials: 'omit' });
  return parseResponse<T>(response);
}

export function listAccountTenants(accountSessionToken: string) {
  return accountRequest<AccountTenantListResponse>('/auth/account/tenants', accountSessionToken);
}

export function createTenantSession(accountSessionToken: string, tenantId: string) {
  return accountRequest<TenantSwitchResponse>('/auth/account/tenant-session', accountSessionToken, {
    method: 'POST',
    body: JSON.stringify({ tenant_id: tenantId }),
  });
}
