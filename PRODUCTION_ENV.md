# 🔒 Production Environment Variables для UDDS

## 📋 Обзор

Этот файл содержит пример production конфигурации для Unified Data Dashboard System.
**ВАЖНО**: Замените все значения `your_*` на реальные безопасные значения.

## 🚨 Security Warning

1. **Никогда не коммитьте** этот файл в git
2. Используйте `.gitignore` для исключения файлов с секретами
3. Регулярно обновляйте пароли и ключи
4. Используйте разные значения для разных окружений

## 📝 Production .env файл

```bash
# =====================================================
# PRODUCTION ENVIRONMENT - SECURE CONFIGURATION
# =====================================================

# Database
POSTGRES_USER=udds_prod
POSTGRES_PASSWORD=your_secure_postgres_password_here_change_immediately
POSTGRES_DB=udds_production
DATABASE_URL=postgresql://udds_prod:${POSTGRES_PASSWORD}@postgres:5432/udds_production

# Redis
REDIS_PASSWORD=your_secure_redis_password_here_change_immediately
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"your-project-id","private_key_id":"your-private-key-id","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"udds-service-account@your-project-id.iam.gserviceaccount.com","client_id":"your-client-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/udds-service-account%40your-project-id.iam.gserviceaccount.com"}'

# Superset
SUPERSET_SECRET_KEY=your_superset_secret_key_here_change_immediately
SUPERSET_DATABASE_PASSWORD=your_superset_db_password_here_change_immediately

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-domain.com","https://app.your-domain.com","https://api.your-domain.com"]
API_V1_STR=/api/v1
LOG_LEVEL=WARNING
WEBHOOK_SECRET=your_webhook_secret_here_change_immediately

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_change_immediately
ENCRYPTION_KEY=your_encryption_key_here_change_immediately

# Sync
DEFAULT_SYNC_INTERVAL_MINUTES=10
DATASETS_CONFIG_PATH=/app/config/datasets.json
REPORTS_CONFIG_PATH=/app/config/reports.json

# Monitoring
SENTRY_DSN=https://your-sentry-dsn.ingest.sentry.io/your-project
PROMETHEUS_METRICS_PORT=9091

# Email (опционально, для уведомлений)
SMTP_HOST=smtp.your-domain.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=noreply@your-domain.com

# Telegram (опционально, для уведомлений)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Session
SESSION_SECRET=your_session_secret_here_change_immediately
SESSION_TIMEOUT=86400

# File Upload (опционально)
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["csv","xlsx","json"]

# Cache
CACHE_TTL_STATS=300  # 5 минут
CACHE_TTL_RECORDS=600  # 10 минут
CACHE_TTL_PAGES=60  # 1 минута

# Performance
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
WORKER_COUNT=4
THREAD_COUNT=2
```

## 🔧 Генерация безопасных значений

### 1. Генерация паролей
```bash
# Генерация безопасного пароля (32 символа)
openssl rand -base64 32

# Генерация hex ключа (64 символа)
openssl rand -hex 32
```

### 2. Генерация JWT секрета
```bash
# Генерация сильного JWT секрета
openssl rand -hex 64
```

### 3. Генерация Superset секрета
```bash
# Генерация секрета для Superset
openssl rand -hex 64
```

## 🛡️ Security Best Practices

### 1. Ротация ключей
- Обновляйте пароли каждые 90 дней
- Создавайте новые ключи перед удалением старых
- Обновляйте все окружения одновременно

### 2. Доступ к секретам
- Используйте Docker secrets для production
- Храните секреты в secure vault (Hashicorp Vault, AWS Secrets Manager)
- Ограничьте доступ к .env файлам

### 3. Мониторинг доступа
- Логируйте все попытки доступа к API
- Настройте алерты на подозрительную активность
- Регулярно проверяйте логи

## 🚀 Быстрая настройка

### 1. Создание .env.production
```bash
# Копируем пример
cp .env.example .env.production

# Генерируем безопасные значения
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "SUPERSET_SECRET_KEY=$(openssl rand -hex 64)" >> .env.production
echo "JWT_SECRET_KEY=$(openssl rand -hex 64)" >> .env.production
echo "WEBHOOK_SECRET=$(openssl rand -hex 32)" >> .env.production

# Редактируем остальные значения
nano .env.production
```

### 2. Проверка .env файла
```bash
# Проверка синтаксиса
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env.production'); print('Environment loaded successfully')"

# Проверка обязательных переменных
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SUPERSET_SECRET_KEY")
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ Missing required variable: $var"
    exit 1
  fi
done
echo "✅ All required variables are set"
```

## 🔄 Обновление секретов

### 1. Процесс обновления
```bash
# 1. Создайте новые секреты
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Обновите .env.production
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_PASSWORD/" .env.production

# 3. Перезапустите сервисы
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 4. Проверьте работу
curl -f https://your-domain.com/api/v1/health
```

### 2. Миграция базы данных
```bash
# При смене пароля PostgreSQL
# 1. Обновите пароль в PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres psql -U postgres -c "ALTER USER udds_prod WITH PASSWORD '$NEW_PASSWORD';"

# 2. Обновите .env.production
# 3. Перезапустите сервисы
```

## 📊 Мониторинг секретов

### 1. Проверка утечек
```bash
# Поиск секретов в коде
grep -r "password\|secret\|key\|token" --include="*.py" --include="*.js" --include="*.json" .

# Проверка .git истории
git log -p --all --full-history -- "**/.env*" "**/*secret*" "**/*password*"
```

### 2. Сканирование зависимостей
```bash
# Проверка уязвимостей в зависимостях
pip-audit
npm audit
```

## 🆘 Emergency Procedures

### 1. Компрометация секретов
```bash
# Немедленные действия:
# 1. Отключите доступ к системе
# 2. Сгенерируйте новые секреты
# 3. Обновите все .env файлы
# 4. Перезапустите все сервисы
# 5. Проверьте логи на подозрительную активность
# 6. Уведомите команду безопасности
```

### 2. Восстановление из бэкапа
```bash
# Если секреты утеряны:
# 1. Восстановите .env.production из бэкапа
# 2. Сгенерируйте новые пароли для безопасности
# 3. Обновите базы данных с новыми паролями
```

## 📞 Контакты для безопасности

### Ответственные лица
- **Security Lead**: security@your-domain.com
- **System Admin**: admin@your-domain.com
- **On-call Engineer**: oncall@your-domain.com

### Процедуры экстренного реагирования
1. Сообщите в security@your-domain.com
2. Отключите доступ к системе
3. Следуйте emergency procedures
4. Документируйте инцидент

Теперь ваши production секреты защищены! 🔒