import os
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import zipfile
import base64
import io


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
import time
import base64


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class VFSNode:
    """Узел виртуальной файловой системы"""
    name: str
    type: FileType
    content: str = ""
    children: Dict[str, 'VFSNode'] = None
    permissions: str = "rw-r--r--"
    owner: str = "user"
    group: str = "user"
    size: int = 0
    created_time: float = None
    modified_time: float = None
    is_binary: bool = False  # Флаг бинарного файла

    def __post_init__(self):
        if self.children is None and self.type == FileType.DIRECTORY:
            self.children = {}
        if self.created_time is None:
            self.created_time = time.time()
        if self.modified_time is None:
            self.modified_time = time.time()
        if self.type == FileType.FILE:
            if self.is_binary:
                # Для бинарных файлов в base64, размер в байтах после декодирования
                try:
                    decoded_size = len(base64.b64decode(self.content))
                    self.size = decoded_size
                except:
                    self.size = len(self.content)
            else:
                self.size = len(self.content.encode('utf-8'))

    def add_child(self, child: 'VFSNode') -> bool:
        """Добавляет дочерний узел"""
        if self.type != FileType.DIRECTORY:
            return False
        if child.name in self.children:
            return False
        self.children[child.name] = child
        self.modified_time = time.time()
        return True

    def remove_child(self, name: str) -> bool:
        """Удаляет дочерний узел по имени"""
        if self.type != FileType.DIRECTORY:
            return False
        if name not in self.children:
            return False
        del self.children[name]
        self.modified_time = time.time()
        return True

    def get_child(self, name: str) -> Optional['VFSNode']:
        """Возвращает дочерний узел по имени"""
        if self.type != FileType.DIRECTORY:
            return None
        return self.children.get(name)

    def list_children(self) -> list:
        """Возвращает список дочерних узлов"""
        if self.type != FileType.DIRECTORY:
            return []
        return list(self.children.values())

    def get_info(self) -> Dict:
        """Возвращает информацию об узле в виде словаря"""
        return {
            'name': self.name,
            'type': self.type.value,
            'permissions': self.permissions,
            'owner': self.owner,
            'group': self.group,
            'size': self.size,
            'is_binary': self.is_binary,
            'created_time': self.created_time,
            'modified_time': self.modified_time,
            'is_directory': self.type == FileType.DIRECTORY,
            'children_count': len(self.children) if self.type == FileType.DIRECTORY else 0
        }

    def update_content(self, new_content: str, is_binary: bool = False) -> bool:
        """Обновляет содержимое файла"""
        if self.type != FileType.FILE:
            return False

        self.content = new_content
        self.is_binary = is_binary
        self.modified_time = time.time()

        # Обновляем размер
        if is_binary:
            try:
                decoded_size = len(base64.b64decode(new_content))
                self.size = decoded_size
            except:
                self.size = len(new_content)
        else:
            self.size = len(new_content.encode('utf-8'))

        return True

    def rename(self, new_name: str) -> bool:
        """Переименовывает узел"""
        if not new_name or '/' in new_name:
            return False
        self.name = new_name
        self.modified_time = time.time()
        return True

    def change_permissions(self, new_permissions: str) -> bool:
        """Изменяет права доступа"""
        # Простая валидация формата прав доступа
        if len(new_permissions) != 9 or not all(c in 'rwx-' for c in new_permissions):
            return False
        self.permissions = new_permissions
        self.modified_time = time.time()
        return True

    def change_owner(self, new_owner: str, new_group: str = None) -> bool:
        """Изменяет владельца и группу"""
        if not new_owner:
            return False
        self.owner = new_owner
        if new_group:
            self.group = new_group
        self.modified_time = time.time()
        return True

    def is_directory(self) -> bool:
        """Проверяет, является ли узел директорией"""
        return self.type == FileType.DIRECTORY

    def is_file(self) -> bool:
        """Проверяет, является ли узел файлом"""
        return self.type == FileType.FILE

    def is_hidden(self) -> bool:
        """Проверяет, является ли файл скрытым (начинается с точки)"""
        return self.name.startswith('.')

    def get_formatted_time(self, time_format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Возвращает время в отформатированном виде"""
        return time.strftime(time_format, time.localtime(self.modified_time))

    def get_formatted_size(self) -> str:
        """Возвращает размер в удобочитаемом формате"""
        if self.size == 0:
            return "0"
        sizes = ['B', 'KB', 'MB', 'GB']
        i = 0
        size = float(self.size)
        while size >= 1024 and i < len(sizes) - 1:
            size /= 1024
            i += 1
        return f"{size:.1f}{sizes[i]}" if i > 0 else f"{int(size)}{sizes[i]}"

    def __str__(self) -> str:
        """Строковое представление узла"""
        type_char = 'd' if self.is_directory() else '-'
        return f"{type_char}{self.permissions} {self.owner:>8} {self.group:>8} {self.size:>8} {self.name}"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"VFSNode(name='{self.name}', type={self.type.value}, size={self.size})"


class VirtualFileSystem:
    """Виртуальная файловая система в памяти, загружаемая из ZIP-архива"""

    def __init__(self, vfs_path: str, force_reload: bool = False):
        self.vfs_path = vfs_path
        self.root = VFSNode("/", FileType.DIRECTORY)
        self.current_directory = self.root

        # Определяем тип VFS: ZIP архив или память
        self.is_zip_archive = self._check_if_zip_archive(vfs_path)

        # Загружаем VFS
        self._load_vfs(force_reload)

    def _check_if_zip_archive(self, path: str) -> bool:
        """Проверяет, является ли путь ZIP архивом"""
        # Если путь заканчивается на .zip, считаем его архивом
        if path.lower().endswith('.zip'):
            return True
        # Если файл существует, проверяем его сигнатуру
        if os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    # Проверяем сигнатуру ZIP файла (первые 4 байта)
                    signature = f.read(4)
                    return signature == b'PK\x03\x04'
            except:
                return False
        return False

    def _load_vfs(self, force_reload: bool = False):
        """Загружает VFS из архива или создает пустую"""
        if self.is_zip_archive:
            self._load_from_zip(force_reload)
        else:
            # Если это не ZIP-архив, создаем пустую VFS в памяти
            print(f"Создана пустая VFS в памяти (путь: {self.vfs_path})")
            self._create_empty_vfs()

    def _load_from_zip(self, force_reload: bool = False):
        """Загружает структуру VFS из ZIP-архива"""
        if not os.path.exists(self.vfs_path):
            print(f"ZIP архив '{self.vfs_path}' не найден. Создана пустая VFS.")
            self._create_empty_vfs()
            return

        try:
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
                # Сначала создаем все директории
                for file_info in zip_ref.filelist:
                    if file_info.is_dir():
                        self._create_directory_structure(file_info.filename)

                # Затем создаем файлы с содержимым
                for file_info in zip_ref.filelist:
                    if not file_info.is_dir():
                        self._create_file_from_zip(zip_ref, file_info)

            print(f"VFS успешно загружена из архива: {self.vfs_path}")

        except zipfile.BadZipFile:
            print(f"Ошибка: файл '{self.vfs_path}' не является корректным ZIP архивом")
            self._create_empty_vfs()
        except PermissionError:
            print(f"Ошибка доступа: нет прав для чтения файла '{self.vfs_path}'")
            self._create_empty_vfs()
        except Exception as e:
            print(f"Ошибка загрузки VFS из архива: {e}")
            self._create_empty_vfs()

    def reload_vfs(self):
        """Перезагружает VFS из архива"""
        # Очищаем текущую структуру
        self.root = VFSNode("/", FileType.DIRECTORY)
        self.current_directory = self.root

        # Загружаем заново
        self._load_from_zip(force_reload=True)

    def _create_directory_structure(self, zip_path: str):
        """Создает структуру директорий из пути в ZIP"""
        components = self._normalize_zip_path(zip_path)
        if not components:
            return

        current_node = self.root
        for component in components:
            if component not in current_node.children:
                node = VFSNode(
                    name=component,
                    type=FileType.DIRECTORY,
                    owner="user",
                    group="user",
                    permissions="rwxr-xr-x"
                )
                current_node.children[component] = node
            current_node = current_node.children[component]

    def _create_file_from_zip(self, zip_ref: zipfile.ZipFile, file_info: zipfile.ZipInfo):
        """Создает файл в VFS из ZIP архива"""
        try:
            components = self._normalize_zip_path(file_info.filename)
            if not components:
                return

            filename = components[-1]
            parent_components = components[:-1]

            # Находим родительскую директорию
            parent_node = self.root
            for component in parent_components:
                if component in parent_node.children:
                    parent_node = parent_node.children[component]
                else:
                    print(f"Предупреждение: не найдена родительская директория для {file_info.filename}")
                    return

            # Читаем содержимое файла
            with zip_ref.open(file_info.filename) as file:
                content = file.read()

                # Для текстовых файлов пробуем декодировать как текст
                try:
                    # Пробуем UTF-8
                    text_content = content.decode('utf-8')
                    is_binary = False
                except UnicodeDecodeError:
                    # Если не UTF-8, кодируем в base64
                    text_content = base64.b64encode(content).decode('ascii')
                    is_binary = True

                # Создаем узел файла
                node = VFSNode(
                    name=filename,
                    type=FileType.FILE,
                    content=text_content,
                    owner="user",
                    group="user",
                    permissions="rw-r--r--",
                    size=len(content),
                    is_binary=is_binary  # Добавляем флаг бинарного файла
                )
                parent_node.children[filename] = node

        except Exception as e:
            print(f"Ошибка создания файла {file_info.filename}: {e}")

    def create_default_vfs_archive(archive_path: str = "default_vfs.zip"):
        """Создает VFS архив по умолчанию"""
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Создаем стандартную структуру директорий
                directories = [
                    "home/",
                    "home/user/",
                    "home/user/documents/",
                    "home/user/downloads/",
                    "home/user/desktop/",
                    "etc/",
                    "tmp/",
                    "var/",
                    "var/log/"
                ]

                for directory in directories:
                    zipf.writestr(directory, "")

                # Создаем стандартные файлы
                files_content = {
                    "readme.txt": """Добро пожаловать в виртуальную файловую систему!

    Эта VFS была инициализирована командой vfs-init.

    Доступные команды:
    - ls: список файлов
    - cd: смена директории
    - pwd: текущий путь
    - echo: вывод текста
    - vfs-init: сброс VFS

    Для выхода используйте команду 'exit'.""",

                    "home/user/.bashrc": """# Файл настройки оболочки
    echo "VFS оболочка загружена"
    export VFS_VERSION="1.0"
    PS1='\\u@vfs:\\w\\$ '""",

                    "home/user/welcome.txt": "Добро пожаловать в вашу домашнюю директорию!",

                    "etc/motd": "Добро пожаловать в эмулятор VFS!",

                    "var/log/vfs.log": "# Лог-файл VFS\n# Создан при инициализации системы"
                }

                for file_path, content in files_content.items():
                    zipf.writestr(file_path, content)

            print(f"Создан архив VFS по умолчанию: {archive_path}")
            return archive_path

        except Exception as e:
            print(f"Ошибка создания архива по умолчанию: {e}")
            return None

    def _normalize_zip_path(self, zip_path: str) -> List[str]:
        """Нормализует путь из ZIP архива"""
        # Убираем ведущий слеш и разбиваем на компоненты
        path = zip_path.rstrip('/')
        components = [comp for comp in path.split('/') if comp]
        return components

    def _create_empty_vfs(self):
        """Создает минимальную структуру VFS"""
        home_dir = VFSNode("home", FileType.DIRECTORY)
        user_dir = VFSNode("user", FileType.DIRECTORY)
        home_dir.children["user"] = user_dir
        self.root.children["home"] = home_dir
        self.current_directory = self.root  # Устанавливаем текущую директорию в корень

    def _create_node(self, name: str, node_type: FileType, parent: VFSNode, content: str = "") -> VFSNode:
        """Создает новый узел в VFS"""
        node = VFSNode(
            name=name,
            type=node_type,
            content=content,
            owner="user",
            group="user",
            permissions="rw-r--r--" if node_type == FileType.FILE else "rwxr-xr-x"
        )
        parent.children[name] = node
        return node

    def read_file_content(self, path: str) -> Optional[Union[str, bytes]]:
        """Читает содержимое файла, возвращает текст или бинарные данные"""
        node = self.resolve_path(path)

        if not node or node.type != FileType.FILE:
            return None

        if node.is_binary:
            # Декодируем base64 обратно в бинарные данные
            try:
                return base64.b64decode(node.content)
            except Exception as e:
                print(f"Ошибка декодирования бинарного файла: {e}")
                return None
        else:
            return node.content

    def get_file_info(self, path: str) -> Optional[Dict]:
        """Возвращает информацию о файле"""
        node = self.resolve_path(path)

        if not node:
            return None

        return {
            'name': node.name,
            'type': node.type.value,
            'permissions': node.permissions,
            'owner': node.owner,
            'group': node.group,
            'size': node.size,
            'is_binary': node.is_binary,
            'modified_time': node.modified_time,
            'created_time': node.created_time
        }

    def get_current_path(self) -> str:
        """Возвращает текущий путь в VFS"""
        if self.current_directory == self.root:
            return "/"

        # Собираем путь от корня до текущей директории
        path_components = []
        current = self.current_directory

        while current != self.root:
            # Находим родителя текущего узла
            parent = self._find_parent(self.root, current)
            if parent:
                # Находим имя текущего узла в родителе
                for name, node in parent.children.items():
                    if node == current:
                        path_components.append(name)
                        break
                current = parent
            else:
                break

        return "/" + "/".join(reversed(path_components))

    def _find_parent(self, current: VFSNode, target: VFSNode) -> Optional[VFSNode]:
        """Рекурсивно ищет родительскую директорию для целевого узла"""
        for child in current.children.values():
            if child == target:
                return current
            if child.type == FileType.DIRECTORY:
                found = self._find_parent(child, target)
                if found:
                    return found
        return None

    def resolve_path(self, path: str) -> Optional[VFSNode]:
        """Разрешает путь и возвращает соответствующий узел"""
        if not path or path == '.':
            return self.current_directory

        if path == '..':
            parent = self._find_parent(self.root, self.current_directory)
            return parent or self.current_directory

        components = self.get_absolute_path(path)
        current_node = self.current_directory if not path.startswith('/') else self.root

        for component in components:
            if component == '..':
                current_node = self._find_parent(self.root, current_node) or current_node
            elif component == '.':
                continue
            elif component in current_node.children:
                current_node = current_node.children[component]
            else:
                return None  # Путь не найден

        return current_node

    def get_absolute_path(self, path: str) -> List[str]:
        """Преобразует путь в список компонентов"""
        if path.startswith('/'):
            components = path.split('/')[1:]
        else:
            components = path.split('/')
        return [comp for comp in components if comp]  # Убираем пустые компоненты

    def list_directory(self, path: str = "") -> List[Dict]:
        """Возвращает список файлов и директорий по указанному пути"""
        target_node = self.resolve_path(path) if path else self.current_directory

        if not target_node or target_node.type != FileType.DIRECTORY:
            return []

        entries = []
        for name, node in target_node.children.items():
            entries.append({
                'name': name,
                'type': node.type.value,
                'permissions': node.permissions,
                'owner': node.owner,
                'group': node.group,
                'size': node.size,
                'modified_time': node.modified_time,
                'node': node  # Добавляем ссылку на узел для простого доступа
            })

        return entries

    def change_directory(self, path: str) -> bool:
        """Изменяет текущую директорию"""
        target_node = self.resolve_path(path)

        if not target_node:
            return False

        if target_node.type != FileType.DIRECTORY:
            return False

        self.current_directory = target_node
        return True