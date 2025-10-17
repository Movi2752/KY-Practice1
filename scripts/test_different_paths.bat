@echo off
chcp 65001 > nul

echo ===============================================
echo Тест 3: Тестирование разных путей
echo ===============================================

echo Тест с абсолютными путями:
python shell_emulator.py --vfs-path "%CD%\vfs_absolute" --log-file "%CD%\logs\absolute_test.log"

echo.
echo Тест с путями в другой директории:
python shell_emulator.py --vfs-path "..\parent_vfs" --log-file "..\parent_logs\parent_test.log"

echo.
echo Тест 3 завершен.
pause