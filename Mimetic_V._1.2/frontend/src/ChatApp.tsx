import { useChatApp } from './chat/useChatApp'
import HistoryPhase from './chat/HistoryPhase'
import SearchPhase from './chat/SearchPhase'
import PatientInfoPhase from './chat/PatientInfoPhase'
import ReportPhase from './chat/ReportPhase'
import SymptomsPhase from './chat/SymptomsPhase'
import { ToastProvider } from './chat/ui'
import './styles/mimetic.css'

export default function ChatApp() {
  const app = useChatApp()

  if (app.phase === 'history') {
    return (
      <ToastProvider>
        <HistoryPhase
          user={app.user}
          onLogout={app.logout}
          onHome={app.resetAll}
          onNewPatient={app.startNewPatient}
          onResume={app.resumeConsultation}
          onStartConsultation={app.startConsultationFromHistory}
        />
      </ToastProvider>
    )
  }

  if (app.phase === 'search') {
    return (
      <ToastProvider>
        <SearchPhase
          user={app.user}
          onLogout={app.logout}
          onHistory={app.openHistory}
          onResume={app.resumeConsultation}
          searchRef={app.searchRef}
          searchQuery={app.searchQuery}
          searching={app.searching}
          showSearchResults={app.showSearchResults}
          searchResults={app.searchResults}
          onSearchChange={app.handleSearchChange}
          onFocusResults={() => app.searchResults.length > 0 && app.setShowSearchResults(true)}
          onBlurResults={() => setTimeout(() => app.setShowSearchResults(false), 200)}
          onSelect={app.selectPatient}
          onNewPatient={app.startNewPatient}
        />
      </ToastProvider>
    )
  }

  if (app.phase === 'patient_info') {
    return (
      <ToastProvider>
        <PatientInfoPhase
          user={app.user}
          onLogout={app.logout}
          onHome={app.resetAll}
          onNewPatient={app.startNewPatient}
          onHistory={app.openHistory}
          onResume={app.resumeConsultation}
          patientInfoMode={app.patientInfoMode}
          patientInfo={app.patientInfo}
          lastSession={app.lastSession}
          formStep={app.formStep}
          setFormStep={app.setFormStep}
          fieldGroups={app.fieldGroups}
          allFieldKeys={app.allFieldKeys}
          sessionFieldKeys={app.sessionFieldKeys}
          sectionRefs={app.sectionRefs}
          messages={app.messages}
          endRef={app.endRef}
          isSending={app.isSending}
          onFieldChange={app.handlePatientFieldChange}
          onSubmit={app.submitPatientForm}
        />
      </ToastProvider>
    )
  }

  if (app.phase === 'report' && app.reportHtml) {
    return (
      <ToastProvider>
        <ReportPhase
          user={app.user}
          onLogout={app.logout}
          patientInfo={app.patientInfo}
          doctorReview={app.doctorReview}
          reportHtml={app.reportHtml}
          onBack={app.backToSymptoms}
          onReset={app.resetAll}
          onNewPatient={app.startNewPatient}
          onHistory={app.openHistory}
          onResume={app.resumeConsultation}
        />
      </ToastProvider>
    )
  }

  return (
    <ToastProvider>
      <SymptomsPhase
        user={app.user}
        onLogout={app.logout}
        onHome={app.resetAll}
        onNewPatient={app.startNewPatient}
        onHistory={app.openHistory}
        onResume={app.resumeConsultation}
        patientInfo={app.patientInfo}
        lastSession={app.lastSession}
        messages={app.messages}
        input={app.input}
        setInput={app.setInput}
        isSending={app.isSending}
        isGeneratingReport={app.isGeneratingReport}
        currentSymptoms={app.currentSymptoms}
        excludedSymptoms={app.excludedSymptoms}
        suggestedSymptoms={app.suggestedSymptoms}
        selectedDiagnosis={app.selectedDiagnosis}
        doctorReview={app.doctorReview}
        endRef={app.endRef}
        onSend={app.handleSend}
        onSuggestion={app.handleSuggestion}
        onSelectDiagnosis={app.handleSelectDiagnosis}
        onGenerateReport={app.generateReport}
        onToggleDiagnosisConfirmation={app.toggleDiagnosisConfirmation}
        onToggleDiagnosisRejection={app.toggleDiagnosisRejection}
        onAddManualDiagnosis={app.addManualDiagnosis}
        onRemoveManualDiagnosis={app.removeManualDiagnosis}
        onToggleMedicine={app.toggleMedicineSelection}
        onUpdateDose={app.updateMedicineDose}
        onSetDoctorNotes={app.setDoctorNotes}
        confidenceColor={app.confidenceColor}
        severityColor={app.severityColor}
      />
    </ToastProvider>
  )
}
