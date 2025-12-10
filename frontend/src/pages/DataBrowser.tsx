import React from 'react'
import { useData, useStats } from '@/hooks/useData'
import { useFilters } from '@/hooks/useFilters'
import DataTable from '@/components/DataTable'
import FilterPanel from '@/components/FilterPanel'
import StatsCard from '@/components/StatsCard'
import { BarChart3, Users, MapPin, CheckCircle } from 'lucide-react'

const DataBrowser: React.FC = () => {
  const datasetId = 'community_requests'
  
  const { params, updateParam, updateMultiple, reset } = useFilters()
  const { data, isLoading, error } = useData(datasetId, params)
  const { data: stats } = useStats(datasetId, params.exclude_spam)

  const handleSearchChange = (value: string) => {
    updateParam('q', value)
  }

  const handleSortChange = (field: string) => {
    updateParam('sort_by', field)
  }

  const handleSortDirChange = (dir: 'asc' | 'desc') => {
    updateParam('sort_dir', dir)
  }

  const handleExcludeSpamChange = (value: boolean) => {
    updateParam('exclude_spam', value)
  }

  const handlePageChange = (page: number) => {
    updateParam('page', page)
  }

  const handlePerPageChange = (perPage: number) => {
    updateParam('per_page', perPage)
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <div className="text-red-600 text-lg font-semibold mb-2">
            Ошибка загрузки данных
          </div>
          <p className="text-gray-600">
            {error instanceof Error ? error.message : 'Неизвестная ошибка'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Обращения граждан
        </h1>
        <p className="text-gray-600">
          Анализ обращений из чатов и социальных сетей
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Всего записей"
          value={stats?.total_records || 0}
          icon={<BarChart3 className="w-6 h-6" />}
          color="blue"
        />
        <StatsCard
          title="Спам"
          value={stats?.total_spam || 0}
          icon={<Users className="w-6 h-6" />}
          color="yellow"
        />
        <StatsCard
          title="Уникальные авторы"
          value={Object.keys(stats?.by_theme || {}).length || 0}
          icon={<MapPin className="w-6 h-6" />}
          color="green"
        />
        <StatsCard
          title="Процент ответов"
          value={`${stats?.response_rate ? (stats.response_rate * 100).toFixed(1) : '0'}%`}
          icon={<CheckCircle className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Filters */}
      <FilterPanel
        params={params}
        onSearchChange={handleSearchChange}
        onSortChange={handleSortChange}
        onSortDirChange={handleSortDirChange}
        onExcludeSpamChange={handleExcludeSpamChange}
        onReset={reset}
      />

      {/* Data table */}
      <DataTable
        data={data?.data || []}
        total={data?.total || 0}
        page={params.page}
        perPage={params.per_page}
        totalPages={data?.total_pages || 1}
        onPageChange={handlePageChange}
        onPerPageChange={handlePerPageChange}
        isLoading={isLoading}
      />

      {/* Additional info */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top themes */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Популярные темы
          </h3>
          <div className="space-y-3">
            {stats?.by_theme ? (
              Object.entries(stats.by_theme)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([theme, count]) => (
                  <div key={theme} className="flex items-center justify-between">
                    <span className="text-gray-700">{theme}</span>
                    <span className="font-medium text-gray-900">{count}</span>
                  </div>
                ))
            ) : (
              <p className="text-gray-500 text-center py-4">Нет данных</p>
            )}
          </div>
        </div>

        {/* Top locations */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Популярные адреса
          </h3>
          <div className="space-y-3">
            {stats?.by_location ? (
              Object.entries(stats.by_location)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([location, count]) => (
                  <div key={location} className="flex items-center justify-between">
                    <span className="text-gray-700">{location}</span>
                    <span className="font-medium text-gray-900">{count}</span>
                  </div>
                ))
            ) : (
              <p className="text-gray-500 text-center py-4">Нет данных</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DataBrowser