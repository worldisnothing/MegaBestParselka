import pytest
import argparse
from unittest.mock import patch, mock_open
from main import main, generate_average_report, read_logs
from util_funcs import check_args, parse_args


def test_check_args_with_valid_args():
    """
    Тест проверки корректных аргументов

    Не должно быть исключений
    """
    args = argparse.Namespace(
        files=['existing_file.log'],
        report='average',
        date='2025-06-22'
    )

    with patch('os.path.exists', return_value=True):
        check_args(args)


def test_check_args_with_missing_file():
    """
    Тест проверки отсутствующих файлов

    Ошибка, файл отсутствует, выход из программы
    """
    args = argparse.Namespace(
        files=['missing_file.log'],
        report='average',
        date=None
    )

    with patch('os.path.exists', return_value=False):
        with pytest.raises(SystemExit):
            check_args(args)


def test_check_args_with_invalid_report():
    """
    Тест проверки недопустимого типа отчета

    Ошибка, недопустимый тип отчета, выход из программы
    """
    args = argparse.Namespace(
        files=['existing_file.log'],
        report='invalid_report',
        date=None
    )

    with patch('os.path.exists', return_value=True):
        with pytest.raises(SystemExit):
            check_args(args)


def test_check_args_with_invalid_date():
    """
    Тест проверки неверного формата даты

    Ошибка, неверный формат даты, выход из программы
    """
    args = argparse.Namespace(
        files=['existing_file.log'],
        report='average',
        date='2025-14-22'  # Неверный месяц
    )

    with patch('os.path.exists', return_value=True):
        with pytest.raises(SystemExit):
            check_args(args)


def test_parse_args_valid():
    """
    Тест парсинга корректных аргументов

    Ожидаем, что все ок
    """
    test_args = [
        '--files', 'file1.log', 'file2.log',
        '--report', 'average',
        '--date', '2025-06-22'
    ]

    with patch('sys.argv', ['main.py'] + test_args):
        with patch('os.path.exists', return_value=True):
            args = parse_args()
            assert args.files == ['file1.log', 'file2.log']
            assert args.report == 'average'
            assert args.date == '2025-06-22'


def test_parse_args_missing_required():
    """
    Тест парсинга без обязательных аргументов

    Ожидаем выход из программы
    """
    with patch('sys.argv', ['main.py']):
        with pytest.raises(SystemExit):
            parse_args()


def test_generate_average_report_without_date_filter():
    """
    Тест функции генерации отчета без фильтрации по дате

    В отчет попадут все записи
    """
    test_logs = [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.02},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/homeworks", "response_time": 0.06},
        {"@timestamp": "2025-06-23T13:57:32+00:00", "url": "/api/homeworks", "response_time": 0.04},
    ]

    report = generate_average_report(test_logs)

    # Проверяем, что отчет содержит ожидаемые данные
    assert "/api/context" in report
    assert "/api/homeworks" in report
    assert "2" in report  # количество запросов для /api/context
    assert "2" in report  # количество запросов для /api/homeworks


def test_generate_average_report_with_date_filter():
    """
    Тест функции генерации отчета с фильтрацией по дате

    В отчет попадет только 2 записи за 2025-06-22
    """
    test_logs = [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.02},
        {"@timestamp": "2025-06-23T13:57:32+00:00", "url": "/api/homeworks", "response_time": 0.04},
    ]

    report = generate_average_report(test_logs, filter_date="2025-06-22")

    # Проверяем, что отчет содержит только записи за указанную дату
    assert "/api/context" in report
    assert "/api/homeworks" not in report
    assert "2" in report  # количество запросов для /api/context


def test_generate_average_report_with_missing_fields():
    """
    Тест генерации отчета с записями, в которых отсутствуют необходимые поля

    Попадет в отчет только 1 запись
    """
    test_logs = [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context"},  # нет response_time
        {"@timestamp": "2025-06-22T13:57:32+00:00", "response_time": 0.04},  # нет url
    ]

    report = generate_average_report(test_logs)

    # Проверяем, что в отчет попала только первая запись
    assert "/api/context" in report
    assert "1" in report


def test_read_logs_with_valid_json():
    """
    Тест чтения логов с валидным JSON

    Ожидаем, что все строки корректны и аргументы правильно считались
    """
    test_data = """{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024}
{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/homeworks", "response_time": 0.06}"""

    with patch('builtins.open', mock_open(read_data=test_data)):
        logs = list(read_logs('test.log'))
        assert len(logs) == 2
        assert logs[0]['@timestamp'] == "2025-06-22T13:57:32+00:00"
        assert logs[0]['url'] == "/api/context"
        assert logs[0]['response_time'] == 0.024

        assert logs[1]['@timestamp'] == "2025-06-22T13:57:32+00:00"
        assert logs[1]['url'] == "/api/homeworks"
        assert logs[1]['response_time'] == 0.06


def test_read_logs_with_invalid_json():
    """
    Тест чтения логов с невалидным JSON

    Ожидаем, что считалось только 2 строки из 3 - одна некорректная
    """
    test_data = """{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024}
invalid json
{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/homeworks", "response_time": 0.06}"""

    with patch('builtins.open', mock_open(read_data=test_data)):
        logs = list(read_logs('test.log'))
        assert len(logs) == 2  # одна строка пропущена из-за ошибки JSON


def test_main_with_sample_data(capsys):
    """
    Тест основной функции с примером данных
    """
    test_args = [
        'main.py',
        '--files', 'example1.log',
        '--report', 'average'
    ]

    # Мокируем sys.argv и открытие файла
    with patch('sys.argv', test_args):
        with patch('builtins.open', mock_open(read_data="""{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.024}
{"@timestamp": "2025-06-22T13:57:32+00:00", "url": "/api/context", "response_time": 0.02}""")):
            with patch('os.path.exists', return_value=True):
                main()

    captured = capsys.readouterr()
    assert "/api/context" in captured.out
    assert "2" in captured.out  # количество запросов
    assert "0.022" in captured.out  # среднее время
