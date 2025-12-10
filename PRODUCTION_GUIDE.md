# 🚀 Production Deployment Guide для Unified Data Dashboard System

## 📋 Содержание

1. [Требования для Production](#требования-для-production)
2. [Security Checklist](#security-checklist)
3. [Docker Security Best Practices](#docker-security-best-practices)
4. [Network Security](#network-security)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Deployment](#deployment)
9. [Performance Optimization](#performance-optimization)

## Требования для Production

### Системные требования
- **CPU**: 4+ ядер (рекомендуется 8)
- **RAM**: 8+ GB (рекомендуется 16GB)
- **Storage**: 50+ GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS, CentOS 7/8, или Docker-совместимая система

### Сетевые требования
- **Порты**: 80, 443, 5432, 6379, 8000, 8088
- **Доступ в интернет**: Для Google Sheets API
- **Firewall**: Настроить правила для доступа

## Security Checklist

### 1. Обновление секретов
```bash
# Генерация безопасных паролей
openssl rand -base64 32  # Для паролей
openssl rand -hex 32     # Для секретных ключей
```

### 2. Обновленный .env для production
Создайте файл `.env.production` с безопасными значениями (см. файл `PRODUCTION_ENV.md`)

## Docker Security Best Practices

Создайте `docker-compose.production.yml` с настройками безопасности:
- Security options: `no-new-privileges:true`
- Read-only файловые системы
- Health checks для всех сервисов
- Изолированные сети

## Network Security

### Настройка firewall
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### Docker network isolation
```bash
docker network create --internal udds-internal
```

## SSL/TLS Configuration

### Создание директории для сертификатов
```bash
mkdir -p nginx/ssl
# Поместите сертификаты:
# - nginx/ssl/certificate.crt
# - nginx/ssl/private.key
# - nginx/ssl/dhparam.pem (опционально)
```

### Конфигурация Nginx для SSL
См. файл `NGINX_SSL_CONFIG.md` для полной конфигурации

## Monitoring & Logging

### Prometheus + Grafana
Добавьте в `docker-compose.production.yml` сервисы:
- **Prometheus**: Сбор метрик
- **Grafana**: Визуализация метрик
- **Loki**: Централизованное логирование
- **Promtail**: Сбор логов

### Health Checks
Каждый сервис имеет health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Backend: `curl -f http://localhost:8000/api/v1/health`

## Backup & Recovery

### Backup Script
Создайте `scripts/backup.sh` для автоматического бэкапа:
- PostgreSQL дампы
- Redis RDB файлы
- Конфигурационные файлы

### Recovery Script
Создайте `scripts/restore.sh` для восстановления из бэкапа

## Deployment

### Automated Deployment
Создайте `scripts/deploy.sh` для автоматического деплоя:
1. Pull latest changes
2. Build services
3. Run migrations
4. Health checks

### CI/CD Pipeline
Настройте GitHub Actions для автоматического деплоя при push в main ветку

## Performance Optimization

### Database Optimization
- Создание индексов
- Materialized views для часто запрашиваемых данных
- Query optimization

### Redis Optimization
- Настройка maxmemory
- Append-only файлы
- Репликация

### Backend Optimization
- Gunicorn workers
- Connection pooling
- Caching strategies

## 🚀 Быстрый старт в Production

1. **Подготовка сервера**
   ```bash
   # Установите Docker и Docker Compose
   # Настройте firewall
   # Создайте пользователя для приложения
   ```

2. **Настройка проекта**
   ```bash
   git clone <repository>
   cd unified-data-dashboard
   
   # Создайте .env.production с безопасными значениями
   cp .env.example .env.production
   # Отредактируйте .env.production
   
   # Настройте SSL сертификаты
   mkdir -p nginx/ssl
   # Поместите сертификаты
   ```

3. **Запуск в production**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

4. **Проверка**
   ```bash
   # Проверьте health
   curl https://your-domain.com/api/v1/health
   
   # Проверьте логи
   docker-compose -f docker-compose.production.yml logs -f
   ```

## 📞 Поддержка

### Мониторинг
- **Grafana**: http://your-domain.com:3001
- **Prometheus**: http://your-domain.com:9090

### Логи
- **Loki**: http://your-domain.com:3100

### Документация
- **API Docs**: https://your-domain.com/docs
- **Frontend**: https://your-domain.com
- **Superset**: https://your-domain.com/superset

## 🔧 Устранение неполадок

### Common Issues
1. **Out of memory**: Увеличьте RAM или настройте swap
2. **Database connection issues**: Проверьте credentials и firewall
3. **SSL errors**: Проверьте сертификаты и их срок действия
4. **Sync failures**: Проверьте Google Sheets API credentials

### Debug Commands
```bash
# Проверка состояния сервисов
docker-compose -f docker-compose.production.yml ps

# Просмотр логов
docker-compose -f docker-compose.production.yml logs -f backend

# Проверка базы данных
docker-compose -f docker-compose.production.yml exec postgres psql -U udds_prod -d udds_production

# Проверка Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli ping
```

Теперь ваша Unified Data Dashboard System готова к работе в production! 🎉