class Solver:
    def __init__(self, board_object):
        """
        Khởi tạo Solver.
        Tham số:
            board_object: đối tượng bãi mìn hiện tại.
        """
        self.board = board_object
    
    def get_neighbor_info(self, r, c):
        """
        Quét các ô xung quanh để thu thập dữ kiện.
        Tham só:
            r, c: địa chỉ ô đang xét.
        Trả về: 
            tuple (unopened, flagged_count):
                unopened (list): danh sách địa chỉ các ô chưa được mở xung quanh.
                flagged_count: số lượng cờ đã cắm xung quanh ô đó.
        """
        unopened = []
        flagged_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.board.rows and 0 <= nc < self.board.cols:
                    cell = self.board.board[nr][nc]
                    if cell.flagged:
                        flagged_count += 1
                    elif not cell.opened:
                        unopened.append((nr, nc))
        return unopened, flagged_count

    def run_component(self, unopened_cells, border_numbers):
        """
        Chạy thuật toán Quay lui (Backtracking) để vét cạn các kịch bản xếp mìn hợp lệ cho một cụm ô độc lập.
        Sử dụng nhánh cận để tối ưu độ phức tạp.
        Tham số:
            unopened_cells (list): Danh sách tọa độ các ô chưa mở thuộc cụm đồ thị (Component) đang xét.
            border_numbers (list): Danh sách các ô số (dữ kiện) có liên kết với cụm ô chưa mở này.
                Mỗi phần tử là dictionary chứa: 'pos' (tọa độ), 'unopened' (tập các ô chưa mở chạm vào nó), 'missing' (số mìn còn thiếu).
        Trả về:
            tuple hoặc None
                - (safe_targets, mine_targets) nếu phân tích thành công và tìm ra ô chắc chắn 100%.
                    + safe_targets (list): Các ô KHÔNG chứa mìn trong MỌI kịch bản hợp lệ.
                    + mine_targets (list): Các ô CHỨA mìn trong MỌI kịch bản hợp lệ.
                - Trả về None nếu không thể suy luận chắc chắn.
        """
        valid_configs = []
        n = len(unopened_cells)
        
        def backtrack(index, current_mines):
            # Kiểm tra xem có ô số nào bị vi phạm ngay lúc này không.
            for num in border_numbers:
                mines_placed = sum(1 for u in num['unopened'] if u in current_mines)
                unassigned = sum(1 for u in num['unopened'] if u in unopened_cells[index:])
                
                # Bị lố số mìn cho phép -> Sai.
                if mines_placed > num['missing']: return
                # Không còn đủ chỗ trống để đặt mìn cho ô này -> Sai.
                if mines_placed + unassigned < num['missing']: return

            # Nếu đã điền thử hết tất cả các ô trong cụm này mà không vi phạm gì.
            if index == n:
                valid_configs.append(set(current_mines))
                return

            cell = unopened_cells[index]
            
            # Giả sử ô này có mìn.
            current_mines.add(cell)
            backtrack(index + 1, current_mines)
            current_mines.remove(cell)

            # Giả sử ô này an toàn.
            backtrack(index + 1, current_mines)

        # Bắt đầu chạy quay lui.
        backtrack(0, set())

        # Nếu không có kịch bản nào hợp lệ bỏ qua.
        if not valid_configs:
            return None

        safe_targets = []
        mine_targets = []

        # Phân tích các kịch bản hợp lệ.
        for cell in unopened_cells:
            is_mine_in_all = all(cell in config for config in valid_configs)
            is_safe_in_all = all(cell not in config for config in valid_configs)

            if is_mine_in_all: mine_targets.append(cell)
            if is_safe_in_all: safe_targets.append(cell)

        return safe_targets, mine_targets

    def get_hint(self):
        """
        Tính toán và trả vè một nước đi chắc chắn đúng dựa trên trạng thái hiện tại.
        Các luồng kiểm tra:
            1. Tìm ô hiển nhiên an toàn hoặc có mìn O(N).
            2. Tìm giao thoa tập hợp 2 ô liên kề 0(N^2).
            3. Tách các vùng biên thành đồ thị, quay lui nhánh cận để vét cạn mọi trường hợp.
        Trả về:
            tuple hoặc None: Trả về (Action, Targets, Clues) nếu tìm thấy gợi ý.
                - Action (str): "SAFE" (Gợi ý mở ô) hoặc "FLAG" (Gợi ý cắm cờ).
                - Targets (list): Danh sách tọa độ (r, c) các ô mục tiêu để thực hiện Action.
                - Clues (list): Danh sách tọa độ (r, c) các ô số đóng vai trò làm dữ kiện suy luận.
            Trả về None nếu Bot hoàn toàn bó tay.
        """
        # Luồng 1 --------------------------------------------------------
        # Tìm mìn hiển nhiên.
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.board[r][c]
                if cell.opened and cell.neighbor_mine > 0:
                    unopened, flags = self.get_neighbor_info(r, c)
                    if len(unopened) > 0 and len(unopened) + flags == cell.neighbor_mine:
                        return ("FLAG", unopened, [(r, c)])
        # Tìm ô an toàn hiển nhiên.
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.board[r][c]
                if cell.opened and cell.neighbor_mine > 0:
                    unopened, flags = self.get_neighbor_info(r, c)
                    if len(unopened) > 0 and flags == cell.neighbor_mine:
                        return ("SAFE", unopened, [(r, c)])
        
        # Luồng 2 -----------------------------------------------------------
        border_cell = []
        unopened_set = set()
        # Gom các ô vùng biện.
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.board[r][c]
                if cell.opened and cell.neighbor_mine > 0:
                    unopened, flags = self.get_neighbor_info(r, c)
                    if len(unopened) > 0:
                        missing_mines = cell.neighbor_mine - flags
                        border_cell.append({
                            'pos': (r, c),
                            'unopened': set(unopened), 
                            'missing': missing_mines
                        })
                        for u in unopened:
                            unopened_set.add(u)
        # So sánh từng cặp ô để đưa ra kết luận.
        for i in range(len(border_cell)):
            for j in range(i + 1, len(border_cell)):
                cell_A = border_cell[i]
                cell_B = border_cell[j]
                if cell_A['unopened'].issubset(cell_B['unopened']):
                    u_diff = cell_B['unopened'] - cell_A['unopened']
                    if len(u_diff) > 0:
                        E_diff = cell_B['missing'] - cell_A['missing']
                        if E_diff == 0:
                            return ("SAFE", list(u_diff), [cell_A['pos'], cell_B['pos']])
                        elif E_diff == len(u_diff):
                            return ("FLAG", list(u_diff), [cell_A['pos'], cell_B['pos']])
                        
                elif cell_B['unopened'].issubset(cell_A['unopened']):
                    U_diff = cell_A['unopened'] - cell_B['unopened']
                    if len(U_diff) > 0:
                        E_diff = cell_A['missing'] - cell_B['missing']
                        
                        if E_diff == 0:
                            return ("SAFE", list(U_diff), [cell_A['pos'], cell_B['pos']])
                        elif E_diff == len(U_diff):
                            return ("FLAG", list(U_diff), [cell_A['pos'], cell_B['pos']])
        
        # Luồng 3 ------------------------------------------------------------------
        visited_cells = set()
        components = []
        # Chia đường biên thành các thành phần liên thông bằng BFS.
        for u in unopened_set:
            if u not in visited_cells:
                comp_cells = []
                comp_nums = []

                q = [u]
                visited_cells.add(u)
                visited_num_pos = set()
                while q:
                    cur_cell = q.pop(0)
                    comp_cells.append(cur_cell)
                    for num in border_cell:
                        if cur_cell in num['unopened'] and num['pos'] not in visited_num_pos:
                            visited_num_pos.add(num['pos'])
                            comp_nums.append(num)

                            for next_cell in num['unopened']:
                                if next_cell not in visited_cells:
                                    visited_cells.add(next_cell)
                                    q.append(next_cell)
                
                components.append((comp_cells, comp_nums))

        # Ưu tiên giải các cụm nhỏ để tiết kiệm thời gian.
        components.sort(key=lambda x: len(x[0]))

        for comp_cells, comp_nums in components:
            # Giới hạn số phần tử 1 cụm để ngăn bị treo O(N^2).
            if 0 < len(comp_cells) <= 20:
                res = self.run_component(comp_cells, comp_nums)
                
                if res:
                    safe_cells, mine_cells = res
                    clues = [num['pos'] for num in comp_nums]
                    
                    if safe_cells:
                        return ("SAFE", safe_cells, clues)
                    if mine_cells:
                        return ("FLAG", mine_cells, clues)

        # Bot không giải được.
        return None
    
