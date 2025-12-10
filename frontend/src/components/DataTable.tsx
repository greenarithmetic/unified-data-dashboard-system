import React from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  flexRender,
  ColumnDef,
} from '@tanstack/react-table'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import type { Record } from '@/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface DataTableProps {
  data: Record[]
  total: number
  page: number
  perPage: number
  totalPages: number
  onPageChange: (page: number) => void
  onPerPageChange: (perPage: number) => void
  isLoading?: boolean
}

const DataTable: React.FC<DataTableProps> = ({
  data,
  total,
  page,
  perPage,
  totalPages,
  onPageChange,
  onPerPageChange,
  isLoading = false,
}) => {
  const columns: ColumnDef<Record>[] = [
    {
      accessorKey: 'data.тема',
      header: 'Тема',
      cell: ({ row }) => (
        <div className="font-medium text-gray-900">
          {row.original.data.тема}
        </div>
      ),
    },
    {
      accessorKey: 'data.от_кого',
      header: 'Автор',
      cell: ({ row }) => (
        <div className="text-gray-700">
          {row.original.data.от_кого}
        </div>
      ),
    },
    {
      accessorKey: 'data.дата',
      header: 'Дата',
      cell: ({ row }) => {
        const date = new Date(row.original.data.дата)
        return (
          <div className="text-gray-600">
            {format(date, 'dd.MM.yyyy HH:mm', { locale: ru })}
          </div>
        )
      },
    },
    {
      accessorKey: 'data.текст',
      header: 'Текст',
      cell: ({ row }) => {
        const text = row.original.data.текст
        const truncated = text.length > 100 ? text.substring(0, 100) + '...' : text
        return (
          <div className="text-gray-700">
            {truncated}
          </div>
        )
      },
    },
    {
      accessorKey: 'data.адрес',
      header: 'Адрес',
      cell: ({ row }) => (
        <div className="text-gray-600">
          {row.original.data.адрес || '-'}
        </div>
      ),
    },
    {
      accessorKey: 'data.ответ',
      header: 'Ответ',
      cell: ({ row }) => (
        <div className="flex items-center">
          {row.original.data.ответ ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Да
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Нет
            </span>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'is_spam',
      header: 'Статус',
      cell: ({ row }) => (
        <div className="flex items-center">
          {row.original.is_spam ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Спам
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              ОК
            </span>
          )}
        </div>
      ),
    },
  ]

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    manualPagination: true,
    rowCount: total,
    state: {
      pagination: {
        pageIndex: page - 1,
        pageSize: perPage,
      },
    },
  })

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded mb-2"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr 
                key={row.id} 
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => {
                  // Navigate to record detail
                  console.log('Navigate to record:', row.original.id)
                }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-6 py-4 whitespace-nowrap text-sm"
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-700">
              Показано{' '}
              <span className="font-medium">
                {data.length > 0 ? (page - 1) * perPage + 1 : 0}
              </span>{' '}
              -{' '}
              <span className="font-medium">
                {Math.min(page * perPage, total)}
              </span>{' '}
              из <span className="font-medium">{total}</span> записей
            </span>
            
            <select
              value={perPage}
              onChange={(e) => onPerPageChange(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {[10, 25, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size} на странице
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => onPageChange(1)}
              disabled={page === 1}
              className="p-1 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <ChevronsLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page === 1}
              className="p-1 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <span className="px-3 py-1 text-sm text-gray-700">
              Страница <span className="font-medium">{page}</span> из{' '}
              <span className="font-medium">{totalPages}</span>
            </span>
            
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="p-1 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => onPageChange(totalPages)}
              disabled={page >= totalPages}
              className="p-1 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              <ChevronsRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DataTable