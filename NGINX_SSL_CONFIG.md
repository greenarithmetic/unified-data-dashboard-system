# 🔐 SSL/TLS Configuration для Nginx в UDDS

## 📋 Обзор

Этот документ описывает настройку SSL/TLS для Unified Data Dashboard System в production окружении.

## 🎯 Цели

1. **Безопасность**: Современные протоколы и шифры
2. **Производительность**: HTTP/2, OCSP stapling
3. **Совместимость**: Поддержка старых браузеров
4. **SEO**: HTTPS для лучшего ранжирования

## 📁 Структура директорий

```
nginx/
├── nginx.conf              # Основная конфигурация
├── ssl/                    # Директория для SSL сертификатов
│   ├── certificate.crt     # SSL сертификат
│   ├── private.key         # Приватный ключ
│   └── dhparam.pem         # Параметры Диффи-Хеллмана (опционально)
└── conf.d/
    └── udds.conf          # Конфигурация UDDS
```

## 🔧 Настройка SSL сертификатов

### 1. Получение сертификатов

#### Let's Encrypt (бесплатно)
```bash
# Установите certbot
sudo apt-get install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

#### Коммерческий SSL сертификат
1. Купите сертификат у провайдера (DigiCert, GlobalSign, etc.)
2. Сгенерируйте CSR (Certificate Signing Request)
3. Получите сертификат и цепочку доверия
4. Поместите файлы в `nginx/ssl/`

### 2. Размещение сертификатов
```bash
# Создайте директорию
mkdir -p nginx/ssl

# Поместите сертификаты
# certificate.crt - ваш SSL сертификат
# private.key - приватный ключ
# dhparam.pem - параметры Диффи-Хеллмана (опционально)

# Установите правильные права
chmod 600 nginx/ssl/private.key
chmod 644 nginx/ssl/certificate.crt
```

## 🛠️ Конфигурация Nginx

### Основная конфигурация (`nginx/nginx.conf`)

```nginx
# Основные настройки
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# Events
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

# HTTP блок
http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # MIME Types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # DH Parameters (опционально)
    # ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    
    # Include конфигурации сайтов
    include /etc/nginx/conf.d/*.conf;
}
```

### Конфигурация сайта (`nginx/conf.d/udds.conf`)

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers для HTTP
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    # SSL оптимизации
    ssl_buffer_size 8k;
    ssl_ecdh_curve secp384r1;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Root директория
    root /usr/share/nginx/html;
    index index.html;
    
    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://your-domain.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://your-domain.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain charset=UTF-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # Superset
    location /superset/ {
        proxy_pass http://superset:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Script-Name /superset;
        
        # WebSocket support для Superset
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Статические файлы
    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health checks
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    location /api/v1/auth/ {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://backend:8000;
    }
    
    location /api/v1/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend:8000;
    }
    
    # Запрещенные location
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ /(config|secrets|env) {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Обработка ошибок
    error_page 404 /404.html;
    location = /404.html {
        internal;
    }
    
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        internal;
    }
}
```

## 🚀 Docker Compose конфигурация

### Nginx service в `docker-compose.production.yml`

```yaml
nginx:
  image: nginx:alpine
  container_name: udds-nginx-prod
  restart: unless-stopped
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - ./nginx/ssl:/etc/nginx/ssl:ro
    - ./logs/nginx:/var/log/nginx
  networks:
    - udds-network
  depends_on:
    - backend
    - frontend
    - superset
  security_opt:
    - no-new-privileges:true
  read_only: true
  tmpfs:
    - /tmp
    - /var/cache/nginx
  healthcheck:
    test: ["CMD", "nginx", "-t"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## 🔍 Тестирование конфигурации

### 1. Проверка синтаксиса
```bash
docker-compose -f docker-compose.production.yml exec nginx nginx -t
```

### 2. Проверка SSL
```bash
# Проверка сертификата
openssl x509 -in nginx/ssl/certificate.crt -text -noout

# Проверка приватного ключа
openssl rsa -in nginx/ssl/private.key -check

# Проверка соответствия ключа и сертификата
openssl x509 -noout -modulus -in nginx/ssl/certificate.crt | openssl md5
openssl rsa -noout -modulus -in nginx/ssl/private.key | openssl md5
```

### 3. Онлайн проверка SSL
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [Mozilla Observatory](https://observatory.mozilla.org/)

## 🛡️ Security Hardening

### 1. Дополнительные security headers
```nginx
# HSTS preload
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Clickjacking protection
add_header X-Frame-Options "DENY" always;

# MIME sniffing protection
add_header X-Content-Type-Options "nosniff" always;

# XSS protection
add_header X-XSS-Protection "1; mode=block" always;

# Referrer policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';" always;

# Permissions Policy
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### 2. Rate limiting
```nginx
# Zone definitions
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=static:10m rate=100r/s;

# Application
limit_req zone=api burst=20 nodelay;
limit_req zone=auth burst=5 nodelay;
limit_req zone=static burst=50 nodelay;
```

### 3. Блокировка ботов и сканеров
```nginx
# Block bad bots
if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
    return 403;
}

# Block suspicious requests
if ($request_uri ~* "(eval\(|base64_|cmd=)") {
    return 403;
}
```

## 🔄 Обновление сертификатов

### Автоматическое обновление с certbot
```bash
# Docker контейнер для certbot
certbot:
  image: certbot/certbot
  container_name: udds-certbot
  volumes:
    - ./nginx/ssl:/etc/letsencrypt
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
  command: certonly --webroot --webroot-path=/var/www/html --email admin@your-domain.com --agree-tos --no-eff-email -d your-domain.com -d www.your-domain.com
```

### Renewal script
```bash
#!/bin/bash
# renew-ssl.sh

docker-compose -f docker-compose.production.yml run --rm certbot renew
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
```

### Cron job для автоматического обновления
```bash
# Добавьте в crontab
0 2 * * * /path/to/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1
```

## 🆘 Troubleshooting

### Common Issues

1. **SSL handshake failed**
   ```bash
   # Проверьте сертификаты
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   
   # Проверьте цепочку доверия
   openssl s_client -connect your-domain.com:443 -showcerts
   ```

2. **Mixed content warnings**
   - Убедитесь, что все ресурсы загружаются по HTTPS
   - Обновите Content-Security-Policy header

3. **HSTS errors**
   ```bash
   # Проверьте HSTS header
   curl -I https://your-domain.com | grep Strict-Transport-Security
   ```

4. **Performance issues**
   ```bash
   # Проверьте SSL handshake time
   curl -w "ssl_handshake: %{time_appconnect}\n" -o /dev/null -s https://your-domain.com
   ```

### Debug Commands
```bash
# Проверка конфигурации
docker-compose -f docker-compose.production.yml exec nginx nginx -T

# Просмотр логов
docker-compose -f docker-compose.production.yml logs -f nginx

# Проверка headers
curl -I https://your-domain.com

# SSL проверка
openssl s_client -connect your-domain.com:443 -tlsextdebug -status
```

Теперь ваш Nginx настроен с современными SSL/TLS настройками для production! 🔒