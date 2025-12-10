import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Calendar, 
  User, 
  MapPin, 
  MessageSquare,
  CheckCircle,
  XCircle,
  Flag
} from 'lucide-react'
import { useRecord } from '@/hooks/useData'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

const RecordDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const datasetId = 'community_requests'
  
  const { data: record, isLoading, error } = useRecord(datasetId, id || '')

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <div className="text-red-600 text-lg font-semibold mb-2">
            Запись не найдена
          </div>
          <p className="text-gray-600 mb-4">
            Запись с ID {id} не существует или была удалена
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Вернуться к списку
          </button>
        </div>
      </div>
    )
  }

  const { data } = record

  return (
    <div>
      {/* Back button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Назад к списку
      </button>

      {/* Record card */}
      <div className="card">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {data.тема}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {format(new Date(data.дата), 'dd.MM.yyyy HH:mm', { locale: ru })}
              </span>
              <span className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                {data.от_кого}
              </span>
              {data.адрес && (
                <span className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  {data.адрес}
                </span>
              )}
            </div>
          </div>

          {/* Status badges */}
          <div className="flex space-x-2">
            {record.is_spam ? (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                <Flag className="w-4 h-4 mr-1" />
                Спам
              </span>
            ) : (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <CheckCircle className="w-4 h-4 mr-1" />
                Проверено
              </span>
            )}
            
            {data.ответ ? (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                <CheckCircle className="w-4 h-4 mr-1" />
                Есть ответ
              </span>
            ) : (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                <XCircle className="w-4 h-4 mr-1" />
                Без ответа
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <MessageSquare className="w-5 h-5 mr-2" />
            Текст обращения
          </h3>
          <div className="bg-gray-50 rounded-lg p-6">
            <p className="text-gray-700 whitespace-pre-wrap">
              {data.текст}
            </p>
          </div>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Информация о записи
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">ID записи:</span>
                <span className="font-medium">{record.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Источник:</span>
                <span className="font-medium">{record.source}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Создано:</span>
                <span className="font-medium">
                  {format(new Date(record.created_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Обновлено:</span>
                <span className="font-medium">
                  {format(new Date(record.updated_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Системная информация
            </h3>
            <div className="space-y-3">
              {record.is_spam && record.spam_reason && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Причина спама:</span>
                  <span className="font-medium text-yellow-600">
                    {record.spam_reason}
                  </span>
                </div>
              )}
              {record.is_duplicate && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Дубликат:</span>
                  <span className="font-medium text-orange-600">
                    Да {record.duplicate_of && `(ID: ${record.duplicate_of})`}
                  </span>
                </div>
              )}
              {record.record_hash && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Хеш записи:</span>
                  <span className="font-medium text-sm font-mono">
                    {record.record_hash.substring(0, 16)}...
                  </span>
                </div>
              )}
              {record.source_id && (
                <div className="flex justify-between">
                  <span className="text-gray-600">ID источника:</span>
                  <span className="font-medium">{record.source_id}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-8 pt-6 border-t border-gray-200 flex justify-end space-x-3">
          <button className="btn-secondary">
            Редактировать
          </button>
          <button className="btn-primary">
            Добавить ответ
          </button>
        </div>
      </div>
    </div>
  )
}

export default RecordDetail