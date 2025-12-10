# Настройка Google Sheets API

## Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите "Создать проект" или выберите существующий
3. Дайте проекту имя (например, "UDDS Data Sync")
4. Запомните Project ID

## Шаг 2: Включение Google Sheets API

1. В меню слева выберите "APIs & Services" → "Library"
2. Найдите "Google Sheets API"
3. Нажмите "Enable"

## Шаг 3: Создание сервисного аккаунта

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "Service Account"
3. Заполните:
   - Service account name: `udds-sync`
   - Service account ID: `udds-sync@ваш-project-id.iam.gserviceaccount.com`
   - Description: "Service account for Unified Data Dashboard System"
4. Нажмите "Create and Continue"
5. Пропустите шаг с ролями (нажмите "Continue")
6. Нажмите "Done"

## Шаг 4: Создание ключа доступа

1. В списке сервисных аккаунтов найдите созданный аккаунт
2. Нажмите на email аккаунта
3. Перейдите на вкладку "Keys"
4. Нажмите "Add Key" → "Create new key"
5. Выберите формат JSON
6. Нажмите "Create"
7. Файл `credentials.json` автоматически скачается

## Шаг 5: Настройка доступа к Google Sheets

1. Откройте ваш Google Sheet
2. Нажмите "Share" (Поделиться)
3. В поле "Add people and groups" введите email сервисного аккаунта
   (например: `udds-sync@ваш-project-id.iam.gserviceaccount.com`)
4. Выберите роль "Editor" (Редактор)
5. Нажмите "Send"

## Шаг 6: Настройка в UDDS

1. Поместите скачанный `credentials.json` в папку проекта:
   ```bash
   cp ~/Downloads/credentials.json /workspace/unified-data-dashboard/
   ```

2. Обновите `.env` файл:
   ```bash
   nano /workspace/unified-data-dashboard/.env
   ```

3. Добавьте или обновите переменную:
   ```
   GOOGLE_SHEETS_CREDENTIALS=$(cat credentials.json)
   ```

4. Обновите `datasets.json` с вашими Sheet ID:
   ```json
   {
     "datasets": [
       {
         "id": "community_requests",
         "sheet_id": "ВАШ_SHEET_ID_ЗДЕСЬ",
         "sheet_name": "Лист1"
       }
     ]
   }
   ```

## Как найти Sheet ID

1. Откройте ваш Google Sheet
2. Посмотрите в адресной строке браузера:
   ```
   https://docs.google.com/spreadsheets/d/ВАШ_SHEET_ID_ЗДЕСЬ/edit#gid=0
   ```
   Часть между `/d/` и `/edit` - это ваш Sheet ID

## Тестирование подключения

1. Запустите проект:
   ```bash
   ./start.sh
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs -f backend
   ```

3. Должны появиться сообщения о успешной загрузке данных

## Устранение неполадок

### Ошибка: "The caller does not have permission"
- Убедитесь, что сервисный аккаунт добавлен как редактор в Google Sheet
- Проверьте, что Sheet ID указан правильно

### Ошибка: "Invalid credentials"
- Убедитесь, что `credentials.json` файл корректный
- Проверьте, что переменная `GOOGLE_SHEETS_CREDENTIALS` правильно установлена

### Ошибка: "API not enabled"
- Убедитесь, что Google Sheets API включен в Google Cloud Console

## Безопасность

⚠️ **ВАЖНО**: Никогда не коммитьте `credentials.json` в git!

1. Добавьте в `.gitignore`:
   ```
   credentials.json
   *.json
   !datasets.json
   !reports.json
   ```

2. Используйте переменные окружения для хранения чувствительных данных
3. Регулярно обновляйте ключи доступа
4. Используйте разные сервисные аккаунты для разных окружений (dev/staging/prod)