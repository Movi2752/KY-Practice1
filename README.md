# Эмулятор командной строки с VFS

## Этап 1: REPL

### Реализованная функциональность

#### ✅ Базовый CLI интерфейс
- Консольное приложение с циклом REPL (Read-Eval-Print Loop)
- Приглашение к вводу в формате: `myvfs:/$ `

#### ✅ Парсер команд с поддержкой переменных окружения
- Раскрытие переменных окружения реальной ОС:
  - `$HOME` / `${HOME}` - домашняя директория
  - `$USER` / `${USER}` - имя пользователя
  - `$USERNAME` / `${USERNAME}` - имя пользователя (Windows)
  - `$USERPROFILE` / `${USERPROFILE}` - профиль пользователя (Windows)
- Поддержка кавычек и специальных символов

#### ✅ Система команд
- **`ls [аргументы]`** - заглушка команды списка файлов
- **`cd [директория]`** - заглушка команды смены директории  
- **`echo [текст]`** - вывод текста с поддержкой переменных
- **`env`** - просмотр переменных окружения
- **`exit`** - выход из эмулятора

#### ✅ Обработка ошибок
- Сообщения о неизвестных командах
- Обработка ошибок парсинга
- Защита от KeyboardInterrupt и EOFError

### Демонстрация работы

#### Пример сессии работы эмулятора:

```bash
$ python shell_emulator.py
Добро пожаловать в эмулятор командной строки!
Введите 'exit' для выхода
Доступные команды: ls, cd, echo, env, exit
----------------------------------------
myvfs:/$ echo "Добро пожаловать в VFS!"
Добро пожаловать в VFS!

myvfs:/$ env
Переменные окружения:
  HOME: C:/Users/Admin
  USERPROFILE: C:/Users/Admin
  USER: не установлена
  USERNAME: Admin
  PWD: D:/project/path

myvfs:/$ echo "Мой домашний каталог: $HOME"
Мой домашний каталог: C:/Users/Admin

myvfs:/$ echo Пользователь: ${USERNAME}
Пользователь: Admin

myvfs:/$ ls -la
Команда: ls, Аргументы: ['-la']

myvfs:/$ cd documents
Команда: cd, Аргументы: ['documents']

myvfs:/$ unknown_command
unknown_command: команда не найдена

myvfs:/$ exit
Выход из эмулятора
```

