import os
import shlex
import re
import zipfile

from Logger import *
from FileType import *

class ShellEmulator:
    def __init__(self, vfs_path, log_file, startup_script=None):
        self.vfs_name = "myvfs"
        self.running = True
        self.startup_script = startup_script
        self.script_mode = False

        # Инициализируем VFS
        self.vfs = VirtualFileSystem(vfs_path)

        # Получаем имя пользователя из переменных окружения
        username = os.environ.get("USER") or os.environ.get("USERNAME", "unknown")

        # Инициализируем логгер
        self.logger = Logger(log_file, username)

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

            # Пробуем разные кодировки для чтения файла
            encodings = ['utf-8', 'cp1251', 'cp866', 'iso-8859-1']
            lines = []

            for encoding in encodings:
                try:
                    with open(script_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    print(f"Файл прочитан в кодировке: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Если ни одна кодировка не подошла, читаем как байты
                with open(script_path, 'rb') as f:
                    content = f.read()
                    # Пробуем декодировать с заменой ошибок
                    lines = content.decode('utf-8', errors='replace').splitlines()
                    print("Файл прочитан с заменой ошибок кодировки")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                if not line:
                    continue

                if line.startswith('#'):
                    print(f"# {line[1:].strip()}")
                    continue

                # ИСПРАВЛЕНИЕ: используем self.vfs.get_current_path() вместо self.current_dir
                current_vfs_path = self.vfs.get_current_path()
                prompt = f"{self.vfs_name}:{current_vfs_path}$ {line}"
                print(prompt)

                parts = self.parse_command(line)
                if parts:
                    command = parts[0]
                    args = parts[1:]
                    self.execute_command(command, args)

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
                self._handle_ls_command(args)

            elif command == "cd":
                self._handle_cd_command(args)

            elif command == "echo":
                if args:
                    print(' '.join(args))
                else:
                    print()

            elif command == "env":
                self._handle_env_command()

            elif command == "run":
                if args:
                    script_path = args[0]
                    self.execute_script(script_path)
                else:
                    error_message = "run: отсутствует путь к скрипту"
                    print(error_message)

            elif command == "pwd":
                self._handle_pwd_command()

            elif command == "vfs-init":
                self._handle_vfs_init_command(args)

            else:
                error_message = f"{command}: команда не найдена"
                print(error_message)

        except Exception as e:
            error_message = f"Ошибка выполнения: {str(e)}"
            print(error_message)

        finally:
            arguments_str = ' '.join(args) if args else ""
            self.logger.log_event(command, arguments_str, error_message)

    def _handle_ls_command(self, args):
        """Обрабатывает команду ls с поддержкой VFS"""
        path = args[0] if args else ""

        try:
            entries = self.vfs.list_directory(path)

            if entries is None:
                print(f"ls: невозможно получить доступ к '{path}': Нет такого файла или каталога")
                return

            # Простой вывод (можно улучшить форматирование позже)
            for entry in entries:
                if entry['type'] == 'directory':
                    print(f"{entry['name']}/")
                else:
                    print(entry['name'])

        except Exception as e:
            print(f"ls: ошибка при получении списка файлов: {e}")

    def _handle_cd_command(self, args):
        """Обрабатывает команду cd с поддержкой VFS"""
        if not args:
            # cd без аргументов - переход в домашнюю директорию
            path = "/home/user"
        else:
            path = args[0]

        success = self.vfs.change_directory(path)
        if not success:
            print(f"cd: {path}: Нет такого файла или каталога")

    def _handle_pwd_command(self):
        """Обрабатывает команду pwd"""
        current_path = self.vfs.get_current_path()
        print(current_path)

    def _handle_env_command(self):
        """Обрабатывает команду env"""
        print("Переменные окружения:")
        home_path = os.environ.get("HOME") or os.environ.get("USERPROFILE", "")
        userprofile = os.environ.get("USERPROFILE", "не установлена")

        print("  HOME: " + home_path.replace("\\", "/"))
        print("  USERPROFILE: " + userprofile.replace("\\", "/"))
        print(f"  USER: {os.environ.get('USER', 'не установлена')}")
        print(f"  USERNAME: {os.environ.get('USERNAME', 'не установлена')}")
        print(f"  VFS_PATH: {self.vfs.vfs_path}")
        print(f"  CURRENT_VFS_DIR: {self.vfs.get_current_path()}")

    def create_default_vfs_archive(self, archive_path: str = "default_vfs.zip"):
            """Создает VFS архив по умолчанию"""
            try:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Создаем стандартную структуру директорий
                    directories = [
                        "home/",
                        "home/user/",
                        "home/user/documents/",
                        "home/user/downloads/",
                        "home/user/desktop/",
                        "etc/",
                        "tmp/",
                        "var/",
                        "var/log/"
                    ]

                    for directory in directories:
                        zipf.writestr(directory, "")

                    # Создаем стандартные файлы
                    files_content = {
                        "readme.txt": """Добро пожаловать в виртуальную файловую систему!

    Эта VFS была инициализирована командой vfs-init.

    Доступные команды:
    - ls: список файлов
    - cd: смена директории
    - pwd: текущий путь
    - echo: вывод текста
    - vfs-init: сброс VFS

    Для выхода используйте команду 'exit'.""",

                        "home/user/.bashrc": """# Файл настройки оболочки
    echo "VFS оболочка загружена"
    export VFS_VERSION="1.0"
    PS1='\\\\u@vfs:\\\\w\\\\$ '""",

                        "home/user/welcome.txt": "Добро пожаловать в вашу домашнюю директорию!",

                        "etc/motd": "Добро пожаловать в эмулятор VFS!",

                        "var/log/vfs.log": "# Лог-файл VFS\n# Создан при инициализации системы"
                    }

                    for file_path, content in files_content.items():
                        zipf.writestr(file_path, content)

                print(f"Создан архив VFS по умолчанию: {archive_path}")
                return archive_path

            except Exception as e:
                print(f"Ошибка создания архива по умолчанию: {e}")
                return None

    def _handle_vfs_init_command(self, args):
            """Обрабатывает команду vfs-init - сбрасывает VFS к состоянию по умолчанию"""
            if args:
                print("vfs-init: команда не принимает аргументов")
                return

            print("Инициализация VFS...")

            # Создаем архив по умолчанию если его нет
            default_archive = "default_vfs.zip"
            if not os.path.exists(default_archive):
                print("Создание VFS по умолчанию...")
                self.create_default_vfs_archive(default_archive)

            # Очищаем текущую VFS и загружаем по умолчанию
            self.vfs = VirtualFileSystem(default_archive, force_reload=True)

            # Обновляем путь к VFS в конфигурации
            self.vfs_path = default_archive

            print("VFS успешно сброшена к состоянию по умолчанию")
            print(f"Загружена из: {default_archive}")

    def run(self):
        """Основной цикл REPL"""
        print("Добро пожаловать в эмулятор командной строки!")
        print("Введите 'exit' для выхода")
        print("Доступные команды: ls, cd, echo, env, pwd, run <script>, vfs-init")
        print("-" * 50)
        print("Конфигурация эмулятора:")
        print(f"  VFS путь: {self.vfs.vfs_path}")
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
                # Используем путь из VFS вместо реальной файловой системы
                current_vfs_path = self.vfs.get_current_path()
                prompt = f"{self.vfs_name}:{current_vfs_path}$ "
                user_input = input(prompt).strip()

                parts = self.parse_command(user_input)
                if not parts:
                    continue

                command = parts[0]
                args = parts[1:]
                self.execute_command(command, args)

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход")
                break