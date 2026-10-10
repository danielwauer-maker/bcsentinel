import type { PropsWithChildren, ReactNode } from 'react';
import type { TrendPoint } from '../core/types';

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) {
  return (
    <header className="page-header">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function SectionCard({ title, subtitle, children, className = '' }: PropsWithChildren<{ title?: string; subtitle?: string; className?: string }>) {
  return (
    <section className={`section-card ${className}`.trim()}>
      {(title || subtitle) && (
        <div className="section-heading">
          {title && <h2>{title}</h2>}
          {subtitle && <p>{subtitle}</p>}
        </div>
      )}
      {children}
    </section>
  );
}

export function MetricCard({ label, value, helper, tone = 'default' }: { label: string; value: ReactNode; helper?: string; tone?: 'default' | 'critical' | 'warning' | 'success' | 'brand' }) {
  return (
    <article className="metric-card" data-tone={tone}>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      {helper && <span className="metric-helper">{helper}</span>}
    </article>
  );
}

export function ScoreGauge({ score, label = 'Health Score' }: { score: number; label?: string }) {
  const safe = Math.max(0, Math.min(100, Number.isFinite(score) ? score : 0));
  return (
    <div className="score-gauge" role="img" aria-label={`${label}: ${safe} von 100`} style={{ '--score-deg': `${safe * 3.6}deg` } as React.CSSProperties}>
      <div className="score-gauge-inner">
        <strong>{safe}</strong>
        <span>/100</span>
      </div>
    </div>
  );
}

export function StatePanel({ title, children, tone = 'neutral' }: PropsWithChildren<{ title: string; tone?: 'neutral' | 'locked' | 'error' | 'warning' }>) {
  return (
    <section className="state-panel" data-tone={tone} role={tone === 'error' ? 'alert' : undefined}>
      <strong>{title}</strong>
      <div>{children}</div>
    </section>
  );
}

export function LockedPanel({ title, body, actionLabel, actionHref = '#subscription' }: { title: string; body: string; actionLabel?: string; actionHref?: string }) {
  return (
    <StatePanel title={title} tone="locked">
      <p>{body}</p>
      {actionLabel && <a className="button button-brand" href={actionHref}>{actionLabel}</a>}
    </StatePanel>
  );
}

export function StatusBadge({ value }: { value: string }) {
  const normalized = value.toLowerCase().replace(/\s+/g, '_');
  return <span className="status-badge" data-status={normalized}>{value.replace(/_/g, ' ')}</span>;
}

export function EmptyValue({ label = 'Nicht verfügbar' }: { label?: string }) {
  return <span className="empty-value" title={label}>—</span>;
}

export function TrendChart({ points, ariaLabel, valueFormatter = (value) => String(value) }: { points: TrendPoint[]; ariaLabel: string; valueFormatter?: (value: number) => string }) {
  if (points.length < 2) {
    return <StatePanel title="Noch keine belastbare Historie">Für diesen Verlauf liegen noch nicht genügend vergleichbare Datenpunkte vor.</StatePanel>;
  }

  const width = 640;
  const height = 180;
  const padding = 18;
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min || 1;
  const path = points.map((point, index) => {
    const x = padding + (index / (points.length - 1)) * (width - padding * 2);
    const y = height - padding - ((point.value - min) / spread) * (height - padding * 2);
    return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ');

  return (
    <div className="trend-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel} preserveAspectRatio="none">
        <path className="trend-line" d={path} fill="none" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="trend-labels" aria-hidden="true">
        <span>{points[0]?.label}</span>
        <strong>{valueFormatter(points[points.length - 1].value)}</strong>
        <span>{points[points.length - 1]?.label}</span>
      </div>
    </div>
  );
}

export function RiskBars({ items }: { items: Array<{ name: string; count: number }> }) {
  if (!items.length) return <StatePanel title="Keine aggregierten Risikodaten">Für den ausgewählten Scan wurden keine Risikobereiche projiziert.</StatePanel>;
  const max = Math.max(...items.map((item) => item.count), 1);
  return (
    <div className="risk-bars">
      {items.map((item) => (
        <div className="risk-bar-row" key={item.name}>
          <div className="risk-bar-meta"><span>{item.name}</span><strong>{item.count}</strong></div>
          <div className="risk-bar-track"><span style={{ width: `${Math.max(4, (item.count / max) * 100)}%` }} /></div>
        </div>
      ))}
    </div>
  );
}
