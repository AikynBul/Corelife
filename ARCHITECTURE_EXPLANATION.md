# 📚 Объяснение архитектуры проекта "AI Calendar"

> **Для начинающих программистов** — простыми словами с примерами

---

## 🗂️ 1. СТРУКТУРА ПРОЕКТА (Какой файл за что отвечает)

### 📁 Корневая структура:
```
Corelife COR/
├── src/                    # Основной код приложения
│   ├── main.py            # 🚀 ТОЧКА ВХОДА - запускает всё приложение
│   ├── components/         # 🎨 UI компоненты (интерфейс)
│   ├── services/           # ⚙️ Сервисы (AI, авторизация)
│   ├── data/              # 💾 Работа с данными (база данных)
│   └── utils/             # 🛠️ Вспомогательные функции
├── .env                   # 🔐 Секретные ключи (API ключи, пароли)
└── requirements.txt       # 📦 Список библиотек Python
```

### 📄 Основные файлы и их роли:

#### **`src/main.py`** — Главный файл приложения
**Что делает:** Это "дирижёр оркестра" — запускает всё приложение и управляет переключением между экранами.

**Пример работы:**
```python
# Когда пользователь входит в систему:
def on_login(user_info):
    store.set_user(user_info["id"])  # Сохраняем ID пользователя
    show_app(user_info)              # Показываем главный экран
```

**Ответственность:**
- ✅ Показывает экран входа (`LoginView`)
- ✅ После входа показывает главный экран (`AppLayout`)
- ✅ Управляет темой (светлая/тёмная)
- ✅ Управляет языком интерфейса

---

#### **`src/components/`** — Компоненты интерфейса

**`layout.py`** — Главный макет приложения
- Содержит боковую панель (sidebar) и область контента
- Переключает виды: Месяц, Неделя, День, Аккаунт

**`chat.py`** — AI чат-виджет
- Плавающая кнопка чата в правом нижнем углу
- Обрабатывает команды пользователя (например, "встреча завтра в 14:00")
- **ВАЖНО:** Сейчас использует простой парсинг, НЕ использует AI сервис

**`calendar.py`** — Календарь (месячный вид)
- Показывает сетку календаря
- Отображает события на датах
- Обрабатывает клики по дням

**`event_dialog.py`** — Диалог создания события
- Форма для создания нового события/задачи
- Поля: название, дата, время, описание, повторение

**`event_details_dialog.py`** — Диалог просмотра/удаления события
- Показывает детали события
- Кнопка "Delete" для удаления

**`header.py`** — Верхняя панель
- Кнопки: Поиск, Помощь, Переключение темы, Настройки
- Аватар пользователя

**`sidebar.py`** — Боковая панель
- Кнопка "Создать" событие
- Переключение видов (Месяц/Неделя/День)
- Мини-календарь
- Фильтры (События/Задачи)

---

#### **`src/services/`** — Сервисы

**`ai_service.py`** — Сервис AI (Google Gemini)
**Что делает:** Использует Google Gemini API для понимания команд пользователя.

**Пример:**
```python
# Пользователь пишет: "Встреча с Иваном завтра в 15:00"
ai_service.process_message("Встреча с Иваном завтра в 15:00")
# Возвращает JSON:
{
    "action": "create",
    "type": "event",
    "title": "Встреча с Иваном",
    "start": "2026-01-29 15:00",
    "end": "2026-01-29 16:00",
    ...
}
```

**⚠️ ВАЖНО:** Этот сервис создан, но **НЕ используется** в `chat.py`! Вместо него используется простой парсинг.

**`auth_service.py`** — Сервис авторизации
- Регистрация пользователей
- Вход в систему (логин)
- Хранение паролей (хеширование SHA-256)
- Работа с MongoDB для хранения пользователей

---

#### **`src/data/store.py`** — Хранилище данных
**Что делает:** Работает с MongoDB — сохраняет и получает события/задачи.

