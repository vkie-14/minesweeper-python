import pygame
import os
import json
from src.board import Board
from src.solver import Solver
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
INITIAL_CELL_SIZE = 40

class Game:
    def __init__(self, rows, cols, mines):
        """
        Khởi tạo trạng thái trò chơi, cửa sổ pygame, các tài nguyên assets và hệ thống menu.
        Tham số:
            rows: số hàng của bãi mìn.
            cols: số cột của bãi mìn.
            mines: số lượng mìn khởi tạo.
        
        Thuộc tính:
            rows: số hàng của bãi mìn.
            cols: số cột của bãi mìn.
            mines: số lượng mìn khởi tạo.
            board: bãi mìn.
            flags_placed: số cờ đã đặt.

            timer_started: bắt đầu đếm giờ.
            start_time: thời gian bắt đầu.
            elapsed_time: biến đếm.

            game_over: trạng thái kết thúc game.
            game_won: trạng thái thắng.

            cell_size: kích thước một cell.
            margin: kích thước khung viền ngoài.
            header_height: kích thước phần phía trên bãi mìn.
            width: kích thước chiều rộng của cả giao diện.
            height: kích thước chiều cao của cả giao diện.

            state: trạng thái hiện thại của game.
            current_mode: chế độ chơi hiện tại.
            current_difficulty: độ khó hiện tại.

            high_score_file: tên file chứa dữ liệu high score.
            high_scores: dự liệu high score.
        """
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.mines = mines 
        self.board = Board(rows, cols, mines)

        # Bộ đếm cờ và thời gian.
        self.flags_placed = 0
        self.timer_started = False
        self.start_time = 0
        self.elapsed_time = 0
        self.game_over = False
        self.game_won = False 

        # Những thông số cơ bản cho giao diện màn chơi chính.
        self.cell_size = INITIAL_CELL_SIZE
        self.margin = self.cell_size // 2  
        self.header_height = int(self.cell_size * 2) 
        
        self.board_offset_x = self.margin
        self.board_offset_y = self.margin + self.header_height + self.margin
        
        self.width = (cols * self.cell_size) + (2 * self.margin)
        self.height = self.board_offset_y + (rows * self.cell_size) + self.margin

        self.face_size = int(self.cell_size * 1.6)
        self.face_x = (self.width - self.face_size) // 2
        self.face_y = self.margin + (self.header_height - self.face_size) // 2
        self.face_rect = pygame.Rect(self.face_x, self.face_y, self.face_size, self.face_size)

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Minesweeper")

        # Tải các tài nguyên Assets.
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

        self.state = "MAIN_MENU"
        self.current_mode = "standard"
        self.current_difficulty = "easy"

        # Thiết lập font chữ, tải high scores từ file.
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Impact", 48)
        self.btn_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.score_font = pygame.font.SysFont("Courier New", 22, bold=True)

        self.high_score_file = "highscore.json"
        self.high_scores = {
            "standard": {"easy": 999, "normal": 999, "hard": 999},
            "no_guessing": {"easy": 999, "normal": 999, "hard": 999}
        }
        self.load_high_scores()

        self.ui_rects = {}
        self.current_hint = None

    def load_high_scores(self):
        """
        Đọc dữ liệu high score từ file json.
        Nếu file không tồn tại, hệ thống sử dụng dữ liệu mặc định.
        """
        if os.path.exists(self.high_score_file):
            try:
                with open(self.high_score_file, "r") as f:
                    loaded_data = json.load(f)
                    for mode in self.high_scores:
                        if mode in loaded_data and isinstance(loaded_data[mode], dict):
                            for diff in self.high_scores[mode]:
                                if diff in loaded_data[mode]:
                                    self.high_scores[mode][diff] = loaded_data[mode][diff]
            except:
                pass
    
    def save_high_scores(self, mode, difficulty, time):
        """
        So sánh và lưu kỷ lục mới vào file json nếu thời gian hiện tại nhanh hơn kỷ lục trước đó.
        Tham số:
            mode: Chế độ chơi (standard hoặc no_guessing).
            difficulty: Độ khó (easy, normal, hoặc hard).
            time: Thời gian hoàn thành trò chơi (giây).
        """
        if time < self.high_scores[mode].get(difficulty, 999):
            self.high_scores[mode][difficulty] = time
            with open(self.high_score_file, "w") as f:
                json.dump(self.high_scores, f)

    def reset_game(self):
        """
        Làm mới trò chơi, trạng thái bảng mìn, bộ đếm giờ.
        """
        self.board = Board(self.rows, self.cols, self.mines)
        self.flags_placed = 0
        self.timer_started = False
        self.start_time = 0
        self.elapsed_time = 0
        self.game_over = False
        self.game_won = False # Reset lại trạng thái thắng
        self.current_hint = None

    def check_win(self):
        """
        Hàm kiểm tra điều kiện thắng game
        Nếu thắng tự động cắm cờ những ô còn lại.
        """
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
            self.flags_placed = self.mines 
            
            # Tự động cắm cờ vào các mìn còn lại
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board.board[i][j].is_mine:
                        self.board.board[i][j].flagged = True
            
            self.save_high_scores(self.current_mode, self.current_difficulty, self.elapsed_time)

    def set_difficulty(self, r, c, m):
        """
        Thiết lập độ khó mới, tính toán lại kích thước cửa sổ hiển thị.
        Tham số:
            r: số hàng mới.
            c: số cột mới.
            m: số mìn mới.
        """
        self.rows = r
        self.cols = c
        self.mines = m
        
        # Cập nhật lại kích thước cửa sổ
        self.width = (self.cols * self.cell_size) + (2 * self.margin)
        self.height = self.board_offset_y + (self.rows * self.cell_size) + self.margin
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        self.face_x = (self.width - self.face_size) // 2
        self.face_y = self.margin + (self.header_height - self.face_size) // 2
        self.face_rect = pygame.Rect(self.face_x, self.face_y, self.face_size, self.face_size)
        
        self.reset_game()
        self.state = "PLAYING"

    def scale_assets(self):
        """
        Scale lại kích thước cái assets cho vừa với cell_size trước đó.
        """
        for key, img in self.original_images.items():
            if key in ["Smile", "Die", "Win"]: # Thêm scale cho ảnh Win
                img_size = int(self.face_size * 0.8) 
                self.images[key] = pygame.transform.scale(img, (img_size, img_size))
            else:
                self.images[key] = pygame.transform.scale(img, (self.cell_size, self.cell_size))

    def draw_bevel(self, surface, rect, sunken=False, border_width=4):
        """
        Vẽ hiệu ứng viền.
        Tham số:
            surface: bề mặt cần vẽ lên.
            rect: đối tượng rect xác định vị trí và kích thước.
            sunken: True nếu muốn hiệu ứng lõm xuống, ngược lại là hiệu ứng lồi lên.
            border_width: độ dày đường viền.
        """
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
        """
        Hàm vẽ chữ số LED 7 đoạn cho bộ đếm giờ.
        Tham số:
            surface: bề mặt vẽ.
            x, y: tọa độ bắt đầu.
            w, h: chiều rộng và chiều cao chữ số.
            digit: Ký tự chữ só cần vẽ ('0' -> '9', '-' và ' ')
        """
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
        """
        Vẽ bảng điện tử chứa 3 chữ số LED (dùng cho bộ đếm mìn và đồng hồ).
        Tham số:
            surface: Bề mặt vẽ.
            x, y: Tọa độ bảng.
            width, height: Kích thước bảng.
            value: Giá trị số cần hiển thị.
        """
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

    

    def draw_playing(self):
        """
        Vẽ giao diện chính khi đang trong màn chơi, bao gồm: header, bộ đếm, mặt cười và bảng mìn.
        """
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

        if self.current_hint:
            action, targets, clues = self.current_hint
            highlight_surf = pygame.Surface((self.cell_size, self.cell_size))
            highlight_surf.set_alpha(100)

            highlight_surf.fill((50, 100, 255)) 
            for r, c in clues:
                x = (c * self.cell_size) + self.board_offset_x
                y = (r * self.cell_size) + self.board_offset_y
                self.screen.blit(highlight_surf, (x, y))
            
            if action == "SAFE":
                highlight_surf.fill((100, 255, 100)) 
            else:
                highlight_surf.fill((255, 50, 50))

            for r, c in targets:
                x = (c * self.cell_size) + self.board_offset_x
                y = (r * self.cell_size) + self.board_offset_y
                self.screen.blit(highlight_surf, (x, y))

        pygame.display.flip()

    def draw_button(self, surface, text, x, y, w, h):
        """
        vẽ nút bấm.
        Tham số:
            surface: Bề mặt vẽ.
            text: Nội dung chữ trên nút.
            x, y, w, h: Tọa độ và kích thước nút.
        Trả về:
            Đối tượng Rect của nút để phục vụ việc kiểm tra va chạm chuột.
        """
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, w, h)
        is_hovered = rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(surface, GRAY, rect)
        self.draw_bevel(surface, rect, sunken=is_hovered, border_width=4)
        
        text_surf = self.btn_font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        if is_hovered: text_rect.y += 2 # Hiệu ứng lún text khi di chuột
        surface.blit(text_surf, text_rect)
        return rect

    def draw_main_menu(self):
        """
        Vẽ màn hình Menu chính khi mới vào game.
        """
        self.screen.fill(GRAY)
        self.draw_bevel(self.screen, pygame.Rect(0, 0, self.width, self.height), sunken=False, border_width=6)
        
        title = self.title_font.render("MINESWEEPER", True, (200, 0, 0))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height * 0.15))
        
        bw, bh = 200, 50
        cx = self.width // 2 - bw // 2
        
        self.ui_rects['btn_start'] = self.draw_button(self.screen, "Start Game", cx, self.height * 0.4, bw, bh)
        self.ui_rects['btn_score'] = self.draw_button(self.screen, "High Score", cx, self.height * 0.55, bw, bh)
        pygame.display.flip()

    def draw_mode_select(self):
        """
        Vẽ màn hình lựa chọn chế độ chơi (Standard hoặc No-guessing).
        """
        self.screen.fill(GRAY)
        self.draw_bevel(self.screen, pygame.Rect(0, 0, self.width, self.height), sunken=False, border_width=6)
        
        title = self.title_font.render("SELECT MODE", True, BLACK)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height * 0.15))
        
        bw, bh = 220, 50
        cx = self.width // 2 - bw // 2
        
        self.ui_rects['btn_standard'] = self.draw_button(self.screen, "Standard Mode", cx, self.height * 0.35, bw, bh)
        self.ui_rects['btn_noguess'] = self.draw_button(self.screen, "No-Guessing", cx, self.height * 0.5, bw, bh)
        self.ui_rects['btn_back'] = self.draw_button(self.screen, "Back", cx, self.height * 0.7, bw, bh)
        pygame.display.flip()

    def draw_difficulty_select(self):
        """
        Vẽ màn hình lựa chọn độ khó tương ứng với chế độ chơi đã chọn.
        """
        self.screen.fill(GRAY)
        self.draw_bevel(self.screen, pygame.Rect(0, 0, self.width, self.height), sunken=False, border_width=6)
        
        mode_text = "STANDARD" if self.current_mode == "standard" else "NO-GUESSING"
        title = self.title_font.render(f"{mode_text} - DIFFICULTY", True, BLACK)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height * 0.15))
        
        bw, bh = 200, 50
        cx = self.width // 2 - bw // 2
        
        self.ui_rects['btn_easy'] = self.draw_button(self.screen, "Easy (9x9)", cx, self.height * 0.3, bw, bh)
        self.ui_rects['btn_med'] = self.draw_button(self.screen, "Normal (16x16)", cx, self.height * 0.45, bw, bh)
        self.ui_rects['btn_hard'] = self.draw_button(self.screen, "Hard (16x30)", cx, self.height * 0.6, bw, bh)
        self.ui_rects['btn_back_diff'] = self.draw_button(self.screen, "Back", cx, self.height * 0.75, bw, bh)
        pygame.display.flip()

    def draw_high_score(self):
        """
        Vẽ bảng hiển thị kỷ lục thời gian cho tất cả các chế độ và độ khó.
        """
        self.screen.fill(GRAY)
        self.draw_bevel(self.screen, pygame.Rect(0, 0, self.width, self.height), sunken=True, border_width=6)
        
        title = self.title_font.render("HIGH SCORES", True, BLACK)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, self.height * 0.05))
        
        col1_x = self.width * 0.25
        col2_x = self.width * 0.75
        
        head_font = pygame.font.SysFont("Arial", 24, bold=True)
        st_head = head_font.render("STANDARD", True, (0, 100, 0))
        ng_head = head_font.render("NO-GUESSING", True, (0, 0, 150))
        
        self.screen.blit(st_head, (col1_x - st_head.get_width()//2, self.height * 0.2))
        self.screen.blit(ng_head, (col2_x - ng_head.get_width()//2, self.height * 0.2))
        
        diffs = ["easy", "normal", "hard"]
        y_start = self.height * 0.35
        y_gap = self.height * 0.12
        
        for i, diff in enumerate(diffs):
            st_val = self.high_scores["standard"][diff]
            ng_val = self.high_scores["no_guessing"][diff]
            
            st_txt = self.score_font.render(f"{diff.capitalize()}: {st_val}s", True, BLACK)
            ng_txt = self.score_font.render(f"{diff.capitalize()}: {ng_val}s", True, BLACK)
            
            self.screen.blit(st_txt, (col1_x - st_txt.get_width()//2, y_start + i*y_gap))
            self.screen.blit(ng_txt, (col2_x - ng_txt.get_width()//2, y_start + i*y_gap))
            
        bw, bh = 150, 45
        self.ui_rects['btn_back'] = self.draw_button(self.screen, "Back", self.width//2 - bw//2, self.height * 0.85, bw, bh)
        pygame.display.flip()

    def draw(self):
        """
        Điều phối hiển thị, quyết định màn hình nào sẽ được vẽ dựa trên self.state.
        """
        if self.state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.state == "MODE_SELECT":
            self.draw_mode_select()
        elif self.state == "DIFFICULTY_SELECT": # Bổ sung thêm state này
            self.draw_difficulty_select()
        elif self.state == "HIGH_SCORE":
            self.draw_high_score()
        elif self.state == "PLAYING":
            self.draw_playing()

    def run(self):
        """
        Vòng lặp chính của trò chơi, xử lý các sự kiện người chơi, cập nhật logic game
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Xử lý sự kiện thay đổi kích thước cửa sổ game.
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

                # Xử lý sự kiện bấm chuột.
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Lấy địa chỉ ô trên bãi mìn dựa vào tọa độ click chuột.
                    self.current_hint = None
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Xử lý điều hướng giao diện bên ngoài trò chơi.
                    if self.state == "MAIN_MENU":
                        if self.ui_rects.get('btn_start', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.state = "MODE_SELECT"
                        elif self.ui_rects.get('btn_score', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.state = "HIGH_SCORE"
                    
                    elif self.state == "MODE_SELECT":
                        if self.ui_rects.get('btn_standard', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.current_mode = "standard"
                            self.state = "DIFFICULTY_SELECT" # Chuyển sang bảng chọn độ khó
                        elif self.ui_rects.get('btn_noguess', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.current_mode = "no_guessing"
                            self.state = "DIFFICULTY_SELECT" # Chuyển sang bảng chọn độ khó
                        elif self.ui_rects.get('btn_back', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.state = "MAIN_MENU"
                            
                    elif self.state == "DIFFICULTY_SELECT":
                        if self.ui_rects.get('btn_easy', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.current_difficulty = "easy"
                            self.set_difficulty(9, 9, 10) # 9x9, 10 mìn
                        elif self.ui_rects.get('btn_med', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.current_difficulty = "normal"
                            self.set_difficulty(16, 16, 40) # 16x16, 40 mìn
                        elif self.ui_rects.get('btn_hard', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.current_difficulty = "hard"
                            self.set_difficulty(16, 30, 99) # 16x30, 99 mìn
                        elif self.ui_rects.get('btn_back_diff', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.state = "MODE_SELECT"

                    elif self.state == "HIGH_SCORE":
                        if self.ui_rects.get('btn_back', pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                            self.state = "MAIN_MENU"

                    elif self.state == "PLAYING":
                        # Bắt sự kiện bấm mặt cười để thoát ra Menu (hoặc có thể đổi thành chơi lại)
                        if self.face_rect.collidepoint(mouse_pos):
                            self.state = "MAIN_MENU"
                        
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
                                    # Xử lý các sự kiện nhấn bằng chuột trái.
                                    if event.button == 1:
                                        if not cell.opened:
                                            if not cell.flagged:
                                                if not self.board.mines_placed:
                                                    if self.current_mode == "no_guessing":
                                                        self.board.generate_no_guess_board(r, c)
                                                    else:
                                                        self.board.place_mines(r, c)
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
                                            # Đếm số cờ xung quanh.
                                            if cell.neighbor_mine > 0:
                                                flags_around = 0
                                                for dr in [-1, 0, 1]:
                                                    for dc in [-1, 0, 1]:
                                                        if dr == 0 and dc == 0: continue
                                                        nr, nc = r + dr, c + dc
                                                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                                            if self.board.board[nr][nc].flagged:
                                                                flags_around += 1
                                                # Chức năng mở ô nhanh khi đã cắm đủ cờ xung quanh.
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
                                    # Xử lý các sự kiện bấm chuột phải.
                                    elif event.button == 3:
                                        if not cell.opened:
                                            cell.flagged = not cell.flagged 
                                            self.flags_placed += 1 if cell.flagged else -1      
                # Chức năng gợi ý.
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_h or event.key == pygame.K_SPACE) and self.state == "PLAYING" and not self.game_over and not self.game_won:
                        if not self.board.mines_placed:
                            self.board.place_mines(self.rows // 2, self.cols // 2)
                            self.timer_started = True
                            self.start_time = pygame.time.get_ticks()

                        bot = Solver(self.board)
                        self.current_hint = bot.get_hint()

            # Kiểm tra điều kiện thắng sau mỗi sự kiện.                      
            self.check_win()
            # Vẽ lại bãi mìn sau mỗi sự kiện.
            self.draw()
            
        pygame.quit()