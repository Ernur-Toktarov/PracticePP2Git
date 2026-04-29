# МОДУЛЬ ОСНОВНОЙ ЛОГИКИ ИГРЫ "ЗМЕЙКА"
import pygame
import random

# КЛАСС ИГРЫ ЗМЕЙКА
class SnakeGame:
    def __init__(self, screen, config, db, player_id, username):
        """Конструктор игры. Получает экран, настройки, БД, ID игрока и имя"""
        self.screen = screen
        self.config = config      # Настройки (цвет змейки, сетка, звук)
        self.db = db              # База данных для сохранения рекордов
        self.player_id = player_id
        self.username = username  # имя не используется, но сохраняется
        
        # РАЗМЕР ИГРОВОГО ПОЛЯ (на весь экран 800x600)
        self.game_width = 800
        self.game_height = 600
        
        # РАЗМЕР КЛЕТКИ: 800/40 = 20, 600/30 = 20
        self.cell_size = 20
        self.grid_width = 40   # 40 клеток по горизонтали (40 * 20 = 800)
        self.grid_height = 30  # 30 клеток по вертикали (30 * 20 = 600)
        
        # ЗАПУСКАЕМ НОВУЮ ИГРУ
        self.reset_game()
        
    def reset_game(self):
        """Сбрасывает все игровые переменные до начальных значений"""
        # НАЧАЛЬНАЯ ПОЗИЦИЯ ЗМЕЙКИ (по центру поля)
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = [(start_x, start_y)]  # Список сегментов (координаты)
        self.direction = (1, 0)      # Текущее направление (вправо)
        self.next_direction = (1, 0) # Следующее направление (для буферизации)
        self.score = 0               # Набранные очки
        self.level = 1               # Текущий уровень
        self.speed = 10              # Скорость движения (чем выше, тем быстрее)
        
        # ИГРОВЫЕ ОБЪЕКТЫ
        self.food = None             # Еда (красная)
        self.poison = None           # Яд (бордовый с крестом)
        self.powerup = None          # Бонус (скорость, замедление, щит)
        self.speed_boost_end = 0     # Время окончания ускорения (мс)
        self.slow_motion_end = 0     # Время окончания замедления (мс)
        self.shield_active = False   # Активен ли щит
        self.obstacles = []          # Список препятствий (с 3 уровня)
        self.game_over = False       # Флаг окончания игры
        self.game_over_reason = ""   # Причина окончания
        
        # ГЕНЕРАЦИЯ ПЕРВОЙ ЕДЫ
        self.spawn_food()
        
        # ЗАГРУЗКА ЛИЧНОГО РЕКОРДА ИЗ БД
        self.personal_best = self.db.get_personal_best(self.player_id)
        self.food_eaten = 0          # Счётчик съеденной еды (для повышения уровня)
    
    def generate_obstacles(self):
        """Генерация препятствий (начиная с 3 уровня)
           Количество препятствий: min(5 + уровень, 20)"""
        num_obstacles = min(5 + self.level, 20)
        self.obstacles = []
        
        for _ in range(num_obstacles):
            attempts = 0
            while attempts < 100:  # Максимум 100 попыток найти свободное место
                # Генерируем случайные координаты (не по краям поля)
                x = random.randint(1, self.grid_width - 2)
                y = random.randint(1, self.grid_height - 2)
                pos = (x, y)
                # Проверяем, что позиция свободна:
                # - не занята змеёй
                # - не занята едой
                # - нет другого препятствия
                # - не занята ядом
                if (pos not in self.snake and pos != self.food and 
                    pos not in self.obstacles and pos != self.poison):
                    self.obstacles.append(pos)
                    break
                attempts += 1
    
    def spawn_food(self):
        """Создаёт новую еду на свободной клетке"""
        attempts = 0
        while attempts < 100:
            # Случайная позиция в пределах поля
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            # Проверяем, что клетка свободна
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.poison and pos != self.food):
                self.food = pos
                
                # Спавн яда с вероятностью 20% (если яда ещё нет)
                if random.random() < 0.2 and not self.poison:
                    self.spawn_poison()
                
                # Спавн бонуса с вероятностью 15% (если бонуса ещё нет)
                if random.random() < 0.15 and not self.powerup:
                    self.spawn_powerup()
                return
            attempts += 1
    
    def spawn_poison(self):
        """Создаёт ядовитую еду на свободной клетке"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.food and pos != self.poison):
                self.poison = pos
                return
            attempts += 1
    
    def spawn_powerup(self):
        """Создаёт бонус (ускорение, замедление, щит) на свободной клетке"""
        powerup_types = ['speed', 'slow', 'shield']  # Возможные типы бонусов
        self.powerup = {
            'pos': None,
            'type': random.choice(powerup_types),          # Случайный тип
            'spawn_time': pygame.time.get_ticks()          # Время появления (для таймаута)
        }
        
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.food and pos != self.poison):
                self.powerup['pos'] = pos
                return
            attempts += 1
        self.powerup = None  # Не удалось разместить - бонус не появляется
    
    def update(self):
        """ОБНОВЛЕНИЕ СОСТОЯНИЯ ИГРЫ (вызывается каждый кадр)"""
        if self.game_over:
            return
        
        # ПРИМЕНЯЕМ БУФЕРИЗИРОВАННОЕ НАПРАВЛЕНИЕ
        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # === ПРОВЕРКА СТОЛКНОВЕНИЙ (с защитой щита) ===
        
        # 1. СТОЛКНОВЕНИЕ С СОБОЙ
        if new_head in self.snake[1:]:  # [1:] - все сегменты, кроме головы
            if not self.shield_active:
                self.end_game("Self collision!")
                return
            else:
                self.shield_active = False  # Щит поглотил удар
        
        # 2. СТОЛКНОВЕНИЕ СО СТЕНОЙ
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            if not self.shield_active:
                self.end_game("Hit the wall!")
                return
            else:
                self.shield_active = False
        
        # 3. СТОЛКНОВЕНИЕ С ПРЕПЯТСТВИЕМ
        if new_head in self.obstacles:
            if not self.shield_active:
                self.end_game("Hit an obstacle!")
                return
            else:
                self.shield_active = False
        
        # === ПРОВЕРКА СЪЕДАНИЯ ОБЪЕКТОВ ===
        
        # 4. СЪЕДАНИЕ ЕДЫ (нормальная еда)
        if new_head == self.food:
            self.snake.insert(0, new_head)  # Добавляем новую голову (растём)
            self.score += 10                # +10 очков
            self.food_eaten += 1            # Увеличиваем счётчик съеденной еды
            self.food = None
            self.poison = None
            self.spawn_food()               # Создаём новую еду
            
            # ПОВЫШЕНИЕ УРОВНЯ (каждые 5 съеденных еды)
            if self.food_eaten % 5 == 0:
                self.level += 1
                if self.level >= 3:         # Начиная с 3 уровня - препятствия
                    self.generate_obstacles()
                # Увеличиваем скорость (но не выше 20)
                self.speed = min(10 + self.level, 20)
            return  # Выходим, не двигаемся дальше (уже добавили голову)
        
        # 5. СЪЕДАНИЕ ЯДА (укорачивает змею)
        if new_head == self.poison:
            # Укорачиваем змею на 2 сегмента
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            
            # Если змея стала слишком короткой - игра окончена
            if len(self.snake) <= 1:
                self.end_game("You became too short!")
                return
            
            # Добавляем новую голову
            self.snake.insert(0, new_head)
            self.poison = None
            self.spawn_food()  # Генерируем новую еду
            return
        
        # 6. СЪЕДАНИЕ БОНУСА
        if self.powerup and new_head == self.powerup['pos']:
            self.activate_powerup(self.powerup['type'])
            self.powerup = None
            self.spawn_food()  # Генерируем новую еду
        
        # УДАЛЕНИЕ ПРОСРОЧЕННОГО БОНУСА (через 8 секунд)
        if self.powerup:
            current_time = pygame.time.get_ticks()
            if current_time - self.powerup['spawn_time'] > 8000:
                self.powerup = None
                self.spawn_food()
        
        # === ОБЫЧНОЕ ДВИЖЕНИЕ (без еды) ===
        self.snake.insert(0, new_head)  # Добавляем новую голову
        self.snake.pop()                # Удаляем последний сегмент (хвост)
        
        # === ОБНОВЛЕНИЕ ДЕЙСТВИЯ БОНУСОВ ===
        current_time = pygame.time.get_ticks()
        
        # Завершение ускорения
        if self.speed_boost_end and current_time > self.speed_boost_end:
            self.speed_boost_end = 0
            self.speed = 10 + self.level if self.level < 20 else 20
        
        # Завершение замедления
        if self.slow_motion_end and current_time > self.slow_motion_end:
            self.slow_motion_end = 0
            self.speed = 10 + self.level if self.level < 20 else 20
    
    def activate_powerup(self, powerup_type):
        """Активирует бонус в зависимости от типа"""
        current_time = pygame.time.get_ticks()
        
        if powerup_type == 'speed':
            # Ускорение на 5 секунд (+5 к скорости, макс 30)
            self.speed_boost_end = current_time + 5000  # +5000 мс = 5 секунд
            self.speed = min(self.speed + 5, 30)
        elif powerup_type == 'slow':
            # Замедление на 5 секунд (-5 к скорости, минимум 5)
            self.slow_motion_end = current_time + 5000
            self.speed = max(self.speed - 5, 5)
        elif powerup_type == 'shield':
            # Щит (без таймера, сбрасывается при столкновении)
            self.shield_active = True
    
    def end_game(self, reason):
        """Завершает игру, сохраняет результат в БД"""
        self.game_over = True
        self.game_over_reason = reason
        self.db.save_game_session(self.player_id, self.score, self.level)
    
    def draw(self):
        """ОТРИСОВКА ВСЕХ ИГРОВЫХ ОБЪЕКТОВ НА ЭКРАНЕ"""
        
        # === ФОН ИГРОВОГО ПОЛЯ ===
        game_rect = pygame.Rect(0, 0, self.game_width, self.game_height)
        pygame.draw.rect(self.screen, (15, 15, 15), game_rect)  # Тёмно-серый фон
        pygame.draw.rect(self.screen, (50, 50, 50), game_rect, 2)  # Рамка
        
        # === СЕТКА (GRID) ===
        if self.config.grid_overlay:
            # Вертикальные линии
            for x in range(0, self.game_width + 1, self.cell_size):
                pygame.draw.line(self.screen, (35, 35, 35), (x, 0), (x, self.game_height), 1)
            # Горизонтальные линии
            for y in range(0, self.game_height + 1, self.cell_size):
                pygame.draw.line(self.screen, (35, 35, 35), (0, y), (self.game_width, y), 1)
        
        # === ПРЕПЯТСТВИЯ ===
        for obs in self.obstacles:
            rect = pygame.Rect(
                obs[0] * self.cell_size,
                obs[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (80, 80, 80), rect)      # Тёмно-серый блок
            pygame.draw.rect(self.screen, (120, 120, 120), rect, 1) # Светлая рамка
        
        # === ЗМЕЙКА ===
        for i, segment in enumerate(self.snake):
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            # ГОЛОВА (отрисовывается ярче и с глазами)
            if i == 0:
                color = self.config.snake_color
                pygame.draw.rect(self.screen, color, rect)
                
                # ГЛАЗА (зависят от направления движения)
                eye_size = self.cell_size // 5
                if self.direction == (1, 0):  # Вправо
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.bottom - eye_size), eye_size // 2)
                elif self.direction == (-1, 0):  # Влево
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.bottom - eye_size), eye_size // 2)
                elif self.direction == (0, -1):  # Вверх
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.top + eye_size), eye_size // 2)
                else:  # Вниз
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.bottom - eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.bottom - eye_size), eye_size // 2)
            else:
                # ТЕЛО (обычный цвет с чёрной обводкой)
                pygame.draw.rect(self.screen, self.config.snake_color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # === ЕДА (КРАСНЫЙ КВАДРАТ С СИЯНИЕМ) ===
        if self.food:
            rect = pygame.Rect(
                self.food[0] * self.cell_size,
                self.food[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (255, 0, 0), rect)
            pygame.draw.circle(self.screen, (255, 100, 100), rect.center, self.cell_size // 3)
        
        # === ЯД (БОРДОВЫЙ С КРЕСТОМ) ===
        if self.poison:
            rect = pygame.Rect(
                self.poison[0] * self.cell_size,
                self.poison[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (139, 0, 0), rect)
            # Рисуем крест (кости черепа)
            pygame.draw.line(self.screen, (0, 0, 0), rect.topleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, (0, 0, 0), rect.topright, rect.bottomleft, 2)
        
        # === БОНУСЫ ===
        if self.powerup:
            rect = pygame.Rect(
                self.powerup['pos'][0] * self.cell_size,
                self.powerup['pos'][1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            
            # Выбираем цвет и иконку в зависимости от типа бонуса
            if self.powerup['type'] == 'speed':
                color = (255, 255, 0)   # Жёлтый
                icon = "⚡"              # Молния
            elif self.powerup['type'] == 'slow':
                color = (0, 255, 255)   # Голубой
                icon = "🐢"              # Черепаха
            else:  # shield
                color = (255, 0, 255)   # Пурпурный
                icon = "🛡️"              # Щит
            
            pygame.draw.rect(self.screen, color, rect)
            
            # РИСУЕМ ИКОНКУ
            icon_font = pygame.font.Font(None, self.cell_size)
            icon_surf = icon_font.render(icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=rect.center)
            self.screen.blit(icon_surf, icon_rect)
        
        # === UI ТЕКСТ (ОЧКИ, УРОВЕНЬ, БОНУСЫ) ===
        font = pygame.font.Font(None, 28)
        
        # ПОЛУПРОЗРАЧНЫЙ ФОН ДЛЯ ТЕКСТА (чтобы текст был читаем на любом фоне)
        text_bg = pygame.Surface((150, 120))
        text_bg.set_alpha(180)        # Прозрачность 180/255
        text_bg.fill((0, 0, 0))       # Чёрный фон
        self.screen.blit(text_bg, (5, 5))
        
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        best_text = font.render(f"Best: {self.personal_best}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(best_text, (10, 70))
        
        # ОТОБРАЖАЕМ АКТИВНЫЕ ЭФФЕКТЫ (скорость, замедление, щит)
        y_offset = 110
        if self.speed_boost_end:
            time_left = max(0, (self.speed_boost_end - pygame.time.get_ticks()) // 1000)
            boost_text = font.render(f"⚡ Speed: {time_left}s", True, (255, 255, 0))
            self.screen.blit(boost_text, (10, y_offset))
            y_offset += 25
        
        if self.slow_motion_end:
            time_left = max(0, (self.slow_motion_end - pygame.time.get_ticks()) // 1000)
            slow_text = font.render(f"🐢 Slow: {time_left}s", True, (0, 255, 255))
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 25
        
        if self.shield_active:
            shield_text = font.render(f"🛡️ Shield", True, (255, 0, 255))
            self.screen.blit(shield_text, (10, y_offset))
    
    def handle_event(self, event):
        """ОБРАБОТКА НАЖАТИЙ КЛАВИШ"""
        if event.type == pygame.KEYDOWN:
            # Защита от разворота на 180 градусов
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)  # Вверх
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)   # Вниз
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)  # Влево
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)   # Вправо