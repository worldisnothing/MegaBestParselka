import argparse
import ctypes
import os
import platform
import sys
from datetime import datetime

from settings import ALLOWED_REPORTS


def check_args(args):
    """
    Проверка аргументов.
    Проверяет, что файлы по переданному пути существуют.
    Проверяет, что тип отчета соответствует average.
    Проверяет, что дата правильная и существует

    :param args: аргументы командной строки
    """
    # Проверка на существование файлов
    missing = [f for f in args.files if not os.path.exists(f)]
    if missing:
        print(f"Файл(-ы) не существуют: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    # Проверка на тип отчета
    if args.report not in ALLOWED_REPORTS:
        print(f"Отчет типа '{args.report}' не поддерживается.", file=sys.stderr)
        sys.exit(1)

    # Проверка на дату
    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Неверная дата: {args.date}", file=sys.stderr)
            sys.exit(1)


def parse_args():
    """
    Парсинг и проверка аргументов командной строки. Ожидает аргументы file и report.

    :return: аргументы командной строки
    """
    parser = argparse.ArgumentParser(description="Генератор отчета по логам")
    parser.add_argument('--files', type=str, nargs='+', required=True, help='Путь до лога(-ов)')
    parser.add_argument('--report', type=str, choices=ALLOWED_REPORTS, required=True, help='Тип отчета')
    parser.add_argument('--date', type=str, help='Дата в формате YYYY-MM-DD (фильтрация по дате)')

    args = parser.parse_args()
    check_args(args)

    return args


def get_free_memory_bytes_linux():
    """
    Определяет доступное количество ОЗУ на ОС Linux

    :return: количество доступной ОЗУ в байтах
    """
    try:
        with open("/proc/meminfo", "r") as meminfo:
            for line in meminfo:
                if line.startswith("MemAvailable:"):
                    parts = line.split()
                    return int(parts[1]) * 1024
    except Exception:
        pass
    return None


def get_free_memory_bytes_windows():
    """
    Определяет доступное количество ОЗУ на ОС Windows

    :return: количество доступной ОЗУ в байтах
    """
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        return mem.ullAvailPhys
    except Exception:
        return None


def get_available_memory_bytes():
    """
    Определяет доступное количество ОЗУ для текущей ОС

    :return: количество доступной ОЗУ в байтах
    """
    system = platform.system()
    if system == "Linux":
        return get_free_memory_bytes_linux()
    elif system == "Windows":
        return get_free_memory_bytes_windows()
    return None
