@echo off
chcp 65001 > nul
echo ===============================================
echo Тест 2: VFS с несколькими файлами
echo ===============================================

echo Создание VFS архива с несколькими файлами...
python -c "
import zipfile
import os

files_content = {
    'readme.txt': 'VFS с несколькими файлами и директориями',
    'home/user/documents/report.pdf': 'PDF документ (имитация)',
    'home/user/documents/data.xlsx': 'Excel файл с данными',
    'home/user/images/photo.jpg': 'Изображение (имитация)',
    'home/user/code/main.py': 'print(\\\"Hello VFS!\\\")',
    'home/user/code/utils.py': 'def helper():\\n    return \\\"helper function\\\"',
    'var/log/system.log': '2024-01-15 INFO: System started',
    'etc/config.json': '{\\\"version\\\": \\\"1.0\\\", \\\"debug\\\": true}',
    'tmp/cache.tmp': 'Временные данные'
}

with zipfile.ZipFile('medium_vfs.zip', 'w') as zipf:
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
"
echo.
echo Запуск эмулятора с VFS среднего размера...
python shell_emulator.py --vfs-path "./medium_vfs.zip" --log-file "./logs/medium_test.log" --startup-script "./scripts/test_medium.txt"

echo.
echo Тест 2 завершен.
del medium_vfs.zip
pause