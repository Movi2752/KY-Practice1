import argparse
import os
import zipfile
from ShellEmulator import *
from FileType import *


def parse_arguments():
    """Парсит аргументы командной строки для настройки эмулятора"""
    parser = argparse.ArgumentParser(
        description='Эмулятор командной строки с виртуальной файловой системой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python shell_emulator.py --vfs-path ./my_vfs.zip --log-file ./logs/shell.log
  python shell_emulator.py --create-test minimal --log-file ./logs/test.log
  python shell_emulator.py --create-test medium --log-file ./logs/test.log --startup-script ./test.txt
  python shell_emulator.py --create-test deep --log-file ./logs/test.log
        """
    )

    parser.add_argument(
        '--vfs-path',
        help='Путь к физическому расположению VFS'
    )

    parser.add_argument(
        '--log-file',
        required=True,
        help='Путь к лог-файлу'
    )

    parser.add_argument(
        '--startup-script',
        help='Путь к стартовому скрипту для автоматического выполнения'
    )

    parser.add_argument(
        '--create-test',
        choices=['minimal', 'medium', 'deep', 'all', 'comprehensive'],
        help='Автоматически создать тестовую VFS указанного типа'
    )

    return parser.parse_args()


def create_minimal_vfs():
    """Создает минимальную VFS"""
    archive_path = "minimal_vfs.zip"
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr('readme.txt', 'Минимальная VFS для тестирования')
            zipf.writestr('home/', '')
            zipf.writestr('home/user/', '')
            zipf.writestr('home/user/test.txt', 'Тестовый файл в минимальной VFS')

        print(f"Создана минимальная VFS: {archive_path}")
        return archive_path
    except Exception as e:
        print(f"Ошибка создания минимальной VFS: {e}")
        return None


def create_medium_vfs():
    """Создает VFS среднего размера с несколькими файлами"""
    archive_path = "medium_vfs.zip"
    try:
        files_content = {
            'readme.txt': 'VFS с несколькими файлами и директориями',
            'home/user/documents/report.pdf': 'PDF документ (имитация)',
            'home/user/documents/data.xlsx': 'Excel файл с данными',
            'home/user/images/photo.jpg': 'Изображение (имитация)',
            'home/user/code/main.py': 'print("Hello VFS!")',
            'home/user/code/utils.py': 'def helper():\n    return "helper function"',
            'var/log/system.log': '2024-01-15 INFO: System started',
            'etc/config.json': '{"version": "1.0", "debug": true}',
            'tmp/cache.tmp': 'Временные данные'
        }

        with zipfile.ZipFile(archive_path, 'w') as zipf:
            # Создаем директории
            directories = [
                'home/', 'home/user/', 'home/user/documents/', 'home/user/images/',
                'home/user/code/', 'var/', 'var/log/', 'etc/', 'tmp/'
            ]
            for directory in directories:
                zipf.writestr(directory, '')

            # Создаем файлы
            for file_path, content in files_content.items():
                zipf.writestr(file_path, content)

        print(f"Создана VFS среднего размера: {archive_path}")
        return archive_path
    except Exception as e:
        print(f"Ошибка создания VFS среднего размера: {e}")
        return None


def create_deep_vfs():
    """Создает VFS с глубокой структурой (3+ уровня)"""
    archive_path = "deep_vfs.zip"
    try:
        # Создаем глубокую структуру директорий
        directories = [
            'apps/', 'data/', 'system/', 'users/',
            'apps/web/', 'apps/mobile/', 'apps/desktop/',
            'data/database/', 'data/backups/', 'data/archives/',
            'system/config/', 'system/logs/', 'system/cache/',
            'users/alice/', 'users/bob/', 'users/charlie/',
            'apps/web/frontend/', 'apps/web/backend/', 'apps/web/api/',
            'apps/mobile/ios/', 'apps/mobile/android/', 'apps/mobile/crossplatform/',
            'data/database/tables/', 'data/database/indexes/', 'data/database/procedures/',
            'users/alice/documents/', 'users/alice/projects/', 'users/alice/settings/',
            'apps/web/frontend/components/', 'apps/web/frontend/styles/', 'apps/web/frontend/assets/',
            'users/alice/projects/vfs_emulator/', 'users/alice/projects/web_app/', 'users/alice/projects/scripts/'
        ]

        # Создаем файлы в разных уровнях
        files = {
            'readme.txt': 'Сложная VFS структура с 4 уровнями вложенности',
            'apps/main.py': '#!/usr/bin/env python3\nprint("Main application")',
            'apps/web/index.html': '<html><body><h1>Welcome</h1></body></html>',
            'apps/web/backend/server.py': 'from flask import Flask\napp = Flask(__name__)',
            'apps/web/frontend/components/header.js': 'export default function Header() { return "Header"; }',
            'data/database/schema.sql': 'CREATE TABLE users (id INT, name VARCHAR(100));',
            'data/database/tables/users.sql': 'INSERT INTO users VALUES (1, "Alice");',
            'system/config/network/ports.conf': 'http: 80\nhttps: 443\nssh: 22',
            'users/alice/projects/vfs_emulator/design.md': '# VFS Emulator Design',
            'users/alice/settings/prefs.json': '{"theme": "dark", "lang": "ru"}',
            'var/log/access.log': '127.0.0.1 - - [15/Jan/2024] "GET / HTTP/1.1" 200'
        }

        with zipfile.ZipFile(archive_path, 'w') as zipf:
            # Создаем все директории
            for directory in directories:
                zipf.writestr(directory, '')

            # Создаем файлы
            for file_path, content in files.items():
                zipf.writestr(file_path, content)

        print(f"Создана глубокая VFS: {archive_path}")
        return archive_path
    except Exception as e:
        print(f"Ошибка создания глубокой VFS: {e}")
        return None


def create_sample_vfs_archive():
    """Создает тестовый ZIP-архив для VFS"""
    archive_path = "sample_vfs.zip"

    # Содержимое тестовых файлов
    files_content = {
        "readme.txt": "Добро пожаловать в VFS!\nЭто виртуальная файловая система, загруженная из ZIP-архива.",
        "home/user/document.txt": "Важные документы пользователя.",
        "home/user/notes.md": "# Заметки\n- Пункт 1\n- Пункт 2\n- Пункт 3",
        "home/user/projects/hello.py": "print('Hello, VFS!')\n\nif __name__ == '__main__':\n    print('Программа запущена')",
        "home/user/projects/data.bin": "binary_data_here"  # Бинарные данные
    }

    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Создаем директории
            directories = [
                "home/",
                "home/user/",
                "home/user/projects/"
            ]

            for directory in directories:
                zipf.writestr(directory, "")

            # Создаем файлы
            for file_path, content in files_content.items():
                zipf.writestr(file_path, content)

        print(f"Создан тестовый VFS архив: {archive_path}")
        return archive_path

    except Exception as e:
        print(f"Ошибка создания архива: {e}")
        return None


def create_test_startup_scripts():
    """Создает тестовые стартовые скрипты"""
    scripts_dir = "scripts"
    os.makedirs(scripts_dir, exist_ok=True)

    # Создаем скрипт для минимальной VFS
    with open(os.path.join(scripts_dir, "test_minimal.txt"), 'w', encoding='utf-8') as f:
        f.write("""# Тест минимальной VFS
echo "=== Тестирование минимальной VFS ==="
pwd
ls
cd home
ls
cd user
ls
echo "=== Тест завершен ==="
""")

    # Создаем скрипт для VFS среднего размера
    with open(os.path.join(scripts_dir, "test_medium.txt"), 'w', encoding='utf-8') as f:
        f.write("""# Тест VFS с несколькими файлами
echo "=== Тестирование VFS среднего размера ==="
pwd
ls
cd home/user
ls
cd documents
ls
cd ../code
ls
cd ../../../
ls var/
echo "=== Тест завершен ==="
""")

    # Создаем скрипт для глубокой VFS
    with open(os.path.join(scripts_dir, "test_deep.txt"), 'w', encoding='utf-8') as f:
        f.write("""# Тест глубокой структуры VFS
echo "=== Тестирование глубокой структуры VFS ==="
pwd
ls
cd apps/web/frontend/components
ls
cd ../../../../data/database/tables
ls
cd ../../../../users/alice/projects/vfs_emulator
ls
cd ../../../../../
pwd
echo "=== Тест завершен ==="
""")

    # СОЗДАЕМ КОМПЛЕКСНЫЙ ТЕСТОВЫЙ СКРИПТ ДЛЯ ВСЕХ КОМАНД
    with open(os.path.join(scripts_dir, "comprehensive_test.txt"), 'w', encoding='utf-8') as f:
        f.write("""# Комплексный тестовый скрипт для всех команд эмулятора
# Тестирование Этапов 1, 2 и 3

echo "================================================"
echo "КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ЭМУЛЯТОРА VFS"
echo "================================================"

echo.
echo "=== ЭТАП 1: Базовые команды REPL ==="

echo "Тестирование команды echo:"
echo "Простой текст"
echo "Текст с переменными: Пользователь - $USERNAME, Домашняя папка - $USERPROFILE"

echo.
echo "Тестирование команды pwd:"
pwd

echo.
echo "Тестирование команды ls:"
ls
ls home

echo.
echo "Тестирование команды cd:"
cd home
pwd
ls
cd ..
pwd

echo.
echo "Тестирование команды env:"
env

echo.
echo "=== ЭТАП 2: Обработка ошибок ==="

echo "Тестирование неизвестной команды:"
unknown_command

echo "Тестирование перехода в несуществующую директорию:"
cd nonexistent_directory

echo "Тестирование команды cd без аргументов:"
cd

echo "Тестирование команды run без аргументов:"
run

echo.
echo "=== ЭТАП 3: Работа с VFS ==="

echo "Тестирование навигации по VFS:"
cd home/user
pwd
ls
cd documents
pwd
cd ../..
pwd

echo.
echo "Тестирование команды vfs-init:"
echo "Перед vfs-init:"
ls
vfs-init
echo "После vfs-init:"
ls

echo.
echo "Тестирование глубокой навигации:"
cd home/user/documents
pwd
cd ../../..
pwd

echo.
echo "=== ТЕСТИРОВАНИЕ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==="

echo "Работа с переменными в команде echo:"
echo "Текущий пользователь ОС: $USERNAME"
echo "Домашняя директория ОС: $USERPROFILE"
echo "Комбинированный путь: $USERPROFILE/Documents/$USERNAME"

echo.
echo "=== ТЕСТИРОВАНИЕ СКРИПТОВОГО РЕЖИМА ==="

echo "Тестирование вложенного скрипта (если есть test_minimal.txt):"
run scripts/test_minimal.txt

echo.
echo "=== ТЕСТИРОВАНИЕ ГРАНИЧНЫХ СЛУЧАЕВ ==="

echo "Пустая команда:"

echo "Команда с лишними пробелами:"
   ls   home   

echo "Команда с кавычками:"
echo "Текст 'в кавычках'"
echo "Текст \\"в двойных кавычках\\""

echo.
echo "================================================"
echo "ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"
echo "================================================"

# Финальная проверка
pwd
ls
echo "Готово!"
""")

    print("Созданы тестовые стартовые скрипты в папке scripts/")


def main():
    """Точка входа в приложение"""
    args = parse_arguments()

    # Создаем тестовую VFS если запрошено
    vfs_path = args.vfs_path
    if args.create_test:
        print(f"Создание тестовой VFS типа: {args.create_test}")

        if args.create_test == 'minimal':
            vfs_path = create_minimal_vfs()
            if not args.startup_script:
                args.startup_script = "scripts/test_minimal.txt"

        elif args.create_test == 'medium':
            vfs_path = create_medium_vfs()
            if not args.startup_script:
                args.startup_script = "scripts/test_medium.txt"

        elif args.create_test == 'deep':
            vfs_path = create_deep_vfs()
            if not args.startup_script:
                args.startup_script = "scripts/test_deep.txt"

        elif args.create_test == 'all':
            print("Создание всех тестовых VFS...")
            create_minimal_vfs()
            create_medium_vfs()
            create_deep_vfs()
            create_test_startup_scripts()
            print("Все тестовые VFS созданы. Запустите с конкретным --vfs-path")
            return

        elif args.create_test == 'comprehensive':
            vfs_path = create_medium_vfs()  # Используем VFS среднего размера для комплексного теста
            if not args.startup_script:
                args.startup_script = "scripts/comprehensive_test.txt"

        if not vfs_path:
            print("Ошибка: не удалось создать тестовую VFS")
            return

        create_test_startup_scripts()

    # Если VFS путь не указан и не создан через --create-test
    if not vfs_path:
        print("Ошибка: необходимо указать --vfs-path или --create-test")
        return

    # Создаем необходимые директории для логов
    os.makedirs(os.path.dirname(args.log_file) if os.path.dirname(args.log_file) else ".", exist_ok=True)

    # Отладочный вывод параметров
    print("=" * 60)
    print("ПАРАМЕТРЫ ЗАПУСКА ЭМУЛЯТОРА:")
    print(f"  VFS источник: {vfs_path}")

    # Определяем тип VFS для отображения
    if vfs_path.lower().endswith('.zip'):
        vfs_type = "ZIP архив"
        if not os.path.exists(vfs_path):
            print(f"  Предупреждение: архив не найден, будет создана пустая VFS")
    else:
        vfs_type = "Память"

    print(f"  Тип VFS: {vfs_type}")
    print(f"  Лог-файл: {args.log_file}")
    print(f"  Стартовый скрипт: {args.startup_script}")
    if args.create_test:
        print(f"  Тип теста: {args.create_test}")
    print("=" * 60)

    shell = ShellEmulator(
        vfs_path=vfs_path,
        log_file=args.log_file,
        startup_script=args.startup_script
    )
    shell.run()


if __name__ == "__main__":
    main()