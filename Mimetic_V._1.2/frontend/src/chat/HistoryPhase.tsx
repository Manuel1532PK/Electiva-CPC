import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { apiFetch } from '../api/client'
import { extractError } from '../api/errors'
import type { ClinicalHistory, RecentPatient, SearchResult, SessionSnapshot } from './types'
import ClinicalShell from './ClinicalShell'
import HistoryReportViewer, { type ViewerDocument } from './HistoryReportViewer'
import { Icon, genderLabel, initials, useToast } from './ui'

type Props = {
  user: { name?: string; role?: string } | null
  onLogout: () => void
  onHome: () => void
  onNewPatient: () => void
  onResume: () => void
  onStartConsultation: (documentNumber: string) => Promise<void>
}

type HistoryTab = 'historial' | 'fhir'
type SessionFilter = 'all' | 'labs' | 'rx' | 'dx' | 'docs'

const TRIAGE_META: Record<number, { label: string; className: string; dot: string }> = {
  1: {
    label: 'Nivel 1 · Rojo',
    className: 'border-rose-300 bg-rose-50 text-rose-700',
    dot: 'bg-rose-500',
  },
  2: {
    label: 'Nivel 2 · Naranja',
    className: 'border-orange-300 bg-orange-50 text-orange-700',
    dot: 'bg-orange-500',
  },
  3: {
    label: 'Nivel 3 · Amarillo',
    className: 'border-amber-300 bg-amber-50 text-amber-800',
    dot: 'bg-amber-500',
  },
  4: {
    label: 'Nivel 4 · Verde',
    className: 'border-emerald-300 bg-emerald-50 text-emerald-700',
    dot: 'bg-emerald-500',
  },
  5: {
    label: 'Nivel 5 · Azul',
    className: 'border-sky-300 bg-sky-50 text-sky-700',
    dot: 'bg-sky-500',
  },
}

const LAB_LABELS: Record<string, { label: string; unit: string }> = {
  pao2: { label: 'pO₂ arterial', unit: 'mmHg' },
  lactate: { label: 'Lactato', unit: 'mmol/L' },
  leukocytes: { label: 'Leucocitos', unit: '10³/µL' },
  creatinine: { label: 'Creatinina', unit: 'mg/dL' },
  crp: { label: 'PCR', unit: 'mg/L' },
}

function formatDate(value?: string, withTime = true) {
  if (!value) return 'Sin fecha'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}),
  })
}

function patientName(patient?: ClinicalHistory | null) {
  if (!patient) return 'Paciente'
  return `${patient.first_name ?? ''} ${patient.last_name ?? ''}`.trim() || 'Paciente sin nombre'
}

function triageOf(session?: SessionSnapshot | null) {
  const level = Number(session?.triage_level ?? 0)
  return TRIAGE_META[level] ?? null
}

function hasReport(session: SessionSnapshot) {
  return Boolean(session.report_html && session.report_html.trim().length > 0)
}

function sessionDiagnoses(session: SessionSnapshot) {
  const confirmed = session.doctor_review?.confirmedDiagnoses ?? []
  const manual = (session.doctor_review?.manualDiagnoses ?? []).map(item => item.disease_name)
  const suggested = (session.diagnoses ?? []).map(item => item.disease_name)
  return [...new Set([...confirmed, ...manual, ...suggested].filter(Boolean))]
}

function sessionMedicines(session: SessionSnapshot) {
  const treatment = session.treatment
  const fromTreatment = [...(treatment?.available ?? []), ...(treatment?.medicines ?? [])]
    .map(item => item.name)
    .filter((name): name is string => Boolean(name))
  const selected = session.doctor_review?.selectedMedicines ?? []
  return [...new Set(selected.length > 0 ? selected : fromTreatment)]
}

function labsPresent(session: SessionSnapshot) {
  return Object.values(session.labs ?? {}).some(value => String(value ?? '').trim().length > 0)
}

function filterMatches(session: SessionSnapshot, filter: SessionFilter) {
  if (filter === 'labs') return labsPresent(session)
  if (filter === 'rx') return sessionMedicines(session).length > 0
  if (filter === 'dx') return sessionDiagnoses(session).length > 0
  if (filter === 'docs') return hasReport(session)
  return true
}

