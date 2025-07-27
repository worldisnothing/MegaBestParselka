# Скрипт для обработки лог-файлов

Python скрипт для обработки, анализа и форматированного отчета по лог файлам

## Возможности

- Обработка **больших** файлов лога
- Поддержка JSON формата лога
- Вычисление среднего времени ответа по каждому Endpoint
- Фильтр по дате записи лога
- Кросс-платформенность (Windows/Linux)
- Адаптивное использование оперативной памяти (Windows/Linux)

## Установка

1. Скопируйте репозиторий:
```bash
git clone https://github.com/worldisnothing/MegaBestParselka.git
cd MegaBestParselka
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

Базовый вариант (без фильтра по дате):
```bash
python main.py --file example1.log example2.log --report average
```

Продвинутый вариант (с фильтром по дате):
```bash
python main.py --file example1.log --report average --date 2025-06-22
```

### Аргументы командной строки

| Аргумент | Описание | Обязательно? |
|----------|-------------|----------|
| `--file` | Путь до файла лога(-ов) | Да |
| `--report` | Тип отчета (поддержан только 'average') | Да |
| `--date` | Фильтр записей лога по дате (YYYY-MM-DD формат) | Нет |

## Пример отчета

```
        handler                total  avg_response_time
------  -------------------  -------  -----------------
     0  /api/homeworks/...       50              0.132
     1  /api/context/...         20              0.028
     2  /api/specializati...     10              0.032
```

## Формат файла лога

Минимально записи JSON лога должны содержать следующий поля:
- `@timestamp`: Timestamp in ISO format
- `url`: Request URL
- `response_time`: Response time in seconds

Пример JSON строки лога:
```json
{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024}
```
