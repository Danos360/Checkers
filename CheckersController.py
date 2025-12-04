class CheckersController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        view.on_piece_click = self.select_piece
        view.on_move_click = self.make_move

        self.view.draw_board(self.model.board)

    def select_piece(self, row, col):
        piece = self.model.get_piece(row, col)
        if not piece:
            return

        if piece != self.model.turn:
            return

        moves = self.model.get_moves(row, col)
        if not moves:
            return

        self.model.selected = (row, col)
        self.view.show_moves(moves)


    def make_move(self, row, col):
        old_row, old_col = self.model.selected
        self.model.move_piece(old_row, old_col, row, col)
        self.model.selected = None
        self.view.draw_board(self.model.board)
