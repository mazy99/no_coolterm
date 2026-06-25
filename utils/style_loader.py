

from .get_resource_path import get_resource_path

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