import os
import sys

# Увеличим лимит рекурсии на случай длинных деревьев-"линий"
sys.setrecursionlimit(2000)

# Динамические структуры данных
class Nest:
    def __init__(self, number, letters):
        self.number = number        # номер гнезда
        self.letters = letters      # количество писем для этого адреса
        self.neighbors = []         # список номеров соседних гнёзд


class Tree:
    def __init__(self):
        self.nests = {}             # словарь: номер -> Nest
        self.root_number = 1        # корень всегда имеет номер 1

    def add_nest(self, number, letters):
        self.nests[number] = Nest(number, letters)

    def set_neighbors(self, number, neighbors):
        self.nests[number].neighbors = neighbors

    def get_max_depth(self):
        if not self.nests:
            return 0
        return self._dfs_depth(self.root_number, -1, 0)

    def _dfs_depth(self, current, parent, depth): #Рекурсивный DFS
        max_d = depth
        for neighbor in self.nests[current].neighbors:
            if neighbor != parent:
                d = self._dfs_depth(neighbor, current, depth + 1)
                if d > max_d:
                    max_d = d
        return max_d

    def count_empty_nests(self): #Считает гнёзда, для которых нет писем (l_i = 0).
        count = 0
        for nest in self.nests.values():
            if nest.letters == 0:
                count += 1
        return count



class PostmanSolver: #Класс для решения задачи о почтальоне-тритоне
    def __init__(self, tree):
        self.tree = tree

    def solve(self): #почему используеится такой алгоритм и формула написано в отчете "Задача №2"
        N = len(self.tree.nests)
        if N == 0:
            return 0

        max_depth = self.tree.get_max_depth()
        empty_count = self.tree.count_empty_nests()

        return N - 1 - max_depth + empty_count


def build_tree_from_lines(lines): #Строит дерево по списку строк входного формата. Возвращает объект Tree или ValueError при ошибке.
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        raise ValueError("Пустые входные данные")

    try:
        M = int(lines[0])
    except ValueError:
        raise ValueError("Первая строка должна содержать число M")

    if M <= 0 or M >= 1000:
        raise ValueError("M должно быть в диапазоне 1..999")

    if len(lines) < M + 1:
        raise ValueError(f"Ожидалось {M + 1} строк, получено {len(lines)}")

    tree = Tree()

    # Проходим по каждой строке и создаём гнёзда
    for i in range(1, M + 1):
        parts = lines[i].split()
        if len(parts) < 2:
            raise ValueError(f"Некорректная строка для гнезда {i}")
        try:
            n_i = int(parts[0])
            l_i = int(parts[1])
            neighbors = [int(x) for x in parts[2:]]
        except ValueError:
            raise ValueError(f"В строке гнезда {i} должны быть только числа")

        if len(neighbors) != n_i:
            raise ValueError(
                f"Для гнезда {i} заявлено {n_i} соседей, а указано {len(neighbors)}"
            )

        tree.add_nest(i, l_i)
        tree.set_neighbors(i, neighbors)

    return tree

def read_tree_from_file(filename):
    """Читает данные дерева из файла."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return build_tree_from_lines(lines)


def clear_screen():
    """Очистка консоли для кроссплатформенности."""
    os.system('cls' if os.name == 'nt' else 'clear')

def solve_from_file(): #Чтение из файла, решение и запись результата в выходной файл.
    print("\n--- Решение из файла ---")
    input_file = input("Введите путь к входному файлу (например, input.txt): ").strip()
    output_file = input("Введите путь к выходному файлу (например, output.txt): ").strip()

    if not input_file:
        print("Ошибка: имя входного файла не может быть пустым.")
        input("\nНажмите Enter для возврата в меню...")
        return
    if not output_file:
        output_file = "output.txt"

    try:
        tree = read_tree_from_file(input_file)
        solver = PostmanSolver(tree)
        result = solver.solve()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(result) + '\n')

        print(f"\nУспешно! Результат: {result}")
        print(f"Результат записан в файл {output_file}")

    except FileNotFoundError:
        print("Ошибка: Входной файл не найден. Проверьте правильность пути.")
    except ValueError as ve:
        print(f"Ошибка данных: {ve}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")

    input("\nНажмите Enter для возврата в меню...")


def solve_manual(): #Ручной ввод данных и вывод результата в консоль.
    print("\n--- Ручной ввод ---")

    # Защищённый ввод количества гнёзд
    while True:
        s = input("Введите количество гнёзд M (1-999): ").strip()
        try:
            M = int(s)
            if M <= 0 or M >= 1000:
                print("  Число должно быть от 1 до 999.")
                continue
            break
        except ValueError:
            print("  Нужно ввести целое число.")

    lines = [str(M)]
    print(f"\nВведите данные для {M} гнёзд.")
    print("Формат строки: кол_соседей кол_писем соседи_через_пробел")
    print("Пример: 3 2 2 5 4  (3 соседа, 2 письма, соседи — гнёзда 2, 5, 4)")
    print()

    for i in range(1, M + 1):
        while True:
            line = input(f"Гнездо {i}: ").strip()
            if line:
                lines.append(line)
                break
            print("  Строка не может быть пустой.")

    try:
        tree = build_tree_from_lines(lines)
        solver = PostmanSolver(tree)
        result = solver.solve()
        print(f"\nРезультат: {result} извинений")
    except ValueError as ve:
        print(f"\nОшибка в данных: {ve}")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")

    input("\nНажмите Enter для возврата в меню...")


def main_menu():
    while True:
        clear_screen()
        print("=" * 50)
        print("   ПРОГРАММА 'ПОЧТАЛЬОН' (Лукоморье)")
        print("   (Реализация на собственном дереве)")
        print("=" * 50)
        print("1. Решить задачу вручную (ввод с клавиатуры)")
        print("2. Решить задачу из файла")
        print("3. Выход из программы")
        print("=" * 50)

        choice = input("Выберите действие (1-3): ").strip()

        if choice == '1':
            solve_manual()
        elif choice == '2':
            solve_from_file()
        elif choice == '3':
            print("Завершение работы программы. До свидания!")
            sys.exit(0)
        else:
            print("\n[Ошибка] Неверный выбор. Пожалуйста, введите число от 1 до 3.")
            input("Нажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. Завершение работы.")
        sys.exit(0)
