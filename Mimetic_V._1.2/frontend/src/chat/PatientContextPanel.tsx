import { useMemo, useState } from 'react'
import type { DoctorReview, PatientInfo, SessionSnapshot } from './types'
import { Icon, initials, genderLabel, Modal, useToast } from './ui'

type Props = {
  patientInfo: PatientInfo
  lastSession?: SessionSnapshot | null
  currentSymptoms?: string[]
  doctorReview?: DoctorReview
}

type LevelMeta = {
  label: string
  short: string
  badge: string
  dot: string
  panel: string
  heading: string
}

const TRIAGE_META: Record<number, LevelMeta> = {
  1: {
    label: 'Nivel 1 · Rojo',
    short: 'Atención inmediata',
    badge: 'border-rose-300 bg-rose-100 text-rose-800',
    dot: 'bg-rose-500',
    panel: 'from-rose-50/80 via-white to-white border-rose-200',
    heading: 'text-rose-950',
  },
  2: {
    label: 'Nivel 2 · Naranja',
    short: 'Emergencia',
    badge: 'border-orange-300 bg-orange-100 text-orange-800',
    dot: 'bg-orange-500',
    panel: 'from-orange-50/80 via-white to-white border-orange-200',
    heading: 'text-orange-950',
  },
  3: {
    label: 'Nivel 3 · Amarillo',
    short: 'Urgente',
    badge: 'border-amber-300 bg-amber-100 text-amber-900',
    dot: 'bg-amber-500',
    panel: 'from-amber-50/80 via-white to-white border-amber-200',
    heading: 'text-amber-950',
  },
  4: {
    label: 'Nivel 4 · Verde',
    short: 'Estándar',
    badge: 'border-emerald-300 bg-emerald-100 text-emerald-800',
    dot: 'bg-emerald-500',
    panel: 'from-emerald-50/80 via-white to-white border-emerald-200',
    heading: 'text-emerald-950',
  },
  5: {
    label: 'Nivel 5 · Azul',
    short: 'No urgente',
    badge: 'border-sky-300 bg-sky-100 text-sky-800',
    dot: 'bg-sky-500',
    panel: 'from-sky-50/80 via-white to-white border-sky-200',
    heading: 'text-sky-950',
  },
}

const LEVEL_FALLBACK = TRIAGE_META[5]

function firstNonEmpty(...values: (string | undefined | null)[]) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return ''
}

function toNumber(value?: string) {
  if (!value) return undefined
  const parsed = Number.parseFloat(value.replace(',', '.'))
  return Number.isFinite(parsed) ? parsed : undefined
}

function parseBloodPressure(value?: string) {
  const match = /(\d{2,3})\s*[/-]\s*(\d{2,3})/.exec(value ?? '')
  if (!match) return { systolic: undefined, diastolic: undefined }
  return { systolic: Number(match[1]), diastolic: Number(match[2]) }
}

function classify(value: number | undefined, min: number, max: number, hardMin?: number, hardMax?: number) {
  if (value === undefined) return 'empty' as const
  if ((hardMin !== undefined && value < hardMin) || (hardMax !== undefined && value > hardMax)) return 'danger' as const
  if (value < min || value > max) return 'warn' as const
  return 'normal' as const
}

const VITAL_TONE = {
  normal: 'border-emerald-100 bg-emerald-50/50 text-emerald-700',
  warn: 'border-amber-200 bg-amber-50/60 text-amber-700',
  danger: 'border-rose-200 bg-rose-50/60 text-rose-700',
  empty: 'border-surface-border bg-surface-subtle/60 text-slate-400',
}

const LAB_ROWS = [
  { key: 'pao2', field: 'lab_pao2', label: 'pO₂ arterial', unit: 'mmHg', reference: '80–100', min: 80, max: 100 },
  { key: 'lactate', field: 'lab_lactate', label: 'Lactato', unit: 'mmol/L', reference: '0.5–2.2', min: 0.5, max: 2.2 },
  { key: 'leukocytes', field: 'lab_leukocytes', label: 'Leucocitos', unit: '10³/µL', reference: '4.0–11.0', min: 4, max: 11 },
  { key: 'creatinine', field: 'lab_creatinine', label: 'Creatinina', unit: 'mg/dL', reference: '0.6–1.3', min: 0.6, max: 1.3 },
  { key: 'crp', field: 'lab_crp', label: 'Proteína C reactiva', unit: 'mg/L', reference: '< 5', min: 0, max: 5 },
] as const

