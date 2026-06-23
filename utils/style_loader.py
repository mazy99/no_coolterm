import os
import sys

def get_resource_path(relative_path):
    """ Возвращает абсолютный путь к ресурсу, учитывая сборку PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Если запущено внутри .exe, PyInstaller распаковывает всё в sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # Если запущено в режиме разработки из папки проекта
    return os.path.join(os.path.abspath("."), relative_path)

def load_stylesheet(path_to_qss):
    """ Функция загрузки стилей, которая теперь не ломается в .exe """
    # Перенаправляем относительный путь через наш обработчик
    resolved_path = get_resource_path(path_to_qss)
    
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[WARN] Файл стилей не найден по пути: {resolved_path}")
        return ""