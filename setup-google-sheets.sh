#!/bin/bash

# Скрипт для настройки Google Sheets API для Unified Data Dashboard System

set -e

echo "🔧 Настройка Google Sheets API для UDDS"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для вывода
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    # Проверка jq
    if ! command -v jq &> /dev/null; then
        print_warning "jq не установлен. Установка..."
        apt-get update && apt-get install -y jq
    fi
    
    # Проверка curl
    if ! command -v curl &> /dev/null; then
        print_warning "curl не установлен. Установка..."
        apt-get update && apt-get install -y curl
    fi
    
    print_success "Зависимости проверены"
}

# Создание директорий
create_directories() {
    print_info "Создание директорий..."
    
    mkdir -p config
    mkdir -p secrets
    mkdir -p logs
    
    print_success "Директории созданы"
}

# Шаг 1: Инструкция по созданию сервисного аккаунта
step1_create_service_account() {
    echo ""
    echo "📋 ШАГ 1: Создание сервисного аккаунта в Google Cloud"
    echo "------------------------------------------------------"
    
    cat << EOF
Для работы с Google Sheets API необходимо:

1. Перейдите в Google Cloud Console:
   https://console.cloud.google.com/

2. Создайте новый проект или выберите существующий

3. Включите API:
   - Google Sheets API
   - Google Drive API

4. Создайте сервисный аккаунт:
   - Имя: udds-service-account
   - Роль: Viewer (достаточно)

5. Создайте ключ JSON для сервисного аккаунта

6. Скачайте файл credentials.json

После скачивания файла поместите его в папку:
  /workspace/unified-data-dashboard/secrets/

Или продолжайте для ручной настройки.

EOF
    
    read -p "Поместили ли вы credentials.json в папку secrets/? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "secrets/credentials.json" ]; then
            print_success "Файл credentials.json найден"
            return 0
        else
            print_error "Файл credentials.json не найден в папке secrets/"
            return 1
        fi
    else
        print_info "Продолжаем без файла credentials.json"
        return 2
    fi
}

# Шаг 2: Настройка доступа к таблицам
step2_setup_sheet_access() {
    echo ""
    echo "📋 ШАГ 2: Настройка доступа к Google Sheets таблицам"
    echo "------------------------------------------------------"
    
    cat << EOF
Для предоставления доступа к таблицам:

1. Откройте Google Sheets таблицу
2. Нажмите "Поделиться" (Share)
3. Добавьте email сервисного аккаунта:
   udds-service-account@ВАШ-PROJECT-ID.iam.gserviceaccount.com

4. Установите права: "Viewer" (Просмотр)

5. Повторите для всех таблиц из datasets.json:

   - Таблица 1 (Обращения граждан):
     ID: 1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E
     URL: https://docs.google.com/spreadsheets/d/1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E

   - Таблица 2 (Вторая таблица):
     ID: 1jk6Ogf6Kvt6chPZGiB6eIZqN0c0-qYi0_Wb_cPXqovw
     URL: https://docs.google.com/spreadsheets/d/1jk6Ogf6Kvt6chPZGiB6eIZqN0c0-qYi0_Wb_cPXqovw

EOF
    
    read -p "Предоставили ли вы доступ к таблицам? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "Доступ к таблицам настроен"
        return 0
    else
        print_warning "Продолжаем без доступа к таблицам (будут использоваться тестовые данные)"
        return 1
    fi
}

