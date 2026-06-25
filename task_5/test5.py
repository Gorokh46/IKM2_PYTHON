import sys
import os

try:
    from main import NumberRingSolver, CircularLinkedList
except ImportError:
    try:
        from _5Var import NumberRingSolver, CircularLinkedList
    except ImportError:
        print("Ошибка: не найден main.py или 5Var.py")
        sys.exit(1)


def verify_solution(input_data: str, output: str) -> tuple:
    if output == "No":
        return True, "Корректно сообщено об отсутствии решения"
    if '+' not in output or '=' not in output:
        return False, "Неверный формат вывода (ожидается A+B=C)"

    try:
        a_str, rest = output.split('+')
        b_str, c_str = rest.split('=')

        if not (a_str.isdigit() and b_str.isdigit() and c_str.isdigit()):
            return False, "Части уравнения содержат нецифровые символы"

        # 1. Проверка полноты использования цифр
        if len(a_str) + len(b_str) + len(c_str) != len(input_data):
            return False, (f"Нарушено покрытие кольца: "
                          f"{len(a_str)}+{len(b_str)}+{len(c_str)} != {len(input_data)}")

        # 2. Проверка математической идентичности
        val_a, val_b, val_c = int(a_str), int(b_str), int(c_str)
        if val_a + val_b != val_c:
            return False, f"Математическая ошибка: {val_a} + {val_b} != {val_c}"

        return True, f"[OK] Решение верно: {val_a} + {val_b} = {val_c}"
    except Exception as e:
        return False, f"Критическая ошибка проверки: {e}"


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.results = []

    def run(self, name, data, expect_solution=True, desc=""):
        print(f"\n[{name}] {desc}")
        print(f"  Вход: {data[:60]}{'...' if len(data) > 60 else ''}")

        try:
            solver = NumberRingSolver(data)
            res = solver.solve()
            ok, msg = verify_solution(data, res)

            if expect_solution and not ok:
                print(f"  [FAIL] ПРОВАЛ: {msg}")
                self.failed += 1
                self.results.append((name, False, msg))
            elif not expect_solution and res != "No":
                print(f"  [FAIL] ПРОВАЛ: Ожидалось 'No', получено '{res}'")
                self.failed += 1
                self.results.append((name, False, "Ожидалось 'No'"))
            else:
                print(f"  [OK] {msg}")
                self.passed += 1
                self.results.append((name, True, msg))
        except Exception as e:
            print(f"  [ERROR] ОШИБКА: {e}")
            self.errors += 1
            self.results.append((name, False, f"Exception: {e}"))