#### Особенности реализации:
- **Кросс-платформенность** - корректная работа с путями Windows (замена `\` на `/`)
- **Устойчивость** - обработка исключений ввода/вывода
- **Расширяемость** - простая структура для добавления новых команд

### Структура проекта
```
project/
├── main.py  # Основной файл эмулятора
└── README.md          # Документация
```

## Этап 2: Конфигурация

### Реализованная функциональность

#### ✅ Параметры командной строки
- `--vfs-path` - путь к физическому расположению VFS (обязательный)
- `--log-file` - путь к лог-файлу (обязательный) 
- `--startup-script` - путь к стартовому скрипту (опциональный)

#### ✅ Логирование в CSV формате
- Запись всех событий в CSV файл с колонками:
  - `timestamp` - временная метка
  - `username` - имя пользователя ОС
  - `command` - выполненная команда
  - `arguments` - аргументы команды
  - `error_message` - сообщение об ошибке (если есть)

#### ✅ Стартовые скрипты
- Поддержка комментариев (символ `#`)
- Имитация диалога с пользователем (отображение ввода и вывода)
- Обработка ошибок выполнения скрипта
- Команда `run` для выполнения скриптов в интерактивном режиме

#### ✅ Система тестирования
- Набор bat-скриптов для Windows
- Тестирование всех параметров командной строки
- Автоматическое создание необходимых директорий

### Использование

#### Базовый запуск:
```bash
python shell_emulator.py --vfs-path ./my_vfs --log-file ./logs/shell.log
```

#### Запуск со стартовым скриптом:
```bash
python shell_emulator.py --vfs-path ./my_vfs --log-file ./logs/shell.log --startup-script ./scripts/startup.txt
```

#### Просмотр справки:
```bash
python shell_emulator.py --help
```

### Примеры

#### Пример лог-файла (shell.log):
```csv
timestamp,username,command,arguments,error_message
2024-01-15 10:30:15,Admin,SYSTEM_START,"VFS: ./my_vfs, Script: None",
2024-01-15 10:30:20,Admin,ls,-la,
2024-01-15 10:30:25,Admin,echo,"Привет, $USERNAME!",
2024-01-15 10:30:30,Admin,unknown_cmd,,unknown_cmd: команда не найдена
2024-01-15 10:30:35,Admin,exit,,
```

#### Пример стартового скрипта (startup.txt):
```bash
# Стартовый скрипт для эмулятора VFS
echo "=== Запуск эмулятора ==="
echo "Пользователь: $USERNAME"
env
ls -la
echo "=== Готов к работе ==="
```

#### Пример сессии со стартовым скриптом:
```bash
$ python shell_emulator.py --vfs-path ./vfs --log-file ./logs/session.log --startup-script ./scripts/demo.txt

ПАРАМЕТРЫ ЗАПУСКА ЭМУЛЯТОРА:
  VFS путь: ./vfs
  Лог-файл: ./logs/session.log
  Стартовый скрипт: ./scripts/demo.txt

Выполнение стартового скрипта...

=== Выполнение скрипта: ./scripts/demo.txt ===
# Демонстрационный скрипт
myvfs:/$ echo "Привет, $USERNAME!"
Привет, Admin!
myvfs:/$ ls -la
file1.txt  file2.txt  documents/
myvfs:/$ env
Переменные окружения:
  HOME: C:/Users/Admin
  USERNAME: Admin
----------------------------------------
myvfs:/$ 
```

### Структура проекта после Этапа 2
```
project/
├── shell_emulator.py      # Основной файл выполнения
├── Shell_emulator.py      # Файл эмулятора
├── Logger.py              # Класс для логирования событий
├── scripts/               # Тестовые скрипты
│   ├── test_basic.bat
│   ├── test_with_script.bat
│   ├── test_different_paths.bat
│   ├── test_error_cases.bat
│   ├── run_all_tests.bat
│   └── demo_script.txt
├── logs/                  # Директория для логов
├── test_vfs/             # Тестовые VFS директории
├── test_vfs2/
└── README.md
```

### Запуск тестов
```bash
# Запуск всех тестов (из командной строки cmd)
scripts\run_all_tests.bat

# Или запуск отдельных тестов
scripts\test_basic.bat
scripts\test_with_script.bat
```


## Этап 3: VFS (Виртуальная файловая система)

### Реализованная функциональность

#### ✅ VFS в памяти
- Полностью виртуальная файловая система, работающая в оперативной памяти
- Поддержка файлов и директорий с метаданными (права доступа, владелец, размер, время изменения)
- Иерархическая структура с неограниченной вложенностью

#### ✅ Загрузка VFS из ZIP-архивов
- Автоматическое определение типа VFS (ZIP архив или память)
- Поддержка бинарных файлов через кодирование base64
- Текстовые файлы сохраняются в исходной кодировке
- Обработка ошибок загрузки архивов

#### ✅ Команда vfs-init
- Сброс VFS к состоянию по умолчанию
- Автоматическое создание архивов VFS при необходимости
- Очистка текущего состояния и загрузка стандартной структуры

#### ✅ Расширенная навигация по VFS
- Поддержка абсолютных и относительных путей
- Команды `cd`, `ls`, `pwd` для работы с виртуальной файловой системой
- Навигация по сложным структурам с 3+ уровнями вложенности

### Команды VFS

- **`ls [путь]`** - список файлов и директорий в VFS
- **`cd [путь]`** - смена текущей директории в VFS  
- **`pwd`** - вывод текущего пути в VFS
- **`vfs-init`** - сброс VFS к состоянию по умолчанию

### Тестовые сценарии

#### Стартовые команды для тестирования:

1. **Минимальная VFS:**
```bash
python shell_emulator.py --create-test minimal --log-file ./logs/minimal.log
```

2. **VFS среднего размера:**
```bash
python shell_emulator.py --create-test medium --log-file ./logs/medium.log
```

3. **Глубокая VFS (3+ уровня):**
```bash
python shell_emulator.py --create-test deep --log-file ./logs/deep.log
```

4. **Создать все тестовые VFS:**
```bash
python shell_emulator.py --create-test all --log-file ./logs/test.log
```

5. **Комплексное тестирование всех команд:**
```bash
python shell_emulator.py --create-test comprehensive --log-file ./logs/comprehensive_test.log
```

6. **Использовать существующую VFS:**
```bash
python shell_emulator.py --vfs-path ./minimal_vfs.zip --log-file ./logs/custom.log --startup-script ./scripts/test_minimal.txt
```

### Структура проекта после Этапа 3
```
project/
├── shell_emulator.py      # Основной файл эмулятора
├── ShellEmulator.py       # Класс эмулятора
├── FileType.py            # Классы VFSNode и VirtualFileSystem
├── scripts/               # Тестовые скрипты
│   ├── test_minimal.txt
│   ├── test_medium.txt
│   ├── test_deep.txt
│   └── comprehensive_test.txt
├── minimal_vfs.zip        # Тестовые VFS архивы
├── medium_vfs.zip
├── deep_vfs.zip
├── logs/                  # Директория для логов
└── README.md
```

### Пример работы с VFS
```
myvfs:/$ ls
home/    readme.txt    etc/    var/
myvfs:/$ cd home/user
myvfs:/home/user$ ls
documents/    downloads/    welcome.txt
myvfs:/home/user$ cd documents/projects/vfs_emulator
myvfs:/home/user/documents/projects/vfs_emulator$ pwd
/home/user/documents/projects/vfs_emulator
myvfs:/home/user/documents/projects/vfs_emulator$ vfs-init
VFS успешно сброшена к состоянию по умолчанию
```