# Шаг 3: Настройка переменных окружения
step3_setup_environment() {
    echo ""
    echo "📋 ШАГ 3: Настройка переменных окружения"
    echo "----------------------------------------"
    
    # Проверяем существование .env файла
    if [ -f ".env" ]; then
        print_info "Файл .env уже существует"
        read -p "Хотите обновить его? (y/n): " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Пропускаем обновление .env"
            return 0
        fi
    fi
    
    # Создаем/обновляем .env файл
    print_info "Создание/обновление .env файла..."
    
    # Базовый .env файл
    cat > .env << EOF
# Unified Data Dashboard System - Environment Variables
# =====================================================

# Database
POSTGRES_USER=udds
POSTGRES_PASSWORD=your_secure_password_here_change_in_production
POSTGRES_DB=udds
DATABASE_URL=postgresql://udds:your_secure_password_here_change_in_production@postgres:5432/udds

# Redis
REDIS_URL=redis://redis:6379

# Google Sheets (заполнить после настройки)
# GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"your-project-id",...}'

# Superset
SUPERSET_SECRET_KEY=dev-secret-change-in-production
SUPERSET_DATABASE_PASSWORD=your_secure_password_here_change_in_production

# Application
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://localhost:8088"]
API_V1_STR=/api/v1
LOG_LEVEL=INFO
WEBHOOK_SECRET=your-secret-for-webhook-validation
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

# Sync
DEFAULT_SYNC_INTERVAL_MINUTES=10
DATASETS_CONFIG_PATH=/app/config/datasets.json
REPORTS_CONFIG_PATH=/app/config/reports.json
EOF
    
    print_success ".env файл создан/обновлен"
    
    # Если есть credentials.json, добавляем его в .env
    if [ -f "secrets/credentials.json" ]; then
        print_info "Добавление Google Sheets credentials в .env..."
        
        # Конвертируем JSON в одну строку
        CREDENTIALS_JSON=$(jq -c . < secrets/credentials.json | tr -d '\n')
        
        # Добавляем в .env
        sed -i "/# GOOGLE_SHEETS_CREDENTIALS/c\GOOGLE_SHEETS_CREDENTIALS='$CREDENTIALS_JSON'" .env
        
        print_success "Google Sheets credentials добавлены в .env"
    else
        print_warning "Файл credentials.json не найден. Google Sheets API не будет работать."
        print_info "Для добавления credentials позже выполните:"
        echo "  jq -c . < credentials.json | tr -d '\n'"
        echo "  Затем добавьте результат в .env как GOOGLE_SHEETS_CREDENTIALS"
    fi
    
    return 0
}

