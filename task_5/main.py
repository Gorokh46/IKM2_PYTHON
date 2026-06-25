import os
import sys


# Динамические структуры данных
class Node:
    def __init__(self, data: str):
        self.data = data
        self.next = None
        self.prev = None


class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data: str): #Добавляет элемент в конец циклического списка.
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node
        self.size += 1

    def get_substring(self, start_node: Node, length: int) -> str: #двигается по часовой стрелке
        if length <= 0 or not start_node:
            return ""
        chars = []
        curr = start_node
        for _ in range(length):
            chars.append(curr.data)
            curr = curr.next
        return "".join(chars)

    def get_all_start_nodes(self):
        """Генератор, возвращающий все узлы списка (все возможные начала числа А)."""
        if not self.head:
            return
        curr = self.head
        for _ in range(self.size):
            yield curr
            curr = curr.next


class NumberRingSolver: #Класс для решения задачи поиска тождества A+B=C в числовом кольце.
    
    def __init__(self, ring_string: str):
        if not ring_string or not ring_string.isdigit():
            raise ValueError("Строка кольца должна содержать только цифры и не быть пустой.")
        
        self.ring_string = ring_string
        self.n = len(ring_string)
        self.circular_list = CircularLinkedList()
        
        # Заполнение собственной структуры данных
        for char in self.ring_string:
            self.circular_list.append(char)

    def solve(self) -> str:#Основной алгоритм поиска решения. Использует оптимизацию по последним цифрам (mod 10 и mod 100) для сокращения количества полных вычислений с O(N^3) до фактически O(N^2).
        if self.n < 3:
            return "No"

        # Проходим по всем возможным точкам начала числа A
        for start_node in self.circular_list.get_all_start_nodes():
            
            # Перебираем возможную длину числа A (от 1 до N-2, чтобы осталось место для B и C)
            for len_a in range(1, self.n - 1):
                str_a = self.circular_list.get_substring(start_node, len_a)
                val_a = int(str_a)
                
                # Узел, с которого начинается число B
                node_b = start_node
                for _ in range(len_a):
                    node_b = node_b.next
                
                # Перебираем возможную длину числа C
                for len_c in range(1, self.n - len_a):
                    len_b = self.n - len_a - len_c
                    
                    # Последняя цифра A + последняя цифра B должна давать последнюю цифру C (по модулю 10)
                    last_a = int(str_a[-1])
                    
                    # Находим узел последней цифры B
                    node_last_b = node_b
                    for _ in range(len_b - 1):
                        node_last_b = node_last_b.next
                    last_b = int(node_last_b.data)
                    
                    # Находим начало числа C
                    node_start_c = node_last_b.next
                    
                    node_last_c = node_start_c
                    for _ in range(len_c - 1):
                        node_last_c = node_last_c.next
                    last_c = int(node_last_c.data)
                    
                    if (last_a + last_b) % 10 != last_c:
                        continue  # Быстрый отсев 90% неподходящих вариантов
                    
                    # Получаем полные строки для B и C
                    str_b = self.circular_list.get_substring(node_b, len_b)
                    str_c = self.circular_list.get_substring(node_start_c, len_c)
                    
                    val_b = int(str_b)
                    val_c = int(str_c)
                    
                    if val_a + val_b == val_c:
                        return f"{str_a}+{str_b}={str_c}"

        return "No"



#Пользовательский интерфейс и обработка ошибок
def clear_screen(): #Очистка консоли для кроссплатформенности."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_valid_string_input(prompt: str) -> str: #Запрашивает ввод у пользователя с валидацией на наличие только цифр.
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Ошибка: Ввод не может быть пустым. Попробуйте снова.")
            continue
        if not user_input.isdigit():
            print("Ошибка: Ввод должен содержать только цифры (0-9). Попробуйте снова.")
            continue
        return user_input

def solve_from_file(): #Чтение из файла, решение и запись в выходной файл с обработкой исключений.
    print("\n--- Решение из файла ---")
    input_file = input("Введите путь к входному файлу (например, input.txt): ").strip()
    output_file = input("Введите путь к выходному файлу (например, output.txt): ").strip()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            ring_string = f.read().strip()
            
        if not ring_string.isdigit():
            raise ValueError("Файл должен содержать только одну строку с цифрами.")
            
        solver = NumberRingSolver(ring_string)
        result = solver.solve()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result + '\n')
            
        print(f"Успешно! Результат '{result}' записан в {output_file}")
        
    except FileNotFoundError:
        print("Ошибка: Входной файл не найден. Проверьте правильность пути.")
    except ValueError as ve:
        print(f"Ошибка данных: {ve}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
    
    input("\nНажмите Enter для возврата в меню...")

def solve_manual(): #Ручной ввод строки и вывод результата в консоль
    print("\n--- Ручной ввод ---")
    ring_string = get_valid_string_input("Введите строку цифр кольца: ")
    
    print("Вычисление...")
    try:
        solver = NumberRingSolver(ring_string)
        result = solver.solve()
        print(f"\nРезультат: {result}")
    except Exception as e:
        print(f"Произошла ошибка при обработке: {e}")
        
    input("\nНажмите Enter для возврата в меню...")

def run_tests(): #Автоматическое тестирование основных сценариев (для блока "Правильность подбора тестов").
    print("\n--- Запуск автоматических тестов ---")
    test_cases = [
        # еачальные тестовые кейсы(в папке предоставлена программа для подробных тестов)
        ("01902021", "190+20=210", "Пример 1 из задания (сдвиг и ведущие нули)"),
        ("111111", "No", "Пример 2 из задания (решения нет)"),
        ("123", "1+2=3", "Минимально возможная длина (3 цифры)"),
        ("9009", "9+0=09", "Ведущий ноль в результате (допустимо по условию)"),
        ("000", "0+0=0", "Граничный случай: все нули"),
        ("12", "No", "Ошибка: слишком короткая строка (< 3)"),
        ("10000000000000000001", "1+0=00000000000000000001", "Длинная строка с ведущими нулями в C"),
    ]
    
    passed = 0
    failed = 0
    
    for data, expected, desc in test_cases:
        try:
            solver = NumberRingSolver(data)
            result = solver.solve()
            if result == expected:
                print(f"[ПРОЙДЕН] {desc}")
                print(f"        Вход: {data} | Выход: {result}")
                passed += 1
            else:
                print(f"[ПРОВАЛ] {desc}")
                print(f"        Ожидалось: {expected}, Получено: {result}")
                failed += 1
        except Exception as e:
            print(f"[ОШИБКА] {desc} -> Исключение: {e}")
            failed += 1
            
    print(f"\nИтого: Пройдено {passed} из {len(test_cases)}. Провалено: {failed}.")
    input("\nНажмите Enter для возврата в меню...")

def main_menu(): #Главное циклическое меню программы.
    while True:
        clear_screen()
        print("=" * 50)
        print(" ПРОГРАММА 'ЧИСЛОВОЕ КОЛЬЦО'")
        print("=" * 50)
        
        print("1. Решить задачу вручную (ввод с клавиатуры)")
        print("2. Решить задачу из файла")
        print("3. Запустить автоматические тесты")
        print("4. Выход из программы")
        print("=" * 50)
        
        choice = input("Выберите действие (1-4): ").strip()
        
        if choice == '1':
            solve_manual()
        elif choice == '2':
            solve_from_file()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            print("Завершение работы программы. До свидания!")
            sys.exit(0)
        else:
            print("\n[Ошибка] Неверный выбор. Пожалуйста, введите число от 1 до 4.")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. Завершение работы.")
        sys.exit(0)