def run_all_tests():
    print("=" * 70)
    print("КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ПРОГРАММЫ 'ЧИСЛОВОЕ КОЛЬЦО'")
    print("=" * 70)
    runner = TestRunner()

    print("\nБЛОК 1: Базовые сценарии из задания")
    runner.run("B1", "01902021", True, "Пример 1 (циклический сдвиг)")
    runner.run("B2", "111111", False, "Пример 2 (решения нет)")
    runner.run("B3", "123", True, "Минимальная длина N=3")

    print("\nБЛОК 2: Граничные случаи")
    runner.run("G1", "000", True, "Все нули")
    runner.run("G2", "12", False, "Слишком короткая строка (<3)")
    runner.run("G3", "1001", True, "Ведущий ноль в результате")
    runner.run("G4", "9999", False, "Все девятки")
    runner.run("G5", "001", False, "Два нуля и единица (решения нет)")
    runner.run("G6", "1010", True, "Чередование 1 и 0")

    print("\nБЛОК 3: Ведущие нули")
    runner.run("LZ1", "00123", True, "Ведущие нули в начале")
    runner.run("LZ2", "100200300", True, "Нули внутри чисел")
    runner.run("LZ3", "010203", True, "Нули между числами")

    print("\nБЛОК 4: Циклические свойства")
    runner.run("C1", "210019020", True, "Сдвиг примера 1")
    runner.run("C2", "20210019", True, "Другой сдвиг")
    runner.run("C3", "312", True, "Сдвиг 1+2=3")

    print("\nБЛОК 5: Различная длина")
    runner.run("D1", "123456", False, "Длина 6 (нет решения)")
    runner.run("D2", "112233", True, "Длина 6 с повторами")
    runner.run("D3", "123456789", False, "Длина 9 (нет решения)")
    runner.run("D4", "5" * 100, False, "Длинная строка из одинаковых цифр")

    print("\nБЛОК 6: Случаи без решения")
    runner.run("N1", "555", False, "Три одинаковые цифры")
    runner.run("N2", "987", False, "Убывающая последовательность")
    runner.run("N3", "135", False, "Нечётные числа")
    runner.run("N4", "2468", False, "Чётные числа")

    print("\nБЛОК 7: Структура данных CircularLinkedList")
    try:
        cl = CircularLinkedList()
        for c in "123":
            cl.append(c)
        assert cl.size == 3 and cl.head is not None
        print("  [OK] S1: Создание и заполнение списка")
        runner.passed += 1
        runner.results.append(("S1", True, "Структура создана"))
    except Exception as e:
        print(f"  [FAIL] S1: {e}")
        runner.failed += 1

    try:
        cl = CircularLinkedList()
        for c in "ABC":
            cl.append(c)
        tail = cl.head.prev
        assert tail.next == cl.head and cl.head.prev == tail
        print("  [OK] S2: Проверка цикличности")
        runner.passed += 1
        runner.results.append(("S2", True, "Цикличность подтверждена"))
    except Exception as e:
        print(f"  [FAIL] S2: {e}")
        runner.failed += 1

    try:
        cl = CircularLinkedList()
        for c in "01902021":
            cl.append(c)
        node = cl.head.next  # цифра '1'
        substr = cl.get_substring(node, 3)
        assert substr == "190"
        print("  [OK] S3: Извлечение подстроки")
        runner.passed += 1
        runner.results.append(("S3", True, "Подстрока извлечена"))
    except Exception as e:
        print(f"  [FAIL] S3: {e}")
        runner.failed += 1

    # ===== ИСПРАВЛЕННЫЙ БЛОК 8 =====
    print("\nБЛОК 8: Валидация входных данных")
    try:
        NumberRingSolver("")
        print("  [FAIL] V1: Пустая строка не вызвала ошибку")
        runner.failed += 1
        runner.results.append(("V1", False, "Пустая строка не вызвала ошибку"))
    except ValueError:
        print("  [OK] V1: Пустая строка отклонена")
        runner.passed += 1
        runner.results.append(("V1", True, "Пустая строка отклонена"))

    try:
        NumberRingSolver("12a34")
        print("  [FAIL] V2: Буквы не вызвали ошибку")
        runner.failed += 1
        runner.results.append(("V2", False, "Буквы не вызвали ошибку"))
    except ValueError:
        print("  [OK] V2: Буквы отклонены")
        runner.passed += 1
        runner.results.append(("V2", True, "Буквы отклонены"))

    try:
        NumberRingSolver("12+34")
        print("  [FAIL] V3: Спецсимволы не вызвали ошибку")
        runner.failed += 1
        runner.results.append(("V3", False, "Спецсимволы не вызвали ошибку"))
    except ValueError:
        print("  [OK] V3: Спецсимволы отклонены")
        runner.passed += 1
        runner.results.append(("V3", True, "Спецсимволы отклонены"))

    print("\nБЛОК 9: Производительность (N=1000)")
    long_str = "1" + "0" * 499 + "1" + "0" * 499
    runner.run("P1", long_str, False, "Строка 1000 цифр")

    # Итоговая сводка
    total = runner.passed + runner.failed + runner.errors
    print("\n" + "=" * 70)
    print(f"СВОДКА: {runner.passed}/{total} тестов пройдено")
    print(f"   Пройдено: {runner.passed} | Провалено: {runner.failed} | Ошибок: {runner.errors}")
    if runner.failed == 0 and runner.errors == 0:
        print("ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ")
    else:
        print("ЕСТЬ ПРОВАЛЫ")
    print("=" * 70)

    # Сохранение отчёта
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write("ОТЧЁТ ТЕСТИРОВАНИЯ\n")
        f.write(f"Всего: {total}, Пройдено: {runner.passed}, "
                f"Провалено: {runner.failed}, Ошибок: {runner.errors}\n\n")
        for name, ok, msg in runner.results:
            status = "[OK] " if ok else "[FAIL] "
            f.write(f"{status} {name}: {msg}\n")
    print("Отчёт сохранён в test_report.txt")

    return runner.failed == 0 and runner.errors == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)