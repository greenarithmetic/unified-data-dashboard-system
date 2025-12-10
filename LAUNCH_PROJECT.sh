#!/bin/bash

# 🚀 Unified Data Dashboard System - Launch Script
# Автоматический запуск и проверка проекта

set -e

echo "🚀 Unified Data Dashboard System - Запуск проекта"
echo "=================================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Проверка Docker
check_docker() {
    print_info "Проверка Docker..."
    if command -v docker &> /dev/null; then
        print_success "Docker установлен"
    else
        print_error "Docker не установлен"
        echo "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose установлен"
    else
        print_error "Docker Compose не установлен"
        echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Проверка файлов проекта
check_project_files() {
    print_info "Проверка файлов проекта..."
    
    required_files=(
        "docker-compose.yml"
        ".env.example"
        "start.sh"
        "backend/Dockerfile"
        "frontend/Dockerfile"
        "config/datasets.json"
    )
    
    missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "Все необходимые файлы присутствуют"
    else
        print_error "Отсутствуют файлы:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

# Настройка .env файла
setup_env() {
    print_info "Настройка переменных окружения..."
    
    if [ -f ".env" ]; then
        print_warning "Файл .env уже существует"
        read -p "Хотите обновить его? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Используем существующий .env файл"
            return 0
        fi
    fi
    
    # Копируем пример
    cp .env.example .env
    
    print_info "Файл .env создан из примера"
    print_info "Отредактируйте .env файл для вашей конфигурации"
    echo ""
    echo "Обязательные настройки:"
    echo "  1. Google Sheets API credentials"
    echo "  2. Database passwords"
    echo "  3. Superset configuration"
    echo ""
    
    read -p "Открыть .env файл для редактирования? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
    
    print_success "Настройка .env завершена"
}

# Запуск проекта
start_project() {
    print_info "Запуск Unified Data Dashboard System..."
    
    # Даем права на выполнение скриптов
    chmod +x start.sh stop.sh status.sh
    
    # Запускаем проект
    ./start.sh
    
    if [ $? -eq 0 ]; then
        print_success "Проект успешно запущен!"
    else
        print_error "Ошибка при запуске проекта"
        echo "Проверьте логи: docker-compose logs"
        exit 1
    fi
}

# Проверка работы сервисов
check_services() {
    print_info "Проверка работы сервисов..."
    echo ""
    
    # Ждем немного для запуска сервисов
    sleep 10
    
    # Проверяем статус
    ./status.sh
    
    echo ""
    print_info "Проверка health endpoints..."
    
    # Проверка backend health
    if curl -s -f http://localhost:8000/api/v1/health > /dev/null; then
        print_success "Backend работает корректно"
    else
        print_error "Backend не отвечает"
    fi
    
    # Проверка frontend (попробуем получить HTML)
    if curl -s -f http://localhost:3000 > /dev/null; then
        print_success "Frontend работает корректно"
    else
        print_warning "Frontend может быть еще не готов, проверьте позже"
    fi
    
    echo ""
}

# Демонстрация возможностей
show_demo() {
    print_info "Демонстрация возможностей системы..."
    echo ""
    
    echo "🚀 Доступные сервисы:"
    echo "  • Frontend:      http://localhost:3000"
    echo "  • Backend API:   http://localhost:8000"
    echo "  • API Docs:      http://localhost:8000/docs"
    echo "  • Superset:      http://localhost:8088"
    echo ""
    
    echo "📊 Примеры API запросов:"
    echo "  1. Проверка здоровья:"
    echo "     curl http://localhost:8000/api/v1/health"
    echo ""
    echo "  2. Получение данных:"
    echo "     curl http://localhost:8000/api/v1/data/community_requests?page=1&per_page=10"
    echo ""
    echo "  3. Статистика:"
    echo "     curl http://localhost:8000/api/v1/data/community_requests/stats"
    echo ""
    
    echo "🔧 Управление системой:"
    echo "  • Просмотр логов:    docker-compose logs -f [service]"
    echo "  • Остановка:         ./stop.sh"
    echo "  • Проверка статуса:  ./status.sh"
    echo ""
}

# Основная функция
main() {
    echo ""
    echo "🚀 Unified Data Dashboard System - Production Ready"
    echo "=================================================="
    echo ""
    
    # Проверка зависимостей
    check_docker
    
    # Проверка файлов проекта
    check_project_files
    
    # Настройка .env
    setup_env
    
    # Запуск проекта
    start_project
    
    # Проверка сервисов
    check_services
    
    # Демонстрация
    show_demo
    
    echo ""
    echo "=================================================="
    echo "🎉 Unified Data Dashboard System успешно запущена!"
    echo ""
    echo "📚 Документация:"
    echo "  • README_FINAL.md - Основная документация"
    echo "  • ARCHITECTURE.md - Архитектура системы"
    echo "  • PRODUCTION_GUIDE.md - Production руководство"
    echo ""
    echo "🚀 Для начала работы откройте:"
    echo "  http://localhost:3000"
    echo ""
    echo "🔧 Для управления используйте скрипты:"
    echo "  ./stop.sh    - Остановка системы"
    echo "  ./status.sh  - Проверка статуса"
    echo ""
    echo "=================================================="
}

# Запуск основной функции
main "$@"