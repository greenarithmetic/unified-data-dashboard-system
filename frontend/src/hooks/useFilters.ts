import { useState, useCallback } from 'react'
import type { QueryParams } from '@/types'

const DEFAULT_PARAMS: QueryParams = {
  page: 1,
  per_page: 50,
  sort_by: 'дата',
  sort_dir: 'desc',
  q: '',
  exclude_spam: true,
}

export const useFilters = (initialParams: Partial<QueryParams> = {}) => {
  const [params, setParams] = useState<QueryParams>({
    ...DEFAULT_PARAMS,
    ...initialParams,
  })

  const updateParam = useCallback(<K extends keyof QueryParams>(
    key: K,
    value: QueryParams[K]
  ) => {
    setParams(prev => ({
      ...prev,
      [key]: value,
      ...(key !== 'page' ? { page: 1 } : {}), // Reset to page 1 when filters change
    }))
  }, [])

  const updateMultiple = useCallback((updates: Partial<QueryParams>) => {
    setParams(prev => ({
      ...prev,
      ...updates,
      ...(Object.keys(updates).some(k => k !== 'page') ? { page: 1 } : {}),
    }))
  }, [])

  const reset = useCallback(() => {
    setParams(DEFAULT_PARAMS)
  }, [])

  return {
    params,
    updateParam,
    updateMultiple,
    reset,
  }
}