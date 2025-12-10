# 🚀 Unified Data Dashboard System (UDDS) - Production Ready

## 📋 О проекте

**Unified Data Dashboard System (UDDS)** - это enterprise-решение для анализа данных из Google Sheets с полным production-ready стеком. Система прошла полный цикл тестирования и готова к развертыванию в production.

**Реальный сценарий**: Сбор и анализ обращений граждан из чатов/Telegram для муниципальных служб с поддержкой дедупликации, спам-фильтрации и продвинутой аналитики.

## 🏆 Ключевые достижения

### ✅ Полностью проверенный рабочий цикл
- **Архитектура**: 7 взаимосвязанных сервисов, протестировано взаимодействие
- **Интеграция**: Реальная работа с Google Sheets API (2 таблицы настроены)
- **Обработка данных**: 3 стратегии дедупликации + 3 уровня спам-фильтрации
- **Производительность**: Backend pagination, Redis кеширование, lazy loading
- **Аналитика**: Встроенные отчеты + Apache Superset для BI

### 🛡️ Production Ready
- **Security**: Полная SSL/TLS конфигурация, firewall, secrets management
- **Monitoring**: Health checks, Prometheus + Grafana, centralized logging (Loki)
- **Backup**: Автоматические бэкапы и recovery scripts
- **CI/CD**: GitHub Actions pipeline для автоматического деплоя
- **Scaling**: Поддержка горизонтального и вертикального масштабирования

## 🚀 Быстрый старт

### 1. Клонирование проекта
```bash
git clone <repository-url>
cd unified-data-dashboard
```

### 2. Development настройка (для тестирования)
```bash
# Базовый .env файл
cp .env.example .env

# Запуск всех сервисов
./start.sh
```

### 3. Production настройка (рекомендуется)
```bash
# Создание production конфигурации
cp .env.example .env.production

# Генерация безопасных значений
./scripts/generate-secrets.sh

# Запуск в production режиме
docker-compose -f docker-compose.production.yml up -d
```

## 📊 Основные возможности

### 🔄 Интеллектуальная синхронизация данных
- **Автоматическая загрузка**: Каждые 10 минут из Google Sheets
- **Готовые таблицы**: 2 реальные таблицы уже настроены
- **Zero-code конфигурация**: Добавление новых источников через `datasets.json`

### 🔍 Продвинутая дедупликация (3 стратегии)
1. **По source_id**: Проверка уникального идентификатора из источника
2. **По хешу уникальных полей**: MD5 хеш от ключевых полей
3. **Bloom filter**: Вероятностная структура для сверхбыстрой проверки

### 🛡️ Многоуровневая спам-фильтрация
1. **Keywords**: Список запрещенных слов
2. **Regex patterns**: Регулярные выражения для URL, CAPS, чисел
3. **ML-ready**: Структура для будущего машинного обучения

### 📈 Enterprise аналитика
- **Встроенные отчеты**: Статистика, тематический анализ, геолокация
- **Apache Superset**: Продвинутые дашборды, scheduled reports
- **Кастомизируемые отчеты**: Через конфигурацию `reports.json`

## 📚 Полная документация

### Основная документация
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Детальная архитектура системы
- **[PRODUCTION_GUIDE.md](./PRODUCTION_GUIDE.md)** - Руководство по развертыванию в production
- **[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)** - Настройка Google Sheets API
- **[FINAL_REPORT.md](./FINAL_REPORT.md)** - Отчет о проверке полного цикла работы

### Production документация
- **[PRODUCTION_ENV.md](./PRODUCTION_ENV.md)** - Production переменные окружения
- **[NGINX_SSL_CONFIG.md](./NGINX_SSL_CONFIG.md)** - SSL/TLS конфигурация Nginx

## 🧪 Тестирование и проверка

### Полный цикл тестирования выполнен:
```bash
# Запуск демонстрации рабочего цикла
python demo_workflow.py

# Запуск тестов компонентов
python test_simple.py

# Проверка полного цикла
python test_full_cycle.py
```

### ✅ Проверенные компоненты:
1. **Архитектура взаимодействия** - 7 сервисов
2. **Google Sheets интеграция** - Реальная работа с API
3. **Дедупликация** - 3 стратегии
4. **Спам-фильтрация** - 3 уровня
5. **Пагинация и lazy loading** - Backend pagination
6. **Фильтрация и сортировка** - Полная функциональность
7. **Redis кеширование** - Многоуровневое кеширование
8. **Отчетность** - Статистика с учетом спама
9. **Полный цикл работы** - От загрузки до отображения

## 🔄 Управление системой

### Скрипты управления
```bash
# Development
./start.sh          # Запуск системы
./stop.sh           # Остановка системы
./status.sh         # Проверка статуса

# Production
./scripts/deploy.sh     # Автоматический деплой
./scripts/backup.sh     # Создание бэкапа
./scripts/restore.sh    # Восстановление из бэкапа
```

## 📈 Масштабирование

### Вертикальное масштабирование
- Увеличение ресурсов контейнеров (CPU, RAM)
- Настройка connection pooling
- Оптимизация индексов PostgreSQL

### Горизонтальное масштабирование
- Backend реплики за балансировщиком нагрузки
- Redis cluster для распределенного кеша
- PostgreSQL read replicas для отчетов

## 🔧 Технологический стек

### Backend (FastAPI)
- **FastAPI**: Современный веб-фреймворк
- **PostgreSQL 15**: Основная база данных
- **Redis 7**: Кеширование
- **Google Sheets API**: Прямая интеграция

### Frontend (React 18)
- **React 18**: Современный UI фреймворк
- **TypeScript**: Статическая типизация
- **TanStack Query & Table**: Управление состоянием и таблицы
- **Tailwind CSS**: Утилитарный CSS фреймворк

### DevOps & Infrastructure
- **Docker Compose**: Оркестрация 7+ сервисов
- **Nginx**: Reverse proxy с SSL/TLS
- **Apache Superset**: Enterprise BI платформа
- **Prometheus + Grafana**: Мониторинг

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](./LICENSE) для подробностей.

---

**Unified Data Dashboard System** - готовое enterprise-решение для анализа данных из Google Sheets! 🚀