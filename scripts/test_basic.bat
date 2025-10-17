@echo off
chcp 65001 > nul
echo ===============================================
echo Тест 1: Базовый запуск эмулятора
echo ===============================================

python shell_emulator.py --vfs-path "./test_vfs" --log-file "./logs/basic_test.log"

echo.
echo Тест 1 завершен. Проверьте файл basic_test.log
pause