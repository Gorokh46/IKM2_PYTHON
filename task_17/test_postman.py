import os
import sys
import tempfile
from datetime import datetime

# Импортируем классы и функции из основной программы
from main import (
    Tree, Nest, PostmanSolver,
    build_tree_from_lines, read_tree_from_file
)


  
# Класс для ведения отчёта (вывод в консоль + запись в файл)
class TestReporter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, 'w', encoding='utf-8')
        self.test_counter = 0  # сквозная нумерация тестов

        # Шапка отчёта
        self.log("=" * 70)
        self.log("  ОТЧЁТ О ТЕСТИРОВАНИИ ПРОЕКТА 'ПОЧТАЛЬОН'")
        self.log(f"  Дата и время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        self.log("=" * 70)
        self.log()

    def log(self, text=""):
        print(text)
        self.file.write(text + '\n')

    def log_group_header(self, group_name):
        self.log()
        self.log("─" * 70)
        self.log(f"  ГРУППА: {group_name}")
        self.log("─" * 70)

    def log_test_result(self, name, input_data, expected, actual, passed, error=None):
        self.test_counter += 1

        # Определяем статус
        if error is not None:
            status = f"✗ ОШИБКА: {error}"
        elif passed:
            status = "✓ ПРОЙДЕН"
        else:
            status = "✗ ПРОВАЛ"

        # Формируем карточку теста
        self.log("┌" + "─" * 68 + "┐")
        self.log(f"│ № теста      : {self.test_counter}")
        self.log(f"│ Название     : {name}")
        self.log(f"│ Что вводится : {input_data}")
        self.log(f"│ Ожидается    : {expected}")
        self.log(f"│ Выведено     : {actual}")
        self.log(f"│ Результат    : {status}")
        self.log("└" + "─" * 68 + "┘")

    def log_group_summary(self, group_name, passed, total):
        self.log()
        self.log(f"  >>> Итого по группе '{group_name}': {passed}/{total}")
        self.log()

    def close(self):
        self.file.close()


  
# Вспомогательные функции
def format_input_lines(lines):
    if not lines:
        return "(пусто)"
    joined = " | ".join(lines)
    if len(joined) <= 60:
        return joined
    preview = " | ".join(lines[:3])
    if len(lines) > 3:
        preview += f" | ... (всего {len(lines)} строк)"
    return preview


def run_test_and_log(reporter, name, input_data, expected, test_func):
    try:
        actual = test_func()
        passed = (expected == actual)
        reporter.log_test_result(
            name=name,
            input_data=input_data,
            expected=str(expected),
            actual=str(actual),
            passed=passed,
        )
        return passed
    except Exception as e:
        reporter.log_test_result(
            name=name,
            input_data=input_data,
            expected=str(expected),
            actual="(исключение)",
            passed=False,
            error=str(e),
        )
        return False


#Базовые сценарии
def run_group_basic(reporter):
    reporter.log_group_header("Базовые сценарии")

    tests = [
        ("Пример из условия задачи",
         ["5", "3 2 2 5 4", "1 1 1", "1 1 4", "2 2 3 1", "1 3 1"], 2),
        ("Дерево-линия (1-2-3-4-5), все с письмами",
         ["5", "1 1 2", "2 1 1 3", "2 1 2 4", "2 1 3 5", "1 1 4"], 0),
        ("Дерево-звезда (1 в центре, 2-3-4-5 листья)",
         ["5", "4 1 2 3 4 5", "1 1 1", "1 1 1", "1 1 1", "1 1 1"], 3),
        ("Полное бинарное дерево (7 узлов)",
         ["7", "2 1 2 3", "3 1 1 4 5", "3 1 1 6 7",
          "1 1 2", "1 1 2", "1 1 3", "1 1 3"], 4),
        ("Простейшее дерево из 2 узлов",
         ["2", "1 5 2", "1 3 1"], 0),
    ]

    passed_count = 0
    for name, lines, expected in tests:
        def make_func(ls=lines):
            return lambda: PostmanSolver(build_tree_from_lines(ls)).solve()
        if run_test_and_log(reporter, name, format_input_lines(lines),
                            expected, make_func()):
            passed_count += 1

    reporter.log_group_summary("Базовые сценарии", passed_count, len(tests))
    return passed_count, len(tests)

#Граничные случаи
def run_group_boundary(reporter):
    reporter.log_group_header("Граничные случаи")

    # Длинная линия из 10 узлов
    M = 10
    long_line = [str(M)]
    for i in range(1, M + 1):
        if i == 1:
            long_line.append("1 1 2")
        elif i == M:
            long_line.append(f"1 1 {M - 1}")
        else:
            long_line.append(f"2 1 {i - 1} {i + 1}")

    tests = [
        ("Одно гнездо (корень) с письмом", ["1", "0 1"], 0),
        ("Одно гнездо без писем", ["1", "0 0"], 1),
        ("Все гнёзда без писем (линия из 3)",
         ["3", "1 0 2", "2 0 1 3", "1 0 2"], 3),
        ("Длинная линия из 10 узлов", long_line, 0),
        ("Большое количество писем (не влияет на ответ)",
         ["3", "1 100 2", "2 999 1 3", "1 500 2"], 0),
    ]

    passed_count = 0
    for name, lines, expected in tests:
        def make_func(ls=lines):
            return lambda: PostmanSolver(build_tree_from_lines(ls)).solve()
        if run_test_and_log(reporter, name, format_input_lines(lines),
                            expected, make_func()):
            passed_count += 1

    reporter.log_group_summary("Граничные случаи", passed_count, len(tests))
    return passed_count, len(tests)


#Обработка ошибок (некорректные данные)
def run_group_errors(reporter):
    reporter.log_group_header("Обработка ошибок (некорректные данные)")

    tests = [
        ("Пустые входные данные", [], "ValueError"),
        ("Первая строка — не число", ["abc", "1 1 2"], "ValueError"),
        ("M = 0 (вне диапазона)", ["0"], "ValueError"),
        ("M = 1000 (вне диапазона)", ["1000"], "ValueError"),
        ("Недостаточно строк (заявлено 3, есть 1)",
         ["3", "1 1 2"], "ValueError"),
        ("Неверное число соседей (заявлено 2, указан 1)",
         ["2", "2 1 2", "1 1 1"], "ValueError"),
        ("Буквы вместо чисел в данных",
         ["2", "1 abc 2", "1 1 1"], "ValueError"),
    ]

    passed_count = 0
    for name, lines, expected_error in tests:
        def make_func(ls=lines):
            def inner():
                try:
                    build_tree_from_lines(ls)
                    return "исключения не было"
                except ValueError:
                    return "ValueError"
            return inner

        try:
            actual = make_func()()
            passed = (actual == expected_error)
            reporter.log_test_result(
                name=name,
                input_data=format_input_lines(lines) if lines else "(пустой список)",
                expected=f"Исключение {expected_error}",
                actual=actual,
                passed=passed,
            )
            if passed:
                passed_count += 1
        except Exception as e:
            reporter.log_test_result(
                name=name,
                input_data=format_input_lines(lines) if lines else "(пустой список)",
                expected=f"Исключение {expected_error}",
                actual="(неожиданное исключение)",
                passed=False,
                error=str(e),
            )

    reporter.log_group_summary("Обработка ошибок", passed_count, len(tests))
    return passed_count, len(tests)


#Работа с файлами
def run_group_files(reporter):
    reporter.log_group_header("Работа с файлами")

    passed_count = 0
    total = 4

    # Тест 1: Чтение корректного файла
    content = "5\n3 2 2 5 4\n1 1 1\n1 1 4\n2 2 3 1\n1 3 1\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False, encoding='utf-8') as f:
        f.write(content)
        tmp_path = f.name
    try:
        tree = read_tree_from_file(tmp_path)
        actual = PostmanSolver(tree).solve()
        passed = (actual == 2)
    except Exception as e:
        actual = f"(исключение: {e})"
        passed = False
    finally:
        os.unlink(tmp_path)

    reporter.log_test_result(
        name="Чтение корректного файла",
        input_data=f"Файл: {os.path.basename(tmp_path)}",
        expected="2",
        actual=str(actual),
        passed=passed,
    )
    if passed:
        passed_count += 1

    # Тест 2: Чтение несуществующего файла
    try:
        read_tree_from_file("nonexistent_file_12345.txt")
        actual = "исключения не было"
        passed = False
    except FileNotFoundError:
        actual = "FileNotFoundError"
        passed = True
    except Exception as e:
        actual = str(e)
        passed = False

    reporter.log_test_result(
        name="Чтение несуществующего файла",
        input_data="Файл: nonexistent_file_12345.txt",
        expected="Исключение FileNotFoundError",
        actual=actual,
        passed=passed,
    )
    if passed:
        passed_count += 1

    # Тест 3: Чтение пустого файла
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False, encoding='utf-8') as f:
        f.write("")
        tmp_path = f.name
    try:
        read_tree_from_file(tmp_path)
        actual = "исключения не было"
        passed = False
    except ValueError:
        actual = "ValueError"
        passed = True
    except Exception as e:
        actual = str(e)
        passed = False
    finally:
        os.unlink(tmp_path)

    reporter.log_test_result(
        name="Чтение пустого файла",
        input_data=f"Файл: {os.path.basename(tmp_path)} (пустой)",
        expected="Исключение ValueError",
        actual=actual,
        passed=passed,
    )
    if passed:
        passed_count += 1

    # Тест 4: Файл с некорректным содержимым
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False, encoding='utf-8') as f:
        f.write("not a number\n")
        tmp_path = f.name
    try:
        read_tree_from_file(tmp_path)
        actual = "исключения не было"
        passed = False
    except ValueError:
        actual = "ValueError"
        passed = True
    except Exception as e:
        actual = str(e)
        passed = False
    finally:
        os.unlink(tmp_path)

    reporter.log_test_result(
        name="Файл с некорректным содержимым",
        input_data=f"Файл: {os.path.basename(tmp_path)} ('not a number')",
        expected="Исключение ValueError",
        actual=actual,
        passed=passed,
    )
    if passed:
        passed_count += 1

    reporter.log_group_summary("Работа с файлами", passed_count, total)
    return passed_count, total