function escapeHtml(value: unknown) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const CONSOLIDATED_CSS = `
@page { size: Letter; margin: 12mm 11mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  background: #e9eef5;
  color: #0f172a;
  font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
  font-size: 9.4pt;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.doc { width: 8.5in; max-width: calc(100% - 8px); margin: 18px auto; padding: 9mm 10mm 8mm; background: #fff; border-radius: 2px; box-shadow: 0 28px 60px -34px rgba(11, 53, 88, .55); }
p { margin: 0; }
h1, h2, h3 { margin: 0; }
.mono { font-family: 'JetBrains Mono', 'Consolas', 'SFMono-Regular', monospace; }
.eyebrow { display: block; font-size: 6.5pt; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: #0284c7; }
.eyebrow.light { color: #7dd3fc; }

.masthead { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; padding: 14px 18px; border-radius: 14px; border-bottom: 3px solid #38bdf8; background: radial-gradient(circle at 82% 0%, rgba(56, 189, 248, .18), transparent 48%), linear-gradient(135deg, #0b3558 0%, #062642 100%); color: #fff; }
.brand { display: flex; align-items: center; gap: 10px; }
.brand-mark { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; background: linear-gradient(135deg, #0ea5e9, #0284c7); border: 1px solid rgba(255, 255, 255, .28); color: #fff; font-size: 15pt; font-weight: 800; letter-spacing: -.03em; box-shadow: inset 0 1px 0 rgba(255, 255, 255, .3); }
.brand-name { font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; font-size: 11.5pt; font-weight: 800; letter-spacing: .24em; line-height: 1.1; }
.brand-tag { margin-top: 3px; font-size: 6.4pt; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: #7dd3fc; }
.masthead-meta { text-align: right; }
.masthead-title { font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; margin-top: 2px; font-size: 12.5pt; font-weight: 700; letter-spacing: -.01em; }
.masthead-line { margin-top: 2px; font-size: 7.3pt; color: #cbd5e1; letter-spacing: .02em; }
.masthead-line strong { color: #fff; font-weight: 700; }

.syncbar { display: flex; align-items: center; gap: 8px; padding: 6px 4px 0; font-size: 6.7pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #64748b; }
.sync-dot { width: 5px; height: 5px; border-radius: 50%; background: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, .15); }
.syncbar .spacer { flex: 1; }
.sync-chip { padding: 2px 6px; border-radius: 999px; border: 1px solid #e2e8f0; background: #f8fafc; color: #475569; font-size: 6.2pt; letter-spacing: .08em; }
.sync-chip.demo { border-color: #fde68a; background: #fffbeb; color: #92400e; }

.patient-card { display: grid; grid-template-columns: 1fr 2.35in; gap: 16px; margin-top: 12px; padding: 14px 16px; border: 1px solid #e2e8f0; border-radius: 12px; background: linear-gradient(180deg, #fff 0%, #f8fafc 100%); }
.patient-card > * { min-width: 0; }
.patient-main { display: flex; gap: 12px; align-items: center; }
.avatar { width: 46px; height: 46px; flex: 0 0 46px; display: flex; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid #bae6fd; background: linear-gradient(135deg, #e0f2fe, #bae6fd); color: #0b3558; font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; font-size: 14pt; font-weight: 800; }
.patient-name { font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; margin-top: 1px; font-size: 15pt; font-weight: 800; letter-spacing: -.02em; color: #0b3558; }
.chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.chip { display: inline-flex; align-items: center; gap: 3px; padding: 1.5px 7px; border: 1px solid #e2e8f0; border-radius: 999px; background: #fff; color: #475569; font-size: 6.6pt; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
.chip.chip-id { border-color: #bae6fd; background: #f0f9ff; color: #075985; letter-spacing: .02em; }
.patient-meta { display: flex; flex-wrap: wrap; gap: 3px 12px; margin-top: 5px; font-size: 7.3pt; color: #64748b; }
.patient-meta strong { color: #334155; font-weight: 600; }
.patient-side { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 12px; align-content: center; padding-left: 14px; border-left: 1px dashed #cbd5e1; }
.meta-item .meta-label { display: block; font-size: 6pt; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; color: #94a3b8; }
.meta-item .meta-value { display: block; margin-top: 1px; font-size: 8pt; font-weight: 600; color: #0b3558; }

.allergy-banner { margin-top: 8px; padding: 6px 10px; border: 1px solid #fecaca; border-left: 3px solid #ef4444; border-radius: 0 8px 8px 0; background: #fef2f2; color: #991b1b; font-size: 7.8pt; }
.allergy-banner strong { font-weight: 800; }

.section { margin-top: 15px; }
.section-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding-bottom: 5px; border-bottom: 1px solid #e2e8f0; break-after: avoid; }
.section-num { width: 21px; height: 21px; flex: 0 0 21px; display: flex; align-items: center; justify-content: center; border-radius: 6px; background: #e0f2fe; color: #0369a1; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 7.3pt; font-weight: 700; }
.section-title h2 { margin-top: 1px; font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; font-size: 10.4pt; font-weight: 700; letter-spacing: -.01em; color: #0b3558; }
.head-aside { margin-left: auto; }

.table { width: 100%; border-collapse: collapse; margin-top: 6px; }
.table th { padding: 4px 7px; border-bottom: 1px solid #cbd5e1; background: #f1f5f9; text-align: left; font-size: 6.2pt; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #475569; }
.table td { padding: 5px 7px; border-bottom: 1px solid #f1f5f9; font-size: 7.9pt; color: #1e293b; vertical-align: top; }
.table tr:last-child td { border-bottom: 0; }
.table .value { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 600; color: #0b3558; }
.table .unit { color: #94a3b8; font-size: 6.8pt; }
.table.compact td { padding: 3.5px 7px; }
.index-table td:first-child { font-family: 'JetBrains Mono', Consolas, monospace; font-weight: 700; color: #0284c7; width: 22px; }
.index-table .idx-date { white-space: nowrap; font-weight: 600; color: #0b3558; }

.encounter { margin-top: 16px; padding: 12px 14px; border: 1px solid #e2e8f0; border-radius: 12px; background: #fff; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.encounter-head { display: flex; align-items: flex-start; gap: 10px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; break-after: avoid; }
.encounter-num { width: 28px; height: 28px; flex: 0 0 28px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: #0b3558; color: #7dd3fc; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 8pt; font-weight: 700; }
.encounter-id { min-width: 0; }
.encounter-id h2 { margin-top: 1px; font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; font-weight: 700; color: #0b3558; line-height: 1.3; }
.encounter-meta { margin-top: 2px; font-size: 7.2pt; color: #64748b; }
.triage-pill { flex: 0 0 auto; margin-left: auto; padding: 2px 8px; border: 1px solid #e2e8f0; border-radius: 999px; background: #f8fafc; color: #475569; font-size: 6.4pt; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
.triage-pill.level-1 { border-color: #fecaca; background: #fef2f2; color: #991b1b; }
.triage-pill.level-2 { border-color: #fed7aa; background: #fff7ed; color: #9a3412; }
.triage-pill.level-3 { border-color: #fde68a; background: #fffbeb; color: #92400e; }
.triage-pill.level-4 { border-color: #a7f3d0; background: #ecfdf5; color: #065f46; }
.triage-pill.level-5 { border-color: #bae6fd; background: #f0f9ff; color: #075985; }

.group-label { display: block; margin: 10px 0 4px; font-size: 6.4pt; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: #94a3b8; }
.group-label:first-child { margin-top: 0; }
.narrative { margin-top: 7px; font-size: 8.4pt; color: #334155; line-height: 1.55; }
.chip-list { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.symptom { padding: 2px 7px; border: 1px solid #bae6fd; border-radius: 999px; background: #f0f9ff; color: #075985; font-size: 7pt; font-weight: 600; }
.empty { font-size: 7.8pt; font-style: italic; color: #94a3b8; }

.vitals { display: grid; grid-template-columns: repeat(6, 1fr); gap: 5px; margin-top: 4px; }
.vital { position: relative; padding: 6px 8px; border: 1px solid #e2e8f0; border-radius: 8px; background: linear-gradient(180deg, #fff, #f8fafc); break-inside: avoid; }
.vital .vital-label { display: block; font-size: 5.6pt; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; color: #64748b; }
.vital .vital-value { display: flex; align-items: baseline; gap: 2px; margin-top: 1px; }
.vital .vital-value b { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 10.5pt; font-weight: 700; letter-spacing: -.02em; color: #0b3558; }
.vital .vital-value span { font-size: 5.8pt; font-weight: 600; color: #94a3b8; }

.triage { margin-top: 6px; padding: 8px 10px; border: 1px solid #fcd34d; border-left: 4px solid #f59e0b; border-radius: 9px; background: linear-gradient(135deg, #fffbeb 0%, #fff 62%); break-inside: avoid; }
.triage.level-1 { border-color: #fecaca; border-left-color: #dc2626; background: linear-gradient(135deg, #fef2f2, #fff 62%); }
.triage.level-2 { border-color: #fed7aa; border-left-color: #ea580c; background: linear-gradient(135deg, #fff7ed, #fff 62%); }
.triage.level-3 { border-color: #fde68a; border-left-color: #f59e0b; background: linear-gradient(135deg, #fffbeb, #fff 62%); }
.triage.level-4 { border-color: #a7f3d0; border-left-color: #059669; background: linear-gradient(135deg, #ecfdf5, #fff 62%); }
.triage.level-5 { border-color: #bae6fd; border-left-color: #0284c7; background: linear-gradient(135deg, #f0f9ff, #fff 62%); }
.triage-title { font-size: 8.6pt; font-weight: 800; color: #7c2d12; }
.triage.level-1 .triage-title { color: #991b1b; }
.triage.level-4 .triage-title { color: #065f46; }
.triage.level-5 .triage-title { color: #075985; }
.triage-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 10px; margin-top: 5px; }
.triage-grid .panel-label { display: block; font-size: 5.9pt; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: #a8a29e; margin-bottom: 1px; }
.triage-grid p { font-size: 7.2pt; color: #44403c; line-height: 1.45; }
.score-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.score-chip { padding: 2px 7px; border: 1px solid #bae6fd; border-radius: 5px; background: #f0f9ff; color: #075985; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 6.8pt; font-weight: 700; }

.dx-list { display: grid; gap: 4px; }
.dx-card { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; padding: 6px 9px; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; border-radius: 7px; background: #f8fafc; break-inside: avoid; }
.dx-name { font-size: 8.6pt; font-weight: 700; color: #0b3558; }
.dx-note { margin-top: 1px; font-size: 7pt; color: #64748b; }
.dx-origin { flex: 0 0 auto; padding: 1px 6px; border: 1px solid #bae6fd; border-radius: 999px; background: #f0f9ff; color: #075985; font-size: 5.9pt; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; }

.med-table thead th { background: #0b3558; border-bottom: 0; color: #e2e8f0; }
.med-name { font-size: 8.1pt; font-weight: 700; color: #0b3558; }
.med-summary { margin-top: 2px; font-size: 6.7pt; color: #64748b; line-height: 1.4; }
.route { display: inline-block; padding: 1px 5px; border: 1px solid #e2e8f0; border-radius: 4px; background: #f8fafc; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 6.5pt; font-weight: 600; color: #475569; white-space: nowrap; }
.alert { margin-top: 3px; padding: 2.5px 5px; border-radius: 4px; font-size: 6.4pt; line-height: 1.35; }
.alert-warn { border-left: 2px solid #f59e0b; background: #fffbeb; color: #92400e; }
.alert-danger { border-left: 2px solid #ef4444; background: #fef2f2; color: #991b1b; }

.note-card { margin-top: 4px; padding: 8px 11px; border: 1px solid #e2e8f0; border-left: 3px solid #0284c7; border-radius: 0 8px 8px 0; background: #f8fafc; font-size: 8.2pt; color: #334155; line-height: 1.55; }
.mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 4px; }
.mini-item { padding: 5px 7px; border: 1px solid #eef2f7; border-radius: 7px; background: #f8fafc; }
.mini-item span { display: block; font-size: 5.8pt; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #94a3b8; }
.mini-item p { margin-top: 1px; font-size: 7.2pt; color: #334155; }

.legal { margin-top: 16px; padding-top: 8px; border-top: 1px solid #e2e8f0; break-inside: avoid; }
.legal-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.legal-brand { font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; font-size: 6.7pt; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: #0b3558; }
.legal-meta { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 5.9pt; color: #94a3b8; }
.legal p { margin-top: 4px; font-size: 6.3pt; line-height: 1.5; color: #94a3b8; }

@media print {
  body { background: #fff; }
  .doc { width: auto; max-width: none; margin: 0; padding: 0; border-radius: 0; box-shadow: none; }
  .encounter { break-inside: auto; break-before: page; box-shadow: none; }
  .encounter:first-of-type { break-before: auto; }
  .patient-card, .vitals, .triage, .dx-card, .note-card, .legal, .table tr { break-inside: avoid; }
  .masthead { border-radius: 10px; }
}
`

