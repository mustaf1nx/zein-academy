# 🦉 Zein Academy — Backend API

Бэкенд платформы управления образовательного центра **Zein Academy**.  
Технологии: **FastAPI** · **SQLAlchemy** · **SQLite / PostgreSQL** · **JWT Auth**

---

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
cp .env.example .env
# Отредактируй .env — измени SECRET_KEY на случайную строку!
```

### 3. Запуск сервера
```bash
uvicorn main:app --reload --port 8000
```

Сервер будет доступен на: `http://localhost:8000`  
Документация (Swagger UI): `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 🔐 Авторизация

Используется **JWT Bearer Token**.

### Дефолтный аккаунт (создаётся при первом запуске)
| ИИН | Пароль | Роль |
|---|---|---|
| `900101350123` | `zein2024` | admin |

### Вход
```http
POST /api/auth/login
Content-Type: application/json

{
  "iin": "900101350123",
  "password": "zein2024"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "full_name": "Администратор",
  "user_id": 1
}
```

Добавляй токен в заголовок всех запросов:
```
Authorization: Bearer eyJ...
```

---

## 👥 Роли

| Роль | Описание |
|---|---|
| `admin` | Полный доступ ко всем функциям |
| `teacher` | Видит только свои группы, сохраняет посещаемость |
| `mentor` | Курирует учеников |
| `manager` | Работает с формами и записью |
| `lidoruby` | Лидо-Руби сотрудники |

---

## 📋 API Эндпоинты

### Авторизация
| Метод | URL | Описание |
|---|---|---|
| POST | `/api/auth/login` | Вход по ИИН + пароль |
| GET | `/api/auth/me` | Данные текущего пользователя |

### Пользователи / Персонал
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/users/` | Список всех сотрудников (фильтр по `role`) |
| POST | `/api/users/` | Создать сотрудника |
| GET | `/api/users/{id}` | Профиль сотрудника |
| PUT | `/api/users/{id}` | Обновить профиль |
| DELETE | `/api/users/{id}` | Удалить сотрудника |

### Ученики
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/students/` | Список (фильтры: `search`, `grade`, `language`, `status`, `branch`) |
| POST | `/api/students/` | Добавить ученика |
| GET | `/api/students/{id}` | Карточка ученика |
| PUT | `/api/students/{id}` | Обновить данные |
| DELETE | `/api/students/{id}` | Удалить |

### Группы
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/groups/` | Список групп |
| POST | `/api/groups/` | Создать группу |
| GET | `/api/groups/{id}` | Данные группы |
| PUT | `/api/groups/{id}` | Обновить группу |
| DELETE | `/api/groups/{id}` | Удалить |
| GET | `/api/groups/{id}/students` | Ученики в группе |
| POST | `/api/groups/{id}/students/{sid}` | Добавить ученика в группу |
| DELETE | `/api/groups/{id}/students/{sid}` | Убрать ученика |
| POST | `/api/groups/{id}/schedule` | Добавить слот расписания |
| DELETE | `/api/groups/schedule/{slot_id}` | Удалить слот |

### Кабинеты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/classrooms/` | Список кабинетов |
| POST | `/api/classrooms/` | Создать |
| PUT | `/api/classrooms/{id}` | Обновить |
| DELETE | `/api/classrooms/{id}` | Удалить |

### Посещаемость
| Метод | URL | Описание |
|---|---|---|
| POST | `/api/attendance/` | Сохранить отчёт за день |
| GET | `/api/attendance/?group_id=X` | Записи посещаемости |
| GET | `/api/attendance/summary/{group_id}` | Статистика по ученикам |

**Пример сохранения отчёта:**
```json
POST /api/attendance/
{
  "group_id": 1,
  "date": "2024-04-10",
  "records": [
    {"student_id": 1, "status": "present", "score_1": 8.5, "score_2": 9},
    {"student_id": 2, "status": "absent"}
  ]
}
```

### Задачи
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/tasks/` | Все задачи (для учителя — только свои) |
| POST | `/api/tasks/` | Создать задачу |
| PUT | `/api/tasks/{id}` | Обновить / изменить статус |
| DELETE | `/api/tasks/{id}` | Удалить |

### Возвраты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/returns/` | Список возвратов |
| POST | `/api/returns/` | Добавить запись о возврате |

### История форм (Запись)
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/forms/` | Список форм записи |
| POST | `/api/forms/` | Создать форму |

### ENT-тесты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/ent/` | Список тестов |
| POST | `/api/ent/` | Создать тест |
| PUT | `/api/ent/{id}` | Обновить |
| DELETE | `/api/ent/{id}` | Удалить |

### Запрещённые даты
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/forbidden-dates/` | Список дат |
| POST | `/api/forbidden-dates/` | Добавить дату |
| DELETE | `/api/forbidden-dates/{id}` | Удалить |

### Менторы
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/mentors/assignments` | Назначения ментор→ученик |
| POST | `/api/mentors/assignments` | Назначить ментора |
| DELETE | `/api/mentors/assignments/{id}` | Снять назначение |

### Аналитика
| Метод | URL | Описание |
|---|---|---|
| GET | `/api/analytics/summary` | Общая статистика |
| GET | `/api/analytics/slots` | Заполненность групп |
| GET | `/api/analytics/group-size-distribution` | Распределение групп по размеру |

---

## 🗄️ Переключение на PostgreSQL

В файле `.env` измени:
```
DATABASE_URL=postgresql://user:password@localhost:5432/zein_db
```

И установи драйвер:
```bash
pip install psycopg2-binary
```

---

## 📁 Структура проекта

```
zein_backend/
├── main.py              ← Точка входа, FastAPI app
├── database.py          ← Подключение к БД
├── models.py            ← Модели SQLAlchemy (таблицы)
├── schemas.py           ← Pydantic схемы (валидация)
├── auth.py              ← JWT + bcrypt утилиты
├── dependencies.py      ← Зависимости (current_user, role checks)
├── routers/
│   ├── auth.py          ← Авторизация
│   ├── users.py         ← Персонал
│   ├── students.py      ← Ученики
│   ├── groups.py        ← Группы + расписание
│   ├── classrooms.py    ← Кабинеты
│   ├── attendance.py    ← Посещаемость
│   └── extra.py         ← Задачи, возвраты, формы, ENT,
│                           запрещённые даты, менторы, аналитика
├── requirements.txt
├── .env.example
└── README.md
```