function suggestTriage(vitals: {
  spo2?: number
  systolic?: number
  heartRate?: number
  respiratoryRate?: number
  temperature?: number
}) {
  const reasons: string[] = []
  let level = 5

  const escalate = (next: number) => {
    if (next < level) level = next
  }

  if (vitals.spo2 !== undefined) {
    if (vitals.spo2 < 85) {
      escalate(1)
      reasons.push(`SpO₂ ${vitals.spo2}%`)
    } else if (vitals.spo2 < 90) {
      escalate(2)
      reasons.push(`SpO₂ ${vitals.spo2}%`)
    } else if (vitals.spo2 < 94) {
      escalate(3)
      reasons.push(`SpO₂ ${vitals.spo2}%`)
    }
  }

  if (vitals.systolic !== undefined) {
    if (vitals.systolic < 80) {
      escalate(1)
      reasons.push(`PAS ${vitals.systolic} mmHg`)
    } else if (vitals.systolic < 90) {
      escalate(2)
      reasons.push(`PAS ${vitals.systolic} mmHg`)
    } else if (vitals.systolic >= 160) {
      escalate(3)
      reasons.push(`PAS ${vitals.systolic} mmHg`)
    }
  }

  if (vitals.heartRate !== undefined) {
    if (vitals.heartRate > 150 || vitals.heartRate < 40) {
      escalate(1)
      reasons.push(`FC ${vitals.heartRate} lpm`)
    } else if (vitals.heartRate > 120) {
      escalate(2)
      reasons.push(`FC ${vitals.heartRate} lpm`)
    } else if (vitals.heartRate > 110) {
      escalate(3)
      reasons.push(`FC ${vitals.heartRate} lpm`)
    }
  }

  if (vitals.respiratoryRate !== undefined) {
    if (vitals.respiratoryRate > 35) {
      escalate(1)
      reasons.push(`FR ${vitals.respiratoryRate} rpm`)
    } else if (vitals.respiratoryRate >= 25) {
      escalate(2)
      reasons.push(`FR ${vitals.respiratoryRate} rpm`)
    } else if (vitals.respiratoryRate >= 22) {
      escalate(3)
      reasons.push(`FR ${vitals.respiratoryRate} rpm`)
    }
  }

  if (vitals.temperature !== undefined) {
    if (vitals.temperature >= 40) {
      escalate(2)
      reasons.push(`T ${vitals.temperature} °C`)
    } else if (vitals.temperature >= 39) {
      escalate(3)
      reasons.push(`T ${vitals.temperature} °C`)
    }
  }

  return { level, reasons }
}

function EcgStrip({ heartRate }: { heartRate?: number }) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-slate-950 p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 font-code-telemetry text-[10.5px] font-bold uppercase tracking-wider text-cyan-400">
          <Icon name="monitor_heart" className="text-[16px]" />
          ECG · Derivación DII
        </span>
        <span className="flex items-center gap-1.5">
          <span className="rounded border border-cyan-400/30 bg-cyan-400/10 px-1.5 py-0.5 font-code-telemetry text-[9px] font-bold text-cyan-300">
            SIMULADO
          </span>
          <span className="font-code-telemetry text-[10px] text-cyan-300">
            {heartRate ? `${heartRate} lpm` : 'sin señal'}
          </span>
        </span>
      </div>
      <div className="ecg-grid relative flex h-20 w-full items-center overflow-hidden rounded bg-slate-950/70">
        <svg
          viewBox="0 0 600 70"
          preserveAspectRatio="none"
          className="h-full w-full text-cyan-400"
          role="img"
          aria-label="Trazado de electrocardiograma simulado"
        >
          <path
            className="ecg-trace"
            d="M0,30 L30,30 L38,28 L42,30 L50,30 L55,10 L60,54 L65,20 L70,35 L75,30 L115,30 L123,28 L127,30 L135,30 L140,8 L145,55 L150,18 L155,36 L160,30 L200,30 L208,28 L212,30 L220,30 L225,9 L230,56 L235,19 L240,35 L245,30 L285,30 L293,28 L297,30 L305,30 L310,8 L315,55 L320,18 L325,36 L330,30 L370,30 L378,28 L382,30 L390,30 L395,9 L400,55 L405,20 L410,35 L415,30 L455,30 L463,28 L467,30 L475,30 L480,10 L485,54 L490,20 L495,35 L500,30 L540,30 L548,28 L552,30 L560,30 L565,9 L570,55 L575,20 L580,35 L600,30"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2.2"
            style={{ filter: 'drop-shadow(0 0 4px rgba(34,211,238,0.55))' }}
          />
        </svg>
      </div>
      <div className="mt-1.5 flex items-center justify-between font-code-telemetry text-[9px] text-slate-500">
        <span>25 mm/s · 10 mm/mV</span>
        <span>Telemetría no conectada · demo</span>
      </div>
    </div>
  )
}

