import React from 'react'
import { BarChart3, PieChart, LineChart, TrendingUp } from 'lucide-react'

const ReportViewer: React.FC = () => {
  const reports = [
    {
      id: 'requests_by_theme',
      title: 'Обращения по темам',
      description: 'Количество обращений по каждой теме',
      type: 'bar',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'blue',
    },
    {
      id: 'requests_by_location',
      title: 'Обращения по районам',
      description: 'Распределение обращений по адресам',
      type: 'bar',
      icon: <PieChart className="w-6 h-6" />,
      color: 'green',
    },
    {
      id: 'response_rate',
      title: 'Процент ответов',
      description: 'Какой процент обращений получили ответ',
      type: 'gauge',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'purple',
    },
    {
      id: 'requests_timeline',
      title: 'Обращения во времени',
      description: 'Динамика обращений по дням',
      type: 'line',
      icon: <LineChart className="w-6 h-6" />,
      color: 'yellow',
    },
  ]

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Отчеты и аналитика
        </h1>
        <p className="text-gray-600">
          Готовые отчеты и визуализация данных
        </p>
      </div>

      {/* Reports grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report) => (
          <div
            key={report.id}
            className={`card border-2 ${colorClasses[report.color as keyof typeof colorClasses]} hover:shadow-md transition-shadow cursor-pointer`}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {report.title}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {report.description}
                </p>
              </div>
              <div className={`p-2 rounded-lg ${colorClasses[report.color as keyof typeof colorClasses].split(' ')[0]}`}>
                {report.icon}
              </div>
            </div>

            {/* Chart placeholder */}
            <div className="h-48 bg-gray-50 rounded-lg flex items-center justify-center mb-4">
              <div className="text-center">
                <div className="text-gray-400 mb-2">
                  {report.type === 'bar' && <BarChart3 className="w-12 h-12 mx-auto" />}
                  {report.type === 'pie' && <PieChart className="w-12 h-12 mx-auto" />}
                  {report.type === 'line' && <LineChart className="w-12 h-12 mx-auto" />}
                  {report.type === 'gauge' && <TrendingUp className="w-12 h-12 mx-auto" />}
                </div>
                <p className="text-sm text-gray-500">
                  График {report.type === 'bar' ? 'столбчатый' : 
                         report.type === 'line' ? 'линейный' : 
                         report.type === 'pie' ? 'круговой' : 'индикатор'}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">
                Обновлено сегодня
              </span>
              <button className="btn-primary text-sm px-4 py-2">
                Открыть отчет
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Report builder */}
      <div className="mt-8 card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Конструктор отчетов
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Создайте собственный отчет с нужными параметрами
            </p>
          </div>
          <button className="btn-primary">
            Создать отчет
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Тип отчета
            </label>
            <select className="input-field">
              <option>Столбчатая диаграмма</option>
              <option>Линейный график</option>
              <option>Круговая диаграмма</option>
              <option>Таблица</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Группировка
            </label>
            <select className="input-field">
              <option>По теме</option>
              <option>По автору</option>
              <option>По адресу</option>
              <option>По дате</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Период
            </label>
            <select className="input-field">
              <option>Последние 7 дней</option>
              <option>Последние 30 дней</option>
              <option>Последние 90 дней</option>
              <option>Все время</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportViewer