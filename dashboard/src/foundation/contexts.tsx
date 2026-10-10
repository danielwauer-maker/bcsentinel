import {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  ApiError,
  createTenantSession,
  listAccountTenants,
  type AccountTenantSummary,
  type TenantSession,
} from '../api/client';

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

export type TenantSwitcherState = {
  tenants: AccountTenantSummary[];
  loading: boolean;
  switching: boolean;
  error?: string;
  canSwitch: boolean;
  switchTenant: (tenantId: string) => Promise<void>;
  refreshTenants: () => Promise<void>;
};

const AuthContext = createContext<AuthState>({ authenticated: false });
const TenantContext = createContext<TenantSession | null>(null);
const TenantSwitcherContext = createContext<TenantSwitcherState>({
  tenants: [],
  loading: false,
  switching: false,
  canSwitch: false,
  switchTenant: async () => undefined,
  refreshTenants: async () => undefined,
});
const EntitlementContext = createContext<EntitlementState>({ features: new Set(), access: 'pending' });

type RuntimeWindow = Window & { __BCSENTINEL_SESSION__?: TenantSession };

function runtimeSession(): TenantSession | null {
  if (typeof window === 'undefined') return null;
  const candidate = (window as RuntimeWindow).__BCSENTINEL_SESSION__;
  if (!candidate?.tenantId) return null;
  if (!candidate.sessionToken && !candidate.apiToken) return null;
  return candidate;
}

function safeSwitcherError(reason: unknown): string {
  if (reason instanceof ApiError) {
    if (reason.status === 401 || reason.status === 403) return 'Die Account-Sitzung ist nicht mehr gültig.';
  }
  return 'Die verfügbaren Tenants konnten nicht geladen werden.';
}

export function FoundationProviders({ children }: PropsWithChildren) {
  const initialTenant = useMemo<TenantSession | null>(() => runtimeSession(), []);
  const [tenant, setTenant] = useState<TenantSession | null>(initialTenant);
  const [tenants, setTenants] = useState<AccountTenantSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState<string | undefined>();
  const accountSessionToken = initialTenant?.accountSessionToken?.trim() || '';

  const refreshTenants = useCallback(async () => {
    if (!accountSessionToken) {
      setTenants([]);
      return;
    }
    setLoading(true);
    setSwitchError(undefined);
    try {
      const result = await listAccountTenants(accountSessionToken);
      setTenants(result.tenants);
    } catch (reason) {
      setSwitchError(safeSwitcherError(reason));
    } finally {
      setLoading(false);
    }
  }, [accountSessionToken]);

  useEffect(() => {
    void refreshTenants();
  }, [refreshTenants]);

  const switchTenant = useCallback(async (tenantId: string) => {
    if (!accountSessionToken) throw new ApiError(401, 'No account session credential is available.');
    if (!tenantId || tenantId === tenant?.tenantId) return;
    setSwitching(true);
    setSwitchError(undefined);
    try {
      const result = await createTenantSession(accountSessionToken, tenantId);
      const summary = tenants.find((item) => item.tenant_id === result.tenant_id);
      setTenant({
        tenantId: result.tenant_id,
        sessionToken: result.session_token,
        accountSessionToken,
        preferredLanguage: tenant?.preferredLanguage,
        tenantLabel: summary?.environment_name || result.tenant_id,
        role: result.role,
        userEmail: tenant?.userEmail,
      });
    } catch (reason) {
      const message = safeSwitcherError(reason);
      setSwitchError(message);
      throw reason;
    } finally {
      setSwitching(false);
    }
  }, [accountSessionToken, tenant, tenants]);

  const auth = useMemo<AuthState>(
    () => ({
      authenticated: Boolean(tenant),
      provider: tenant ? 'runtime-session' : undefined,
      identity: tenant?.userEmail || tenant?.tenantId,
      credentialMode: tenant?.sessionToken ? 'session-token' : tenant?.apiToken ? 'legacy-api-token' : undefined,
    }),
    [tenant],
  );

  // Authentication, tenant lifecycle and entitlements remain separate. The
  // presence of a runtime session never grants a product feature by itself.
  const entitlements = useMemo<EntitlementState>(() => ({ features: new Set<string>(), access: 'pending' }), [tenant?.tenantId]);

  const switcher = useMemo<TenantSwitcherState>(() => ({
    tenants,
    loading,
    switching,
    error: switchError,
    canSwitch: Boolean(accountSessionToken && tenants.length > 1),
    switchTenant,
    refreshTenants,
  }), [tenants, loading, switching, switchError, accountSessionToken, switchTenant, refreshTenants]);

  return (
    <AuthContext.Provider value={auth}>
      <TenantContext.Provider value={tenant}>
        <TenantSwitcherContext.Provider value={switcher}>
          <EntitlementContext.Provider value={entitlements}>{children}</EntitlementContext.Provider>
        </TenantSwitcherContext.Provider>
      </TenantContext.Provider>
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
export const useTenant = () => useContext(TenantContext);
export const useTenantSwitcher = () => useContext(TenantSwitcherContext);
export const useEntitlements = () => useContext(EntitlementContext);

export function EntitlementGate({ feature, children, fallback }: PropsWithChildren<{ feature: string; fallback?: React.ReactNode }>) {
  const { features, access } = useEntitlements();
  if (access !== 'granted' || !features.has(feature)) return <>{fallback ?? null}</>;
  return <>{children}</>;
}