export default function PatientContextPanel({
  patientInfo,
  lastSession,
  currentSymptoms = [],
  doctorReview,
}: Props) {
  const showToast = useToast()
  const [tab, setTab] = useState<'vitals' | 'antecedents' | 'fhir'>('vitals')
  const [bedOpen, setBedOpen] = useState(false)
  const [bedPriority, setBedPriority] = useState<'1' | '2'>('1')
  const [bedService, setBedService] = useState('UCI médica · monitorización invasiva')

  const name =
    firstNonEmpty(patientInfo.name, `${patientInfo.first_name ?? ''} ${patientInfo.last_name ?? ''}`) ||
    'Paciente sin identificar'
  const documentNumber = firstNonEmpty(patientInfo.id_document)
  const age = firstNonEmpty(patientInfo.age)
  const gender = genderLabel(firstNonEmpty(patientInfo.gender))

  const allergies = firstNonEmpty(patientInfo.allergies, lastSession?.allergies)
  const hasSevereAllergy = Boolean(
    allergies && !/^(ninguna?|ninguno|no|sin|niega)/i.test(allergies.trim()),
  )

  const bloodPressureRaw = firstNonEmpty(patientInfo.blood_pressure, lastSession?.blood_pressure)
  const { systolic } = parseBloodPressure(bloodPressureRaw)
  const heartRate = toNumber(firstNonEmpty(patientInfo.heart_rate, lastSession?.heart_rate))
  const respiratoryRate = toNumber(firstNonEmpty(patientInfo.respiratory_rate, lastSession?.respiratory_rate))
  const temperature = toNumber(firstNonEmpty(patientInfo.temperature, lastSession?.temperature))
  const oxygenSaturation = toNumber(
    firstNonEmpty(patientInfo.oxygen_saturation, lastSession?.oxygen_saturation),
  )
  const weight = toNumber(firstNonEmpty(patientInfo.weight, lastSession?.weight))
  const height = toNumber(firstNonEmpty(patientInfo.height, lastSession?.height))
  const bmi = weight && height ? weight / (height / 100) ** 2 : undefined

  const registeredTriageLevel = Number(
    firstNonEmpty(
      patientInfo.triage_level,
      lastSession?.triage_level ? String(lastSession.triage_level) : '',
    ),
  )
  const suggestion = useMemo(
    () =>
      suggestTriage({
        spo2: oxygenSaturation,
        systolic,
        heartRate,
        respiratoryRate,
        temperature,
      }),
    [oxygenSaturation, systolic, heartRate, respiratoryRate, temperature],
  )

  const usingSuggestion = !(registeredTriageLevel >= 1 && registeredTriageLevel <= 5)
  const triageLevel = usingSuggestion ? suggestion.level : registeredTriageLevel
  const triageMeta = TRIAGE_META[triageLevel] ?? LEVEL_FALLBACK
  const triageSystem = firstNonEmpty(
    patientInfo.triage_system,
    lastSession?.triage_system,
    usingSuggestion ? 'NEWS2 (sugerencia demo)' : '',
  )
  const triageScore = firstNonEmpty(patientInfo.triage_score, lastSession?.triage_score)
  const discriminators = firstNonEmpty(
    patientInfo.triage_discriminators,
    lastSession?.triage_discriminators,
    suggestion.reasons.join(', '),
  )

  const antecedents = {
    medical: firstNonEmpty(patientInfo.medical_history, lastSession?.medical_history),
    surgical: firstNonEmpty(patientInfo.surgical_history, lastSession?.surgical_history),
    pharmacological: firstNonEmpty(
      patientInfo.pharmacological_history,
      lastSession?.pharmacological_history,
    ),
    tobacco: firstNonEmpty(patientInfo.tobacco),
    alcohol: firstNonEmpty(patientInfo.alcohol),
    substances: firstNonEmpty(patientInfo.substances),
  }

  const activeSymptoms = currentSymptoms.length > 0 ? currentSymptoms : lastSession?.symptoms ?? []
  const lastDiagnoses = (lastSession?.diagnoses ?? []).slice(0, 4)
  const confirmedDiagnoses = doctorReview?.confirmedDiagnoses ?? []

  const labValues = LAB_ROWS.map(row => {
    const current = patientInfo[row.field as keyof PatientInfo]
    const previous = lastSession?.labs?.[row.key]
    const raw = firstNonEmpty(typeof current === 'string' ? current : undefined, previous)
    const value = toNumber(raw)
    const flag =
      value === undefined
        ? 'empty'
        : value < row.min
          ? 'low'
          : value > row.max
            ? 'high'
            : 'normal'
    return { ...row, raw, value, flag }
  })

  const fcStatus = classify(heartRate, 60, 100, 45, 140)
  const spo2Status = classify(oxygenSaturation, 95, 100, 90, 100)
  const bpStatus = classify(systolic, 90, 130, 80, 180)
  const rrStatus = classify(respiratoryRate, 12, 20, 8, 30)

  const fhirBundle = useMemo(
    () => ({
      resourceType: 'Bundle',
      type: 'collection',
      timestamp: new Date().toISOString(),
      meta: {
        tag: [{ system: 'https://mimetic.health/flags', code: 'SIMULATED-DEMO' }],
      },
      entry: [
        {
          resource: {
            resourceType: 'Patient',
            id: `demo-${documentNumber || 'sin-documento'}`,
            identifier: [{ system: 'MIMETIC/NHC', value: documentNumber || 'N/A' }],
            name: [{ text: name }],
            gender: gender === 'Masculino' ? 'male' : gender === 'Femenino' ? 'female' : 'unknown',
            birthDate: patientInfo.birth_date || undefined,
          },
        },
        {
          resource: {
            resourceType: 'Observation',
            status: 'preliminary',
            code: { text: 'Signos vitales' },
            component: ([
              { code: { text: 'FC' }, valueQuantity: heartRate !== undefined ? { value: heartRate, unit: '/min' } : undefined },
              { code: { text: 'SpO2' }, valueQuantity: oxygenSaturation !== undefined ? { value: oxygenSaturation, unit: '%' } : undefined },
              { code: { text: 'PA' }, valueString: bloodPressureRaw || undefined },
              { code: { text: 'FR' }, valueQuantity: respiratoryRate !== undefined ? { value: respiratoryRate, unit: '/min' } : undefined },
            ] as Array<{
              code: { text: string }
              valueQuantity?: { value: number; unit: string }
              valueString?: string
            }>).filter(component => component.valueQuantity || component.valueString),
          },
        },
        {
          resource: {
            resourceType: 'Condition',
            clinicalStatus: { text: 'active' },
            code: { text: confirmedDiagnoses[0] ?? lastDiagnoses[0]?.disease_name ?? 'Sin diagnóstico confirmado' },
          },
        },
      ],
    }),
    [
      bloodPressureRaw,
      confirmedDiagnoses,
      documentNumber,
      gender,
      heartRate,
      lastDiagnoses,
      name,
      oxygenSaturation,
      patientInfo.birth_date,
      respiratoryRate,
    ],
  )

  const copyText = async (text: string, message: string) => {
    try {
      await navigator.clipboard.writeText(text)
      showToast(message, { icon: 'content_copy' })
    } catch {
      showToast('El navegador bloqueó el portapapeles. Copia manualmente el contenido.', {
        icon: 'warning',
        tone: 'warn',
      })
    }
  }

  const copySynthesis = () => {
    const lines = [
      `Paciente: ${name}`,
      `Documento: ${documentNumber || 'sin documento'}`,
      `Edad: ${age || 'sin dato'} · Género: ${gender}`,
      `Triaje: ${triageMeta.label} (${triageSystem || 'sin sistema'})`,
      `Discriminadores: ${discriminators || 'sin registro'}`,
      `Signos vitales: PA ${bloodPressureRaw || '—'} · FC ${heartRate ?? '—'} lpm · FR ${respiratoryRate ?? '—'} rpm · T ${temperature ?? '—'} °C · SpO₂ ${oxygenSaturation ?? '—'}%`,
      `Síntomas activos: ${activeSymptoms.length > 0 ? activeSymptoms.join(', ') : 'sin registro'}`,
    ]
    void copyText(lines.join('\n'), 'Síntesis clínica copiada al portapapeles.')
  }

  const tabs = [
    { id: 'vitals' as const, label: 'Vitales', icon: 'monitor_heart', count: undefined },
    { id: 'antecedents' as const, label: 'Antecedentes', icon: 'history_edu', count: activeSymptoms.length || undefined },
    { id: 'fhir' as const, label: 'FHIR R4', icon: 'hub', count: undefined },
  ]

  return (
    <div className="flex w-full flex-col gap-4">
      {/* ── Identidad ─────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl border border-surface-border bg-white p-3.5 shadow-sm">
        <div className="absolute left-0 right-0 top-0 h-1.5 bg-gradient-to-r from-clinical-primary via-sky-600 to-sky-400" />
        <div className="flex flex-col gap-3 pt-1 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex min-w-0 items-center gap-3">
            <div className="relative flex-shrink-0">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-sky-200 bg-gradient-to-br from-sky-100 to-sky-200 text-base font-bold text-clinical-primary shadow-inner">
                {initials(name)}
              </div>
              <span
                className={`absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full ring-2 ring-white ${triageMeta.dot}`}
                title={`Prioridad ${triageMeta.short}`}
              />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-1.5">
                <h2 className="truncate font-headline-sm text-[17px] font-bold leading-tight text-text-primary">
                  {name}
                </h2>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700">
                  {age ? `${age} años` : 'Edad sin dato'}
                </span>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-1.5 font-code-telemetry text-[10.5px] text-text-secondary">
                <span className="font-bold text-sky-700">ID: {documentNumber || 'sin documento'}</span>
                <span className="text-slate-300">·</span>
                <span>{gender}</span>
                {patientInfo.birth_date && (
                  <>
                    <span className="text-slate-300">·</span>
                    <span>{patientInfo.birth_date}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex w-full flex-col items-start gap-1 sm:w-auto sm:items-end">
            {hasSevereAllergy ? (
              <>
                <span className="allergy-pulse inline-flex max-w-full items-center gap-1.5 rounded-xl border border-rose-300 bg-rose-50 px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wide text-rose-700">
                  <Icon name="warning" className="text-[15px]" filled />
                  <span className="truncate">Alergia: {allergies}</span>
                </span>
                <span className="text-[9.5px] text-text-muted">Verificar antes de prescribir</span>
              </>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">
                <Icon name="verified_user" className="text-[15px]" />
                {allergies ? `Sin alergia grave · ${allergies}` : 'Alergias sin registrar'}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
            <div className="flex items-center justify-between text-[9.5px] font-semibold uppercase tracking-wider text-text-muted">
              Ubicación
              <span className="rounded bg-white px-1 text-[8px] font-bold text-text-muted">demo</span>
            </div>
            <p className="mt-0.5 flex items-center gap-1 text-[12px] font-bold text-text-primary">
              <Icon name="bed" className="text-[15px] text-sky-600" /> Consultorio 04
            </p>
          </div>
          <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
            <div className="text-[9.5px] font-semibold uppercase tracking-wider text-text-muted">Peso</div>
            <p className="mt-0.5 text-[12px] font-bold text-text-primary">
              {weight !== undefined ? `${weight} kg` : '—'}
            </p>
          </div>
          <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
            <div className="text-[9.5px] font-semibold uppercase tracking-wider text-text-muted">Talla</div>
            <p className="mt-0.5 text-[12px] font-bold text-text-primary">
              {height !== undefined ? `${height} cm` : '—'}
            </p>
          </div>
          <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
            <div className="text-[9.5px] font-semibold uppercase tracking-wider text-text-muted">IMC</div>
            <p className="mt-0.5 text-[12px] font-bold text-text-primary">
              {bmi !== undefined ? bmi.toFixed(1) : '—'}
            </p>
          </div>
        </div>
      </section>

      {/* ── Triaje ────────────────────────────────────────────── */}
      <section
        className={`rounded-2xl border bg-gradient-to-r p-3.5 shadow-sm ${triageMeta.panel}`}
      >
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
              <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-70 ${triageMeta.dot}`} />
              <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${triageMeta.dot}`} />
            </span>
            <h3 className={`font-headline-sm text-xs font-black uppercase tracking-wide ${triageMeta.heading}`}>
              Triaje clínico: {triageMeta.label}
            </h3>
            <span className={`rounded-full border px-2 py-0.5 text-[9.5px] font-bold ${triageMeta.badge}`}>
              {triageSystem || 'Manchester'}
              {triageScore ? ` · ${triageScore}` : ''}
            </span>
          </div>
          <span className="flex items-center gap-1 font-code-telemetry text-[10px] font-semibold text-text-secondary">
            <Icon name="timer" className="text-[13px] text-amber-600" />
            {triageMeta.short}
          </span>
        </div>

        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          <div className="rounded-lg border border-surface-border/80 bg-white/80 p-2">
            <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
              <Icon name="fact_check" className="text-[13px] text-sky-600" />
              Discriminadores
            </span>
            <p className="mt-0.5 text-[11px] leading-snug text-text-secondary">
              {discriminators || 'Sin discriminadores registrados para esta sesión.'}
            </p>
          </div>
          <div className="flex flex-col justify-between rounded-lg border border-surface-border/80 bg-white/80 p-2">
            <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
              <Icon name="analytics" className="text-[13px] text-clinical-primary" />
              Puntuación de gravedad
            </span>
            <div className="mt-0.5 flex flex-wrap items-center gap-1">
              {triageScore ? (
                <span className="rounded border border-sky-200 bg-sky-50 px-1.5 py-0.5 font-code-telemetry text-[10px] font-bold text-clinical-primary">
                  {triageScore}
                </span>
              ) : (
                <span className="text-[11px] text-text-secondary">Sin escala calculada</span>
              )}
              {usingSuggestion && (
                <span className="rounded border border-violet-200 bg-violet-50 px-1.5 py-0.5 text-[9px] font-bold text-violet-700">
                  sugerencia demo
                </span>
              )}
            </div>
            <span className="mt-1 text-[9.5px] leading-tight text-text-muted">
              {usingSuggestion
                ? 'Estimado a partir de los signos vitales; requiere validación de enfermería.'
                : 'Registrado por el equipo de triaje.'}
            </span>
          </div>
        </div>
      </section>

      {/* ── Tabs ──────────────────────────────────────────────── */}
      <section className="overflow-hidden rounded-2xl border border-surface-border bg-white shadow-sm">
        <div className="flex items-stretch border-b border-surface-border px-1.5">
          {tabs.map(item => {
            const active = tab === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                className={`flex flex-1 items-center justify-center gap-1 border-b-2 px-2 py-2.5 text-[11px] font-bold transition-colors ${
                  active
                    ? 'border-clinical-primary text-clinical-primary'
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                <Icon name={item.icon} className={`text-[16px] ${active ? 'text-sky-600' : 'text-slate-400'}`} />
                {item.label}
                {item.count !== undefined && (
                  <span className="rounded-full bg-sky-100 px-1.5 text-[9px] font-bold text-sky-700">
                    {item.count}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        <div className="p-3">
          {tab === 'vitals' && (
            <div className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-2">
                {[
                  {
                    label: 'FC',
                    value: heartRate !== undefined ? String(heartRate) : '—',
                    unit: 'lpm',
                    icon: 'favorite',
                    status: fcStatus,
                    reference: '60–100',
                  },
                  {
                    label: 'SpO₂',
                    value: oxygenSaturation !== undefined ? String(oxygenSaturation) : '—',
                    unit: '%',
                    icon: 'air',
                    status: spo2Status,
                    reference: '≥ 95',
                  },
                  {
                    label: 'PA',
                    value: bloodPressureRaw || '—',
                    unit: 'mmHg',
                    icon: 'blood_pressure',
                    status: bpStatus,
                    reference: '< 130/85',
                  },
                  {
                    label: 'FR',
                    value: respiratoryRate !== undefined ? String(respiratoryRate) : '—',
                    unit: 'rpm',
                    icon: 'respiratory_rate',
                    status: rrStatus,
                    reference: '12–20',
                  },
                ].map(vital => (
                  <div
                    key={vital.label}
                    className={`rounded-xl border p-2.5 ${VITAL_TONE[vital.status]}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider">
                        <Icon name={vital.icon} className="text-[14px]" filled={vital.status !== 'empty'} />
                        {vital.label}
                      </span>
                      <span className="font-code-telemetry text-[8.5px] opacity-70">{vital.reference}</span>
                    </div>
                    <p className="mt-1 flex items-baseline gap-1">
                      <span className="font-headline-sm text-lg font-black leading-none">{vital.value}</span>
                      <span className="text-[9.5px] font-semibold opacity-70">{vital.unit}</span>
                    </p>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between rounded-lg border border-surface-border bg-surface-subtle px-2.5 py-1.5">
                <span className="flex items-center gap-1 text-[10px] font-semibold text-text-secondary">
                  <Icon name="thermostat" className="text-[14px] text-orange-500" />
                  Temperatura
                </span>
                <span className="font-code-telemetry text-[11px] font-bold text-text-primary">
                  {temperature !== undefined ? `${temperature} °C` : '—'}
                </span>
              </div>

              <EcgStrip heartRate={heartRate} />

              {/* Labs */}
              <div className="rounded-xl border border-surface-border bg-white">
                <div className="flex flex-wrap items-center justify-between gap-1.5 border-b border-surface-border px-2.5 py-2">
                  <h4 className="flex items-center gap-1.5 text-[11px] font-bold text-text-primary">
                    <Icon name="science" className="text-[16px] text-violet-600" />
                    Gasometría & laboratorio urgente
                  </h4>
                  <span className="rounded border border-violet-200 bg-violet-50 px-1.5 py-0.5 text-[8.5px] font-bold uppercase text-violet-700">
                    {patientInfo.lab_pao2 || lastSession?.labs?.pao2 ? 'sesión' : 'sin datos'}
                  </span>
                </div>
                <div className="divide-y divide-slate-100 px-2.5 py-1">
                  {labValues.map(lab => (
                    <div key={lab.key} className="flex items-center justify-between gap-2 py-1.5">
                      <span className="text-[10.5px] text-text-secondary">{lab.label}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="font-code-telemetry text-[10.5px] font-bold text-text-primary">
                          {lab.raw || '—'} <span className="font-normal text-text-muted">{lab.unit}</span>
                        </span>
                        {lab.flag !== 'empty' && (
                          <span
                            className={`rounded px-1 py-0.5 text-[8.5px] font-bold ${
                              lab.flag === 'normal'
                                ? 'bg-emerald-50 text-emerald-700'
                                : lab.flag === 'low'
                                  ? 'bg-sky-50 text-sky-700'
                                  : 'bg-rose-50 text-rose-700'
                            }`}
                          >
                            {lab.flag === 'normal' ? 'normal' : lab.flag === 'low' ? 'bajo' : 'alto'}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="border-t border-surface-border px-2.5 py-2 text-[9.5px] leading-snug text-text-muted">
                  Valores referenciales orientativos. La correlación diagnóstica la realiza el motor
                  existente a partir de los síntomas.
                </p>
              </div>
            </div>
          )}

          {tab === 'antecedents' && (
            <div className="flex flex-col gap-3">
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {[
                  { label: 'Antecedentes médicos', value: antecedents.medical, icon: 'medical_information' },
                  { label: 'Antecedentes quirúrgicos', value: antecedents.surgical, icon: 'healing' },
                  { label: 'Medicamentos actuales', value: antecedents.pharmacological, icon: 'medication' },
                  { label: 'Alergias', value: allergies, icon: 'warning' },
                ].map(item => (
                  <div key={item.label} className="rounded-xl border border-surface-border bg-surface-subtle/60 p-2.5">
                    <span className="flex items-center gap-1 text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
                      <Icon name={item.icon} className="text-[13px] text-sky-600" />
                      {item.label}
                    </span>
                    <p className={`mt-0.5 text-[11px] leading-snug ${item.value ? 'text-text-primary' : 'italic text-text-muted'}`}>
                      {item.value || 'Sin registrar en esta sesión'}
                    </p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'Tabaco', value: antecedents.tobacco },
                  { label: 'Alcohol', value: antecedents.alcohol },
                  { label: 'Sustancias', value: antecedents.substances },
                ].map(item => (
                  <div key={item.label} className="rounded-lg border border-surface-border p-2 text-center">
                    <div className="text-[9px] font-bold uppercase tracking-wider text-text-muted">{item.label}</div>
                    <div className={`mt-0.5 text-[10.5px] font-semibold ${item.value ? 'text-text-primary' : 'text-text-muted'}`}>
                      {item.value || '—'}
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-text-secondary">
                    Síntomas activos
                  </span>
                  <span className="font-code-telemetry text-[10px] text-text-muted">{activeSymptoms.length}</span>
                </div>
                {activeSymptoms.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {activeSymptoms.map(symptom => (
                      <span
                        key={symptom}
                        className="rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-[10px] font-semibold text-sky-800"
                      >
                        {symptom}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-[11px] italic text-text-muted">
                    Aún no hay síntomas normalizados en esta consulta.
                  </p>
                )}
              </div>

              {(confirmedDiagnoses.length > 0 || lastDiagnoses.length > 0) && (
                <div>
                  <div className="mb-1.5 text-[10px] font-bold uppercase tracking-wider text-text-secondary">
                    Diagnósticos de referencia
                  </div>
                  <div className="flex flex-col gap-1">
                    {(confirmedDiagnoses.length > 0
                      ? confirmedDiagnoses.map(disease => ({ disease_name: disease, confidence: undefined }))
                      : lastDiagnoses
                    ).map(diagnosis => (
                      <div
                        key={diagnosis.disease_name}
                        className="flex items-center justify-between gap-2 rounded-lg border border-surface-border bg-white px-2 py-1.5"
                      >
                        <span className="text-[10.5px] font-semibold text-text-primary">
                          {diagnosis.disease_name}
                        </span>
                        <span className="text-[9px] font-bold uppercase text-text-muted">
                          {confirmedDiagnoses.length > 0 ? 'confirmado' : 'última consulta'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === 'fhir' && (
            <div className="flex flex-col gap-2">
              <div className="flex flex-wrap items-center justify-between gap-1.5">
                <span className="flex items-center gap-1 text-[10px] font-bold text-text-secondary">
                  <Icon name="hub" className="text-[15px] text-indigo-600" />
                  Bundle FHIR R4 (vista previa)
                </span>
                <span className="rounded border border-indigo-200 bg-indigo-50 px-1.5 py-0.5 text-[8.5px] font-bold uppercase text-indigo-700">
                  simulado · roadmap
                </span>
              </div>
              <pre className="max-h-64 overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-2.5 font-code-telemetry text-[9.5px] leading-relaxed text-emerald-300">
{JSON.stringify(fhirBundle, null, 2)}
              </pre>
              <button
                type="button"
                onClick={() =>
                  void copyText(JSON.stringify(fhirBundle, null, 2), 'Bundle FHIR simulado copiado.')
                }
                className="flex items-center justify-center gap-1.5 rounded-lg border border-surface-border bg-surface-subtle px-2.5 py-1.5 text-[10.5px] font-semibold text-text-secondary transition-colors hover:bg-white hover:text-text-primary"
              >
                <Icon name="content_copy" className="text-[15px]" /> Copiar bundle de demostración
              </button>
            </div>
          )}
        </div>
      </section>

      {/* ── Acciones clínicas ─────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => setBedOpen(true)}
          className="flex items-center justify-center gap-1.5 rounded-xl bg-clinical-primary px-2.5 py-2.5 text-[11px] font-bold text-white shadow-sm transition-all hover:bg-[#072a4a] active:scale-[0.99]"
        >
          <Icon name="meeting_room" className="text-[16px]" />
          Solicitar cama
        </button>
        <button
          type="button"
          onClick={copySynthesis}
          className="flex items-center justify-center gap-1.5 rounded-xl border border-surface-border bg-white px-2.5 py-2.5 text-[11px] font-semibold text-text-secondary shadow-sm transition-colors hover:bg-surface-subtle hover:text-text-primary"
        >
          <Icon name="content_copy" className="text-[16px]" />
          Copiar síntesis
        </button>
      </div>

      <Modal
        open={bedOpen}
        onClose={() => setBedOpen(false)}
        icon="meeting_room"
        title="Solicitud de cama / quirófano"
        subtitle="Protocolo de derivación asistencial prioritaria"
        footer={
          <>
            <button
              type="button"
              onClick={() => setBedOpen(false)}
              className="rounded-xl bg-surface-subtle px-3.5 py-2 text-[11px] font-semibold text-text-secondary transition-colors hover:text-text-primary"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => {
                setBedOpen(false)
                showToast(
                  `Solicitud simulada registrada: ${bedService} · prioridad ${bedPriority}. No se envió a ningún servicio real.`,
                  { icon: 'meeting_room', tone: 'info' },
                )
              }}
              className="rounded-xl bg-clinical-primary px-3.5 py-2 text-[11px] font-bold text-white transition-colors hover:bg-[#072a4a]"
            >
              Confirmar requerimiento
            </button>
          </>
        }
      >
        <div className="rounded-xl border border-surface-border bg-surface-subtle p-2.5">
          <span className="block text-[9.5px] uppercase tracking-wider text-text-muted">Paciente asignado</span>
          <span className="text-[12px] font-bold text-text-primary">{name}</span>
          <span className="block text-[10.5px] text-text-secondary">
            {documentNumber || 'Sin documento'} · {triageMeta.label}
          </span>
        </div>

        <label className="flex flex-col gap-1">
          <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
            Servicio requerido
          </span>
          <select
            value={bedService}
            onChange={event => setBedService(event.target.value)}
            className="rounded-lg border border-surface-border bg-surface-subtle px-2 py-1.5 text-[11px] font-medium text-text-primary focus:outline-none focus:ring-2 focus:ring-sky-200"
          >
            <option>UCI médica · monitorización invasiva</option>
            <option>Unidad de cuidados intermedios (UCIM)</option>
            <option>Pabellón quirúrgico de urgencia</option>
            <option>Hospitalización general</option>
          </select>
        </label>

        <div className="flex flex-col gap-1">
          <span className="text-[9.5px] font-bold uppercase tracking-wider text-text-muted">
            Prioridad de triaje
          </span>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setBedPriority('1')}
              className={`flex items-center justify-between rounded-lg border px-2 py-1.5 text-left text-[10.5px] font-bold transition-colors ${
                bedPriority === '1'
                  ? 'border-rose-300 bg-rose-50 text-rose-700'
                  : 'border-surface-border bg-surface-subtle text-text-secondary'
              }`}
            >
              Prioridad 1 (inmediata)
              <Icon name="priority_high" className="text-[14px]" />
            </button>
            <button
              type="button"
              onClick={() => setBedPriority('2')}
              className={`rounded-lg border px-2 py-1.5 text-left text-[10.5px] font-semibold transition-colors ${
                bedPriority === '2'
                  ? 'border-amber-300 bg-amber-50 text-amber-800'
                  : 'border-surface-border bg-surface-subtle text-text-secondary'
              }`}
            >
              Prioridad 2 (&lt; 2 horas)
            </button>
          </div>
        </div>

        <p className="rounded-lg border border-dashed border-amber-200 bg-amber-50 px-2.5 py-1.5 text-[9.5px] leading-snug text-amber-800">
          Demostración: la asignación de camas y el envío al servicio no están conectados al backend.
        </p>
      </Modal>
    </div>
  )
}