function buildConsolidatedHtml(patient: ClinicalHistory, sessions: SessionSnapshot[]) {
  const name = patientName(patient)
  const ordered = [...sessions].sort(
    (a, b) => new Date(a.date ?? 0).getTime() - new Date(b.date ?? 0).getTime(),
  )
  const documentCount = ordered.filter(hasReport).length
  const firstDate = formatDate(ordered[0]?.date, false)
  const lastDate = formatDate(ordered[ordered.length - 1]?.date, false)
  const latestDoctor = [...ordered].reverse().find(session => session.doctor_name)?.doctor_name
  const latestAllergies = [...ordered].reverse().find(session => session.allergies)?.allergies

  const indexRows = ordered
    .map((session, index) => {
      const confirmed = session.doctor_review?.confirmedDiagnoses ?? []
      const suggested = session.diagnoses ?? []
      const main = confirmed[0] ?? suggested[0]?.disease_name ?? 'Sin diagnóstico registrado'
      return `<tr>
        <td>${String(index + 1).padStart(2, '0')}</td>
        <td class="idx-date">${escapeHtml(formatDate(session.date, false))}</td>
        <td>${escapeHtml(session.consultation_reason || 'Consulta clínica')}</td>
        <td>${escapeHtml(main)}</td>
        <td>${escapeHtml(session.doctor_name || 'Médico asistencial')}</td>
      </tr>`
    })
    .join('')

  const blocks = ordered
    .map((session, index) => {
      const triage = triageOf(session)
      const triageLevel = Number(session.triage_level ?? 0)
      const confirmed = session.doctor_review?.confirmedDiagnoses ?? []
      const manual = session.doctor_review?.manualDiagnoses ?? []
      const suggested = (session.diagnoses ?? []).filter(
        diagnosis => !confirmed.includes(diagnosis.disease_name),
      )
      const triageScores = String(session.triage_score ?? '')
        .split(/\s*[·;|]\s*/)
        .filter(Boolean)

      const vitals = [
        ['PA', session.blood_pressure ? `${session.blood_pressure}` : '', 'mmHg'],
        ['FC', session.heart_rate ? `${session.heart_rate}` : '', 'lpm'],
        ['FR', session.respiratory_rate ? `${session.respiratory_rate}` : '', 'rpm'],
        ['Temp.', session.temperature ? `${session.temperature}` : '', '°C'],
        ['SpO₂', session.oxygen_saturation ? `${session.oxygen_saturation}` : '', '%'],
        [
          'Peso / talla',
          session.weight || session.height
            ? `${session.weight || '—'} / ${session.height || '—'}`
            : '',
          session.height ? 'kg / cm' : 'kg',
        ],
      ].filter(([, value]) => value)

      const labs = Object.entries(session.labs ?? {}).filter(([, value]) => String(value ?? '').trim())
      const labsRows = labs
        .map(([key, value]) => {
          const meta = LAB_LABELS[key]
          return `<tr><td>${escapeHtml(meta?.label ?? key)}</td><td class="value">${escapeHtml(value)}${
            meta ? ` <span class="unit">${escapeHtml(meta.unit)}</span>` : ''
          }</td></tr>`
        })
        .join('')

      const treatment = session.treatment
      const sourceMeds = [...(treatment?.available ?? []), ...(treatment?.medicines ?? [])]
      const selected = session.doctor_review?.selectedMedicines ?? []
      const medicines = (selected.length > 0
        ? sourceMeds.filter(medicine => selected.includes(medicine.name))
        : sourceMeds
      ).filter(
        (medicine, position, list) =>
          list.findIndex(candidate => candidate.name === medicine.name) === position,
      )

      const medRows = medicines
        .map(medicine => {
          const dosage =
            session.doctor_review?.modifiedDoses?.[medicine.name] || medicine.dosage || '—'
          const contraindications = medicine.contraindications
          const alerts: string[] = []
          if (contraindications?.allergies?.length) {
            alerts.push(`Alergias: ${contraindications.allergies.join(', ')}`)
          }
          if (contraindications?.conditions?.length) {
            alerts.push(`Contraindicado en: ${contraindications.conditions.join(', ')}`)
          }
          if (medicine.interactions_warning) alerts.push(medicine.interactions_warning)
          const alertHtml = alerts
            .map(text => `<div class="alert alert-warn">${escapeHtml(text)}</div>`)
            .join('')
          const summary = medicine.patient_summary
            ? `<div class="med-summary">${escapeHtml(medicine.patient_summary)}</div>`
            : ''
          return `<tr>
            <td><div class="med-name">${escapeHtml(medicine.name)}</div>${summary}${alertHtml}</td>
            <td class="value">${escapeHtml(dosage)}</td>
            <td><span class="route">${escapeHtml(medicine.route || 'Oral')}</span></td>
            <td>${escapeHtml(medicine.frequency || '—')}</td>
            <td>${escapeHtml(medicine.duration || '—')}</td>
            <td>${escapeHtml(medicine.monitoring || '—')}</td>
          </tr>`
        })
        .join('')

      const nonPharm = (treatment?.non_pharmacological ?? []).filter(Boolean)
      const background = [
        ['Médicos', session.medical_history],
        ['Quirúrgicos', session.surgical_history],
        ['Farmacológicos', session.pharmacological_history],
      ].filter(([, value]) => String(value ?? '').trim()) as Array<[string, string]>

      const hasDiagnoses = confirmed.length > 0 || manual.length > 0 || suggested.length > 0

      return `<article class="encounter">
  <header class="encounter-head">
    <span class="encounter-num">${String(index + 1).padStart(2, '0')}</span>
    <div class="encounter-id">
      <span class="eyebrow">Atención ${String(index + 1).padStart(2, '0')} · ${escapeHtml(formatDate(session.date))}</span>
      <h2>${escapeHtml(session.consultation_reason || 'Consulta clínica')}</h2>
      <p class="encounter-meta">${escapeHtml(session.doctor_name || 'Médico asistencial')}${
        session.hospital_name ? ` · ${escapeHtml(session.hospital_name)}` : ''
      }</p>
    </div>
    ${
      triage
        ? `<span class="triage-pill level-${triageLevel}">${escapeHtml(triage.label)}</span>`
        : ''
    }
  </header>

  ${
    session.symptom_evolution
      ? `<p class="narrative"><strong>Evolución:</strong> ${escapeHtml(session.symptom_evolution)}</p>`
      : ''
  }

  ${
    (session.symptoms ?? []).length > 0
      ? `<div class="chip-list">${(session.symptoms ?? [])
          .map(symptom => `<span class="symptom">${escapeHtml(symptom)}</span>`)
          .join('')}</div>`
      : ''
  }

  ${
    vitals.length > 0
      ? `<span class="group-label">Signos vitales</span>
        <div class="vitals">${vitals
          .map(
            ([label, value, unit]) => `<div class="vital">
              <span class="vital-label">${escapeHtml(label)}</span>
              <span class="vital-value"><b>${escapeHtml(value)}</b><span>${escapeHtml(unit)}</span></span>
            </div>`,
          )
          .join('')}</div>`
      : ''
  }

  ${
    triage
      ? `<div class="triage level-${triageLevel}">
          <div class="triage-title">${escapeHtml(triage.label)}${
            session.triage_system ? ` · ${escapeHtml(session.triage_system)}` : ''
          }</div>
          <div class="triage-grid">
            <div>
              <span class="panel-label">Discriminadores</span>
              <p>${escapeHtml(session.triage_discriminators || 'Sin discriminadores registrados.')}</p>
            </div>
            <div>
              <span class="panel-label">Puntuación</span>
              <div class="score-chips">${
                triageScores.length > 0
                  ? triageScores.map(score => `<span class="score-chip">${escapeHtml(score)}</span>`).join('')
                  : '<span class="empty">Sin puntuación</span>'
              }</div>
            </div>
          </div>
        </div>`
      : ''
  }

  ${
    labsRows
      ? `<span class="group-label">Laboratorio urgente</span>
        <table class="table compact">
          <thead><tr><th>Determinación</th><th>Resultado</th></tr></thead>
          <tbody>${labsRows}</tbody>
        </table>`
      : ''
  }

  ${
    background.length > 0
      ? `<span class="group-label">Antecedentes de la atención</span>
        <div class="mini-grid">${background
          .map(
            ([label, value]) =>
              `<div class="mini-item"><span>${escapeHtml(label)}</span><p>${escapeHtml(value)}</p></div>`,
          )
          .join('')}</div>`
      : ''
  }

  ${
    hasDiagnoses
      ? `<span class="group-label">Impresión diagnóstica</span>
        <div class="dx-list">
          ${confirmed
            .map(
              diagnosis =>
                `<div class="dx-card"><div><div class="dx-name">${escapeHtml(diagnosis)}</div></div><span class="dx-origin">Confirmado</span></div>`,
            )
            .join('')}
          ${manual
            .map(
              item =>
                `<div class="dx-card"><div><div class="dx-name">${escapeHtml(item.disease_name)}</div>${
                  item.notes ? `<div class="dx-note">${escapeHtml(item.notes)}</div>` : ''
                }</div><span class="dx-origin">Manual</span></div>`,
            )
            .join('')}
          ${suggested
            .map(
              diagnosis =>
                `<div class="dx-card"><div><div class="dx-name">${escapeHtml(diagnosis.disease_name)}</div>
                  <div class="dx-note">${escapeHtml(diagnosis.severity || 'Sin severidad')} · ${escapeHtml(
                    diagnosis.description || '',
                  )}</div></div>
                <span class="dx-origin">IA · ${Math.round((diagnosis.confidence ?? 0) * 100)}%</span></div>`,
            )
            .join('')}
        </div>`
      : ''
  }

  ${
    medRows
      ? `<span class="group-label">Plan farmacológico</span>
        <table class="table med-table">
          <thead><tr><th>Medicamento</th><th>Dosis</th><th>Vía</th><th>Frecuencia</th><th>Duración</th><th>Monitoreo</th></tr></thead>
          <tbody>${medRows}</tbody>
        </table>
        ${
          nonPharm.length > 0
            ? `<div class="chip-list">${nonPharm
                .map(item => `<span class="symptom">${escapeHtml(item)}</span>`)
                .join('')}</div>`
            : ''
        }`
      : ''
  }

  ${
    session.doctor_review?.doctorNotes
      ? `<span class="group-label">Nota clínica</span>
        <div class="note-card">${escapeHtml(session.doctor_review.doctorNotes)}</div>`
      : ''
  }
</article>`
    })
    .join('')

  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>historia-clinica-${escapeHtml(patient.document_number)}</title>
<style>${CONSOLIDATED_CSS}</style>
</head>
<body>
<div class="doc">
  <header class="masthead">
    <div class="brand">
      <div class="brand-mark">M</div>
      <div>
        <div class="brand-name">MIMETIC</div>
        <div class="brand-tag">Clinical Intelligence Suite</div>
      </div>
    </div>
    <div class="masthead-meta">
      <span class="eyebrow light">Historia clínica</span>
      <div class="masthead-title">Expediente consolidado</div>
      <div class="masthead-line">HC · <strong>${escapeHtml(patient.document_number)}</strong></div>
      <div class="masthead-line">${escapeHtml(String(ordered.length))} atenciones · ${escapeHtml(
        String(documentCount),
      )} documentos</div>
    </div>
  </header>

  <div class="syncbar">
    <span class="sync-dot"></span>
    <span>Registro unificado de atenciones</span>
    <span class="spacer"></span>
    <span class="sync-chip mono">Generado ${escapeHtml(formatDate(new Date().toISOString(), false))}</span>
    <span class="sync-chip demo">Demostración</span>
  </div>

  <section class="patient-card">
    <div class="patient-main">
      <div class="avatar">${escapeHtml(initials(name))}</div>
      <div>
        <span class="eyebrow">Paciente</span>
        <h1 class="patient-name">${escapeHtml(name)}</h1>
        <div class="chips">
          <span class="chip chip-id mono">${escapeHtml(patient.document_type)} ${escapeHtml(
            patient.document_number,
          )}</span>
          ${patient.age ? `<span class="chip">${escapeHtml(patient.age)} años</span>` : ''}
          ${patient.gender ? `<span class="chip">${escapeHtml(genderLabel(patient.gender))}</span>` : ''}
        </div>
        <div class="patient-meta">
          ${patient.phone ? `<span>Tel. <strong>${escapeHtml(patient.phone)}</strong></span>` : ''}
          ${
            patient.city || patient.department
              ? `<span>Residencia <strong>${escapeHtml(
                  [patient.city, patient.department].filter(Boolean).join(', '),
                )}</strong></span>`
              : ''
          }
          ${
            patient.birth_date
              ? `<span>Nacimiento <strong>${escapeHtml(patient.birth_date)}</strong></span>`
              : ''
          }
          ${
            patient.occupation
              ? `<span>Ocupación <strong>${escapeHtml(patient.occupation)}</strong></span>`
              : ''
          }
        </div>
      </div>
    </div>
    <div class="patient-side">
      <div class="meta-item"><span class="meta-label">Atenciones</span><span class="meta-value">${
        ordered.length
      }</span></div>
      <div class="meta-item"><span class="meta-label">Documentos</span><span class="meta-value">${
        documentCount
      }</span></div>
      <div class="meta-item"><span class="meta-label">Primera atención</span><span class="meta-value">${escapeHtml(
        firstDate,
      )}</span></div>
      <div class="meta-item"><span class="meta-label">Última atención</span><span class="meta-value">${escapeHtml(
        lastDate,
      )}</span></div>
      <div class="meta-item"><span class="meta-label">Último profesional</span><span class="meta-value">${escapeHtml(
        latestDoctor || 'Médico asistencial',
      )}</span></div>
    </div>
  </section>

  ${
    latestAllergies
      ? `<div class="allergy-banner"><strong>Alergias registradas:</strong> ${escapeHtml(
          latestAllergies,
        )}</div>`
      : ''
  }

  <section class="section">
    <div class="section-head">
      <span class="section-num">00</span>
      <div class="section-title">
        <span class="eyebrow">Índice</span>
        <h2>Resumen de atenciones</h2>
      </div>
      <span class="head-aside"><span class="sync-chip">${ordered.length} registros</span></span>
    </div>
    ${
      ordered.length > 0
        ? `<table class="table compact index-table">
            <thead><tr><th>#</th><th>Fecha</th><th>Motivo de consulta</th><th>Diagnóstico principal</th><th>Profesional</th></tr></thead>
            <tbody>${indexRows}</tbody>
          </table>`
        : '<p class="empty">No hay atenciones registradas.</p>'
    }
  </section>

  ${blocks || '<p class="empty">No hay atenciones registradas.</p>'}

  <footer class="legal">
    <div class="legal-top">
      <span class="legal-brand">MIMETIC · Historia clínica digital</span>
      <span class="legal-meta">historia-${escapeHtml(patient.document_number)}</span>
    </div>
    <p>Generado por MIMETIC a partir de la historia clínica y las sesiones persistidas en MongoDB. Documento de demostración sin firma electrónica ni envío al HIS institucional; no sustituye el criterio de un profesional de la salud.</p>
    <p>Ley 23 de 1981 — Colombia. Documento confidencial de uso clínico.</p>
  </footer>
</div>
</body>
</html>`
}

function buildFhirBundle(patient: ClinicalHistory | null, sessions: SessionSnapshot[]) {
  const entries: Array<{ resource: Record<string, unknown> }> = []
  if (!patient) {
    return {
      resourceType: 'Bundle',
      type: 'collection',
      total: 0,
      entry: entries,
    }
  }

  const reference = `Patient/${patient.document_number}`
  entries.push({
    resource: {
      resourceType: 'Patient',
      id: patient.document_number,
      identifier: [
        { system: 'MIMETIC/NHC', value: patient.document_number },
        { system: 'MIMETIC/DOC', type: { text: patient.document_type }, value: patient.document_number },
      ],
      name: [{ text: patientName(patient) }],
      gender:
        genderLabel(patient.gender) === 'Masculino'
          ? 'male'
          : genderLabel(patient.gender) === 'Femenino'
            ? 'female'
            : 'unknown',
      birthDate: patient.birth_date || undefined,
      telecom: patient.phone ? [{ system: 'phone', value: patient.phone }] : undefined,
    },
  })

  for (const session of sessions) {
    const sessionId = session.id ?? `sesion-${session.date ?? entries.length}`
    entries.push({
      resource: {
        resourceType: 'Encounter',
        id: `enc-${sessionId}`,
        status: 'finished',
        class: { system: 'http://terminology.hl7.org/CodeSystem/v3-ActCode', code: 'AMB' },
        subject: { reference },
        period: { start: session.date },
        reasonCode: [{ text: session.consultation_reason || 'Consulta clínica' }],
        serviceProvider: { display: session.hospital_name || 'MIMETIC' },
      },
    })

    const components = [
      session.blood_pressure
        ? { code: { text: 'Presión arterial' }, valueString: `${session.blood_pressure} mmHg` }
        : null,
      session.heart_rate
        ? { code: { text: 'Frecuencia cardíaca' }, valueQuantity: { value: Number(session.heart_rate), unit: '/min' } }
        : null,
      session.respiratory_rate
        ? {
            code: { text: 'Frecuencia respiratoria' },
            valueQuantity: { value: Number(session.respiratory_rate), unit: '/min' },
          }
        : null,
      session.temperature
        ? { code: { text: 'Temperatura' }, valueQuantity: { value: Number(session.temperature), unit: 'Cel' } }
        : null,
      session.oxygen_saturation
        ? {
            code: { text: 'SpO₂' },
            valueQuantity: { value: Number(session.oxygen_saturation), unit: '%' },
          }
        : null,
    ].filter(Boolean)

    if (components.length > 0) {
      entries.push({
        resource: {
          resourceType: 'Observation',
          id: `obs-vitals-${sessionId}`,
          status: 'final',
          category: [{ text: 'vital-signs' }],
          code: { text: 'Signos vitales' },
          subject: { reference },
          effectiveDateTime: session.date,
          component: components,
        },
      })
    }

    const labs = Object.entries(session.labs ?? {}).filter(([, value]) => String(value ?? '').trim())
    if (labs.length > 0) {
      entries.push({
        resource: {
          resourceType: 'Observation',
          id: `obs-labs-${sessionId}`,
          status: 'final',
          category: [{ text: 'laboratory' }],
          code: { text: 'Laboratorio urgente' },
          subject: { reference },
          effectiveDateTime: session.date,
          component: labs.map(([key, value]) => ({
            code: { text: LAB_LABELS[key]?.label ?? key },
            valueQuantity: { value: Number(value), unit: LAB_LABELS[key]?.unit ?? '' },
          })),
        },
      })
    }

    sessionDiagnoses(session)
      .slice(0, 4)
      .forEach((diagnosis, index) => {
        entries.push({
          resource: {
            resourceType: 'Condition',
            id: `cond-${sessionId}-${index + 1}`,
            clinicalStatus: { text: index === 0 ? 'active' : 'active' },
            verificationStatus: { text: 'confirmed' },
            code: { text: diagnosis },
            subject: { reference },
            recordedDate: session.date,
          },
        })
      })

    const medicines = [...(session.treatment?.available ?? []), ...(session.treatment?.medicines ?? [])]
    medicines.slice(0, 5).forEach((medicine, index) => {
      entries.push({
        resource: {
          resourceType: 'MedicationRequest',
          id: `med-${sessionId}-${index + 1}`,
          status: 'active',
          intent: 'order',
          medicationCodeableConcept: { text: medicine.name },
          subject: { reference },
          authoredOn: session.date,
          dosageInstruction: [
            {
              text: [medicine.dosage, medicine.route, medicine.frequency].filter(Boolean).join(' · ') || undefined,
            },
          ],
        },
      })
    })

    if (hasReport(session)) {
      entries.push({
        resource: {
          resourceType: 'DocumentReference',
          id: `doc-${sessionId}`,
          status: 'current',
          docStatus: 'final',
          type: { text: 'Historia clínica de la atención' },
          subject: { reference },
          date: session.date,
          description: session.consultation_reason || undefined,
        },
      })
    }
  }

  return {
    resourceType: 'Bundle',
    id: `bundle-${patient.document_number}`,
    type: 'collection',
    timestamp: new Date().toISOString(),
    meta: {
      tag: [{ system: 'https://mimetic.health/flags', code: 'SIMULATED-DEMO', display: 'Mapeo local no validado' }],
    },
    total: entries.length,
    entry: entries,
  }
}

function downloadText(content: string, filename: string, mime: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }))
  const link = window.document.createElement('a')
  link.href = url
  link.download = filename
  window.document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export default function HistoryPhase({
  user,
  onLogout,
  onHome,
  onNewPatient,
  onResume,
  onStartConsultation,
}: Props) {
  const showToast = useToast()

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [recent, setRecent] = useState<RecentPatient[]>([])
  const [loadingRecent, setLoadingRecent] = useState(true)

  const [patient, setPatient] = useState<ClinicalHistory | null>(null)
  const [sessions, setSessions] = useState<SessionSnapshot[]>([])
  const [loadingPatient, setLoadingPatient] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [tab, setTab] = useState<HistoryTab>('historial')
  const [filter, setFilter] = useState<SessionFilter>('all')
  const [expanded, setExpanded] = useState<string | null>(null)
  const [viewerDoc, setViewerDoc] = useState<ViewerDocument | null>(null)
  const [starting, setStarting] = useState(false)
  const [showFhirJson, setShowFhirJson] = useState(false)

  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const loadRecent = useCallback(async () => {
    setLoadingRecent(true)
    try {
      const res = await apiFetch('/api/clinical-history/recent')
      if (!res.ok) throw new Error(await extractError(res, 'No se pudo cargar la actividad reciente.'))
      setRecent((await res.json()) as RecentPatient[])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar la actividad reciente.')
    } finally {
      setLoadingRecent(false)
    }
  }, [])

  useEffect(() => {
    void loadRecent()
    return () => {
      if (searchTimer.current) clearTimeout(searchTimer.current)
    }
  }, [loadRecent])

  const runSearch = useCallback(async (value: string) => {
    if (!value.trim()) {
      setResults([])
      setSearching(false)
      return
    }
    setSearching(true)
    try {
      const res = await apiFetch(`/api/clinical-history/search?q=${encodeURIComponent(value.trim())}`)
      if (!res.ok) throw new Error(await extractError(res, 'No se pudo buscar pacientes.'))
      setResults((await res.json()) as SearchResult[])
    } catch (err) {
      setResults([])
      setError(err instanceof Error ? err.message : 'No se pudo buscar pacientes.')
    } finally {
      setSearching(false)
    }
  }, [])

  const handleQueryChange = (value: string) => {
    setQuery(value)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => void runSearch(value), 250)
  }

  const openPatient = useCallback(
    async (documentNumber: string) => {
      setLoadingPatient(true)
      setError(null)
      setTab('historial')
      setFilter('all')
      try {
        const [historyRes, sessionsRes] = await Promise.all([
          apiFetch(`/api/clinical-history/${documentNumber}`),
          apiFetch(`/api/clinical-history/${documentNumber}/sessions`),
        ])
        if (!historyRes.ok) {
          throw new Error(await extractError(historyRes, 'No se pudo abrir la historia clínica.'))
        }
        if (!sessionsRes.ok) {
          throw new Error(await extractError(sessionsRes, 'No se pudieron cargar las atenciones.'))
        }
        const history = (await historyRes.json()) as ClinicalHistory
        const sessionList = (await sessionsRes.json()) as SessionSnapshot[]
        setPatient(history)
        setSessions(sessionList)
        setExpanded(sessionList[0]?.id ?? null)
        setQuery(`${history.document_number} — ${patientName(history)}`)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (err) {
        setPatient(null)
        setSessions([])
        showToast(err instanceof Error ? err.message : 'No se pudo abrir la historia clínica.', {
          icon: 'error',
          tone: 'error',
        })
      } finally {
        setLoadingPatient(false)
      }
    },
    [showToast],
  )

  const closePatient = () => {
    setPatient(null)
    setSessions([])
    setQuery('')
    setResults([])
    setError(null)
    setExpanded(null)
    setTab('historial')
    setFilter('all')
    setViewerDoc(null)
    void loadRecent()
  }

  const handleNewConsultation = async () => {
    if (!patient) return
    setStarting(true)
    try {
      await onStartConsultation(patient.document_number)
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'No se pudo iniciar la consulta.', {
        icon: 'error',
        tone: 'error',
      })
      setStarting(false)
    }
  }

  const openSessionDocument = (session: SessionSnapshot, autoPrint = false) => {
    if (!patient) return
    if (!hasReport(session)) {
      showToast('Esta atención aún no tiene documento generado. Se crea al cerrar la consulta.', {
        icon: 'info',
        tone: 'warn',
      })
      return
    }
    setViewerDoc({
      html: session.report_html ?? '',
      title: 'Historia clínica de la atención',
      subtitle: `${formatDate(session.date)} · ${session.consultation_reason || 'Consulta clínica'}`,
      patientName: patientName(patient),
      documentNumber: `${patient.document_type} ${patient.document_number}`,
      sourceLabel: autoPrint ? 'documento guardado · PDF' : 'documento guardado',
      fileBase: `historia-${patient.document_number}-${(session.date ?? '').slice(0, 10) || 'atencion'}`,
      autoPrint,
    })
  }

  const openConsolidated = (autoPrint: boolean) => {
    if (!patient) return
    if (sessions.length === 0) {
      showToast('Este paciente no tiene atenciones para consolidar.', { icon: 'info', tone: 'warn' })
      return
    }
    setViewerDoc({
      html: buildConsolidatedHtml(patient, sessions),
      title: 'Historia clínica consolidada',
      subtitle: `${sessions.length} atenciones · ${autoPrint ? 'lista para guardar como PDF' : 'vista previa generada en el navegador'}`,
      patientName: patientName(patient),
      documentNumber: `${patient.document_type} ${patient.document_number}`,
      sourceLabel: autoPrint ? 'consolidada · PDF' : 'consolidada',
      fileBase: `historia-completa-${patient.document_number}`,
      autoPrint,
    })
  }

  const latest = sessions[0] ?? null
  const latestTriage = triageOf(latest)
  const latestDiagnoses = latest ? sessionDiagnoses(latest).slice(0, 4) : []
  const allergies = latest?.allergies ?? ''
  const hasSevereAllergy = Boolean(allergies && !/^(ninguna?|ninguno|no|sin|niega)/i.test(allergies.trim()))

  const recurringDiagnoses = useMemo(() => {
    const counts = new Map<string, number>()
    sessions.forEach(session => {
      sessionDiagnoses(session).forEach(diagnosis => {
        counts.set(diagnosis, (counts.get(diagnosis) ?? 0) + 1)
      })
    })
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
  }, [sessions])

  const lastMedicines = useMemo(() => (latest ? sessionMedicines(latest).slice(0, 5) : []), [latest])

  const counts = useMemo(
    () => ({
      all: sessions.length,
      labs: sessions.filter(session => filterMatches(session, 'labs')).length,
      rx: sessions.filter(session => filterMatches(session, 'rx')).length,
      dx: sessions.filter(session => filterMatches(session, 'dx')).length,
      docs: sessions.filter(session => filterMatches(session, 'docs')).length,
    }),
    [sessions],
  )

  const filteredSessions = useMemo(
    () => sessions.filter(session => filterMatches(session, filter)),
    [sessions, filter],
  )

  const fhirBundle = useMemo(() => buildFhirBundle(patient, sessions), [patient, sessions])
  const fhirJson = useMemo(() => JSON.stringify(fhirBundle, null, 2), [fhirBundle])
  const fhirCounts = useMemo(() => {
    const totals = new Map<string, number>()
    ;(fhirBundle.entry ?? []).forEach(entry => {
      const type = String(entry.resource.resourceType ?? 'Recurso')
      totals.set(type, (totals.get(type) ?? 0) + 1)
    })
    return [...totals.entries()]
  }, [fhirBundle])

  const handleDownloadFhir = () => {
    if (!patient) return
    downloadText(
      fhirJson,
      `bundle-fhir-demo-${patient.document_number}.json`,
      'application/fhir+json;charset=utf-8',
    )
    showToast('Bundle descargado. Es un mapeo de demostración: no fue validado ni enviado a un HIS.', {
      icon: 'data_object',
      tone: 'info',
    })
  }

  const handleCopyFhir = async () => {
    try {
      await navigator.clipboard.writeText(fhirJson)
      showToast('Bundle FHIR de demostración copiado.', { icon: 'content_copy' })
    } catch {
      showToast('El navegador bloqueó el portapapeles.', { icon: 'warning', tone: 'warn' })
    }
  }

  const filters: Array<{ id: SessionFilter; label: string; icon: string }> = [
    { id: 'all', label: `Todas (${counts.all})`, icon: 'timeline' },
    { id: 'dx', label: `Diagnósticos (${counts.dx})`, icon: 'clinical_notes' },
    { id: 'labs', label: `Laboratorio (${counts.labs})`, icon: 'biotech' },
    { id: 'rx', label: `Recetas (${counts.rx})`, icon: 'prescriptions' },
    { id: 'docs', label: `Documentos (${counts.docs})`, icon: 'description' },
  ]

  return (
    <ClinicalShell
      user={user}
      onLogout={onLogout}
      phase="history"
      onHome={onHome}
      onNewPatient={onNewPatient}
      onHistory={() => {}}
      onResume={onResume}
      breadcrumb={[
        'Urgencias Hospital Central',
        patient ? patientName(patient) : 'Archivo clínico',
        'Historial & FHIR',
      ]}
    >
      {viewerDoc && (
        <HistoryReportViewer document={viewerDoc} onClose={() => setViewerDoc(null)} />
      )}

      <div className="flex flex-col gap-4">
        <header className="relative overflow-hidden rounded-2xl border border-surface-border bg-white p-4 shadow-sm">
          <div className="absolute left-0 right-0 top-0 h-1.5 bg-gradient-to-r from-clinical-primary via-sky-600 to-cyan-400" />
          <div className="flex flex-col gap-3 pt-1 xl:flex-row xl:items-end xl:justify-between">
            <div className="min-w-0">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-sky-800">
                <Icon name="folder_shared" className="text-[14px]" />
                Archivo clínico persistido
              </span>
              <h1 className="mt-2 font-headline-lg text-[26px] font-bold leading-tight text-clinical-primary sm:text-[30px]">
                Historial Clínico & Evolución
              </h1>
              <p className="mt-1 max-w-2xl font-body-md text-[12.5px] leading-relaxed text-text-secondary">
                Atenciones, diagnósticos, laboratorio y documentos del paciente. La vista previa y el
                PDF se abren sobre la atención seleccionada.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {patient && (
                <>
                  <button
                    type="button"
                    onClick={() => openConsolidated(false)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-surface-border bg-white px-3 py-2 text-[11px] font-semibold text-text-secondary shadow-sm transition-colors hover:bg-surface-subtle hover:text-text-primary"
                  >
                    <Icon name="visibility" className="text-[16px] text-sky-600" />
                    Vista previa
                  </button>
                  <button
                    type="button"
                    onClick={() => openConsolidated(true)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-[11px] font-bold text-sky-800 shadow-sm transition-colors hover:bg-sky-100"
                  >
                    <Icon name="picture_as_pdf" className="text-[16px]" />
                    Descargar PDF
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleNewConsultation()}
                    disabled={starting}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-clinical-primary px-3.5 py-2 text-[11px] font-bold text-white shadow-sm transition-colors hover:bg-[#072a4a] disabled:opacity-60"
                  >
                    <Icon name={starting ? 'progress_activity' : 'add_notes'} className="text-[16px]" />
                    {starting ? 'Abriendo…' : 'Nueva atención'}
                  </button>
                </>
              )}
              {!patient && (
                <button
                  type="button"
                  onClick={onNewPatient}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-clinical-primary px-3.5 py-2 text-[11px] font-bold text-white shadow-sm transition-colors hover:bg-[#072a4a]"
                >
                  <Icon name="person_add" className="text-[16px]" />
                  Nueva consulta
                </button>
              )}
            </div>
          </div>
        </header>

        {loadingPatient && (
          <div className="flex items-center gap-2 rounded-xl border border-sky-200 bg-sky-50 px-3.5 py-2.5 text-[11px] font-semibold text-sky-900">
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-sky-200 border-t-sky-700" />
            Cargando historia clínica y atenciones…
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3.5 py-2.5 text-[11px] font-semibold text-amber-900">
            <Icon name="warning" className="mt-0.5 text-[16px] text-amber-600" />
            <span className="flex-1">{error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-[10px] font-bold uppercase text-amber-800 hover:text-amber-950"
            >
              Cerrar
            </button>
          </div>
        )}

        {!patient ? (
          <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
            <section className="flex flex-col gap-3 xl:col-span-7">
              <div className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                <label className="flex flex-col gap-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">
                    Buscar paciente
                  </span>
                  <div className="relative">
                    <Icon
                      name="search"
                      className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[20px] text-slate-400"
                    />
                    <input
                      type="search"
                      value={query}
                      onChange={event => handleQueryChange(event.target.value)}
                      placeholder="Documento del paciente · ej. 1020304050"
                      className="w-full rounded-xl border border-transparent bg-surface-subtle py-2.5 pl-10 pr-24 text-[13px] text-text-primary outline-none transition-all placeholder:text-slate-400 focus:border-sky-200 focus:bg-white focus:ring-4 focus:ring-sky-100"
                    />
                    <span className="absolute right-2.5 top-1/2 -translate-y-1/2 font-code-telemetry text-[9.5px] text-text-muted">
                      {searching ? 'buscando…' : 'MongoDB'}
                    </span>
                  </div>
                </label>

                {query.trim() && (
                  <div className="mt-2.5 flex flex-col gap-1.5">
                    {results.length === 0 && !searching ? (
                      <p className="rounded-lg border border-dashed border-surface-border bg-surface-subtle px-2.5 py-2 text-[11px] text-text-secondary">
                        Sin coincidencias para «{query.trim()}». Prueba con el número de documento
                        completo.
                      </p>
                    ) : (
                      results.map(result => (
                        <button
                          key={result.document_number}
                          type="button"
                          onClick={() =>
                            result.has_clinical_history
                              ? void openPatient(result.document_number)
                              : showToast(
                                  'Ese documento pertenece a una cuenta sin historia clínica. Inicia una nueva consulta.',
                                  { icon: 'info', tone: 'warn' },
                                )
                          }
                          className="flex w-full items-center justify-between gap-2 rounded-xl border border-surface-border bg-white px-3 py-2 text-left transition-colors hover:border-sky-200 hover:bg-sky-50/40"
                        >
                          <div className="flex min-w-0 items-center gap-2.5">
                            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-sky-100 to-sky-200 text-[10px] font-bold text-clinical-primary">
                              {initials(`${result.first_name} ${result.last_name}`)}
                            </div>
                            <div className="min-w-0">
                              <p className="truncate text-[12px] font-bold text-text-primary">
                                {result.first_name} {result.last_name}
                              </p>
                              <p className="font-code-telemetry text-[10px] text-text-secondary">
                                {result.document_type} {result.document_number}
                                {result.base_data?.age ? ` · ${result.base_data.age} años` : ''}
                              </p>
                            </div>
                          </div>
                          <span
                            className={`flex-shrink-0 rounded border px-1.5 py-0.5 text-[8.5px] font-bold uppercase ${
                              result.has_clinical_history
                                ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                                : 'border-slate-200 bg-slate-50 text-slate-500'
                            }`}
                          >
                            {result.has_clinical_history ? 'historia' : 'sin historia'}
                          </span>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>

              <div className="overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm">
                <div className="flex items-center justify-between gap-2 border-b border-surface-border px-3.5 py-2.5">
                  <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                    <Icon name="history" className="text-[17px] text-sky-600" />
                    Actividad reciente
                  </h2>
                  <span className="rounded-full bg-sky-50 px-2 py-0.5 text-[9px] font-bold uppercase text-sky-800">
                    {recent.length} pacientes
                  </span>
                </div>

                {loadingRecent ? (
                  <div className="flex items-center gap-2 px-3.5 py-5 text-[11px] text-text-secondary">
                    <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-slate-200 border-t-sky-600" />
                    Cargando actividad…
                  </div>
                ) : recent.length === 0 ? (
                  <div className="px-3.5 py-5 text-center">
                    <Icon name="folder_off" className="text-[30px] text-slate-300" />
                    <p className="mt-1 text-[11px] font-semibold text-text-secondary">
                      Aún no hay atenciones registradas.
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {recent.map(item => (
                      <button
                        key={item.document_number}
                        type="button"
                        onClick={() => void openPatient(item.document_number)}
                        className="flex w-full items-center justify-between gap-3 px-3.5 py-2.5 text-left transition-colors hover:bg-surface-subtle/70"
                      >
                        <div className="flex min-w-0 items-center gap-2.5">
                          <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-100 to-sky-200 text-[10.5px] font-bold text-clinical-primary">
                            {initials(`${item.first_name} ${item.last_name}`)}
                          </div>
                          <div className="min-w-0">
                            <p className="truncate text-[12.5px] font-bold text-text-primary">
                              {item.first_name} {item.last_name}
                            </p>
                            <p className="truncate font-code-telemetry text-[10px] text-text-secondary">
                              {item.document_number} · {item.age || '—'} años · {item.last_reason || 'Sin motivo'}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-shrink-0 flex-col items-end gap-0.5">
                          <span className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[9px] font-bold text-sky-800">
                            {item.session_count} atenciones
                          </span>
                          <span className="font-code-telemetry text-[9px] text-text-muted">
                            {formatDate(item.last_session_date, false)}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </section>

            <aside className="flex flex-col gap-3 xl:col-span-5">
              <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                  <Icon name="route" className="text-[17px] text-sky-600" />
                  Ciclo real del expediente
                </h2>
                <ol className="mt-2.5 flex flex-col gap-2.5">
                  {[
                    {
                      icon: 'person_search',
                      title: '1. Identificas al paciente',
                      text: 'Buscas por documento; la identidad y las atenciones vienen de clinical_histories y sessions.',
                    },
                    {
                      icon: 'timeline',
                      title: '2. Revisas la evolución',
                      text: 'Cada tarjeta es una atención con vitales, triaje, diagnósticos, laboratorio y receta.',
                    },
                    {
                      icon: 'visibility',
                      title: '3. Abres la vista previa',
                      text: 'El segundo panel muestra el documento guardado o la historia consolidada.',
                    },
                    {
                      icon: 'picture_as_pdf',
                      title: '4. Guardas el PDF',
                      text: 'Desde el visor imprimes o eliges «Guardar como PDF» en el navegador.',
                    },
                  ].map(step => (
                    <li key={step.title} className="flex items-start gap-2.5">
                      <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-sky-200 bg-sky-50 text-sky-700">
                        <Icon name={step.icon} className="text-[16px]" />
                      </span>
                      <div>
                        <p className="text-[11px] font-bold text-text-primary">{step.title}</p>
                        <p className="mt-0.5 text-[10.5px] leading-relaxed text-text-secondary">{step.text}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </section>

              <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                  <Icon name="fact_check" className="text-[17px] text-emerald-600" />
                  Qué es real y qué no
                </h2>
                <div className="mt-2 flex flex-col gap-1.5 text-[10.5px]">
                  {[
                    ['Historia, atenciones, triaje, laboratorio y reportes', true],
                    ['Documento HTML guardado por atención', true],
                    ['Vista consolidada del expediente', true],
                    ['Firma electrónica y envío al HIS', false],
                    ['Validación HAPI FHIR / interoperabilidad real', false],
                  ].map(([label, real]) => (
                    <div key={String(label)} className="flex items-start gap-1.5">
                      <Icon
                        name={real ? 'check_circle' : 'schedule'}
                        className={`mt-0.5 text-[14px] ${real ? 'text-emerald-600' : 'text-amber-500'}`}
                      />
                      <span className={real ? 'text-text-secondary' : 'text-text-muted'}>
                        {label} {real ? '' : '· roadmap'}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            </aside>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {/* Ficha del paciente */}
            <section className="relative overflow-hidden rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
              <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
                <div className="flex min-w-0 items-start gap-3">
                  <div className="relative flex-shrink-0">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-sky-200 bg-gradient-to-br from-sky-100 to-sky-200 text-[15px] font-bold text-clinical-primary shadow-inner">
                      {initials(patientName(patient))}
                    </div>
                    <span
                      className={`absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full ring-2 ring-white ${
                        latestTriage?.dot ?? 'bg-slate-400'
                      }`}
                    />
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <h2 className="truncate font-headline-sm text-[17px] font-bold text-text-primary">
                        {patientName(patient)}
                      </h2>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700">
                        {patient.age ? `${patient.age} años` : 'Edad sin dato'}
                      </span>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700">
                        {genderLabel(patient.gender)}
                      </span>
                      {latestTriage && (
                        <span
                          className={`rounded-full border px-2 py-0.5 text-[9.5px] font-bold ${latestTriage.className}`}
                        >
                          {latestTriage.label}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 font-code-telemetry text-[10.5px] text-text-secondary">
                      <span>
                        <strong className="text-sky-700">
                          {patient.document_type} {patient.document_number}
                        </strong>
                      </span>
                      <span className="text-slate-300">·</span>
                      <span>{patient.birth_date || 'Nacimiento sin dato'}</span>
                      <span className="text-slate-300">·</span>
                      <span>{patient.city || 'Ciudad sin dato'}</span>
                      <span className="text-slate-300">·</span>
                      <span>{sessions.length} atenciones</span>
                    </p>
                    <button
                      type="button"
                      onClick={closePatient}
                      className="mt-1.5 inline-flex items-center gap-1 text-[10.5px] font-semibold text-sky-700 hover:text-clinical-primary"
                    >
                      <Icon name="arrow_back" className="text-[14px]" />
                      Cambiar paciente
                    </button>
                  </div>
                </div>

                <div className="flex flex-col items-start gap-1 xl:items-end">
                  {hasSevereAllergy ? (
                    <span className="allergy-pulse inline-flex max-w-full items-center gap-1.5 rounded-xl border border-rose-300 bg-rose-50 px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wide text-rose-700">
                      <Icon name="warning" className="text-[15px]" filled />
                      <span className="truncate">Alergia: {allergies}</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">
                      <Icon name="verified_user" className="text-[15px]" />
                      {allergies ? `Alergias: ${allergies}` : 'Alergias sin registrar'}
                    </span>
                  )}
                  <span className="font-code-telemetry text-[9.5px] text-text-muted">
                    Última atención: {formatDate(latest?.date)}
                  </span>
                </div>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                {[
                  { label: 'PA', value: latest?.blood_pressure || '—', unit: 'mmHg', icon: 'blood_pressure' },
                  { label: 'FC', value: latest?.heart_rate || '—', unit: 'lpm', icon: 'favorite' },
                  { label: 'SpO₂', value: latest?.oxygen_saturation || '—', unit: '%', icon: 'air' },
                  { label: 'Temp.', value: latest?.temperature || '—', unit: '°C', icon: 'thermostat' },
                ].map(vital => (
                  <div key={vital.label} className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                    <span className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-text-muted">
                      <Icon name={vital.icon} className="text-[13px] text-sky-600" />
                      {vital.label}
                    </span>
                    <p className="mt-0.5 flex items-baseline gap-1">
                      <span className="font-code-telemetry text-[15px] font-bold text-text-primary">
                        {vital.value}
                      </span>
                      <span className="text-[9px] text-text-muted">{vital.unit}</span>
                    </p>
                    <span className="text-[8.5px] text-text-muted">última atención</span>
                  </div>
                ))}
              </div>

              {latestDiagnoses.length > 0 && (
                <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                  <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                    Diagnósticos de la última atención:
                  </span>
                  {latestDiagnoses.map(diagnosis => (
                    <span
                      key={diagnosis}
                      className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[9.5px] font-semibold text-sky-800"
                    >
                      {diagnosis}
                    </span>
                  ))}
                </div>
              )}
            </section>

            {/* Pestañas */}
            <div className="flex items-center gap-1.5 overflow-x-auto rounded-xl border border-surface-border bg-white p-1.5 shadow-sm">
              {[
                { id: 'historial' as const, label: 'Historial de atenciones', icon: 'timeline' },
                { id: 'fhir' as const, label: 'FHIR R4 · simulado', icon: 'hub' },
              ].map(item => {
                const active = tab === item.id
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setTab(item.id)}
                    className={`flex flex-shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-[11px] font-semibold transition-colors ${
                      active
                        ? 'bg-sky-50 font-bold text-clinical-primary ring-1 ring-inset ring-sky-200'
                        : 'text-text-secondary hover:bg-surface-subtle'
                    }`}
                  >
                    <Icon name={item.icon} className={`text-[16px] ${active ? 'text-sky-600' : 'text-slate-400'}`} />
                    {item.label}
                  </button>
                )
              })}
            </div>

            {tab === 'historial' ? (
              <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
                <section className="flex flex-col gap-3 xl:col-span-7">
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
                    {filters.map(item => {
                      const active = filter === item.id
                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setFilter(item.id)}
                          className={`flex flex-shrink-0 items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-semibold transition-colors ${
                            active
                              ? 'bg-clinical-primary text-white shadow-sm'
                              : 'border border-surface-border bg-white text-text-secondary hover:bg-surface-subtle'
                          }`}
                        >
                          <Icon name={item.icon} className="text-[13px]" />
                          {item.label}
                        </button>
                      )
                    })}
                  </div>

                  {filteredSessions.length === 0 ? (
                    <div className="rounded-2xl border border-dashed border-surface-border bg-white px-4 py-8 text-center">
                      <Icon name="filter_alt_off" className="text-[32px] text-slate-300" />
                      <p className="mt-1 text-[11.5px] font-semibold text-text-secondary">
                        No hay atenciones con ese filtro.
                      </p>
                    </div>
                  ) : (
                    filteredSessions.map((session, index) => {
                      const triage = triageOf(session)
                      const diagnoses = sessionDiagnoses(session)
                      const medicines = sessionMedicines(session)
                      const sessionKey = session.id ?? `session-${index}`
                      const isOpen = expanded === sessionKey
                      const labs = Object.entries(session.labs ?? {}).filter(([, value]) =>
                        String(value ?? '').trim(),
                      )

                      return (
                        <article
                          key={sessionKey}
                          className="overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm"
                        >
                          <div className="flex items-start gap-2.5 p-3.5 pb-2">
                            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border border-sky-200 bg-sky-50 text-sky-700">
                              <Icon name="clinical_notes" className="text-[20px]" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex flex-wrap items-center gap-1.5">
                                <span className="rounded border border-surface-border bg-surface-subtle px-1.5 py-0.5 font-code-telemetry text-[9px] font-semibold text-text-secondary">
                                  {formatDate(session.date)}
                                </span>
                                {triage && (
                                  <span className={`rounded-full border px-2 py-0.5 text-[9px] font-bold ${triage.className}`}>
                                    {triage.label}
                                  </span>
                                )}
                                {hasReport(session) && (
                                  <span className="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[8.5px] font-bold uppercase text-emerald-700">
                                    documento
                                  </span>
                                )}
                                {!hasReport(session) && (
                                  <span className="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[8.5px] font-bold uppercase text-slate-500">
                                    sin documento
                                  </span>
                                )}
                              </div>
                              <h3 className="mt-1 truncate font-headline-sm text-[13px] font-bold text-text-primary">
                                {session.consultation_reason || 'Consulta clínica'}
                              </h3>
                              <p className="truncate text-[10px] text-text-muted">
                                {session.doctor_name || 'Médico asistencial'}
                                {session.hospital_name ? ` · ${session.hospital_name}` : ''}
                                {session.triage_system ? ` · ${session.triage_system}` : ''}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-1.5 px-3.5 pb-2.5 sm:grid-cols-4">
                            {[
                              { label: 'PA', value: session.blood_pressure || '—' },
                              { label: 'FC', value: session.heart_rate ? `${session.heart_rate} lpm` : '—' },
                              { label: 'SpO₂', value: session.oxygen_saturation ? `${session.oxygen_saturation}%` : '—' },
                              { label: 'T°', value: session.temperature ? `${session.temperature} °C` : '—' },
                            ].map(vital => (
                              <div
                                key={vital.label}
                                className="rounded-lg border border-surface-border bg-surface-subtle/70 px-2 py-1.5"
                              >
                                <span className="text-[8.5px] font-bold uppercase tracking-wider text-text-muted">
                                  {vital.label}
                                </span>
                                <p className="font-code-telemetry text-[11px] font-bold text-text-primary">
                                  {vital.value}
                                </p>
                              </div>
                            ))}
                          </div>

                          {diagnoses.length > 0 && (
                            <div className="flex flex-wrap gap-1 px-3.5 pb-2.5">
                              {diagnoses.slice(0, 3).map(diagnosis => (
                                <span
                                  key={diagnosis}
                                  className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[9.5px] font-semibold text-sky-800"
                                >
                                  {diagnosis}
                                </span>
                              ))}
                            </div>
                          )}

                          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-surface-border bg-surface-subtle/50 px-3 py-2">
                            <button
                              type="button"
                              onClick={() => setExpanded(isOpen ? null : sessionKey)}
                              className="inline-flex items-center gap-1 text-[10.5px] font-bold text-sky-700 hover:text-clinical-primary"
                            >
                              <Icon name={isOpen ? 'expand_less' : 'expand_more'} className="text-[16px]" />
                              {isOpen ? 'Ocultar detalle' : 'Ver detalle clínico'}
                            </button>
                            <div className="flex flex-wrap items-center gap-1.5">
                              <button
                                type="button"
                                onClick={() => openSessionDocument(session)}
                                disabled={!hasReport(session)}
                                className="inline-flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2 py-1 text-[10px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary disabled:opacity-50"
                              >
                                <Icon name="visibility" className="text-[14px]" />
                                Vista previa
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  openSessionDocument(session, true)
                                }}
                                disabled={!hasReport(session)}
                                className="inline-flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2 py-1 text-[10px] font-bold text-sky-800 transition-colors hover:bg-sky-100 disabled:opacity-50"
                              >
                                <Icon name="picture_as_pdf" className="text-[14px]" />
                                PDF
                              </button>
                            </div>
                          </div>

                          {isOpen && (
                            <div className="mimetic-fade-up grid grid-cols-1 gap-3 border-t border-surface-border p-3.5 sm:grid-cols-2">
                              <div>
                                <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                  Evolución
                                </span>
                                <p className="mt-0.5 text-[10.5px] leading-relaxed text-text-secondary">
                                  {session.symptom_evolution || 'Sin evolución registrada.'}
                                </p>
                              </div>
                              <div>
                                <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                  Triaje
                                </span>
                                <p className="mt-0.5 text-[10.5px] leading-relaxed text-text-secondary">
                                  {session.triage_score || session.triage_discriminators || 'Sin detalle de triaje.'}
                                </p>
                                {session.triage_discriminators && session.triage_score && (
                                  <p className="mt-1 text-[9.5px] leading-relaxed text-text-muted">
                                    {session.triage_discriminators}
                                  </p>
                                )}
                              </div>

                              {(session.symptoms ?? []).length > 0 && (
                                <div>
                                  <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                    Síntomas
                                  </span>
                                  <div className="mt-1 flex flex-wrap gap-1">
                                    {(session.symptoms ?? []).map(symptom => (
                                      <span
                                        key={symptom}
                                        className="rounded-full border border-surface-border bg-surface-subtle px-1.5 py-0.5 text-[9px] font-medium text-text-secondary"
                                      >
                                        {symptom}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {labs.length > 0 && (
                                <div>
                                  <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                    Laboratorio urgente
                                  </span>
                                  <div className="mt-1 divide-y divide-slate-100 rounded-lg border border-surface-border">
                                    {labs.map(([key, value]) => (
                                      <div key={key} className="flex items-center justify-between px-2 py-1">
                                        <span className="text-[9.5px] text-text-secondary">
                                          {LAB_LABELS[key]?.label ?? key}
                                        </span>
                                        <span className="font-code-telemetry text-[9.5px] font-bold text-text-primary">
                                          {value} {LAB_LABELS[key]?.unit ?? ''}
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {medicines.length > 0 && (
                                <div>
                                  <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                    Plan farmacológico
                                  </span>
                                  <ul className="mt-1 flex flex-col gap-0.5">
                                    {medicines.map(medicine => (
                                      <li key={medicine} className="flex items-start gap-1 text-[10px] text-text-secondary">
                                        <Icon name="medication" className="mt-0.5 text-[13px] text-sky-600" />
                                        {medicine}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {session.doctor_review?.doctorNotes && (
                                <div className="sm:col-span-2">
                                  <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                                    Nota clínica
                                  </span>
                                  <p className="mt-0.5 whitespace-pre-wrap rounded-lg border border-sky-100 bg-sky-50/60 px-2 py-1.5 text-[10.5px] leading-relaxed text-sky-950">
                                    {session.doctor_review.doctorNotes}
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </article>
                      )
                    })
                  )}
                </section>

                <aside className="flex flex-col gap-3 xl:col-span-5">
                  <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                    <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                      <Icon name="summarize" className="text-[17px] text-sky-600" />
                      Resumen del expediente
                    </h2>
                    <div className="mt-2.5 grid grid-cols-2 gap-2">
                      <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Atenciones
                        </span>
                        <p className="font-headline-sm text-lg font-black text-clinical-primary">{sessions.length}</p>
                      </div>
                      <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Documentos
                        </span>
                        <p className="font-headline-sm text-lg font-black text-clinical-primary">
                          {counts.docs}/{sessions.length}
                        </p>
                      </div>
                    </div>

                    <div className="mt-3">
                      <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                        Diagnósticos recurrentes
                      </span>
                      {recurringDiagnoses.length > 0 ? (
                        <div className="mt-1 flex flex-col gap-1">
                          {recurringDiagnoses.map(([diagnosis, count]) => (
                            <div
                              key={diagnosis}
                              className="flex items-center justify-between gap-2 rounded-lg border border-surface-border bg-white px-2 py-1"
                            >
                              <span className="truncate text-[10.5px] font-semibold text-text-primary">
                                {diagnosis}
                              </span>
                              <span className="rounded bg-sky-50 px-1.5 py-0.5 font-code-telemetry text-[9px] font-bold text-sky-700">
                                {count}×
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-0.5 text-[10.5px] italic text-text-muted">Sin diagnósticos registrados.</p>
                      )}
                    </div>

                    {lastMedicines.length > 0 && (
                      <div className="mt-3">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Medicamentos de la última atención
                        </span>
                        <ul className="mt-1 flex flex-col gap-0.5">
                          {lastMedicines.map(medicine => (
                            <li key={medicine} className="flex items-start gap-1 text-[10px] text-text-secondary">
                              <Icon name="medication" className="mt-0.5 text-[13px] text-sky-600" />
                              {medicine}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <button
                      type="button"
                      onClick={() => openConsolidated(false)}
                      className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-xl border border-sky-200 bg-sky-50 px-2.5 py-2 text-[10.5px] font-bold text-sky-800 transition-colors hover:bg-sky-100"
                    >
                      <Icon name="visibility" className="text-[15px]" />
                      Ver historia consolidada
                    </button>
                  </section>

                  <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                    <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                      <Icon name="description" className="text-[17px] text-sky-600" />
                      Documentos por atención
                    </h2>
                    {counts.docs === 0 ? (
                      <p className="mt-1.5 rounded-lg border border-dashed border-surface-border bg-surface-subtle px-2.5 py-2 text-[10.5px] text-text-secondary">
                        Aún no hay documentos generados. Se crean al cerrar una consulta.
                      </p>
                    ) : (
                      <div className="mt-1.5 flex flex-col gap-1">
                        {sessions
                          .filter(hasReport)
                          .slice(0, 5)
                          .map(session => (
                            <button
                              key={session.id ?? session.date}
                              type="button"
                              onClick={() => openSessionDocument(session)}
                              className="flex items-center justify-between gap-2 rounded-lg border border-surface-border bg-surface-subtle/60 px-2 py-1.5 text-left transition-colors hover:bg-sky-50"
                            >
                              <div className="min-w-0">
                                <p className="truncate text-[10.5px] font-semibold text-text-primary">
                                  {session.consultation_reason || 'Consulta clínica'}
                                </p>
                                <p className="font-code-telemetry text-[9px] text-text-muted">
                                  {formatDate(session.date, false)}
                                </p>
                              </div>
                              <Icon name="visibility" className="flex-shrink-0 text-[15px] text-sky-600" />
                            </button>
                          ))}
                      </div>
                    )}
                  </section>

                  <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                    <h2 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                      <Icon name="verified_user" className="text-[17px] text-emerald-600" />
                      Trazabilidad real
                    </h2>
                    <dl className="mt-2 flex flex-col gap-1.5 text-[10px]">
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                        <dt className="text-text-muted">Historia creada</dt>
                        <dd className="font-code-telemetry font-semibold text-text-primary">
                          {formatDate(patient.created_at, false)}
                        </dd>
                      </div>
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                        <dt className="text-text-muted">Última actualización</dt>
                        <dd className="font-code-telemetry font-semibold text-text-primary">
                          {formatDate(patient.updated_at, false)}
                        </dd>
                      </div>
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                        <dt className="text-text-muted">Origen</dt>
                        <dd className="font-semibold text-text-primary">MongoDB · MIMETIC</dd>
                      </div>
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1">
                        <dt className="text-text-muted">Firma electrónica</dt>
                        <dd className="font-semibold text-amber-700">roadmap</dd>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <dt className="text-text-muted">Envío al HIS</dt>
                        <dd className="font-semibold text-amber-700">roadmap</dd>
                      </div>
                    </dl>
                  </section>
                </aside>
              </div>
            ) : (
              <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-12">
                <section className="flex flex-col gap-3 xl:col-span-8">
                  <div className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[9.5px] font-bold uppercase tracking-wider text-amber-800">
                          <Icon name="science" className="text-[13px]" />
                          Simulación · no validado
                        </span>
                        <h2 className="mt-1.5 font-headline-sm text-[15px] font-bold text-text-primary">
                          Bundle FHIR R4 de {patientName(patient)}
                        </h2>
                        <p className="mt-0.5 text-[11px] leading-relaxed text-text-secondary">
                          Mapeo local de los datos reales de MongoDB con fines de demostración. No se
                          envía a HAPI FHIR, SAP/Cerner ni a ningún HIS.
                        </p>
                      </div>
                      <span className="rounded-lg border border-surface-border bg-surface-subtle px-2 py-1 font-code-telemetry text-[9.5px] text-text-secondary">
                        Bundle/{patient.document_number}
                      </span>
                    </div>

                    <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                      <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Recursos
                        </span>
                        <p className="font-code-telemetry text-[16px] font-bold text-clinical-primary">
                          {fhirBundle.total}
                        </p>
                      </div>
                      <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Atenciones
                        </span>
                        <p className="font-code-telemetry text-[16px] font-bold text-clinical-primary">
                          {sessions.length}
                        </p>
                      </div>
                      <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-text-muted">
                          Documentos
                        </span>
                        <p className="font-code-telemetry text-[16px] font-bold text-clinical-primary">
                          {counts.docs}
                        </p>
                      </div>
                      <div className="rounded-xl border border-amber-200 bg-amber-50 p-2.5">
                        <span className="text-[9px] font-bold uppercase tracking-wider text-amber-700">
                          Validación FHIR
                        </span>
                        <p className="font-code-telemetry text-[12px] font-bold text-amber-800">no ejecutada</p>
                        <span className="text-[8px] text-amber-700">roadmap</span>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-1.5">
                      <button
                        type="button"
                        onClick={handleDownloadFhir}
                        className="inline-flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2.5 py-1.5 text-[10.5px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
                      >
                        <Icon name="download" className="text-[15px]" />
                        Descargar JSON
                      </button>
                      <button
                        type="button"
                        onClick={() => void handleCopyFhir()}
                        className="inline-flex items-center gap-1 rounded-lg border border-surface-border bg-white px-2.5 py-1.5 text-[10.5px] font-semibold text-text-secondary transition-colors hover:bg-surface-subtle hover:text-text-primary"
                      >
                        <Icon name="content_copy" className="text-[15px]" />
                        Copiar bundle
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowFhirJson(current => !current)}
                        className="inline-flex items-center gap-1 rounded-lg border border-sky-200 bg-sky-50 px-2.5 py-1.5 text-[10.5px] font-bold text-sky-800 transition-colors hover:bg-sky-100"
                      >
                        <Icon name={showFhirJson ? 'unfold_less' : 'data_object'} className="text-[15px]" />
                        {showFhirJson ? 'Ocultar JSON' : 'Ver JSON'}
                      </button>
                    </div>

                    {showFhirJson && (
                      <pre className="mimetic-fade-up mt-2 max-h-[420px] overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-3 font-code-telemetry text-[9.5px] leading-relaxed text-emerald-300">
                        {fhirJson}
                      </pre>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {fhirCounts.map(([type, total]) => (
                      <div key={type} className="rounded-xl border border-surface-border bg-white p-2.5 shadow-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-text-primary">{type}</span>
                          <span className="font-code-telemetry text-[11px] font-bold text-sky-700">{total}</span>
                        </div>
                        <p className="mt-0.5 text-[9px] leading-snug text-text-muted">
                          {type === 'Patient'
                            ? 'Identidad del paciente'
                            : type === 'Encounter'
                              ? 'Una por atención'
                              : type === 'Observation'
                                ? 'Vitales y laboratorio'
                                : type === 'Condition'
                                  ? 'Diagnósticos registrados'
                                  : type === 'MedicationRequest'
                                    ? 'Plan farmacológico'
                                    : 'Documentos disponibles'}
                        </p>
                      </div>
                    ))}
                  </div>
                </section>

                <aside className="flex flex-col gap-3 xl:col-span-4">
                  <section className="rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
                    <h3 className="flex items-center gap-1.5 font-headline-sm text-[12.5px] font-bold text-text-primary">
                      <Icon name="conversion_path" className="text-[17px] text-sky-600" />
                      Correspondencia usada
                    </h3>
                    <ul className="mt-2 flex flex-col gap-1.5 text-[10.5px] text-text-secondary">
                      <li>· Sesión clínica → <strong className="text-text-primary">Encounter</strong></li>
                      <li>· Signos vitales y labs → <strong className="text-text-primary">Observation</strong></li>
                      <li>· Diagnósticos → <strong className="text-text-primary">Condition</strong></li>
                      <li>· Medicamentos → <strong className="text-text-primary">MedicationRequest</strong></li>
                      <li>· Reporte HTML → <strong className="text-text-primary">DocumentReference</strong></li>
                    </ul>
                    <p className="mt-2 rounded-lg border border-dashed border-amber-200 bg-amber-50 px-2.5 py-1.5 text-[9.5px] leading-snug text-amber-800">
                      Los códigos LOINC/SNOMED/RxNorm no se resuelven todavía: el bundle usa texto
                      libre. La validación de perfiles está en roadmap.
                    </p>
                  </section>

                  <button
                    type="button"
                    onClick={() => setTab('historial')}
                    className="flex items-center justify-center gap-1.5 rounded-xl border border-surface-border bg-white px-2.5 py-2 text-[10.5px] font-semibold text-text-secondary shadow-sm transition-colors hover:bg-surface-subtle hover:text-text-primary"
                  >
                    <Icon name="arrow_back" className="text-[15px]" />
                    Volver al historial
                  </button>
                </aside>
              </div>
            )}
          </div>
        )}
      </div>
    </ClinicalShell>
  )
}
