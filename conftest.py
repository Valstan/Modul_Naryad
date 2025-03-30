# conftest.py (в корне проекта)
import sys
from pathlib import Path

# Добавляем корневую директорию в путь поиска модулей
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))