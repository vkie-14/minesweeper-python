import pygame
import os
from src.board import Board

WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
INITIAL_CELL_SIZE = 40

class Game:
    def __init__(self, rows, cols, mines):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.mines = mines 
        self.board = Board(rows, cols, mines)

        self.flags_placed = 0
        self.timer_started = False
        self.start_time = 0
        self.elapsed_time = 0
        self.game_over = False
        self.game_won = False # Thêm trạng thái Thắng

        self.cell_size = INITIAL_CELL_SIZE
        self.margin = self.cell_size // 2  
        self.header_height = int(self.cell_size * 2.5) 
        
        self.board_offset_x = self.margin
        self.board_offset_y = self.margin + self.header_height + self.margin
        
        self.width = (cols * self.cell_size) + (2 * self.margin)
        self.height = self.board_offset_y + (rows * self.cell_size) + self.margin

        self.face_size = int(self.cell_size * 1.6)
        self.face_x = (self.width - self.face_size) // 2
        self.face_y = self.margin + (self.header_height - self.face_size) // 2
        self.face_rect = pygame.Rect(self.face_x, self.face_y, self.face_size, self.face_size)

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Minesweeper Retro")

        self.original_images = {}
        self.images = {}

        assets_path = os.path.join(os.path.dirname(__file__), '..', 'Assets')
        image_files = {
            "Tile1": "Tile1.png", "Tile2": "Tile2.png", "Tile3": "Tile3.png",
            "Tile4": "Tile4.png", "Tile5": "Tile5.png", "Tile6": "Tile6.png",
            "Tile7": "Tile7.png", "Tile8": "Tile8.png", "Tile0": "TileEmpty.png",
            "Exploded": "TileExploded.png", "Flag": "TileFlag.png",
            "Mine": "TileMine.png", "Unknown": "TileUnknown.png",
            "Smile": "smile.png", "Die": "die.png", "Win": "win.png" # Load ảnh win
        }

        for key, file_name in image_files.items():
            full_path = os.path.join(assets_path, file_name)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                self.original_images[key] = img
            
        self.scale_assets()
        self.running = True

    def reset_game(self):
        self.board = Board(self.rows, self.cols, self.mines)
        self.flags_placed = 0
        self.timer_started = False
        self.start_time = 0
        self.elapsed_time = 0
        self.game_over = False
        self.game_won = False # Reset lại trạng thái thắng

    def check_win(self):
        """Hàm kiểm tra điều kiện thắng game"""
        if self.game_over or self.game_won:
            return
            
        opened_count = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board.board[i][j].opened:
                    opened_count += 1
                    
        # Nếu tổng số ô đã mở bằng tổng số ô trừ đi số mìn -> Thắng
        if opened_count == (self.rows * self.cols) - self.mines:
            self.game_won = True
            self.flags_placed = self.mines # Tự động update bộ đếm cờ về 0
            
            # Tự động cắm cờ vào các mìn còn lại
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board.board[i][j].is_mine:
                        self.board.board[i][j].flagged = True

    def scale_assets(self):
        for key, img in self.original_images.items():
            if key in ["Smile", "Die", "Win"]: # Thêm scale cho ảnh Win
                img_size = int(self.face_size * 0.8) 
                self.images[key] = pygame.transform.scale(img, (img_size, img_size))
            else:
                self.images[key] = pygame.transform.scale(img, (self.cell_size, self.cell_size))

    def draw_bevel(self, surface, rect, sunken=False, border_width=4):
        color_light = WHITE
        color_dark = DARK_GRAY
        if sunken: 
            color_light, color_dark = color_dark, color_light
            
        pygame.draw.polygon(surface, color_light, [
            (rect.left, rect.top), (rect.right, rect.top), 
            (rect.right - border_width, rect.top + border_width), 
            (rect.left + border_width, rect.top + border_width),
            (rect.left + border_width, rect.bottom - border_width),
            (rect.left, rect.bottom)
        ])
        pygame.draw.polygon(surface, color_dark, [
            (rect.left, rect.bottom), (rect.right, rect.bottom), 
            (rect.right, rect.top), 
            (rect.right - border_width, rect.top + border_width),
            (rect.right - border_width, rect.bottom - border_width),
            (rect.left + border_width, rect.bottom - border_width)
        ])

    def draw_7_segment_digit(self, surface, x, y, w, h, digit):
        on_color = (255, 0, 0)
        off_color = (60, 0, 0) 
        
        states = {
            '0': (1,1,1,1,1,1,0), '1': (0,1,1,0,0,0,0), '2': (1,1,0,1,1,0,1),
            '3': (1,1,1,1,0,0,1), '4': (0,1,1,0,0,1,1), '5': (1,0,1,1,0,1,1),
            '6': (1,0,1,1,1,1,1), '7': (1,1,1,0,0,0,0), '8': (1,1,1,1,1,1,1),
            '9': (1,1,1,1,0,1,1), '-': (0,0,0,0,0,0,1), ' ': (0,0,0,0,0,0,0)
        }
        st = states.get(digit, states[' '])
        
        t = w * 0.25 
        m = y + h / 2 
        
        A = [(x+t/2, y), (x+w-t/2, y), (x+w-t, y+t), (x+t, y+t)]
        B = [(x+w, y+t/2), (x+w, m-t/4), (x+w-t, m), (x+w-t, y+t)]
        C = [(x+w, m+t/4), (x+w, y+h-t/2), (x+w-t, y+h-t), (x+w-t, m)]
        D = [(x+t, y+h-t), (x+w-t, y+h-t), (x+w-t/2, y+h), (x+t/2, y+h)]
        E = [(x, y+h-t/2), (x, m+t/4), (x+t, m), (x+t, y+h-t)]
        F = [(x, m-t/4), (x, y+t/2), (x+t, y+t), (x+t, m)]
        G = [(x+t/2, m), (x+t, m-t/2), (x+w-t, m-t/2), (x+w-t/2, m), (x+w-t, m+t/2), (x+t, m+t/2)]
        
        polys = [A, B, C, D, E, F, G]
        
        for i, poly in enumerate(polys):
            color = on_color if st[i] else off_color
            pygame.draw.polygon(surface, color, [(int(px), int(py)) for px, py in poly])
            pygame.draw.polygon(surface, BLACK, [(int(px), int(py)) for px, py in poly], 1)

    def draw_led_panel(self, surface, x, y, width, height, value):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, BLACK, rect)
        
        bw = max(2, self.cell_size // 15)
        self.draw_bevel(surface, rect, sunken=True, border_width=bw)
        
        if value < -99: value = -99
        if value > 999: value = 999
        text = f"-{abs(value):02d}" if value < 0 else f"{value:03d}"
            
        pad_x = width * 0.08
        pad_y = height * 0.15
        
        digit_w = (width - 2 * pad_x) / 3
        digit_h = height - 2 * pad_y
        char_w = digit_w * 0.75 
        
        start_x = x + pad_x + (digit_w - char_w) / 2
        start_y = y + pad_y
        
        for i, char in enumerate(text):
            char_x = start_x + i * digit_w
            self.draw_7_segment_digit(surface, char_x, start_y, char_w, digit_h, char)

    def draw(self):
        self.screen.fill(GRAY)
        bw = max(2, self.cell_size // 10)
        
        outer_rect = pygame.Rect(0, 0, self.width, self.height)
        self.draw_bevel(self.screen, outer_rect, sunken=False, border_width=bw)

        header_rect = pygame.Rect(self.margin - bw, self.margin - bw, 
                                  self.width - (2 * self.margin) + (2 * bw), 
                                  self.header_height + (2 * bw))
        self.draw_bevel(self.screen, header_rect, sunken=True, border_width=bw)

        board_rect = pygame.Rect(self.board_offset_x - bw, self.board_offset_y - bw,
                                 self.cols * self.cell_size + (2 * bw), 
                                 self.rows * self.cell_size + (2 * bw))
        self.draw_bevel(self.screen, board_rect, sunken=True, border_width=bw)

        led_width = int(self.cell_size * 2.5)
        led_height = int(self.cell_size * 1.5)
        led_y = self.margin + (self.header_height - led_height) // 2
        
        mines_left = self.board.mine_cnt - self.flags_placed
        self.draw_led_panel(self.screen, self.margin + self.cell_size // 2, led_y, led_width, led_height, mines_left)
        
        # Dừng đồng hồ khi Thắng hoặc Thua
        if self.timer_started and not self.game_over and not self.game_won:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            self.elapsed_time = min(self.elapsed_time, 999) 
            
        led_x_right = self.width - self.margin - led_width - (self.cell_size // 2)
        self.draw_led_panel(self.screen, led_x_right, led_y, led_width, led_height, self.elapsed_time)

        pygame.draw.rect(self.screen, GRAY, self.face_rect)
        self.draw_bevel(self.screen, self.face_rect, sunken=False, border_width=bw)
        
        # Đổi ảnh mặt cười tùy theo trạng thái game
        if self.game_over:
            face_img = self.images.get("Die")
        elif self.game_won:
            face_img = self.images.get("Win")
        else:
            face_img = self.images.get("Smile")
            
        if face_img:
            img_x = self.face_rect.x + (self.face_size - face_img.get_width()) // 2
            img_y = self.face_rect.y + (self.face_size - face_img.get_height()) // 2
            self.screen.blit(face_img, (img_x, img_y))

        for i in range(self.rows):
            for j in range(self.cols):
                x = (j * self.cell_size) + self.board_offset_x
                y = (i * self.cell_size) + self.board_offset_y
                cell = self.board.board[i][j]
                
                if not cell.opened:
                    if cell.flagged:
                        self.screen.blit(self.images.get("Flag"), (x, y))
                    else:
                        self.screen.blit(self.images.get("Unknown"), (x, y))
                else:
                    if cell.is_mine:
                        self.screen.blit(self.images.get("Mine"), (x, y))
                        if cell.exploded:
                            self.screen.blit(self.images.get("Exploded"), (x, y))
                    else:
                        key = "Tile" + str(cell.neighbor_mine)
                        self.screen.blit(self.images.get(key), (x, y))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.cell_size = min(event.w // (self.cols + 1), event.h // (self.rows + 4))
                    self.cell_size = max(10, int(self.cell_size))
                    
                    self.margin = self.cell_size // 2
                    self.header_height = int(self.cell_size * 2.5)
                    self.board_offset_x = self.margin
                    self.board_offset_y = self.margin + self.header_height + self.margin
                    
                    self.width = (self.cols * self.cell_size) + (2 * self.margin)
                    self.height = self.board_offset_y + (self.rows * self.cell_size) + self.margin
                    
                    self.face_size = int(self.cell_size * 1.6)
                    self.face_x = (self.width - self.face_size) // 2
                    self.face_y = self.margin + (self.header_height - self.face_size) // 2
                    self.face_rect = pygame.Rect(self.face_x, self.face_y, self.face_size, self.face_size)
                    
                    self.scale_assets()
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    if self.face_rect.collidepoint(mouse_x, mouse_y):
                        if event.button == 1: 
                            self.reset_game()
                            
                    # Nếu chưa thua và chưa thắng thì mới cho phép click vào bãi mìn
                    elif not self.game_over and not self.game_won:
                        in_board_x = self.board_offset_x <= mouse_x < self.width - self.margin
                        in_board_y = self.board_offset_y <= mouse_y < self.height - self.margin
                        
                        if in_board_x and in_board_y:
                            if not self.timer_started:
                                self.timer_started = True
                                self.start_time = pygame.time.get_ticks()

                            c = (mouse_x - self.board_offset_x) // self.cell_size
                            r = (mouse_y - self.board_offset_y) // self.cell_size
                            
                            if 0 <= r < self.rows and 0 <= c < self.cols:
                                cell = self.board.board[r][c]
                                
                                if event.button == 1:
                                    if not cell.opened:
                                        if not cell.flagged:
                                            if not cell.is_mine:
                                                self.board.flood_fill(r, c) 
                                            else:
                                                cell.exploded = True
                                                self.game_over = True 
                                                for i in range(self.rows):
                                                    for j in range(self.cols):
                                                        if self.board.board[i][j].is_mine:
                                                            self.board.board[i][j].opened = True
                                                            
                                    else:
                                        if cell.neighbor_mine > 0:
                                            flags_around = 0
                                            for dr in [-1, 0, 1]:
                                                for dc in [-1, 0, 1]:
                                                    if dr == 0 and dc == 0: continue
                                                    nr, nc = r + dr, c + dc
                                                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                                        if self.board.board[nr][nc].flagged:
                                                            flags_around += 1
                                            
                                            if flags_around == cell.neighbor_mine:
                                                for dr in [-1, 0, 1]:
                                                    for dc in [-1, 0, 1]:
                                                        if dr == 0 and dc == 0: continue
                                                        nr, nc = r + dr, c + dc
                                                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                                            n_cell = self.board.board[nr][nc]
                                                            if not n_cell.opened and not n_cell.flagged:
                                                                if n_cell.is_mine:
                                                                    n_cell.exploded = True
                                                                    self.game_over = True
                                                                    for i in range(self.rows):
                                                                        for j in range(self.cols):
                                                                            if self.board.board[i][j].is_mine:
                                                                                self.board.board[i][j].opened = True
                                                                else:
                                                                    self.board.flood_fill(nr, nc)
                                                                    
                                elif event.button == 3:
                                    if not cell.opened:
                                        cell.flagged = not cell.flagged 
                                        self.flags_placed += 1 if cell.flagged else -1
                                        
                            # Kiểm tra điều kiện thắng sau khi xử lý xong click
                            self.check_win()
            
            self.draw()
            
        pygame.quit()