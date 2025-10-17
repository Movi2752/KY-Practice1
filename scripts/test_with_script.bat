@echo off
chcp 65001 > nul

echo ===============================================
echo Тест 2: Запуск со стартовым скриптом
echo ===============================================

:: Создаем тестовый стартовый скрипт
echo # Стартовый скрипт для тестирования > startup.txt
echo echo "Тестирование стартового скрипта" >> startup.txt
echo echo "Пользователь: %USERNAME%" >> startup.txt
echo echo "Домашняя папка: %USERPROFILE%" >> startup.txt
echo ls -la >> test_startup.txt
echo env >> test_startup.txt

python shell_emulator.py --vfs-path "./test_vfs2" --log-file "./logs/script_test.log" --startup-script "./startup.txt"

echo.
echo Тест 2 завершен. Проверьте файл script_test.log
del test_startup.txt
pause