import os
import shlex
import re


class ShellEmulator:
    def __init__(self):
        self.vfs_name = "myvfs"  # Имя нашей виртуальной файловой системы
        self.running = True  # Флаг работы эмулятора
        self.current_dir = "/"  # Текущая директория в VFS

    def expand_environment_variables(self, text):
        """Раскрывает переменные окружения в тексте ($HOME, ${USER})"""

        def replace_var(match):
            var_name = match.group(1) or match.group(2)

            # Специальная обработка для HOME, которая в Windows может быть USERPROFILE
            if var_name == "HOME":
                home_path = os.environ.get("HOME") or os.environ.get("USERPROFILE", "")
                # Заменяем обратные слеши на прямые для consistency
                return home_path.replace("\\", "/")
            elif var_name == "USER":
                return os.environ.get("USER") or os.environ.get("USERNAME", "")
            else:
                value = os.environ.get(var_name, f"${var_name}")
                # Для путей заменяем обратные слеши на прямые
                if "\\" in value:
                    return value.replace("\\", "/")
                return value

        pattern = r'\$\{([^}]+)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)'
        return re.sub(pattern, replace_var, text)

    def parse_command(self, input_line):
        """Парсит команду с раскрытием переменных окружения"""
        try:
            # Сначала раскрываем переменные окружения
            expanded_line = self.expand_environment_variables(input_line)
            # Затем разбиваем на части с учетом кавычек
            return shlex.split(expanded_line)
        except ValueError as e:
            print(f"Ошибка парсинга команды: {e}")
            return []

    def execute_command(self, user_input):
        """Обрабатывает введенную команду"""
        if not user_input:
            return

        # Используем новый парсер с поддержкой переменных окружения
        parts = self.parse_command(user_input)
        if not parts:  # Если парсинг не удался
            return

        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if command == "exit":
            self.running = False
            print("Выход из эмулятора")

        elif command == "ls":
            print(f"Команда: ls, Аргументы: {args}")

        elif command == "cd":
            print(f"Команда: cd, Аргументы: {args}")

        elif command == "echo":
            if args:
                print(' '.join(args))
            else:
                print()



        elif command == "env":
            print("Переменные окружения:")
            home_path = os.environ.get("HOME") or os.environ.get("USERPROFILE", "")
            userprofile = os.environ.get("USERPROFILE", "не установлена")
            print("  HOME: " + home_path.replace("\\", "/"))
            print("  USERPROFILE: " + userprofile.replace("\\", "/"))
            print(f"  USER: {os.environ.get('USER', 'не установлена')}")
            print(f"  USERNAME: {os.environ.get('USERNAME', 'не установлена')}")
            print("  PWD: " + os.getcwd().replace("\\", "/"))

        else:
            print(f"{command}: команда не найдена")

    def run(self):
        """Основной цикл REPL"""
        print("Добро пожаловать в эмулятор командной строки!")
        print("Введите 'exit' для выхода")
        print("Доступные команды: ls, cd, exit")
        print("-" * 40)

        # Главный цикл "Читать-Выполнить-Вывести"
        while self.running:
            try:
                # Пункт 2: Приглашение с именем VFS
                prompt = f"{self.vfs_name}:{self.current_dir}$ "
                user_input = input(prompt).strip()

                # Обработка команды
                self.execute_command(user_input)

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход")
                break

def main():
    """Точка входа в приложение"""
    shell = ShellEmulator()
    shell.run()


if __name__ == "__main__":
    main()