# 🔧 Настройка Google Sheets API для Unified Data Dashboard System

## 📋 Предварительные требования

### 1. Google Cloud Project
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Запомните **Project ID**

### 2. Включение API
1. В Google Cloud Console перейдите в **APIs & Services** → **Library**
2. Найдите и включите следующие API:
   - **Google Sheets API**
   - **Google Drive API** (для доступа к таблицам)

### 3. Создание сервисного аккаунта
1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **+ CREATE CREDENTIALS** → **Service Account**
3. Заполните:
   - **Service account name**: `udds-service-account`
   - **Service account ID**: `udds-service-account@ваш-project-id.iam.gserviceaccount.com`
   - **Description**: "Service account for Unified Data Dashboard System"
4. Нажмите **CREATE AND CONTINUE**
5. Пропустите шаг 2 (Grant access) - нажмите **CONTINUE**
6. Нажмите **DONE**

## 🔐 Получение credentials JSON

### 1. Создание ключа сервисного аккаунта
1. В списке сервисных аккаунтов найдите `udds-service-account`
2. Нажмите на email сервисного аккаунта
3. Перейдите на вкладку **KEYS**
4. Нажмите **ADD KEY** → **Create new key**
5. Выберите тип ключа: **JSON**
6. Нажмите **CREATE**
7. Файл с ключами автоматически скачается (например: `udds-service-account-credentials.json`)

### 2. Структура credentials файла
```json
{
  "type": "service_account",
  "project_id": "ваш-project-id",
  "private_key_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "udds-service-account@ваш-project-id.iam.gserviceaccount.com",
  "client_id": "xxxxxxxxxxxxxxxxxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/udds-service-account%40ваш-project-id.iam.gserviceaccount.com"
}
```

## 🔗 Предоставление доступа к Google Sheets

### 1. Предоставление доступа к конкретным таблицам
1. Откройте Google Sheets таблицу, к которой нужен доступ
2. Нажмите **Share** (Поделиться) в правом верхнем углу
3. В поле "Add people and groups" введите email сервисного аккаунта:
   ```
   udds-service-account@ваш-project-id.iam.gserviceaccount.com
   ```
4. Установите права доступа: **Viewer** (достаточно для чтения)
5. Нажмите **Send**

### 2. Предоставление доступа ко всем таблицам в папке (рекомендуется)
1. Создайте папку в Google Drive
2. Поместите все нужные таблицы в эту папку
3. Поделитесь **папкой** с сервисным аккаунтом
4. Все новые таблицы в папке автоматически будут доступны

## ⚙️ Настройка в Unified Data Dashboard System

### 1. Способ 1: Переменная окружения (рекомендуется для Docker)
1. Конвертируйте JSON credentials в одну строку:
   ```bash
   # Linux/Mac
   cat udds-service-account-credentials.json | jq -c | tr -d '\n'
   
   # Или вручную отформатируйте в одну строку
   ```
   
2. Добавьте в файл `.env`:
   ```bash
   GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"ваш-project-id",...}'
   ```

### 2. Способ 2: Файл credentials
1. Поместите файл `udds-service-account-credentials.json` в папку:
   ```
   /workspace/unified-data-dashboard/backend/config/
   ```
   
2. Обновите `.env`:
   ```bash
   GOOGLE_SHEETS_CREDENTIALS_PATH=/app/config/udds-service-account-credentials.json
   ```

### 3. Способ 3: Base64 кодирование (для Docker secrets)
1. Закодируйте credentials в base64:
   ```bash
   base64 udds-service-account-credentials.json
   ```
   
2. Используйте в docker-compose.yml:
   ```yaml
   secrets:
     google_sheets_credentials:
       file: ./secrets/google_sheets_credentials.json
   ```

## 📊 Настройка datasets.json

### 1. Получение Sheet ID
Sheet ID можно найти в URL Google Sheets:
```
https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0
```

Пример:
- URL: `https://docs.google.com/spreadsheets/d/1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E/edit`
- Sheet ID: `1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E`

### 2. Пример конфигурации в datasets.json
```json
{
  "datasets": [
    {
      "id": "community_requests",
      "name": "Обращения граждан",
      "description": "Сбор обращений из чатов/Telegram",
      "source": "google_sheets",
      "sheet_id": "1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E",
      "sheet_name": "Лист1",
      "sync_interval_minutes": 10,
      "schema": {
        "тема": {
          "type": "text",
          "display_name": "Тема обращения",
          "required": true,
          "filterable": true
        },
        "дата": {
          "type": "datetime",
          "display_name": "Дата обращения",
          "required": true,
          "sortable": true
        }
        // ... другие поля
      }
    }
  ]
}
```