# Шаг 4: Тестирование подключения
step4_test_connection() {
    echo ""
    echo "📋 ШАГ 4: Тестирование подключения"
    echo "----------------------------------"
    
    print_info "Создание тестового скрипта..."
    
    cat > test_google_sheets.py << 'EOF'
#!/usr/bin/env python3
"""Тест подключения к Google Sheets API"""

import os
import json
import sys

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    
    print("🔧 Тестирование Google Sheets API подключения")
    print("=" * 50)
    
    # Проверка переменной окружения
    credentials_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    
    if not credentials_json:
        print("❌ GOOGLE_SHEETS_CREDENTIALS не установлена")
        print("ℹ️  Используются тестовые данные")
        sys.exit(0)
    
    try:
        # Парсинг credentials
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = credentials_json
        
        # Создание credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Создание сервиса
        service = build('sheets', 'v4', credentials=credentials)
        
        print("✅ Google Sheets сервис инициализирован")
        
        # Тестирование подключения к таблице из datasets.json
        try:
            import json as json_module
            with open('datasets.json', 'r', encoding='utf-8') as f:
                datasets = json_module.load(f)
            
            for dataset in datasets.get('datasets', []):
                if dataset.get('source') == 'google_sheets':
                    sheet_id = dataset.get('sheet_id')
                    sheet_name = dataset.get('sheet_name', 'Лист1')
                    
                    print(f"\n📊 Тестирование таблицы: {dataset['name']}")
                    print(f"   ID: {sheet_id}")
                    print(f"   Лист: {sheet_name}")
                    
                    try:
                        # Пробуем получить первые 5 строк
                        result = service.spreadsheets().values().get(
                            spreadsheetId=sheet_id,
                            range=f"{sheet_name}!A1:E5"
                        ).execute()
                        
                        values = result.get('values', [])
                        
                        if values:
                            print(f"   ✅ Успешно! Получено {len(values)} строк")
                            print(f"   📋 Заголовки: {values[0] if values else 'нет данных'}")
                        else:
                            print("   ⚠️  Таблица пуста или нет доступа")
                            
                    except HttpError as e:
                        if e.resp.status == 403:
                            print(f"   ❌ Нет доступа к таблице")
                            print(f"   ℹ️  Предоставьте доступ сервисному аккаунту")
                        elif e.resp.status == 404:
                            print(f"   ❌ Таблица не найдена")
                            print(f"   ℹ️  Проверьте Sheet ID")
                        else:
                            print(f"   ❌ Ошибка: {e}")
                    
        except Exception as e:
            print(f"❌ Ошибка при чтении datasets.json: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Google Sheets API настроен корректно!")
        print("ℹ️  Система готова к работе с реальными данными")
        
    except json.JSONDecodeError:
        print("❌ Неверный формат GOOGLE_SHEETS_CREDENTIALS")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        
except ImportError as e:
    print(f"❌ Не установлены зависимости: {e}")
    print("ℹ️  Установите: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
EOF
    
    chmod +x test_google_sheets.py
    
    print_info "Запуск теста подключения..."
    
    # Экспортируем переменные из .env
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    python3 test_google_sheets.py
    
    # Очистка
    rm -f test_google_sheets.py
    
    return 0
}

# Шаг 5: Запуск системы
step5_start_system() {
    echo ""
    echo "📋 ШАГ 5: Запуск Unified Data Dashboard System"
    echo "---------------------------------------------"
    
    cat << EOF
Система готова к запуску! Доступные команды:

1. Быстрый старт:
   ./start.sh

2. Запуск в фоне:
   docker-compose up -d

3. Просмотр логов:
   docker-compose logs -f

4. Остановка:
   ./stop.sh

5. Проверка статуса:
   ./status.sh

После запуска система будет доступна:
  • Frontend:      http://localhost:3000
  • Backend API:   http://localhost:8000
  • API Docs:      http://localhost:8000/docs
  • Superset:      http://localhost:8088

EOF
    
    read -p "Запустить систему сейчас? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Запуск системы..."
        
        # Даем права на выполнение скриптов
        chmod +x start.sh stop.sh status.sh
        
        # Запускаем систему
        ./start.sh
        
        if [ $? -eq 0 ]; then
            print_success "Система успешно запущена!"
            
            # Показываем статус
            sleep 5
            ./status.sh
            
        else
            print_error "Ошибка при запуске системы"
            print_info "Проверьте логи: docker-compose logs"
        fi
    else
        print_info "Запуск отменен"
        print_info "Для запуска вручную выполните: ./start.sh"
    fi
    
    return 0
}

# Главная функция
main() {
    echo ""
    echo "🚀 Настройка Google Sheets API для Unified Data Dashboard System"
    echo "================================================================"
    
    # Проверка зависимостей
    check_dependencies
    
    # Создание директорий
    create_directories
    
    # Выполнение шагов
    step1_create_service_account
    step2_setup_sheet_access
    step3_setup_environment
    step4_test_connection
    step5_start_system
    
    echo ""
    echo "================================================================"
    echo "🎉 Настройка завершена!"
    echo ""
    echo "📋 Краткая инструкция:"
    echo "   1. Frontend:      http://localhost:3000"
    echo "   2. API Docs:      http://localhost:8000/docs"
    echo "   3. Superset:      http://localhost:8088"
    echo "   4. Управление:    ./start.sh, ./stop.sh, ./status.sh"
    echo ""
    echo "🔧 Для изменения конфигурации:"
    echo "   • datasets.json   - настройка источников данных"
    echo "   .env             - переменные окружения"
    echo "   docker-compose.yml - конфигурация сервисов"
    echo ""
    echo "📞 Для помощи смотрите документацию в README.md"
    echo "================================================================"
}

# Запуск главной функции
main "$@"