class Cell:
    """
    Khởi tạo Cell ban đầu.

    Các thuộc tính:
        is_mine: Cell đó có chứa mìn không.
        opened: Cell đã được mở chưa.
        flagged: Cell có được cắm cờ không.
        neighbor_mine: Số lượng mìn xung quanh Cell.
        exploded: người chơi dẫm bom.
    """
    def __init__(self):
        self.is_mine = False
        self.opened = False
        self.flagged = False
        self.neighbor_mine = 0
        self.exploded = False

    """
    Thiết lập hiển thị cho Cell.
    """
    def __repr__(self):
        if self.is_mine:
            return "X"
        return str(self.neighbor_mine)