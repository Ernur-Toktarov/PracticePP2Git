# ГЛАВНЫЙ МОДУЛЬ ПРИЛОЖЕНИЯ - ЗАПУСК И УПРАВЛЕНИЕ ВСЕМИ ЭКРАНАМИ
import pygame
import sys
from db import Database
from config import Config
from game import SnakeGame

# КЛАСС ГЛАВНОГО ПРИЛОЖЕНИЯ (УПРАВЛЯЕТ МЕНЮ И ПЕРЕКЛЮЧЕНИЯМИ)
class GameApp:
    def __init__(self):
        """Инициализация приложения: окно, база данных, настройки, шрифты"""
        pygame.init()  # Запуск Pygame
        
        # УСТАНАВЛИВАЕМ ФИКСИРОВАННЫЙ РАЗМЕР ОКНА 800x600
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")  # Заголовок окна
        self.clock = pygame.time.Clock()  # Для контроля FPS
        
        # КОМПОНЕНТЫ ПРИЛОЖЕНИЯ
        self.config = Config()        # Настройки игры (цвет змейки, сетка, звук)
        self.db = Database()          # База данных (PostgreSQL)
        
        # ПЕРЕМЕННЫЕ СОСТОЯНИЯ
        self.username = ""            # Имя текущего игрока
        self.player_id = None         # ID игрока из БД
        self.game = None              # Объект игры (создаётся при старте)
        self.running = True           # Флаг работы приложения
        
        # ЦВЕТА (RGB) ДЛЯ UI
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 50, 200)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.GRAY = (100, 100, 100)
        
        # ШРИФТЫ ДЛЯ РАЗНЫХ ЭЛЕМЕНТОВ UI
        self.title_font = pygame.font.Font(None, 72)    # Заголовки (72px)
        self.button_font = pygame.font.Font(None, 48)   # Кнопки (48px)
        self.text_font = pygame.font.Font(None, 32)     # Обычный текст (32px)
        
        self.clicked = False  # Для предотвращения множественных кликов
    
    def draw_button(self, text, x, y, width, height, color, hover_color=None):
        """Универсальная функция отрисовки кнопки с эффектом наведения
           Возвращает True если кнопка была нажата"""
        mouse = pygame.mouse.get_pos()           # Позиция курсора
        mouse_click = pygame.mouse.get_pressed() # Состояние кнопок мыши
        
        rect = pygame.Rect(x, y, width, height)
        hover = rect.collidepoint(mouse)         # Курсор над кнопкой?
        
        # РИСУЕМ КНОПКУ (с цветом наведения если нужно)
        if hover and hover_color:
            pygame.draw.rect(self.screen, hover_color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect)
        
        pygame.draw.rect(self.screen, self.WHITE, rect, 3)  # Белая рамка
        
        # ТЕКСТ КНОПКИ
        text_surface = self.button_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # ОБРАБОТКА НАЖАТИЯ (с защитой от многократного срабатывания)
        if hover and mouse_click[0] and not self.clicked:
            self.clicked = True
            return True
        
        if not mouse_click[0]:
            self.clicked = False
            
        return False
    
    def draw_text_input(self, text, x, y, width, height, active):
        """Отрисовка поля ввода текста с курсором
           Возвращает прямоугольник поля для проверки кликов"""
        rect = pygame.Rect(x, y, width, height)
        
        # Цвет рамки зависит от активности поля
        color = self.GREEN if active else self.GRAY
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
        
        # ТЕКСТ ПОЛЯ (если пусто - отображаем подсказку "Enter name")
        display_text = text if text else "Enter name"
        text_surface = self.text_font.render(display_text, True, self.WHITE)
        self.screen.blit(text_surface, (x + 10, y + 5))
        
        # МИГАЮЩИЙ КУРСОР (активно только когда поле в фокусе)
        if active:
            current_time = pygame.time.get_ticks()
            # Меняем состояние каждые 500 мс
            if current_time % 1000 < 500:
                cursor_x = x + 10 + text_surface.get_width()
                pygame.draw.line(self.screen, self.WHITE, 
                               (cursor_x, y + 5), (cursor_x, y + height - 5), 2)
        
        return rect
    
    # === ГЛАВНОЕ МЕНЮ ===
    def main_menu(self):
        """Главное меню: ввод имени, кнопки PLAY/SCORES/OPTIONS/QUIT"""
        username_input_active = True  # Поле ввода активно по умолчанию
        input_rect = None
        
        while self.running:
            self.screen.fill(self.BLACK)  # Очищаем экран
            
            # ЗАГОЛОВОК
            title = self.title_font.render("SNAKE GAME", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 100))
            self.screen.blit(title, title_rect)
            
            # ПОДПИСЬ ПОЛЯ ВВОДА
            input_label = self.text_font.render("YOUR NAME:", True, self.WHITE)
            input_label_rect = input_label.get_rect(center=(400, 200))
            self.screen.blit(input_label, input_label_rect)
            
            # ПОЛЕ ВВОДА ИМЕНИ
            input_rect = self.draw_text_input(self.username, 300, 240, 200, 40, username_input_active)
            
            # КНОПКИ МЕНЮ
            if self.draw_button("PLAY", 300, 320, 200, 50, self.BLUE, self.GREEN):
                if self.username.strip():  # Имя не пустое?
                    self.player_id = self.db.get_or_create_player(self.username)
                    self.game_loop()      # Запускаем игру
            
            if self.draw_button("SCORES", 300, 390, 200, 50, self.BLUE, self.GREEN):
                self.leaderboard_screen()  # Показываем таблицу рекордов
            
            if self.draw_button("OPTIONS", 300, 460, 200, 50, self.BLUE, self.GREEN):
                self.settings_screen()     # Показываем настройки
            
            if self.draw_button("QUIT", 300, 530, 200, 50, self.RED, (150, 0, 0)):
                self.running = False
                break
            
            # ОБРАБОТКА СОБЫТИЙ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                # КЛИК МЫШИ - активируем поле ввода если кликнули по нему
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect and input_rect.collidepoint(event.pos):
                        username_input_active = True
                    else:
                        username_input_active = False
                
                # ВВОД ТЕКСТА (только если поле активно)
                if event.type == pygame.KEYDOWN and username_input_active:
                    if event.key == pygame.K_RETURN:
                        if self.username.strip():
                            self.player_id = self.db.get_or_create_player(self.username)
                            self.game_loop()
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]  # Удалить символ
                    else:
                        # Добавляем символ (макс 20 символов, только печатаемые)
                        if len(self.username) < 20 and event.unicode.isprintable():
                            self.username += event.unicode
            
            pygame.display.flip()
            self.clock.tick(60)
    
    # === ИГРОВОЙ ЦИКЛ ===
    def game_loop(self):
        """Запускает игру и обрабатывает игровой процесс"""
        # СОЗДАЁМ НОВУЮ ИГРУ
        self.game = SnakeGame(self.screen, self.config, self.db, self.player_id, self.username)
        last_time = pygame.time.get_ticks()  # Время последнего обновления
        
        while self.running:
            current_time = pygame.time.get_ticks()
            delta = current_time - last_time
            
            # ОБРАБОТКА СОБЫТИЙ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game.game_over:
                        return  # Выход в меню после окончания игры
                
                self.game.handle_event(event)
            
            # ОБНОВЛЕНИЕ ИГРЫ (с учётом скорости)
            if not self.game.game_over:
                # Обновляем только когда прошло достаточно времени (1000/скорость мс)
                if delta > 1000 // self.game.speed:
                    self.game.update()
                    last_time = current_time
            
            # ОТРИСОВКА
            self.screen.fill(self.BLACK)
            self.game.draw()
            
            # ЭКРАН GAME OVER (если игра окончена)
            if self.game.game_over:
                # ЗАТЕМНЕНИЕ (полупрозрачный чёрный слой)
                overlay = pygame.Surface((800, 600))
                overlay.set_alpha(200)  # Прозрачность 200/255
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                
                # ЗАГОЛОВОК "GAME OVER"
                go_text = self.title_font.render("GAME OVER", True, self.RED)
                go_rect = go_text.get_rect(center=(400, 150))
                self.screen.blit(go_text, go_rect)
                
                # ПРИЧИНА ПОРАЖЕНИЯ
                reason_text = self.text_font.render(f"REASON: {self.game.game_over_reason}", True, self.WHITE)
                reason_rect = reason_text.get_rect(center=(400, 220))
                self.screen.blit(reason_text, reason_rect)
                
                # ОЧКИ И УРОВЕНЬ
                score_text = self.text_font.render(f"SCORE: {self.game.score}", True, self.WHITE)
                score_rect = score_text.get_rect(center=(400, 280))
                self.screen.blit(score_text, score_rect)
                
                level_text = self.text_font.render(f"LEVEL: {self.game.level}", True, self.WHITE)
                level_rect = level_text.get_rect(center=(400, 310))
                self.screen.blit(level_text, level_rect)
                
                # КНОПКИ GAME OVER
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                # КНОПКА "RETRY" (сыграть снова)
                retry_rect = pygame.Rect(250, 380, 120, 50)
                if retry_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.GREEN, retry_rect)
                    if click[0]:
                        pygame.time.wait(200)  # Небольшая задержка для избежания двойного клика
                        # СОЗДАЁМ НОВУЮ ИГРУ (с теми же параметрами)
                        self.game = SnakeGame(self.screen, self.config, self.db, self.player_id, self.username)
                        last_time = pygame.time.get_ticks()
                        continue  # Пропускаем отрисовку кнопок дальше
                else:
                    pygame.draw.rect(self.screen, (0, 150, 0), retry_rect)
                pygame.draw.rect(self.screen, self.WHITE, retry_rect, 2)
                retry_text = self.button_font.render("RETRY", True, self.WHITE)
                retry_text_rect = retry_text.get_rect(center=retry_rect.center)
                self.screen.blit(retry_text, retry_text_rect)
                
                # КНОПКА "MENU" (вернуться в главное меню)
                menu_rect = pygame.Rect(430, 380, 120, 50)
                if menu_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.BLUE, menu_rect)
                    if click[0]:
                        pygame.time.wait(200)
                        return  # Возврат в main_menu
                else:
                    pygame.draw.rect(self.screen, (0, 0, 150), menu_rect)
                pygame.draw.rect(self.screen, self.WHITE, menu_rect, 2)
                menu_text = self.button_font.render("MENU", True, self.WHITE)
                menu_text_rect = menu_text.get_rect(center=menu_rect.center)
                self.screen.blit(menu_text, menu_text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    # === ЭКРАН ТАБЛИЦЫ РЕКОРДОВ ===
    def leaderboard_screen(self):
        """Отображает топ-10 рекордов из базы данных"""
        leaderboard = self.db.get_leaderboard()  # Получаем из БД
        
        while self.running:
            self.screen.fill(self.BLACK)
            
            # ЗАГОЛОВОК
            title = self.title_font.render("TOP SCORES", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 60))
            self.screen.blit(title, title_rect)
            
            # ЗАГОЛОВКИ ТАБЛИЦЫ
            headers = ["#", "PLAYER", "SCORE", "LEVEL", "DATE"]
            for i, header in enumerate(headers):
                text = self.text_font.render(header, True, self.WHITE)
                self.screen.blit(text, (50 + i * 150, 130))
            
            # ВЫВОД ЗАПИСЕЙ (максимум 10)
            for idx, entry in enumerate(leaderboard[:10]):
                y_pos = 170 + idx * 35
                rank = idx + 1
                username, score, level, played_at = entry
                date_str = played_at.strftime("%m/%d")  # Формат: месяц/день
                
                texts = [str(rank), username[:15], str(score), str(level), date_str]
                for i, text in enumerate(texts):
                    text_surface = self.text_font.render(text, True, self.WHITE)
                    self.screen.blit(text_surface, (50 + i * 150, y_pos))
            
            # КНОПКА НАЗАД
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            back_rect = pygame.Rect(350, 520, 100, 40)
            
            if back_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, back_rect)
                if click[0]:
                    pygame.time.wait(200)
                    return  # Возврат в главное меню
            else:
                pygame.draw.rect(self.screen, self.BLUE, back_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, back_rect, 2)
            back_text = self.button_font.render("BACK", True, self.WHITE)
            back_text_rect = back_text.get_rect(center=back_rect.center)
            self.screen.blit(back_text, back_text_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            pygame.display.flip()
            self.clock.tick(60)
    
    # === ЭКРАН НАСТРОЕК ===
    def settings_screen(self):
        """Настройки игры: сетка, звук, цвет змейки"""
        colors = [(0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        color_names = ["GREEN", "YELLOW", "PURPLE", "CYAN"]
        
        while self.running:
            self.screen.fill(self.BLACK)
            
            # ЗАГОЛОВОК
            title = self.title_font.render("GAME OPTIONS", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 80))
            self.screen.blit(title, title_rect)
            
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            # === КНОПКА ВКЛ/ВЫКЛ СЕТКИ ===
            grid_text = f"GRID: {'ON' if self.config.grid_overlay else 'OFF'}"
            grid_rect = pygame.Rect(300, 160, 200, 50)
            
            if grid_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, grid_rect)
                if click[0]:
                    self.config.grid_overlay = not self.config.grid_overlay  # Переключение
                    pygame.time.wait(200)
            else:
                pygame.draw.rect(self.screen, self.BLUE, grid_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, grid_rect, 2)
            grid_surf = self.button_font.render(grid_text, True, self.WHITE)
            grid_text_rect = grid_surf.get_rect(center=grid_rect.center)
            self.screen.blit(grid_surf, grid_text_rect)
            
            # === КНОПКА ВКЛ/ВЫКЛ ЗВУКА ===
            sound_text = f"SOUND: {'ON' if self.config.sound_on else 'OFF'}"
            sound_rect = pygame.Rect(300, 230, 200, 50)
            
            if sound_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, sound_rect)
                if click[0]:
                    self.config.sound_on = not self.config.sound_on  # Переключение
                    pygame.time.wait(200)
            else:
                pygame.draw.rect(self.screen, self.BLUE, sound_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, sound_rect, 2)
            sound_surf = self.button_font.render(sound_text, True, self.WHITE)
            sound_text_rect = sound_surf.get_rect(center=sound_rect.center)
            self.screen.blit(sound_surf, sound_text_rect)
            
            # === ВЫБОР ЦВЕТА ЗМЕЙКИ ===
            color_label = self.text_font.render("SNAKE COLOR:", True, self.WHITE)
            color_label_rect = color_label.get_rect(center=(400, 320))
            self.screen.blit(color_label, color_label_rect)
            
            # КНОПКИ ЦВЕТОВ (горизонтальный ряд)
            button_w = 85
            button_h = 40
            total_w = (button_w * len(colors)) + (15 * (len(colors) - 1))
            start_x = (800 - total_w) // 2  # Центрирование
            
            for i, (color, name) in enumerate(zip(colors, color_names)):
                x = start_x + i * (button_w + 15)
                color_rect = pygame.Rect(x, 350, button_w, button_h)
                
                if color_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.WHITE, color_rect)  # Обводка белым
                    if click[0]:
                        self.config.snake_color = color  # Устанавливаем цвет
                        pygame.time.wait(200)
                else:
                    pygame.draw.rect(self.screen, color, color_rect)
                
                pygame.draw.rect(self.screen, self.WHITE, color_rect, 2)
                color_surf = self.text_font.render(name, True, self.WHITE)
                color_text_rect = color_surf.get_rect(center=color_rect.center)
                self.screen.blit(color_surf, color_text_rect)
            
            # === КНОПКА СОХРАНЕНИЯ И ВЫХОДА ===
            save_rect = pygame.Rect(300, 440, 200, 50)
            
            if save_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, save_rect)
                if click[0]:
                    self.config.save_settings()  # Сохраняем в файл
                    pygame.time.wait(200)
                    return  # Возврат в главное меню
            else:
                pygame.draw.rect(self.screen, (0, 150, 0), save_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, save_rect, 2)
            save_surf = self.button_font.render("SAVE & BACK", True, self.WHITE)
            save_text_rect = save_surf.get_rect(center=save_rect.center)
            self.screen.blit(save_surf, save_text_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def run(self):
        """Запуск приложения (точка входа)"""
        self.main_menu()  # Показать главное меню
        pygame.quit()     # Завершить Pygame
        sys.exit()        # Выйти из программы

# ТОЧКА ВХОДА В ПРОГРАММУ
if __name__ == "__main__":
    app = GameApp()
    app.run()