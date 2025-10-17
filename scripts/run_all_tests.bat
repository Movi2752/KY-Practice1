@echo off
chcp 65001 > nul

echo ===============================================
echo ЗАПУСК ВСЕХ ТЕСТОВ ЭМУЛЯТОРА
echo ===============================================

echo Создание необходимых директорий...
if not exist "logs" mkdir logs
if not exist "test_vfs" mkdir test_vfs
if not exist "test_vfs2" mkdir test_vfs2

echo.
call scripts\test_basic.bat
echo.
call scripts\test_with_script.bat
echo.
call scripts\test_different_paths.bat
echo.
call scripts\test_error_cases.bat

echo.
echo ===============================================
echo ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ
echo ===============================================
echo Проверьте логи в папке logs/
pause