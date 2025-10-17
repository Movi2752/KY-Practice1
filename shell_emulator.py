import argparse
from ShellEmulator import ShellEmulator


def parse_arguments():
        """Парсит аргументы командной строки для настройки эмулятора"""
        parser = argparse.ArgumentParser(
            description='Эмулятор командной строки с виртуальной файловой системой',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            '--vfs-path',
            required=True,
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

        return parser.parse_args()

def main():
    """Точка входа в приложение"""
    args = parse_arguments()

    # Отладочный вывод параметров (требование этапа)
    print("=" * 60)
    print("ПАРАМЕТРЫ ЗАПУСКА ЭМУЛЯТОРА:")
    print(f"  VFS путь: {args.vfs_path}")
    print(f"  Лог-файл: {args.log_file}")
    print(f"  Стартовый скрипт: {args.startup_script}")
    print("=" * 60)

    shell = ShellEmulator(
        vfs_path=args.vfs_path,
        log_file=args.log_file,
        startup_script=args.startup_script
    )
    shell.run()

if __name__ == "__main__":
    main()