## 🧪 Тестирование подключения

### 1. Тест через Python скрипт
Создайте файл `test_google_sheets.py`:
```python
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Загрузите credentials
with open('udds-service-account-credentials.json', 'r') as f:
    credentials_info = json.load(f)

credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# Создайте сервис
service = build('sheets', 'v4', credentials=credentials)

# Протестируйте доступ
sheet_id = "1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E"
result = service.spreadsheets().values().get(
    spreadsheetId=sheet_id,
    range="Лист1!A1:E5"
).execute()

values = result.get('values', [])
print(f"Успешно! Получено {len(values)} строк")
```

### 2. Тест через систему UDDS
1. Запустите систему:
   ```bash
   docker-compose up -d
   ```
   
2. Проверьте health endpoint:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   
3. Проверьте синхронизацию:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/community_requests/sync
   ```

## 🔒 Безопасность

### 1. Рекомендации по безопасности
1. **Никогда не коммитьте** credentials файлы в git
2. Используйте `.gitignore`:
   ```gitignore
   *.json
   *.key
   credentials/
   secrets/
   ```
   
3. Ограничьте права сервисного аккаунта:
   - Только необходимые API (Sheets, Drive)
   - Только права на чтение
   - Только к конкретным таблицам/папкам

### 2. Ротация ключей
1. Регулярно обновляйте ключи сервисного аккаунта (каждые 90 дней)
2. Создавайте новый ключ перед удалением старого
3. Обновляйте credentials во всех окружениях

## 🚀 Быстрый старт

### 1. Минимальная настройка
```bash
# 1. Создайте сервисный аккаунт в Google Cloud
# 2. Скачайте credentials.json
# 3. Добавьте в .env:
echo 'GOOGLE_SHEETS_CREDENTIALS='"'"'$(cat udds-service-account-credentials.json | jq -c)'"'"'' >> .env

# 4. Предоставьте доступ к таблицам
# 5. Запустите систему
docker-compose up -d
```

### 2. Проверка работы
```bash
# Проверьте, что сервисный аккаунт имеет доступ
curl http://localhost:8000/api/v1/health

# Запустите тестовую синхронизацию
curl -X POST http://localhost:8000/api/v1/ingest/community_requests/sync

# Проверьте данные
curl http://localhost:8000/api/v1/data/community_requests?page=1&per_page=10
```

## 🛠️ Устранение неполадок

### 1. Ошибка: "Google Sheets service not available"
**Причина**: Неправильные credentials или отсутствие доступа
**Решение**:
1. Проверьте правильность credentials в `.env`
2. Убедитесь, что сервисный аккаунт имеет доступ к таблице
3. Проверьте, что Sheet ID правильный

### 2. Ошибка: "The caller does not have permission"
**Причина**: Недостаточно прав у сервисного аккаунта
**Решение**:
1. Предоставьте доступ к таблице
2. Убедитесь, что email сервисного аккаунта правильный
3. Проверьте, что таблица не в режиме "Private"

### 3. Ошибка: "Request had insufficient authentication scopes"
**Причина**: Неправильные scopes
**Решение**:
1. Убедитесь, что credentials созданы с правильными scopes
2. Проверьте, что включены Google Sheets API и Google Drive API

### 4. Ошибка: "Spreadsheet not found"
**Причина**: Неправильный Sheet ID или таблица удалена
**Решение**:
1. Проверьте Sheet ID в URL таблицы
2. Убедитесь, что таблица существует
3. Проверьте, что сервисный аккаунт имеет к ней доступ

## 📞 Поддержка

### Полезные ссылки:
1. [Google Sheets API Documentation](https://developers.google.com/sheets/api)
2. [Google Cloud Console](https://console.cloud.google.com/)
3. [Service Accounts Documentation](https://cloud.google.com/iam/docs/service-accounts)

### Контакты для помощи:
- Google Cloud Support: https://cloud.google.com/support
- Stack Overflow: Используйте теги `google-sheets-api`, `google-cloud`

Теперь ваша Unified Data Dashboard System готова к работе с реальными Google Sheets таблицами! 🚀