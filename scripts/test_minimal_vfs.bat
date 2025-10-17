@echo off
chcp 65001 > nul
echo ===============================================
echo Тест 1: Минимальная VFS
echo ===============================================

echo Создание минимального VFS архива...
python -c "
import zipfile
with zipfile.ZipFile('minimal_vfs.zip', 'w') as zipf:
    zipf.writestr('readme.txt', 'Минимальная VFS для тестирования')
    zipf.writestr('home/', '')
    zipf.writestr('home/user/', '')
    zipf.writestr('home/user/test.txt', 'Тестовый файл')
"
echo.
echo Запуск эмулятора с минимальной VFS...
python shell_emulator.py --vfs-path "./minimal_vfs.zip" --log-file "./logs/minimal_test.log" --startup-script "./scripts/test_minimal.txt"

echo.
echo Тест 1 завершен.
del minimal_vfs.zip
pause