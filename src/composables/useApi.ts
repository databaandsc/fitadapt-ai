import { useAuth } from '@clerk/vue'

export function useApi() {
  const { getToken } = useAuth()

  const fetchWithAuth = async (input: RequestInfo | URL, init: RequestInit = {}) => {
    const token = await getToken.value?.()
    const headers = new Headers(init.headers || {})
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    if (!headers.has('Content-Type') && init.body) {
      headers.set('Content-Type', 'application/json')
    }
    return fetch(input, { ...init, headers })
  }

  return { fetchWithAuth }
}
