import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { dataApi } from '@/api/client'
import type { QueryParams, Record, StatsResponse } from '@/types'

export const useData = (datasetId: string, params: QueryParams) => {
  return useQuery({
    queryKey: ['data', datasetId, params],
    queryFn: () => dataApi.getData(datasetId, params).then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useRecord = (datasetId: string, recordId: string) => {
  return useQuery({
    queryKey: ['record', datasetId, recordId],
    queryFn: () => dataApi.getRecord(datasetId, recordId).then(res => res.data),
    enabled: !!recordId,
  })
}

export const useStats = (datasetId: string, excludeSpam: boolean = true) => {
  return useQuery({
    queryKey: ['stats', datasetId, excludeSpam],
    queryFn: () => dataApi.getStats(datasetId, excludeSpam).then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useInfiniteData = (datasetId: string, params: Omit<QueryParams, 'page'>) => {
  return useInfiniteQuery({
    queryKey: ['infiniteData', datasetId, params],
    queryFn: ({ pageParam = 1 }) =>
      dataApi.getData(datasetId, { ...params, page: pageParam }).then(res => res.data),
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1
      }
      return undefined
    },
    initialPageParam: 1,
  })
}