import json
from collections import defaultdict
from itertools import chain

from tabulate import tabulate

from settings import LOG_ENCODING, CHUNK_SIZE_DEFAULT, ALLOWED_MEM
from util_funcs import parse_args, get_available_memory_bytes


def read_logs(file_path):
    """
    Читает содержимое файла и возвращает генератор JSON-строк

    :param file_path: путь к файлам
    :return: генератор JSON-строк
    """
    available_mem = get_available_memory_bytes()
    if available_mem is None:
        chunk_size = CHUNK_SIZE_DEFAULT
    else:
        chunk_size = int(available_mem * ALLOWED_MEM)
        chunk_size = max(CHUNK_SIZE_DEFAULT, min(chunk_size, 100 * CHUNK_SIZE_DEFAULT))

    with open(file_path, 'r', encoding=LOG_ENCODING) as f:
        buffer = []
        buffer_size = 0
        for line in f:
            if not line.strip():
                continue
            buffer.append(line)
            buffer_size += len(line.encode(LOG_ENCODING))  # суммирует размер строки в байтах

            if buffer_size >= chunk_size:
                for json_line in buffer:
                    try:
                        yield json.loads(json_line)
                    except json.JSONDecodeError:
                        continue
                buffer.clear()
                buffer_size = 0

        # Обработка оставшихся строк
        for json_line in buffer:
            try:
                yield json.loads(json_line)
            except json.JSONDecodeError:
                continue


def generate_average_report(log_lines, filter_date=None):
    """
    Генерирует отчет и выводит его в консоль

    :param log_lines: строки из JSON логов
    """
    stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})

    for entry in log_lines:
        # проверка даты
        if filter_date:
            log_date = entry.get('@timestamp')
            if not log_date.startswith(filter_date):
                continue

        url = entry.get('url')
        response_time = entry.get('response_time')

        if url is not None and response_time is not None:
            stats[url]['count'] += 1
            stats[url]['total_time'] += response_time

    report_data = []
    for url, data in stats.items():
        avg_time = data['total_time'] / data['count']
        report_data.append([url, data['count'], round(avg_time, 3)])

    report_data.sort(key=lambda x: x[1], reverse=True)  # сортировка по числу запросов

    # добавление колонки с нумерацией строк после сортировки
    col_num = 0
    for data in report_data:
        data.insert(0, col_num)
        col_num += 1

    return tabulate(report_data, headers=["", "handler", "total", "avg_response_time"])


def main():
    args = parse_args()

    # Чтение логов из всех файлов в один через генератор (lazy, не использует всю память сразу)
    log_lines = chain.from_iterable(read_logs(file_path) for file_path in args.files)

    # Генерация отчета
    report = generate_average_report(log_lines, filter_date=args.date)
    print(report)

if __name__ == '__main__':
    main()
