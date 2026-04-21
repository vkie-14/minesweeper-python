import pygame
import os
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
        pygame.display.set_caption("Minesweeper")


        self.images = {}
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'Assets')
        image_files = {
            "Tile1": "Tile1.png",
            "Tile2": "Tile2.png",
            "Tile3": "Tile3.png",
            "Tile4": "Tile4.png",
            "Tile5": "Tile5.png",
            "Tile6": "Tile6.png",
            "Tile7": "Tile7.png",
            "Tile8": "Tile8.png",
            "Tile0": "TileEmpty.png",
            "Exploded": "TileExploded.png",
            "Flag": "TileFlag.png",
            "Mine": "TileMine.png",
            "Unknown": "TileUnknown.png"
        }

        for key, file_name in image_files.items():
            full_path = os.path.join(assets_path, file_name)
            img = pygame.image.load(full_path).convert_alpha()
            img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            self.images[key] = img

        self.running = True

    def draw(self):
        self.screen.fill(WHITE)
        for i in range(self.rows):
            for j in range(self.cols):
                x = j * CELL_SIZE
                y = i * CELL_SIZE
                cell = self.board.board[i][j]
                if not cell.opened:
                    if cell.flagged:
                        self.screen.blit(self.images["Flag"], (x, y))
                    else:
                        self.screen.blit(self.images["Unknown"], (x, y))
                else:
                    if cell.is_mine:
                        self.screen.blit(self.images["Mine"], (x, y))
                        if cell.exploded:
                            self.screen.blit(self.images["Exploded"], (x, y))
                    else:
                        key = "Tile" + str(cell.neighbor_mine)
                        self.screen.blit(self.images[key], (x, y))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    c = mouse_x // CELL_SIZE
                    r = mouse_y // CELL_SIZE
                    cell = self.board.board[r][c]
                    if event.button == 1:
                        if not cell.is_mine:
                            self.board.flood_fill(r, c) 
                        else:
                            cell.exploded = True
                            for i in range(self.rows):
                                for j in range(self.cols):
                                    if self.board.board[i][j].is_mine:
                                        self.board.board[i][j].opened = True
                    elif event.button == 3:
                        cell.flagged = not cell.flagged 
            
            self.draw()
            
        
        pygame.quit()