import type { ReactNode } from 'react'
import { Icon } from './ui'

type Props = {
  title: string
  subtitle?: string
  badge?: string
  icon?: string
  status?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  bodyClassName?: string
}

export default function AiWorkspace({
  title,
  subtitle,
  badge,
  icon = 'smart_toy',
  status,
  actions,
  children,
  className = '',
  bodyClassName = '',
}: Props) {
  return (
    <section
      className={`flex flex-col overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm ${className}`}
    >
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border bg-gradient-to-r from-white via-white to-sky-50/50 p-3.5">
        <div className="flex min-w-0 items-center gap-2.5">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-clinical-primary text-white shadow-sm ring-2 ring-sky-200">
            <Icon name={icon} className="text-[23px] text-sky-400" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <h1 className="truncate font-headline-sm text-[15px] font-extrabold leading-tight text-text-primary">
                {title}
              </h1>
              {badge && (
                <span className="rounded bg-sky-100 px-1.5 py-0.5 text-[9.5px] font-bold text-clinical-primary">
                  {badge}
                </span>
              )}
              {status}
            </div>
            {subtitle && (
              <p className="truncate text-[10.5px] text-text-muted">{subtitle}</p>
            )}
          </div>
        </div>
        {actions && <div className="flex flex-wrap items-center gap-1.5">{actions}</div>}
      </header>
      <div className={`flex min-h-0 flex-1 flex-col ${bodyClassName}`}>{children}</div>
    </section>
  )
}
