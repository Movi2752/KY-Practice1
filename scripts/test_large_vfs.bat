@echo off
chcp 65001 > nul
echo ===============================================
echo Тест 3: VFS с 3+ уровнями вложенности
echo ===============================================

echo Создание сложной VFS структуры...
python -c "
import zipfile
import os

def create_deep_structure():
    '''Создает глубокую структуру директорий и файлов'''
    structure = {}

    # Уровень 1: корневые директории
    level1_dirs = ['apps/', 'data/', 'system/', 'users/']

    # Уровень 2: поддиректории
    level2_dirs = {
        'apps/': ['web/', 'mobile/', 'desktop/'],
        'data/': ['database/', 'backups/', 'archives/'],
        'system/': ['config/', 'logs/', 'cache/'],
        'users/': ['alice/', 'bob/', 'charlie/']
    }

    # Уровень 3: глубокие вложенности
    level3_dirs = {
        'apps/web/': ['frontend/', 'backend/', 'api/'],
        'apps/mobile/': ['ios/', 'android/', 'crossplatform/'],
        'apps/desktop/': ['windows/', 'linux/', 'macos/'],
        'data/database/': ['tables/', 'indexes/', 'procedures/'],
        'data/backups/': ['daily/', 'weekly/', 'monthly/'],
        'system/config/': ['network/', 'security/', 'services/'],
        'users/alice/': ['documents/', 'projects/', 'settings/'],
        'users/bob/': ['work/', 'personal/', 'shared/']
    }

    # Уровень 4: самые глубокие директории
    level4_dirs = {
        'apps/web/frontend/': ['components/', 'styles/', 'assets/'],
        'apps/web/backend/': ['controllers/', 'models/', 'middleware/'],
        'data/database/tables/': ['users/', 'products/', 'orders/'],
        'users/alice/projects/': ['vfs_emulator/', 'web_app/', 'scripts/']
    }

    # Собираем все директории
    all_dirs = []
    all_dirs.extend(level1_dirs)

    for parent, children in level2_dirs.items():
        all_dirs.extend([parent + child for child in children])

    for parent, children in level3_dirs.items():
        all_dirs.extend([parent + child for child in children])

    for parent, children in level4_dirs.items():
        all_dirs.extend([parent + child for child in children])

    # Создаем файлы в разных уровнях
    files = {
        'readme.txt': 'Сложная VFS структура с 4 уровнями вложенности',
        'apps/main.py': '#!/usr/bin/env python3\\nprint(\\\"Main application\\\")',
        'apps/web/index.html': '<html><body><h1>Welcome</h1></body></html>',
        'apps/web/backend/server.py': 'from flask import Flask\\napp = Flask(__name__)',
        'apps/web/frontend/components/header.js': 'export default function Header() { return \\\"Header\\\"; }',
        'data/database/schema.sql': 'CREATE TABLE users (id INT, name VARCHAR(100));',
        'data/database/tables/users.sql': 'INSERT INTO users VALUES (1, \\\"Alice\\\");',
        'system/config/network/ports.conf': 'http: 80\\nhttps: 443\\nssh: 22',
        'users/alice/projects/vfs_emulator/design.md': '# VFS Emulator Design',
        'users/alice/settings/prefs.json': '{\\\"theme\\\": \\\"dark\\\", \\\"lang\\\": \\\"ru\\\"}',
        'var/log/access.log': '127.0.0.1 - - [15/Jan/2024] \\\"GET / HTTP/1.1\\\" 200'
    }

    return all_dirs, files

directories, files = create_deep_structure()

with zipfile.ZipFile('deep_vfs.zip', 'w') as zipf:
    # Создаем все директории
    for directory in directories:
        zipf.writestr(directory, '')

    # Создаем файлы
    for file_path, content in files.items():
        zipf.writestr(file_path, content)
"
echo.
echo Запуск эмулятора с глубокой структурой VFS...
python shell_emulator.py --vfs-path "./deep_vfs.zip" --log-file "./logs/deep_test.log" --startup-script "./scripts/test_deep.txt"

echo.
echo Тест 3 завершен.
del deep_vfs.zip
pause@echo off
chcp 65001 > nul
echo ===============================================
echo ЗАПУСК ВСЕХ ТЕСТОВ VFS
echo ===============================================

echo Создание директорий для логов...
if not exist "logs" mkdir logs
if not exist "scripts" mkdir scripts

echo.
call scripts\test_minimal_vfs.bat
echo.
call scripts\test_medium_vfs.bat
echo.
call scripts\test_large_vfs.bat

echo.
echo ===============================================
echo ВСЕ ТЕСТЫ VFS ЗАВЕРШЕНЫ
echo ===============================================
echo Проверьте логи в папке logs/
pause