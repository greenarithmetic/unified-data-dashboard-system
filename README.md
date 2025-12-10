# Unified Data Dashboard System (UDDS)

Полнофункциональная система дашбордов для анализа данных из Google Sheets с поддержкой универсальной загрузки таблиц, дедупликации, спам-фильтрации, быстрого поиска/фильтрации/сортировки, кастомизируемых отчетов и production-ready Docker Compose.

## 🎯 Основные возможности

### Backend (FastAPI)
- **Google Sheets синхронизация** - автоматическая загрузка данных каждый час
- **Дедупликация** - 3 стратегии: по source_id, по хешу, bloom-фильтр
- **Спам-фильтр** - трехуровневая система: keywords + regex + ML-ready
- **REST API** - полный API для работы с данными
- **Webhook** - интеграция с внешними системами
- **PostgreSQL + Redis** - оптимальное хранение и кеширование

### Frontend (React)
- **Умная таблица** - lazy loading, backend pagination
- **Поиск** - full-text поиск по всем полям
- **Фильтрация и сортировка** - гибкая настройка фильтров
- **Адаптивный дизайн** - работает на всех устройствах
- **Детальный просмотр** - полная информация о записи

### DevOps
- **Docker Compose** - 7 сервисов: backend, frontend, PostgreSQL, Redis, Nginx, Superset
- **Nginx reverse proxy** - production-ready конфигурация
- **Apache Superset** - продвинутая аналитика и отчеты
- **Health checks** - мониторинг состояния всех сервисов

### Конфигурация
- **Zero-code** - настройка через JSON файлы
- **datasets.json** - конфигурация источников данных
- **reports.json** - готовые отчеты и визуализации
- **.env** - все переменные окружения

## 🚀 Быстрый старт

### 1. Клонирование и настройка
```bash
# Клонировать проект
git clone <repository-url>
cd unified-data-dashboard

# Создать .env файл из примера
cp .env.example .env

# Отредактировать .env файл
nano .env
```

### 2. Настройка Google Sheets API
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API
4. Создайте сервисный аккаунт и скачайте credentials.json
5. Добавьте сервисный аккаунт как редактора в ваши Google Sheets

### 3. Запуск проекта
```bash
# Запустить все сервисы
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановить все сервисы
docker-compose down
```

### 4. Доступ к приложениям
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **API документация**: http://localhost:8000/docs
- **Superset**: http://localhost:8088
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 Структура проекта

```
unified-data-dashboard/
├── backend/                    # FastAPI приложение
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── services/          # Бизнес-логика
│   │   ├── schemas/           # Pydantic схемы
│   │   └── database.py        # Модели SQLAlchemy
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # React приложение
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/            # Страницы приложения
│   │   ├── api/              # API клиент
│   │   └── hooks/            # React хуки
│   ├── Dockerfile
│   └── package.json
├── configs/                   # Конфигурационные файлы
│   ├── datasets.json         # Конфигурация источников данных
│   ├── reports.json         # Конфигурация отчетов
│   └── .env.example         # Пример переменных окружения
├── docker-compose.yml        # Docker Compose конфигурация
├── nginx.conf               # Nginx конфигурация
├── init-db.sql              # SQL инициализация
└── README.md                # Эта документация
```

## ⚙️ Конфигурация

### datasets.json
Конфигурация источников данных:
```json
{
  "datasets": [
    {
      "id": "community_requests",
      "name": "Обращения граждан",
      "source": "google_sheets",
      "sheet_id": "your-sheet-id",
      "sync_interval_minutes": 60,
      "schema": {
        "тема": {"type": "text", "required": true},
        "дата": {"type": "datetime", "required": true}
      },
      "deduplication": {
        "enabled": true,
        "strategy": "source_id_or_hash"
      }
    }
  ]
}
```

### reports.json
Конфигурация отчетов:
```json
{
  "reports": [
    {
      "id": "requests_by_theme",
      "title": "Обращения по темам",
      "type": "bar_chart",
      "group_by": "тема",
      "aggregate": {"type": "count"}
    }
  ]
}
```

## 🔧 API Endpoints

### Данные
- `GET /api/v1/data/{dataset_id}` - Получить данные с пагинацией
- `GET /api/v1/data/{dataset_id}/{record_id}` - Получить конкретную запись
- `GET /api/v1/data/{dataset_id}/stats` - Статистика по датасету

### Ингейст
- `POST /api/v1/ingest/{dataset_id}` - Загрузить данные
- `POST /api/v1/ingest/{dataset_id}/sync` - Принудительная синхронизация

### Здоровье
- `GET /api/v1/health` - Проверка здоровья системы
- `GET /api/v1/health/detailed` - Детальная проверка

## 📊 Пример использования

### Сценарий: Анализ обращений граждан
1. **Настройка источника**: Добавьте Google Sheet с обращениями в datasets.json
2. **Синхронизация**: Система автоматически загрузит данные каждый час
3. **Дедупликация**: Дубликаты будут автоматически обнаружены и помечены
4. **Спам-фильтрация**: Нежелательные записи будут отфильтрованы
5. **Анализ**: Используйте готовые отчеты или создайте свои
6. **Экспорт**: Экспортируйте данные через API или Superset

## 🐛 Отладка

### Просмотр логов
```bash
# Все логи
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Проверка здоровья
```bash
# Проверить все сервисы
docker-compose ps

# Проверить API
curl http://localhost:8000/api/v1/health

# Проверить базу данных
docker-compose exec postgres pg_isready -U udds -d udds
```

### Миграции базы данных
```bash
# Запустить миграции
docker-compose run --rm alembic alembic upgrade head

# Создать новую миграцию
docker-compose run --rm alembic alembic revision --autogenerate -m "Описание изменений"
```

## 🔒 Безопасность

### Рекомендации для production
1. **Измените все пароли** в .env файле
2. **Настройте SSL/TLS** для Nginx
3. **Ограничьте доступ** к API с помощью firewall
4. **Настройте мониторинг** и алерты
5. **Регулярно обновляйте** зависимости

### Переменные окружения для безопасности
```bash
# Обязательные для production
DB_PASSWORD=strong_random_password_here
SUPERSET_SECRET_KEY=another_strong_random_key
WEBHOOK_SECRET=webhook_validation_secret

# Опциональные
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-domain.com"]
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл LICENSE для деталей.

## 📞 Поддержка

- **Issues**: [Создать issue](https://github.com/your-username/unified-data-dashboard/issues)
- **Документация**: [Документация проекта](https://github.com/your-username/unified-data-dashboard/wiki)
- **Email**: support@example.com

---

**Примечание**: Это production-ready система, готовая к развертыванию. Все компоненты настроены для работы в контейнерах, с health checks, мониторингом и отказоустойчивостью.