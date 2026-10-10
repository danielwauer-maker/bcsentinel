import { createContext, PropsWithChildren, useContext, useMemo } from 'react';
import type { TenantSession } from '../api/client';

export type AuthState = {
  authenticated: boolean;
  identity?: string;
  provider?: string;
};

export type EntitlementState = {
  features: ReadonlySet<string>;
  access: 'granted' | 'locked' | 'expired' | 'consumed' | 'suspended' | 'pending';
};

const AuthContext = createContext<AuthState>({ authenticated: false });
const TenantContext = createContext<TenantSession | null>(null);
const EntitlementContext = createContext<EntitlementState>({ features: new Set(), access: 'pending' });

export function FoundationProviders({ children }: PropsWithChildren) {
  // Runtime identity-provider/session binding is injected here in D8/E1.
  // D6 intentionally does not invent credentials or treat authentication as product access.
  const auth = useMemo<AuthState>(() => ({ authenticated: false }), []);
  const tenant = useMemo<TenantSession | null>(() => null, []);
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
