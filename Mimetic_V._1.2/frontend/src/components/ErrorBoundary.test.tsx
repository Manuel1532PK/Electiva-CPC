import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import type { ReactNode } from 'react'
import ErrorBoundary from './ErrorBoundary'

function Bomb(): ReactNode {
  throw new Error('fallo en el render')
}

describe('ErrorBoundary', () => {
  it('renderiza el fallback cuando un hijo lanza error', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Algo salió mal')).toBeInTheDocument()
    expect(screen.getByText('fallo en el render')).toBeInTheDocument()
    spy.mockRestore()
  })

  it('muestra a los hijos cuando no hay error', () => {
    render(
      <ErrorBoundary>
        <p>contenido sano</p>
      </ErrorBoundary>,
    )

    expect(screen.getByText('contenido sano')).toBeInTheDocument()
  })
})