**Основные функции:**
- `add_event()` — создать событие
- `update_event()` — обновить событие
- `delete_event()` — удалить событие
- `get_events_for_month()` — получить события за месяц

**Пример:**
```python
# Создать событие
store.add_event(
    title="Встреча с командой",
    start_date="2026-01-29 14:00",
    end_date="2026-01-29 15:00",
    description="Обсуждение проекта",
    event_type="event"
)
```

---

## 🤖 2. ЛОГИКА AI ЧАТА (Обработка команд)

### 📍 Где находится: `src/components/chat.py`

### 🔍 Как работает сейчас:

**Функция `process_command()`** (строки 110-174) — обрабатывает команды пользователя.

**Что она делает:**
1. **Парсит текст** — ищет ключевые слова:
   - "tomorrow" → завтра
   - "today" → сегодня
   - "next week" → через неделю
   - "at 14" → время 14:00

2. **Извлекает данные:**
   ```python
   # Пример: "Встреча завтра в 14"
   lower_text = "встреча завтра в 14"
   
   if "tomorrow" in lower_text:
       target_date += timedelta(days=1)  # +1 день
       title = "встреча"
   
   time_match = re.search(r"at (\d+)", lower_text)
   hour = 14  # Нашли "14"
   ```

3. **Создаёт событие:**
   ```python
   store.add_event(
       title="Встреча",
       start_date="2026-01-29 14:00",
       ...
   )
   ```

### ⚠️ ПРОБЛЕМА:
**Сейчас чат НЕ умеет:**
- ❌ Удалять события (команды типа "удали встречу")
- ❌ Редактировать события
- ❌ Использовать AI сервис (`AIService`) — используется простой парсинг

**Что нужно добавить:**
- Использовать `AIService` для понимания команд
- Обрабатывать команды "delete", "remove", "edit"
- Искать события по названию для удаления

---

## 💾 3. ГДЕ ХРАНЯТСЯ ВСТРЕЧИ/МИТИНГИ

### 📍 Хранилище: **MongoDB** (облачная база данных)

**Файл:** `src/data/store.py`

### 🔌 Подключение:
```python
# В .env файле:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

### 📊 Структура данных:

**База данных:** `ai_calendar_db`
**Коллекция:** `events` (таблица событий)

**Пример документа в MongoDB:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "user_id": "507f191e810c19729de860ea",
  "title": "Встреча с командой",
  "start": "2026-01-29 14:00",
  "end": "2026-01-29 15:00",
  "description": "Обсуждение проекта",
  "type": "event",  // или "task"
  "recurrence": null,  // или "daily", "weekly", "monthly"
  "priority": "Medium",
  "completed": false,
  "created_at": "2026-01-28T10:30:00"
}
```

### 🔐 Безопасность:
- Каждый пользователь видит только свои события (`user_id`)
- При удалении проверяется, что событие принадлежит пользователю

---

## 🎨 4. СИСТЕМА ТЕМ (Светлая/Тёмная)

### 📍 Где находится: `src/components/header.py`

### 🔧 Как работает:

**Функция `toggle_theme()`** (строки 41-47 в `header.py`):

```python
def toggle_theme(self, e):
    e.control.selected = not e.control.selected
    # Переключаем тему
    self.page_ref.theme_mode = ft.ThemeMode.DARK if e.control.selected else ft.ThemeMode.LIGHT
    self.page_ref.update()
```

### 🎯 Где применяется:

1. **В `main.py`** (строка 11):
   ```python
   page.theme_mode = ft.ThemeMode.LIGHT  # По умолчанию светлая
   ```

2. **В `header.py`** (строки 18-23):
   - Кнопка с иконкой 🌙/☀️
   - При клике вызывается `toggle_theme()`

3. **Автоматически применяется:**
   - Flet (библиотека UI) автоматически меняет цвета всех компонентов
   - Например, в `calendar.py` (строка 98):
     ```python
     bgcolor=ft.Colors.SURFACE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_50
     ```

