import { useEffect, useState } from 'react';
import { ApiError } from '../api/client';
import {
  loadAnalyticsDashboard,
  loadExecutiveReport,
  loadLatestScanStatus,
  loadRemediationActions,
  loadRemediationMetrics,
} from '../api/corePages';
import { useTenant } from '../foundation/contexts';
import type {
  AnalyticsDashboardData,
  ExecutiveReport,
  RemediationAction,
  RemediationMetrics,
  ScanRuntimeStatus,
} from './types';

export type AsyncState<T> =
  | { status: 'session_required'; data?: undefined; error?: undefined }
  | { status: 'loading'; data?: undefined; error?: undefined }
  | { status: 'loaded'; data: T; error?: undefined }
  | { status: 'error'; data?: undefined; error: string; code?: number };

function safeError(error: unknown): { message: string; code?: number } {
  if (error instanceof ApiError) return { message: error.message, code: error.status };
  return { message: 'Die Daten konnten nicht geladen werden.' };
}

export function useDashboardData(scanId?: string | null): AsyncState<AnalyticsDashboardData> {
  const session = useTenant();
  const [state, setState] = useState<AsyncState<AnalyticsDashboardData>>(
    session ? { status: 'loading' } : { status: 'session_required' },
  );

  useEffect(() => {
    if (!session) {
      setState({ status: 'session_required' });
      return;
    }
    let active = true;
    setState({ status: 'loading' });
    loadAnalyticsDashboard(session, scanId)
      .then((data) => active && setState({ status: 'loaded', data }))
      .catch((error) => {
        if (!active) return;
        const safe = safeError(error);
        setState({ status: 'error', error: safe.message, code: safe.code });
      });
    return () => { active = false; };
  }, [session, scanId]);

  return state;
}

export function useActionsData(filters: { status?: string; priority?: string }): AsyncState<{ metrics: RemediationMetrics; actions: RemediationAction[] }> {
  const session = useTenant();
  const [state, setState] = useState<AsyncState<{ metrics: RemediationMetrics; actions: RemediationAction[] }>>(
    session ? { status: 'loading' } : { status: 'session_required' },
  );

  useEffect(() => {
    if (!session) {
      setState({ status: 'session_required' });
      return;
    }
    let active = true;
    setState({ status: 'loading' });
    Promise.all([loadRemediationMetrics(session), loadRemediationActions(session, filters)])
      .then(([metrics, actions]) => active && setState({ status: 'loaded', data: { metrics, actions } }))
      .catch((error) => {
        if (!active) return;
        const safe = safeError(error);
        setState({ status: 'error', error: safe.message, code: safe.code });
      });
    return () => { active = false; };
  }, [session, filters.status, filters.priority]);

  return state;
}

export function useExecutiveReport(scanId: string | null, enabled: boolean): AsyncState<ExecutiveReport | null> {
  const session = useTenant();
  const [state, setState] = useState<AsyncState<ExecutiveReport | null>>(
    session ? { status: 'loading' } : { status: 'session_required' },
  );

  useEffect(() => {
    if (!session) {
      setState({ status: 'session_required' });
      return;
    }
    if (!enabled || !scanId) {
      setState({ status: 'loaded', data: null });
      return;
    }
    let active = true;
    setState({ status: 'loading' });
    loadExecutiveReport(session, scanId)
      .then((data) => active && setState({ status: 'loaded', data }))
      .catch((error) => {
        if (!active) return;
        const safe = safeError(error);
        setState({ status: 'error', error: safe.message, code: safe.code });
      });
    return () => { active = false; };
  }, [session, scanId, enabled]);

  return state;
}

export function useLatestScanStatus(): AsyncState<ScanRuntimeStatus | null> {
  const session = useTenant();
  const [state, setState] = useState<AsyncState<ScanRuntimeStatus | null>>(
    session ? { status: 'loading' } : { status: 'session_required' },
  );

  useEffect(() => {
    if (!session) {
      setState({ status: 'session_required' });
      return;
    }
    let active = true;
    loadLatestScanStatus(session)
      .then((data) => active && setState({ status: 'loaded', data }))
      .catch((error) => {
        if (!active) return;
        const safe = safeError(error);
        setState({ status: 'error', error: safe.message, code: safe.code });
      });
    return () => { active = false; };
  }, [session]);

  return state;
}
