const apiFromEnv = import.meta.env.VITE_API_URL as string | undefined

const apiUrl = apiFromEnv && apiFromEnv.trim() !== ''
  ? apiFromEnv
  : import.meta.env.DEV
    ? ''
    : 'https://mimetic-ai-api.onrender.com'

export const API = apiUrl
