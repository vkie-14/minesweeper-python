import pygame
from src.board import Board

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
CELL_SIZE = 40

class Game:
    def __init__(self, rows, cols, mines):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.board = Board(rows, cols, mines)
        
        # Tính toán kích thước cửa sổ dựa trên số ô
        self.width = cols * CELL_SIZE
        self.height = rows * CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper UIT")
        
        self.running = True

    def draw(self):
        self.screen.fill(WHITE)
        for i in range(self.rows):
            for j in range(self.cols):
                x = i * CELL_SIZE
                y = j * CELL_SIZE
                cell = self.board.board[i][j]
                if not cell.opened:
                    pygame.draw.rect(self.screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(self.screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.draw()
        pygame.quit()