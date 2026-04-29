# МОДУЛЬ РАБОТЫ С БАЗОЙ ДАННЫХ ДЛЯ ИГРЫ "ЗМЕЙКА"
# Сохраняет результаты игроков и ведёт таблицу рекордов

import psycopg2  # Драйвер для работы с PostgreSQL (подключение и запросы)
from datetime import datetime  # Класс для работы с датой и временем

# КЛАСС ДЛЯ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ
class Database:
    def __init__(self):
        """Конструктор - устанавливает соединение с PostgreSQL при создании объекта"""
        try:
            # ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
            # Параметры подключения (localhost - локальный сервер, порт по умолчанию 5432)
            self.conn = psycopg2.connect(
                host='localhost',        # Адрес сервера БД (локальный компьютер)
                database='snake_game',   # Имя базы данных
                user='postgres',         # Имя пользователя PostgreSQL
                password='Nurtore2008'   # Пароль пользователя (НЕ БЕЗОПАСНО хранить в коде!)
            )
            # СОЗДАЁМ КУРСОР - объект для выполнения SQL-запросов
            self.cursor = self.conn.cursor()
            print("✓ Database connected!")  # Сообщение об успешном подключении
            
        except Exception as e:
            # Если произошла ошибка (неверный пароль, БД не запущена, нет сети)
            print(f"✗ Database error: {e}")
            # Устанавливаем соединение и курсор в None (невалидное состояние)
            self.conn = None
            self.cursor = None
    
    def get_or_create_player(self, username):
        """Находит игрока по имени или создаёт нового
           Возвращает ID игрока (число)
           
           Алгоритм:
           1. Ищем игрока с таким username
           2. Если нашли - возвращаем его ID
           3. Если не нашли - создаём нового и возвращаем новый ID
        """
        # Если нет соединения с БД - возвращаем ID по умолчанию (1)
        if not self.cursor:
            return 1
        
        try:
            # 1. ПОИСК ИГРОКА
            # %s - плейсхолдер, защищает от SQL-инъекций
            self.cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            result = self.cursor.fetchone()  # Получаем первую строку результата
            
            if result:
                # ИГРОК СУЩЕСТВУЕТ - возвращаем его ID (первый элемент кортежа)
                return result[0]
            else:
                # 2. СОЗДАНИЕ НОВОГО ИГРОКА
                # RETURNING id - возвращает автоматически сгенерированный ID
                self.cursor.execute(
                    "INSERT INTO players (username) VALUES (%s) RETURNING id", 
                    (username,)
                )
                player_id = self.cursor.fetchone()[0]  # Извлекаем ID из результата
                self.conn.commit()  # ФИКСИРУЕМ изменения (сохраняем в БД)
                return player_id
                
        except Exception:
            # При любой ошибке (например, нарушение уникальности) возвращаем ID=1
            return 1
    
    def save_game_session(self, player_id, score, level_reached):
        """Сохраняет результат игровой сессии в таблицу game_sessions
           Аргументы:
           - player_id: ID игрока из таблицы players
           - score: набранные очки
           - level_reached: достигнутый уровень
        """
        # Если нет соединения - выходим (ничего не сохраняем)
        if not self.cursor:
            return
        
        try:
            # ВСТАВКА НОВОЙ ЗАПИСИ
            # played_at автоматически установится как CURRENT_TIMESTAMP в БД
            self.cursor.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                (player_id, score, level_reached)
            )
            self.conn.commit()  # Сохраняем изменения
        except Exception:
            # Игнорируем ошибки (не прерываем игру из-за проблем с БД)
            pass
    
    def get_leaderboard(self):
        """Возвращает таблицу лидеров (топ-10 по очкам)
           Результат: список кортежей вида
           (username, score, level_reached, played_at)
        """
        # Если нет соединения - возвращаем пустой список
        if not self.cursor:
            return []
        
        try:
            # СЛОЖНЫЙ ЗАПРОС С JOIN
            # Выбираем: имя игрока, очки, уровень, дату игры
            # FROM game_sessions gs - основная таблица (псевдоним gs)
            # JOIN players p - присоединяем таблицу игроков (псевдоним p)
            # ON gs.player_id = p.id - условие соединения
            # ORDER BY gs.score DESC - сортировка по очкам от большего к меньшему
            # LIMIT 10 - только первые 10 записей
            self.cursor.execute("""
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return self.cursor.fetchall()  # Возвращаем все строки результата
            
        except Exception:
            return []  # При ошибке - пустой список
    
    def get_personal_best(self, player_id):
        """Возвращает лучший результат (максимальные очки) для конкретного игрока"""
        # Если нет соединения - возвращаем 0
        if not self.cursor:
            return 0
        
        try:
            # MAX(score) - агрегатная функция, возвращает максимальное значение
            self.cursor.execute(
                "SELECT MAX(score) FROM game_sessions WHERE player_id = %s", 
                (player_id,)
            )
            result = self.cursor.fetchone()
            # Если результат есть и не None - возвращаем его, иначе 0
            return result[0] if result[0] else 0
            
        except Exception:
            return 0
    
    def close(self):
        """Закрывает соединение с базой данных (освобождает ресурсы)"""
        if self.conn:
            self.conn.close()  # Закрываем соединение с PostgreSQL