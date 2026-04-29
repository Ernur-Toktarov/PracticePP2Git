# МОДУЛЬ УПРАВЛЕНИЯ НАСТРОЙКАМИ ДЛЯ ИГРЫ "ЗМЕЙКА"
import json  # Модуль для работы с JSON (сохранение/загрузка настроек)
import os    # Модуль для работы с файловой системой (проверка существования файлов)

# КЛАСС ДЛЯ ХРАНЕНИЯ И УПРАВЛЕНИЯ НАСТРОЙКАМИ ИГРЫ
class Config:
    def __init__(self):
        # ИМЯ ФАЙЛА ДЛЯ СОХРАНЕНИЯ НАСТРОЕК (в текущей директории)
        self.config_file = 'settings.json'
        
        # ЗНАЧЕНИЯ НАСТРОЕК ПО УМОЛЧАНИЮ
        self.snake_color = (0, 255, 0)    # Цвет змейки: зелёный (RGB)
        self.grid_overlay = True           # Отображать сетку на игровом поле
        self.sound_on = True               # Звук включён
        
        # ЗАГРУЖАЕМ СОХРАНЁННЫЕ НАСТРОЙКИ (если есть)
        self.load_settings()
        
    def load_settings(self):
        """Загружает настройки из JSON файла, если он существует"""
        try:
            # ПРОВЕРЯЕМ, СУЩЕСТВУЕТ ЛИ ФАЙЛ
            if os.path.exists(self.config_file):
                # Открываем файл для чтения
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)  # Преобразуем JSON в словарь Python
                    
                    # ЗАГРУЖАЕМ КАЖДУЮ НАСТРОЙКУ (с защитой от отсутствия ключей)
                    # settings.get('snake_color', [0, 255, 0]) - если ключа нет, используем значение по умолчанию
                    # tuple(...) - преобразуем список из JSON обратно в кортеж
                    self.snake_color = tuple(settings.get('snake_color', [0, 255, 0]))
                    
                    # Загружаем остальные настройки (булевы значения)
                    self.grid_overlay = settings.get('grid_overlay', True)
                    self.sound_on = settings.get('sound_on', True)
        except:
            # Если произошла ошибка (битый файл, неверный формат) - просто игнорируем
            # Настройки остаются со значениями по умолчанию
            pass
    
    def save_settings(self):
        """Сохраняет текущие настройки в JSON файл"""
        try:
            # СОЗДАЁМ СЛОВАРЬ ДЛЯ СОХРАНЕНИЯ
            settings = {
                # Преобразуем кортеж цвета в список (JSON не поддерживает кортежи)
                'snake_color': list(self.snake_color),
                'grid_overlay': self.grid_overlay,
                'sound_on': self.sound_on
            }
            
            # Открываем файл для записи
            with open(self.config_file, 'w') as f:
                # Записываем настройки в JSON с отступами для читаемости
                json.dump(settings, f, indent=4)
        except:
            # Если произошла ошибка (нет прав на запись) - игнорируем
            pass