### 💡 Как это работает:
- Flet имеет встроенную систему тем
- При изменении `page.theme_mode` все компоненты автоматически перерисовываются
- Цвета берутся из темы (например, `ft.Colors.SURFACE` — разный цвет в светлой/тёмной теме)

---

## ⚙️ 5. ФУНКЦИИ ДЛЯ РАБОТЫ С МИТИНГАМИ

### ✅ 5.1. Создание митингов

**Файл:** `src/data/store.py`  
**Функция:** `add_event()` (строки 32-55)

```python
def add_event(self, title, start_date, end_date, description, 
              event_type="event", recurrence=None, priority="Medium", completed=False):
    new_event = {
        "user_id": self.user_id,
        "title": title,
        "start": start_date,
        "end": end_date,
        "description": description,
        "type": event_type,  # "event" или "task"
        "recurrence": recurrence,  # "daily", "weekly", "monthly", "yearly"
        "priority": priority,
        "completed": completed,
        "created_at": datetime.now()
    }
    result = self.collection.insert_one(new_event)
    return new_event
```

**Где вызывается:**
1. **`src/components/event_dialog.py`** (строка 123) — при создании через форму
2. **`src/components/chat.py`** (строка 156) — при создании через AI чат

**Пример использования:**
```python
store.add_event(
    title="Встреча с командой",
    start_date="2026-01-29 14:00",
    end_date="2026-01-29 15:00",
    description="Обсуждение проекта",
    event_type="event"
)
```

---

### ✏️ 5.2. Редактирование митингов

**Файл:** `src/data/store.py`  
**Функция:** `update_event()` (строки 57-71)

```python
def update_event(self, event_id, updates):
    # updates - словарь с полями для обновления
    # Например: {"title": "Новое название", "description": "Новое описание"}
    result = self.collection.update_one(
        {"_id": ObjectId(event_id), "user_id": self.user_id},
        {"$set": updates}
    )
    return result.modified_count > 0
```

**⚠️ ВАЖНО:** 
- Функция есть, но **НЕ используется** в UI!
- В `event_details_dialog.py` нет кнопки "Edit"
- Нужно добавить форму редактирования

**Пример использования:**
```python
store.update_event(
    event_id="507f1f77bcf86cd799439011",
    updates={"title": "Новое название встречи"}
)
```

---

### 🗑️ 5.3. Удаление митингов

**Файл:** `src/data/store.py`  
**Функция:** `delete_event()` (строки 73-81)

```python
def delete_event(self, event_id):
    self.collection.delete_one(
        {"_id": ObjectId(event_id), "user_id": self.user_id}
    )
```

**Где вызывается:**
- **`src/components/event_details_dialog.py`** (строка 30) — при клике на кнопку "Delete"

**Пример использования:**
```python
# Пользователь кликает на событие → открывается диалог
# В диалоге нажимает "Delete"
store.delete_event(event["id"])
```

**Как это работает:**
1. Пользователь кликает на событие в календаре
2. Открывается `EventDetailsDialog`
3. Нажимает кнопку "Delete"
4. Вызывается `store.delete_event(event_id)`
5. Событие удаляется из MongoDB
6. Календарь обновляется (`refresh_calendar()`)

---

### 🧠 5.4. Парсинг команд пользователя

**Файл:** `src/components/chat.py`  
**Функция:** `process_command()` (строки 110-174)

**Что делает:**
1. **Парсит дату:**
   ```python
   if "tomorrow" in lower_text:
       target_date += timedelta(days=1)
   elif "today" in lower_text:
       target_date = datetime.now()
   elif "in" in lower_text and "days" in lower_text:
       days_match = re.search(r"in (\d+) days", lower_text)
       days = int(days_match.group(1))
       target_date += timedelta(days=days)
   ```

2. **Парсит время:**
   ```python
   time_match = re.search(r"at (\d+)", lower_text)
   if time_match:
       hour = int(time_match.group(1))
   ```

