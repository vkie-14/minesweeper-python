"""
Quản lý board
"""
import random
from cell import Cell

class Board:
    """
    Khởi tạo ra bãi mìn ban đầu.

    Các thuộc tính:
        rows: Số hàng.
        cols: Số cột.
        mine_cnt: Số mìn.
        board: Ma trận chứa các phần tử là các Cells
    """
    def __init__(self, rows, cols, mine_cnt):
        self.rows = rows
        self.cols = cols
        self.mine_cnt = mine_cnt
        self.board = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.place_mines()
        self.count_neighbors()
    
    """
    Sinh mìn ngẫu nhiên lên board.
    """
    def place_mines(self):
        cnt = 0
        while cnt < self.mine_cnt:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            if not self.board[x][y].is_mine:
                self.board[x][y].is_mine = True
                cnt += 1
    
    """
    Đém số mìn xung quanh một ô
    Input: Board sau khi được sinh mìn.
    Output: Tất cả các ô còn lại chứa giá trị là số mìn xung quanh chúng.
    """
    def count_neighbors(self):
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
        if not (0 <= row < self.rows and 0 <= col <= self.cols):
            return
        cell = self.board[row][col]
        cell.opened = True
        if cell.opened or cell.is_mine:
            return
        
        if cell.neighbor_mine == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    if (0 <= row + dx < self.rows and 0 <= col + dy < self.cols):
                        self.flood_fill(row + dx, col + dy)