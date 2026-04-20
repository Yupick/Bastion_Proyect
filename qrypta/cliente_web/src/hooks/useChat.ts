import { useQuery } from '@tanstack/react-query'
import { readCachedMessages } from '../services/indexedDbService'

export function useChat() {
  const cached = useQuery({
    queryKey: ['chat-cache'],
    queryFn: readCachedMessages,
    staleTime: 1000 * 60,
  })

  return {
    cached,
  }
}