3. **Извлекает название:**
   ```python
   title = lower_text.split("tomorrow")[0].strip()
   title = title.replace("schedule", "").replace("add", "").strip()
   ```

4. **Определяет тип:**
   ```python
   event_type = "task" if "remind" in lower_text or "task" in lower_text else "event"
   ```

**Примеры команд:**
- ✅ "Встреча завтра в 14" → создаёт событие на завтра в 14:00
- ✅ "Задача через 3 дня" → создаёт задачу через 3 дня
- ❌ "Удали встречу" → **НЕ РАБОТАЕТ** (нет обработки удаления)
- ❌ "Измени встречу" → **НЕ РАБОТАЕТ** (нет обработки редактирования)

---

## 🔄 ПОТОК ДАННЫХ (Как всё работает вместе)

### Пример: Пользователь создаёт событие через чат

```
1. Пользователь пишет: "Встреча завтра в 14"
   ↓
2. chat.py → send_message() → process_command()
   ↓
3. process_command() парсит текст:
   - "завтра" → +1 день
   - "в 14" → 14:00
   - "Встреча" → название
   ↓
4. store.add_event() → сохраняет в MongoDB
   ↓
5. chat.add_message() → показывает ответ пользователю
   ↓
6. on_refresh() → обновляет календарь
   ↓
7. calendar.render_calendar() → показывает новое событие
```

### Пример: Пользователь удаляет событие

```
1. Пользователь кликает на событие в календаре
   ↓
2. calendar.py → open_event_details(event)
   ↓
3. EventDetailsDialog открывается
   ↓
4. Пользователь нажимает "Delete"
   ↓
5. event_details_dialog.py → delete_event()
   ↓
6. store.delete_event(event_id) → удаляет из MongoDB
   ↓
7. refresh_calendar() → обновляет календарь
```

---

## 🎯 ИТОГОВАЯ СХЕМА

```
┌─────────────────────────────────────────────────┐
│              main.py (Точка входа)              │
│  - Показывает LoginView → AppLayout             │
│  - Управляет темой и языком                     │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────┐
│  AppLayout  │  │   ChatWidget    │
│  (layout.py)│  │   (chat.py)     │
│             │  │                 │
│ ┌─────────┐ │  │ process_command()│
│ │ Sidebar │ │  │  (парсинг)      │
│ └─────────┘ │  └────────┬─────────┘
│             │           │
│ ┌─────────┐ │           │
│ │ Calendar│ │           │
│ │ (views) │ │           │
│ └────┬────┘ │           │
└──────┼──────┘           │
       │                  │
       └────────┬─────────┘
                │
        ┌───────▼────────┐
        │  store.py      │
        │  (MongoDB)     │
        │                │
        │  add_event()   │
        │  update_event()│
        │  delete_event()│
        └────────────────┘
```

---

## 📝 ЧТО НУЖНО ДОБАВИТЬ (TODO)

1. **Использовать AI сервис в чате:**
   - Сейчас `AIService` создан, но не используется
   - Нужно заменить простой парсинг на `ai_service.process_message()`

2. **Добавить удаление через чат:**
   - Обработка команд "удали встречу", "remove meeting"
   - Поиск события по названию
   - Вызов `store.delete_event()`

3. **Добавить редактирование:**
   - Кнопка "Edit" в `EventDetailsDialog`
   - Форма редактирования
   - Вызов `store.update_event()`

4. **Улучшить парсинг:**
   - Поддержка больше форматов дат
   - Распознавание названий событий для удаления

---

## 🎓 КЛЮЧЕВЫЕ ПОНЯТИЯ

- **MongoDB** — база данных (облачная, как Google Drive для данных)
- **Flet** — библиотека для создания UI (интерфейса)
- **Component** — компонент (часть интерфейса, например, кнопка или форма)
- **Service** — сервис (логика работы, не UI)
- **Store** — хранилище (работа с данными)
- **Dialog** — диалоговое окно (всплывающее окно)

---

*Создано: 28 января 2026*
