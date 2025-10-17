import csv
from datetime import datetime


class Logger:
    """Класс для логирования событий в CSV формате"""

    def __init__(self, log_file, username):
        self.log_file = log_file
        self.username = username
        self._ensure_log_directory()
        self._init_log_file()

    def _ensure_log_directory(self):
        """Создает директорию для лог-файла если нужно"""
        import os
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    def _init_log_file(self):
        """Инициализирует лог-файл с заголовками CSV"""
        import os
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'username', 'command', 'arguments', 'error_message'])

    def log_event(self, command, arguments="", error_message=""):
        """Логирует событие в CSV файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, self.username, command, arguments, error_message])
        except Exception as e:
            print(f"Ошибка записи в лог-файл: {e}")