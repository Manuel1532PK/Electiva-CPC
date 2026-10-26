import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { error: Error | null }

const fallbackStyle: React.CSSProperties = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 24,
  fontFamily: 'system-ui, sans-serif',
}

const cardStyle: React.CSSProperties = {
  maxWidth: 480,
  padding: 24,
  border: '1px solid #e2e2e2',
  borderRadius: 12,
  background: '#fff',
  boxShadow: '0 4px 16px rgba(0,0,0,.08)',
  textAlign: 'center',
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('ErrorBoundary capturó un error:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div style={fallbackStyle}>
          <div style={cardStyle}>
            <h2 style={{ marginTop: 0 }}>Algo salió mal</h2>
            <p style={{ color: '#555' }}>{this.state.error.message}</p>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: 12,
                padding: '10px 18px',
                border: 'none',
                borderRadius: 8,
                background: '#0b6bcb',
                color: '#fff',
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              Recargar la página
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary