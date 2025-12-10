import React from 'react'
import { Search, Filter, X } from 'lucide-react'
import type { QueryParams } from '@/types'

interface FilterPanelProps {
  params: QueryParams
  onSearchChange: (value: string) => void
  onSortChange: (field: string) => void
  onSortDirChange: (dir: 'asc' | 'desc') => void
  onExcludeSpamChange: (value: boolean) => void
  onReset: () => void
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  params,
  onSearchChange,
  onSortChange,
  onSortDirChange,
  onExcludeSpamChange,
  onReset,
}) => {
  const sortFields = [
    { value: 'дата', label: 'Дата' },
    { value: 'тема', label: 'Тема' },
    { value: 'от_кого', label: 'Автор' },
  ]

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Filter className="w-5 h-5 mr-2" />
          Фильтры и поиск
        </h3>
        <button
          onClick={onReset}
          className="text-sm text-gray-600 hover:text-gray-900 flex items-center"
        >
          <X className="w-4 h-4 mr-1" />
          Сбросить
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Поиск
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={params.q || ''}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Поиск по тексту..."
              className="input-field pl-10"
            />
          </div>
        </div>

        {/* Sort field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Сортировка по
          </label>
          <select
            value={params.sort_by || 'дата'}
            onChange={(e) => onSortChange(e.target.value)}
            className="input-field"
          >
            {sortFields.map((field) => (
              <option key={field.value} value={field.value}>
                {field.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sort direction */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Направление
          </label>
          <select
            value={params.sort_dir}
            onChange={(e) => onSortDirChange(e.target.value as 'asc' | 'desc')}
            className="input-field"
          >
            <option value="desc">По убыванию</option>
            <option value="asc">По возрастанию</option>
          </select>
        </div>

        {/* Spam filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Фильтр спама
          </label>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="exclude-spam"
              checked={params.exclude_spam}
              onChange={(e) => onExcludeSpamChange(e.target.checked)}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="exclude-spam" className="ml-2 text-sm text-gray-700">
              Скрыть спам
            </label>
          </div>
        </div>
      </div>

      {/* Active filters */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex flex-wrap gap-2">
          {params.q && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Поиск: {params.q}
              <button
                onClick={() => onSearchChange('')}
                className="ml-1 text-blue-600 hover:text-blue-800"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Сортировка: {sortFields.find(f => f.value === params.sort_by)?.label} ({params.sort_dir === 'desc' ? '↓' : '↑'})
          </span>
          {params.exclude_spam && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Спам скрыт
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default FilterPanel