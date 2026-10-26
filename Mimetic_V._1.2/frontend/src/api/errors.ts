const STATUS_MESSAGES: Record<number, string> = {
  400: 'Los datos enviados no son válidos. Verifica e intenta de nuevo.',
  401: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
  403: 'No tienes permisos para realizar esta acción.',
  404: 'No se encontró el recurso solicitado.',
  409: 'Ya existe un registro con esos datos.',
  422: 'Los datos enviados no son válidos.',
  429: 'Demasiadas solicitudes. Espera un momento e intenta de nuevo.',
  500: 'Ocurrió un error inesperado. Intenta de nuevo más tarde.',
  503: 'El servicio no está disponible temporalmente.',
}

const DEFAULT_ERROR = 'Ocurrió un error inesperado.'

export async function extractError(res: Response, fallback?: string): Promise<string> {
  try {
    const data = await res.json()
    return data.detail || fallback || STATUS_MESSAGES[res.status] || DEFAULT_ERROR
  } catch {
    return fallback || STATUS_MESSAGES[res.status] || 'Error de conexión con el servidor.'
  }
}