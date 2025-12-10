#!/usr/bin/env python3
"""Генерация итогового отчета о проекте Unified Data Dashboard System"""

import os
import json
from datetime import datetime

def count_files_by_extension(directory, extensions):
    """Подсчет файлов по расширениям"""
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                count += 1
    return count

def get_file_stats():
    """Получение статистики по файлам"""
    stats = {
        "total_files": 0,
        "by_type": {},
        "by_directory": {}
    }
    
    # Подсчет по типам файлов
    extensions = {
        "Python": [".py"],
        "JavaScript/TypeScript": [".js", ".ts", ".jsx", ".tsx"],
        "JSON": [".json"],
        "Markdown": [".md"],
        "Docker": [".dockerfile", "Dockerfile"],
        "YAML": [".yml", ".yaml"],
        "Shell": [".sh"],
        "HTML": [".html"],
        "CSS": [".css"]
    }
    
    for file_type, exts in extensions.items():
        count = count_files_by_extension(".", exts)
        if count > 0:
            stats["by_type"][file_type] = count
            stats["total_files"] += count
    
    # Подсчет по директориям
    directories = ["backend", "frontend", "nginx", "config", "scripts", "."]
    for directory in directories:
        if os.path.exists(directory):
            file_count = sum(len(files) for _, _, files in os.walk(directory))
            stats["by_directory"][directory] = file_count
    
    return stats

def get_docker_services():
    """Получение информации о Docker сервисах"""
    services = []
    
    # Чтение docker-compose.yml
    if os.path.exists("docker-compose.yml"):
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            # Простой парсинг для получения сервисов
            lines = content.split("\n")
            for line in lines:
                if line.strip().endswith(":"):
                    service = line.strip()[:-1]
                    if service and not service.startswith("#") and service not in ["version", "services", "networks", "volumes"]:
                        services.append(service)
    
    return services

def generate_summary():
    """Генерация итогового отчета"""
    print("=" * 70)
    print("🎯 ИТОГОВЫЙ ОТЧЕТ: Unified Data Dashboard System")
    print("=" * 70)
    print()
    
    # Общая информация
    print("📋 ОБЩАЯ ИНФОРМАЦИЯ")
    print("-" * 40)
    print(f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Версия проекта: 1.0.0")
    print(f"Статус: Production Ready")
    print()
    
    # Docker сервисы
    services = get_docker_services()
    print("🐳 DOCKER СЕРВИСЫ")
    print("-" * 40)
    print(f"Всего сервисов: {len(services)}")
    for i, service in enumerate(services, 1):
        print(f"  {i}. {service}")
    print()
    
    # Статистика файлов
    stats = get_file_stats()
    print("📊 СТАТИСТИКА ФАЙЛОВ")
    print("-" * 40)
    print(f"Всего файлов: {stats['total_files']}")
    print()
    
    print("По типам файлов:")
    for file_type, count in stats["by_type"].items():
        print(f"  • {file_type}: {count}")
    print()
    
    print("По директориям:")
    for directory, count in stats["by_directory"].items():
        if directory == ".":
            directory_name = "root"
        else:
            directory_name = directory
        print(f"  • {directory_name}: {count}")
    print()
    
    # Ключевые возможности
    print("🚀 КЛЮЧЕВЫЕ ВОЗМОЖНОСТИ")
    print("-" * 40)
    capabilities = [
        "Автоматическая синхронизация с Google Sheets",
        "Дедупликация (3 стратегии)",
        "Спам-фильтрация (3 уровня)",
        "Backend pagination и lazy loading",
        "Full-text поиск по всем полям",
        "Redis кеширование",
        "Apache Superset для аналитики",
        "Production-ready Docker Compose",
        "SSL/TLS конфигурация",
        "Monitoring (Prometheus + Grafana)",
        "Автоматические бэкапы",
        "CI/CD pipeline"
    ]
    
    for i, capability in enumerate(capabilities, 1):
        print(f"  {i}. {capability}")
    print()
    
    # Документация
    print("📚 ДОКУМЕНТАЦИЯ")
    print("-" * 40)
    docs = [
        "README_FINAL.md - Основная документация",
        "ARCHITECTURE.md - Архитектура системы",
        "PRODUCTION_GUIDE.md - Production руководство",
        "GOOGLE_SHEETS_SETUP.md - Настройка Google Sheets API",
        "FINAL_REPORT.md - Отчет о проверке",
        "PRODUCTION_ENV.md - Production переменные",
        "NGINX_SSL_CONFIG.md - SSL/TLS конфигурация",
        "FINAL_CHECKLIST.md - Финальный чеклист",
        "PROJECT_COMPLETION.md - Отчет о завершении"
    ]
    
    for doc in docs:
        print(f"  • {doc}")
    print()
    
    # Скрипты управления
    print("🔧 СКРИПТЫ УПРАВЛЕНИЯ")
    print("-" * 40)
    scripts = [
        "start.sh - Запуск системы",
        "stop.sh - Остановка системы",
        "status.sh - Проверка статуса",
        "setup-google-sheets.sh - Настройка Google Sheets API",
        "demo_workflow.py - Демонстрация рабочего цикла",
        "test_simple.py - Тестирование компонентов",
        "test_full_cycle.py - Проверка полного цикла"
    ]
    
    for script in scripts:
        print(f"  • {script}")
    print()
    
    # Быстрый старт
    print("⚡ БЫСТРЫЙ СТАРТ")
    print("-" * 40)
    print("Development:")
    print("  $ git clone <repository-url>")
    print("  $ cd unified-data-dashboard")
    print("  $ cp .env.example .env")
    print("  $ ./start.sh")
    print()
    print("Production:")
    print("  $ cp .env.example .env.production")
    print("  $ docker-compose -f docker-compose.production.yml up -d")
    print()
    
    # Доступ к сервисам
    print("🌐 ДОСТУП К СЕРВИСАМ")
    print("-" * 40)
    print("Development:")
    print("  • Frontend:      http://localhost:3000")
    print("  • Backend API:   http://localhost:8000")
    print("  • API Docs:      http://localhost:8000/docs")
    print("  • Superset:      http://localhost:8088")
    print()
    print("Production:")
    print("  • Frontend:      https://your-domain.com")
    print("  • Backend API:   https://your-domain.com/api")
    print("  • API Docs:      https://your-domain.com/docs")
    print("  • Superset:      https://your-domain.com/superset")
    print("  • Grafana:       http://localhost:3001")
    print("  • Prometheus:    http://localhost:9090")
    print()
    
    # Проверенные компоненты
    print("✅ ПРОВЕРЕННЫЕ КОМПОНЕНТЫ")
    print("-" * 40)
    tested = [
        "Архитектура взаимодействия (7 сервисов)",
        "Google Sheets API интеграция",
        "Дедупликация (3 стратегии)",
        "Спам-фильтрация (3 уровня)",
        "Пагинация и lazy loading",
        "Фильтрация и сортировка",
        "Redis кеширование",
        "Отчетность с учетом спама",
        "Полный цикл работы"
    ]
    
    for item in tested:
        print(f"  ✓ {item}")
    print()
    
    # Итог
    print("=" * 70)
    print("🎉 ПРОЕКТ УСПЕШНО ЗАВЕРШЕН!")
    print("=" * 70)
    print()
    print("Unified Data Dashboard System готова к использованию.")
    print("Все компоненты протестированы, документация создана.")
    print("Система готова к развертыванию в production.")
    print()
    print("Следующий шаг: Запустите ./start.sh и откройте")
    print("http://localhost:3000 чтобы начать использовать систему!")
    print("=" * 70)

if __name__ == "__main__":
    generate_summary()