import { createRef } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import SearchPhase from './SearchPhase'
import type { SearchResult } from './types'

const result: SearchResult = {
  document_number: '12345678',
  first_name: 'Ana',
  last_name: 'Gómez',
  document_type: 'CC',
  source: 'test',
  has_clinical_history: false,
  has_user_account: true,
  base_data: {},
}

function setup(overrides: Partial<Parameters<typeof SearchPhase>[0]> = {}) {
  const onSearchChange = vi.fn()
  const onSelect = vi.fn()
  const onNewPatient = vi.fn()
  const onLogout = vi.fn()
  const onFocusResults = vi.fn()
  const onBlurResults = vi.fn()
  const user = { name: 'Dr. Marino' }

  render(
    <SearchPhase
      user={user}
      onLogout={onLogout}
      onHistory={vi.fn()}
      onResume={vi.fn()}
      searchRef={createRef<HTMLInputElement>()}
      searchQuery=""
      searching={false}
      showSearchResults={false}
      searchResults={[]}
      onSearchChange={onSearchChange}
      onFocusResults={onFocusResults}
      onBlurResults={onBlurResults}
      onSelect={onSelect}
      onNewPatient={onNewPatient}
      {...overrides}
    />,
  )

  return { onSearchChange, onSelect, onNewPatient, onLogout }
}

describe('SearchPhase', () => {
  it('permite buscar un documento y propaga el cambio', () => {
    const { onSearchChange } = setup()

    fireEvent.change(screen.getByPlaceholderText(/ingrese el documento/i), {
      target: { value: '12345' },
    })

    expect(onSearchChange).toHaveBeenCalledWith('12345')
  })

  it('muestra resultados y selecciona el paciente', () => {
    const { onSelect } = setup({
      showSearchResults: true,
      searchResults: [result],
    })

    fireEvent.mouseDown(screen.getByText(/ana gómez/i))

    expect(onSelect).toHaveBeenCalledWith(result)
  })

  it('muestra aviso cuando no hay coincidencias', () => {
    setup({
      showSearchResults: true,
      searchQuery: '99',
      searchResults: [],
    })

    expect(screen.getByText(/no se encontraron pacientes/i)).toBeInTheDocument()
  })

  it('ofrece registrar un paciente nuevo', () => {
    const { onNewPatient } = setup()

    fireEvent.click(screen.getByRole('button', { name: /registrar nuevo paciente/i }))

    expect(onNewPatient).toHaveBeenCalled()
  })
})