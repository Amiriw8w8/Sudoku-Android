import random
import copy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

BG = get_color_from_hex("#F4F6FB")
BLUE = get_color_from_hex("#2864E8")
GREEN = get_color_from_hex("#16A34A")
DARK = get_color_from_hex("#263445")

def valid(board, r, c, n):
    if n in board[r]:
        return False
    if any(board[i][c] == n for i in range(9)):
        return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == n:
                return False
    return True

def find_empty(board):
    best, count = None, 10
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                opts = sum(valid(board, r, c, n) for n in range(1, 10))
                if opts < count:
                    best, count = (r, c), opts
                if opts <= 1:
                    return best
    return best

def solve_board(board):
    pos = find_empty(board)
    if pos is None:
        return True
    r, c = pos
    nums = list(range(1, 10))
    for n in nums:
        if valid(board, r, c, n):
            board[r][c] = n
            if solve_board(board):
                return True
            board[r][c] = 0
    return False

def make_game():
    board = [[0] * 9 for _ in range(9)]
    def fill():
        pos = find_empty(board)
        if pos is None:
            return True
        r, c = pos
        nums = list(range(1, 10))
        random.shuffle(nums)
        for n in nums:
            if valid(board, r, c, n):
                board[r][c] = n
                if fill():
                    return True
                board[r][c] = 0
        return False
    fill()
    solution = copy.deepcopy(board)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:42]:
        board[r][c] = 0
    return board, solution

class SudokuApp(App):
    def build(self):
        self.title = "Sudoku Classic"
        Window.clearcolor = BG
        self.history = []
        self.selected = None
        self.new_game()
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        header = BoxLayout(size_hint_y=None, height=dp(42))
        title = Label(text="[b]SUDOKU CLASSIC[/b]", markup=True, color=DARK, font_size="20sp")
        header.add_widget(title)
        root.add_widget(header)

        self.grid = GridLayout(cols=9, spacing=dp(1), size_hint=(1, .72))
        root.add_widget(self.grid)

        self.status = Label(text="یک خانه را انتخاب کن", color=DARK,
                            size_hint_y=None, height=dp(30), font_size="13sp")
        root.add_widget(self.status)

        numbers = GridLayout(cols=9, spacing=dp(3), size_hint_y=None, height=dp(48))
        for n in range(1, 10):
            b = Button(text=str(n), font_size="20sp", background_normal="",
                       background_color=get_color_from_hex("#E5EAF3"), color=DARK)
            b.bind(on_release=lambda _b, x=n: self.enter_number(x))
            numbers.add_widget(b)
        root.add_widget(numbers)

        actions = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(46))
        for label, callback, color in [
            ("پاک کردن", self.erase, DARK),
            ("راهنمایی", self.hint, BLUE),
            ("بازگشت", self.undo, DARK),
        ]:
            b = Button(text=label, font_size="14sp", background_normal="", background_color=color)
            b.bind(on_release=lambda _b, fn=callback: fn())
            actions.add_widget(b)
        root.add_widget(actions)

        actions2 = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(46))
        for label, callback, color in [
            ("بررسی جواب", self.check, GREEN),
            ("بازی جدید", self.new_game, BLUE),
        ]:
            b = Button(text=label, font_size="14sp", background_normal="", background_color=color)
            b.bind(on_release=lambda _b, fn=callback: fn())
            actions2.add_widget(b)
        root.add_widget(actions2)

        self.refresh_grid()
        return root

    def new_game(self, *_):
        self.puzzle, self.solution = make_game()
        self.values = copy.deepcopy(self.puzzle)
        self.fixed = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.history = []
        self.selected = None
        if hasattr(self, "status"):
            self.status.text = "بازی جدید شروع شد"
        if hasattr(self, "grid"):
            self.refresh_grid()

    def refresh_grid(self):
        self.grid.clear_widgets()
        for r in range(9):
            for c in range(9):
                v = self.values[r][c]
                fixed = self.fixed[r][c]
                bg = "#E7EDF7" if fixed else "#FFFFFF"
                if self.selected == (r, c):
                    bg = "#CFE0FF"
                btn = Button(text=str(v) if v else "", font_size="17sp",
                             bold=bool(fixed), color=get_color_from_hex("#171717" if fixed else "#2459BD"),
                             background_normal="", background_color=get_color_from_hex(bg),
                             size_hint=(1, 1))
                btn.bind(on_release=lambda _b, rr=r, cc=c: self.select(rr, cc))
                self.grid.add_widget(btn)

    def select(self, r, c):
        self.selected = (r, c)
        self.status.text = f"خانه انتخاب‌شده: سطر {r+1}، ستون {c+1}"
        self.refresh_grid()

    def save(self):
        self.history.append(copy.deepcopy(self.values))
        if len(self.history) > 100:
            self.history.pop(0)

    def enter_number(self, n):
        if self.selected is None:
            self.status.text = "اول یک خانه را انتخاب کن"
            return
        r, c = self.selected
        if self.fixed[r][c]:
            self.status.text = "این خانه از ابتدا پر بوده است"
            return
        self.save()
        self.values[r][c] = n
        self.refresh_grid()

    def erase(self):
        if self.selected is None:
            self.status.text = "اول یک خانه را انتخاب کن"
            return
        r, c = self.selected
        if self.fixed[r][c]:
            self.status.text = "نمی‌توان خانه ثابت را پاک کرد"
            return
        self.save()
        self.values[r][c] = 0
        self.refresh_grid()

    def undo(self):
        if self.history:
            self.values = self.history.pop()
            self.refresh_grid()
            self.status.text = "حرکت قبلی برگشت"
        else:
            self.status.text = "حرکتی برای بازگشت وجود ندارد"

    def hint(self):
        if self.selected is None:
            self.status.text = "برای راهنمایی یک خانه خالی انتخاب کن"
            return
        r, c = self.selected
        if self.fixed[r][c] or self.values[r][c]:
            self.status.text = "یک خانه خالی انتخاب کن"
            return
        self.save()
        self.values[r][c] = self.solution[r][c]
        self.refresh_grid()
        self.status.text = "راهنمایی وارد شد"

    def check(self):
        wrong = [(r, c) for r in range(9) for c in range(9)
                 if self.values[r][c] and self.values[r][c] != self.solution[r][c]]
        if wrong:
            self.status.text = f"{len(wrong)} خانه اشتباه است"
        elif all(all(row) for row in self.values):
            self.status.text = "آفرین! جدول را حل کردی"
            Popup(title="تبریک!", content=Label(text="سودوکو را با موفقیت حل کردی!"),
                  size_hint=(.8, .3)).open()
        else:
            self.status.text = "تا اینجا همه اعداد درست هستند"

    def solve(self):
        board = copy.deepcopy(self.values)
        if solve_board(board):
            self.save()
            self.values = board
            self.refresh_grid()
            self.status.text = "جدول حل شد"

if __name__ == "__main__":
    SudokuApp().run()
