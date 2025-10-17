@echo off
chcp 65001 > nul

echo ===============================================
echo Тест 4: Тестирование обработки ошибок
echo ===============================================

echo Тест без обязательных параметров:
python shell_emulator.py

echo.
echo Тест без --vfs-path:
python shell_emulator.py --log-file "./logs/test.log"

echo.
echo Тест без --log-file:
python shell_emulator.py --vfs-path "./test_vfs"

echo.
echo Тест с несуществующим стартовым скриптом:
python shell_emulator.py --vfs-path "./test_vfs" --log-file "./logs/error_test.log" --startup-script "./nonexistent_script.txt"

echo.
echo Тест 4 завершен.
pause