# Развертывание Unified Data Dashboard System

## 🚀 Быстрое развертывание (Development)

### Требования
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM минимум
- 10GB свободного места на диске

### Шаги развертывания

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd unified-data-dashboard

# 2. Настроить окружение
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# 3. Настроить Google Sheets API (опционально)
# См. SETUP-GOOGLE-SHEETS.md

# 4. Запустить проект
./start.sh

# 5. Проверить статус
./status.sh
```

### Проверка работоспособности
1. Откройте http://localhost:3000 - должен загрузиться интерфейс
2. Откройте http://localhost:8000/docs - должна открыться документация API
3. Проверьте логи: `docker-compose logs -f`

## 🏭 Production развертывание

### Рекомендуемые серверные требования
- **CPU**: 4+ ядер
- **RAM**: 8GB+ 
- **Storage**: 50GB+ SSD
- **OS**: Ubuntu 20.04 LTS или выше

### Шаг 1: Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### Шаг 2: Настройка проекта

```bash
# Клонировать проект
git clone <repository-url> /opt/udds
cd /opt/udds

# Создать production .env файл
cat > .env << EOF
# ===== PRODUCTION CONFIGURATION =====
ENVIRONMENT=production
DEBUG=false

# ===== DATABASE =====
DB_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=postgresql://udds:\${DB_PASSWORD}@postgres:5432/udds

# ===== REDIS =====
REDIS_URL=redis://redis:6379

# ===== SUPERSET =====
SUPERSET_SECRET_KEY=$(openssl rand -base64 64)
SUPERSET_DATABASE_PASSWORD=\${DB_PASSWORD}

# ===== SECURITY =====
CORS_ORIGINS=["https://ваш-домен.com"]
WEBHOOK_SECRET=$(openssl rand -base64 32)

# ===== GOOGLE SHEETS =====
# GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}

# ===== LOGGING =====
LOG_LEVEL=INFO
EOF

# Настроить права
chmod 600 .env
```

### Шаг 3: Настройка Nginx для production

Создайте файл `/etc/nginx/sites-available/udds`:

```nginx
server {
    listen 80;
    server_name ваш-домен.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ваш-домен.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/ваш-домен.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ваш-домен.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=frontend:10m rate=100r/s;
    
    # Frontend
    location / {
        limit_req zone=frontend burst=20 nodelay;
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/ {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Superset
    location /superset/ {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Шаг 4: Настройка SSL (Let's Encrypt)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить SSL сертификат
sudo certbot --nginx -d ваш-домен.com

# Настроить автоматическое обновление
sudo certbot renew --dry-run
```

### Шаг 5: Запуск в production

```bash
# Перейти в директорию проекта
cd /opt/udds

# Собрать образы для production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Запустить в фоновом режиме
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose ps

# Просмотреть логи
docker-compose logs -f
```

### Шаг 6: Настройка мониторинга

```bash
# Установить Prometheus и Grafana
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

## ☁️ Развертывание в облаке

### AWS (EC2 + RDS + ElastiCache)

1. **Создать EC2 инстанс** (t3.medium или выше)
2. **Настроить RDS** (PostgreSQL) и ElastiCache (Redis)
3. **Обновить .env файл** с облачными endpoint'ами
4. **Настроить Security Groups** для доступа
5. **Запустить приложение** как описано выше

### Google Cloud Platform

1. **Создать Compute Engine VM**
2. **Настроить Cloud SQL** (PostgreSQL) и Memorystore (Redis)
3. **Настроить Load Balancer** и Cloud CDN
4. **Развернуть через Cloud Run** (контейнеризированное приложение)

### Azure

1. **Создать Azure VM**
2. **Настроить Azure Database for PostgreSQL** и Azure Cache for Redis
3. **Настроить Application Gateway**
4. **Развернуть через Azure Container Instances**

## 🔄 CI/CD Pipeline (GitHub Actions)

Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy UDDS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/ -v
          
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: your-username/udds-backend:latest
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: your-username/udds-frontend:latest
          
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/udds
            git pull origin main
            docker-compose pull
            docker-compose up -d --build
            docker system prune -f
```

## 📊 Мониторинг и логирование

### Prometheus + Grafana

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
```

### Логирование (ELK Stack)

```yaml
# logging/docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      
  logstash:
    image: logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      
  kibana:
    image: kibana:8.0.0
    ports:
      - "5601:5601"
```

## 🔒 Безопасность в production

### Обязательные меры безопасности
1. **Изменить все пароли по умолчанию**
2. **Настроить firewall** (UFW или iptables)
3. **Регулярно обновлять** Docker образы
4. **Использовать secrets management** (HashiCorp Vault или AWS Secrets Manager)
5. **Настроить backup** базы данных

### Рекомендуемая конфигурация firewall
```bash
# Установить UFW
sudo apt install ufw -y

# Настроить правила
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Backup базы данных
```bash
# Создать скрипт backup
cat > /opt/udds/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/udds"
DATE=$(date +%Y%m%d_%H%M%S)

# Создать backup PostgreSQL
docker-compose exec -T postgres pg_dump -U udds udds > $BACKUP_DIR/udds_$DATE.sql

# Сжать backup
gzip $BACKUP_DIR/udds_$DATE.sql

# Удалить старые backups (хранить 30 дней)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

# Настроить cron job
echo "0 2 * * * /opt/udds/backup.sh" | sudo crontab -
```

## 🚨 Аварийное восстановление

### Восстановление из backup
```bash
# Остановить приложение
cd /opt/udds
docker-compose down

# Восстановить базу данных
gunzip -c /backups/udds/latest_backup.sql.gz | docker-compose exec -T postgres psql -U udds udds

# Запустить приложение
docker-compose up -d
```

### Миграция на новый сервер
1. **Создать backup** базы данных и конфигураций
2. **Настроить новый сервер** как описано выше
3. **Восстановить данные** из backup
4. **Обновить DNS записи**
5. **Проверить работоспособность**

## 📞 Поддержка production

### Полезные команды
```bash
# Просмотр логов
docker-compose logs -f [service_name]

# Проверка использования ресурсов
docker stats

# Проверка состояния базы данных
docker-compose exec postgres psql -U udds -d udds -c "SELECT version();"

# Перезапуск сервиса
docker-compose restart [service_name]

# Обновление образов
docker-compose pull
docker-compose up -d
```

### Мониторинг метрик
- **CPU/RAM usage**: `docker stats`
- **Database connections**: через pgAdmin или psql
- **API response time**: через Prometheus/Grafana
- **Error rates**: через логгирование

Проект готов к production использованию и включает все необходимые компоненты для надежной работы в продакшн среде.