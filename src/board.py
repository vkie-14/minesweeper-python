import random
from src.cell import Cell
from src.solver import Solver

class Board:
    def __init__(self, rows, cols, mine_cnt):
        """
        Khởi tạo ra bãi mìn ban đầu.
        Tham số:
            rows: số hàng.
            cols: số cột.
            mine_cnt: số mìn.
        Các thuộc tính:
            rows: Số hàng.
            cols: Số cột.
            mine_cnt: Số mìn.
            board: Ma trận chứa các phần tử là các Cells
        """
        self.rows = rows
        self.cols = cols
        self.mine_cnt = mine_cnt
        self.board = [[Cell() for _ in range(cols)] for _ in range(rows)]

        self.mines_placed = False
        
    def place_mines(self, first_row, first_col):
        """
        Sinh mìn ngẫu nhiên lên board. Không sinh lên phạm vị 3x3 ô xung quanh cú click đầu tiên của người chơi.
        Tham số:
            first_row, first_col: Địa chỉ cú click đầu tiên của người chơi
        """
        cnt = 0
        while cnt < self.mine_cnt:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)

            is_in_safe_zone = abs(x - first_row) <= 1 and abs(y - first_col) <= 1
            if not self.board[x][y].is_mine and not is_in_safe_zone:
                self.board[x][y].is_mine = True
                cnt += 1
            
        self.mines_placed = True
        self.count_neighbors()

    def count_neighbors(self):
        """
        Đém số mìn xung quanh một ô
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j].is_mine:
                    continue
                cnt = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        if 0 <= i + dx < self.rows and 0 <= j + dy < self.cols and self.board[i + dx][j + dy].is_mine:
                            cnt += 1
                self.board[i][j].neighbor_mine = cnt

    def flood_fill(self, row, col):
        """
        Hàm loang khi mở Cell.
        Tham số:
            row: số hàng của bãi mìn.
            col: số cột của bãi mìn
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        cell = self.board[row][col]
        
        if cell.opened or cell.is_mine:
            return
        cell.opened = True
        if cell.neighbor_mine == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    if (0 <= row + dx < self.rows and 0 <= col + dy < self.cols):
                        self.flood_fill(row + dx, col + dy)

    def swap_a_mine(self, safe_r, safe_c):
        """
        Hỗ trợ: Bốc 1 quả mìn ngẫu nhiên đổi chỗ với 1 ô trống
        Tham số:
            safe_r, safe_c: địa chỉ cú click đầu tiên của người chơi, tránh sinh mìn lên phạm vi 3x3 xung quanh.
        """
        mines = []
        empties = []
        
        for i in range(self.rows):
            for j in range(self.cols):
                is_safe_zone = abs(i - safe_r) <= 1 and abs(j - safe_c) <= 1
                
                if self.board[i][j].is_mine:
                    mines.append((i, j))
                elif not is_safe_zone:
                    empties.append((i, j))
                    
        if mines and empties:
            mr, mc = random.choice(mines)
            er, ec = random.choice(empties)
            # Hoán đổi vị trí.
            self.board[mr][mc].is_mine = False
            self.board[er][ec].is_mine = True
            
            self.count_neighbors()

    def generate_no_guess_board(self, first_r, first_c):
        """
        Thuật toán Generate & Swap tạo bảng No-guessing
        """
        self.place_mines(first_r, first_c)
        bot = Solver(self) 
        
        attempts = 0
        while attempts < 500:
            attempts += 1
            
            # Reset
            for i in range(self.rows):
                for j in range(self.cols):
                    self.board[i][j].opened = False
                    self.board[i][j].flagged = False
                    
            self.flood_fill(first_r, first_c)
            stuck = False
            
            while True:
                opened_count = sum(1 for i in range(self.rows) for j in range(self.cols) if self.board[i][j].opened)
                if opened_count == self.rows * self.cols - self.mine_cnt:
                    break 
                    
                hint = bot.get_hint()
                if hint:
                    action, targets, clues = hint
                    if action == "SAFE":
                        for tr, tc in targets:
                            self.flood_fill(tr, tc)
                    elif action == "FLAG":
                        for tr, tc in targets:
                            self.board[tr][tc].flagged = True
                else:
                    stuck = True 
                    break
                    
            if not stuck:
                break 
            else:
                self.swap_a_mine(first_r, first_c)

        # Trả bảng về trạng thái ban đầu để bắt đầu chơi.
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].opened = False
                self.board[i][j].flagged = False