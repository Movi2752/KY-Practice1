import os
import shlex
import re

from Logger import *

class ShellEmulator:
    def __init__(self, vfs_path, log_file, startup_script=None):
        self.vfs_name = "myvfs"
        self.running = True
        self.current_dir = "/"
        self.vfs_path = vfs_path
        self.startup_script = startup_script
        self.script_mode = False  # Флаг для режима выполнения скрипта

        # Получаем имя пользователя из переменных окружения
        username = os.environ.get("USER") or os.environ.get("USERNAME", "unknown")

        # Инициализируем логгер
        self.logger = Logger(log_file, username)

        # Создаем необходимые директории
        os.makedirs(vfs_path, exist_ok=True)

        # Логируем старт системы
        self.logger.log_event("SYSTEM_START", f"VFS: {vfs_path}, Script: {startup_script}")

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

    def execute_script(self, script_path):
        """Выполняет скрипт с комментариями и имитацией диалога"""
        if not os.path.exists(script_path):
            error_msg = f"Скрипт не найден: {script_path}"
            print(error_msg)
            self.logger.log_event("SCRIPT_EXECUTION", script_path, error_msg)
            return False

        original_script_mode = self.script_mode
        self.script_mode = True

        try:
            print(f"\n=== Выполнение скрипта: {script_path} ===")
            self.logger.log_event("SCRIPT_START", script_path)

            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                if not line:
                    continue

                if line.startswith('#'):
                    print(f"# {line[1:].strip()}")
                    continue

                current_dir_name = os.path.basename(self.current_dir)
                prompt = f"{self.vfs_name}:{self.current_dir}$ {line}"
                print(prompt)

                parts = self.parse_command(line)
                if parts:
                    command = parts[0]
                    args = parts[1:]
                    self.execute_command(command, args)  # Теперь передаем 2 аргумента

                    if command == "exit":
                        break

            print(f"=== Завершение скрипта: {script_path} ===\n")
            self.logger.log_event("SCRIPT_END", script_path, "Успешное выполнение")
            return True

        except Exception as e:
            error_msg = f"Ошибка выполнения скрипта {script_path} на строке {line_num}: {e}"
            print(error_msg)
            self.logger.log_event("SCRIPT_ERROR", script_path, error_msg)
            return False

        finally:
            self.script_mode = original_script_mode

    def execute_command(self, command, args):
        """Обрабатывает команду и аргументы"""
        error_message = ""

        try:
            if command == "exit":
                self.running = False
                if not self.script_mode:
                    print("Выход из эмулятора")

            elif command == "ls":
                if not self.script_mode:
                    print(f"Команда: ls, Аргументы: {args}")
                print("file1.txt  file2.txt  documents/")

            elif command == "cd":
                if not self.script_mode:
                    print(f"Команда: cd, Аргументы: {args}")
                if args:
                    print(f"Изменение директории на: {args[0]}")
                else:
                    error_message = "cd: отсутствует аргумент"
                    print(error_message)

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

            elif command == "run":
                if args:
                    script_path = args[0]
                    self.execute_script(script_path)
                else:
                    error_message = "run: отсутствует путь к скрипту"
                    print(error_message)

            else:
                error_message = f"{command}: команда не найдена"
                print(error_message)

        except Exception as e:
            error_message = f"Ошибка выполнения: {str(e)}"
            print(error_message)

        finally:
            arguments_str = ' '.join(args) if args else ""
            self.logger.log_event(command, arguments_str, error_message)

    def run(self):
        """Основной цикл REPL"""
        print("Добро пожаловать в эмулятор командной строки!")
        print("Введите 'exit' для выхода")
        print("Доступные команды: ls, cd, echo, env, exit, run <script>")
        print("-" * 50)
        print("Конфигурация эмулятора:")
        print(f"  VFS путь: {self.vfs_path}")
        print(f"  Лог-файл: {self.logger.log_file}")
        print(f"  Стартовый скрипт: {self.startup_script}")
        print(f"  Пользователь: {self.logger.username}")
        print("-" * 50)

        # Выполнение стартового скрипта если указан
        if self.startup_script:
            print("Выполнение стартового скрипта...")
            success = self.execute_script(self.startup_script)
            if not success:
                print("!!! ОШИБКА ВЫПОЛНЕНИЯ СТАРТОВОГО СКРИПТА !!!")
            print("-" * 50)

        # Главный цикл REPL
        while self.running:
            try:
                current_dir_name = os.path.basename(self.current_dir)
                prompt = f"{self.vfs_name}:{self.current_dir}$ "
                user_input = input(prompt).strip()

                parts = self.parse_command(user_input)
                if not parts:
                    continue

                command = parts[0]
                args = parts[1:]
                self.execute_command(command, args)  # Теперь передаем 2 аргумента

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход")
                break
