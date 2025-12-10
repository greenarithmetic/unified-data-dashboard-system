export interface Record {
  id: string
  dataset_id: string
  source: string
  source_id?: string
  record_hash?: string
  data: {
    тема: string
    дата: string
    от_кого: string
    текст: string
    адрес?: string
    ответ?: boolean
    is_spam?: boolean
    spam_reason?: string
  }
  is_spam: boolean
  spam_reason?: string
  is_duplicate: boolean
  duplicate_of?: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse {
  success: boolean
  total: number
  total_spam: number
  page: number
  per_page: number
  total_pages: number
  data: Record[]
}

export interface StatsResponse {
  total_records: number
  total_spam: number
  by_theme?: Record<string, number>
  by_location?: Record<string, number>
  response_rate?: number
  last_sync?: string
}

export interface QueryParams {
  page: number
  per_page: number
  sort_by?: string
  sort_dir: 'asc' | 'desc'
  q?: string
  exclude_spam: boolean
}

export interface Report {
  id: string
  name: string
  description?: string
  dataset_id: string
  config: any
  is_active: boolean
  created_at: string
  updated_at: string
}