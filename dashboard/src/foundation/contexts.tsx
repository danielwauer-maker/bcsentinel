import { createContext, PropsWithChildren, useContext, useMemo } from 'react';
import type { TenantSession } from '../api/client';

export type AuthState = {
  authenticated: boolean;
  identity?: string;
  provider?: string;
  credentialMode?: 'session-token' | 'legacy-api-token';
};

export type EntitlementState = {
  features: ReadonlySet<string>;
  access: 'granted' | 'locked' | 'expired' | 'consumed' | 'suspended' | 'pending';
};

const AuthContext = createContext<AuthState>({ authenticated: false });
const TenantContext = createContext<TenantSession | null>(null);
const EntitlementContext = createContext<EntitlementState>({ features: new Set(), access: 'pending' });

type RuntimeWindow = Window & { __BCSENTINEL_SESSION__?: TenantSession };

function runtimeSession(): TenantSession | null {
  if (typeof window === 'undefined') return null;
  const candidate = (window as RuntimeWindow).__BCSENTINEL_SESSION__;
  if (!candidate?.tenantId) return null;
  if (!candidate.sessionToken && !candidate.apiToken) return null;
  return candidate;
}

export function FoundationProviders({ children }: PropsWithChildren) {
  const tenant = useMemo<TenantSession | null>(() => runtimeSession(), []);
  const auth = useMemo<AuthState>(
    () => ({
      authenticated: Boolean(tenant),
      provider: tenant ? 'runtime-session' : undefined,
      identity: tenant?.tenantId,
      credentialMode: tenant?.sessionToken ? 'session-token' : tenant?.apiToken ? 'legacy-api-token' : undefined,
    }),
    [tenant],
  );
  // Authentication, tenant lifecycle and entitlements remain separate. The
  // presence of a runtime session never grants a product feature by itself.
  const entitlements = useMemo<EntitlementState>(() => ({ features: new Set<string>(), access: 'pending' }), []);

  return (
    <AuthContext.Provider value={auth}>
      <TenantContext.Provider value={tenant}>
        <EntitlementContext.Provider value={entitlements}>{children}</EntitlementContext.Provider>
      </TenantContext.Provider>
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
export const useTenant = () => useContext(TenantContext);
export const useEntitlements = () => useContext(EntitlementContext);

export function EntitlementGate({ feature, children, fallback }: PropsWithChildren<{ feature: string; fallback?: React.ReactNode }>) {
  const { features, access } = useEntitlements();
  if (access !== 'granted' || !features.has(feature)) return <>{fallback ?? null}</>;
  return <>{children}</>;
}