# Главный запуск тестов
def main():

    # Формируем имя файла отчёта с датой и временем
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"test_report_{timestamp}.txt"

    try:
        reporter = TestReporter(report_filename)
    except Exception as e:
        print(f"Не удалось создать файл отчёта: {e}")
        print("    Тестирование будет выполнено только с выводом в консоль.")

        class ConsoleOnlyReporter:
            def __init__(self):
                self.test_counter = 0

            def log(self, text=""):
                print(text)

            def log_group_header(self, group_name):
                print()
                print("─" * 70)
                print(f"  ГРУППА: {group_name}")
                print("─" * 70)

            def log_test_result(self, name, input_data, expected, actual,
                                passed, error=None):
                self.test_counter += 1
                status = (f" ОШИБКА: {error}" if error is not None
                          else ("ПРОЙДЕН" if passed else "✗ ПРОВАЛ"))
                print("┌" + "─" * 68 + "┐")
                print(f"│ № теста      : {self.test_counter}")
                print(f"│ Название     : {name}")
                print(f"│ Что вводится : {input_data}")
                print(f"│ Ожидается    : {expected}")
                print(f"│ Выведено     : {actual}")
                print(f"│ Результат    : {status}")
                print("└" + "─" * 68 + "┘")

            def log_group_summary(self, group_name, passed, total):
                print()
                print(f"  >>> Итого по группе '{group_name}': {passed}/{total}")
                print()

            def close(self):
                pass

        reporter = ConsoleOnlyReporter()
        report_filename = None

    # Запускаем все группы тестов
    results = []
    results.append(run_group_basic(reporter))
    results.append(run_group_boundary(reporter))
    results.append(run_group_errors(reporter))
    results.append(run_group_files(reporter))

    # Итоговая статистика
    total_passed = sum(p for p, _ in results)
    total_tests = sum(t for _, t in results)

    reporter.log("=" * 70)
    reporter.log("ИТОГОВЫЙ РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ")
    reporter.log("=" * 70)
    reporter.log(f"  Всего тестов : {total_tests}")
    reporter.log(f"  Пройдено     : {total_passed}")
    reporter.log(f"  Провалено    : {total_tests - total_passed}")
    if total_tests > 0:
        percent = total_passed * 100 // total_tests
        reporter.log(f"  Процент      : {percent}%")
    reporter.log("=" * 70)

    if total_passed == total_tests:
        reporter.log("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        reporter.log("ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ — требуется проверка!")
    reporter.log("=" * 70)

    reporter.close()

    # Сообщение о сохранении файла
    if report_filename is not None:
        abs_path = os.path.abspath(report_filename)
        print(f"\nОтчёт о тестировании сохранён в файл:")
        print(f"    {abs_path}")
        print(f"    Этот файл можно приложить к отчёту по проекту.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем.")
        sys.exit(0)