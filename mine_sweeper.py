import tkinter as tk
import random
import tkinter.font as tkFont


class MinesweeperApp:
    def __init__(self, master, rows=20, cols=20, num_mines=50):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]
        self.mines = set()
        self.visited = set()
        self.flags = set()
        self.first_click = True  # Initialize the first_click attribute

        self.create_board()
        self.create_buttons()


    def create_board(self):
        # Place mines randomly
        while len(self.mines) < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mines.add((r, c))
        # Place numbers indicating adjacent mines
        for r, c in self.mines:
            self.board[r][c] = '*'

    def count_adjacent_mines(self, row, col):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        count = 0
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] == '*':
                count += 1
        return count

    def reveal_cell(self, row, col, cascade_depth=5):
        if (row, col) in self.visited or (row, col) in self.flags:
            return
        self.visited.add((row, col))

        # If mine, game over
        if (row, col) in self.mines:
            self.buttons[row][col].config(text='💣', bg='red')
            self.game_over()
            return

        # Count adjacent mines
        adjacent_mines = self.count_adjacent_mines(row, col)
        self.board[row][col] = str(adjacent_mines) if adjacent_mines > 0 else ' '

        # Choose text color based on the number of adjacent mines
        colors = {
            1: 'blue',
            2: 'green',
            3: 'red',
            4: 'purple',
            5: 'maroon',
            6: 'cyan',
            7: 'black',
            8: 'gray'
        }
        color = colors.get(adjacent_mines, 'black')  # Default to black if no mines

        # Create a bold font with a smaller size
        bold_font = tkFont.Font(weight="bold", size=8)

        # Update button display
        self.buttons[row][col].config(
            text=self.board[row][col],
            state=tk.DISABLED,
            relief=tk.SUNKEN,
            bg='grey',
            disabledforeground=color,  # Correct parameter for disabled buttons
            font=bold_font  # Apply bold font with smaller size
        )

        # If no adjacent mines and cascade_depth > 0, reveal neighbors
        if adjacent_mines == 0 and cascade_depth > 0:
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    self.reveal_cell(nr, nc, cascade_depth - 1)




    def toggle_flag(self, row, col):
        button = self.buttons[row][col]

        if (row, col) in self.flags:  # Remove the flag
            self.flags.remove((row, col))
            button.config(text='', bg='SystemButtonFace')
        elif button['state'] != tk.DISABLED:  # Add a flag
            self.flags.add((row, col))
            button.config(text='🚩', bg='yellow')

    def check_win(self):
        # Win if all non-mine cells are revealed
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.mines and self.buttons[r][c]['state'] != tk.DISABLED:
                    return False
        return True

    def game_over(self):
        # Reveal all mines
        for r, c in self.mines:
            self.buttons[r][c].config(text='💣', bg='red')
        for r in range(self.rows):
            for c in range(self.cols):
                self.buttons[r][c].config(state=tk.DISABLED)
        self.master.title("Game Over!")

    def create_buttons(self):
        for r in range(self.rows):
            for c in range(self.cols):
                button = tk.Button(
                    self.master, width=2, height=1, command=lambda r=r, c=c: self.on_click(r, c)
                )
                button.grid(row=r, column=c)
                button.bind('<Button-3>', lambda event, r=r, c=c: self.on_right_click(r, c))
                self.buttons[r][c] = button

    def on_click(self, row, col):
        if self.first_click:
            self.adjust_board_for_first_click(row, col)
            self.first_click = False
            self.reveal_cell(row, col, cascade_depth=3)  # Limit cascade on the first click
        else:
            if (row, col) in self.flags:  # Ignore clicks on flagged cells
                return
            if (row, col) in self.mines:
                self.game_over()
            else:
                self.reveal_cell(row, col)  # Normal behavior
                # Check win condition immediately after revealing a cell
                if self.check_win():
                    self.master.title("You Win!")
                    for r in range(self.rows):
                        for c in range(self.cols):
                            self.buttons[r][c].config(state=tk.DISABLED)


    def on_right_click(self, row, col):
        self.toggle_flag(row, col)

    def adjust_board_for_first_click(self, row, col):
        """
        Ensure the first click is safe by removing mines from the clicked cell and its neighbors.
        """
        # Remove any mine in the clicked cell or its neighbors
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        safe_zone = set()

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                safe_zone.add((nr, nc))

        # Remove mines from the safe zone
        self.mines -= safe_zone

        # Add back mines to maintain the correct count, avoiding the safe zone
        while len(self.mines) < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if (r, c) not in self.mines and (r, c) not in safe_zone:
                self.mines.add((r, c))

        # Recalculate the board to reflect the updated mine positions
        self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        for r, c in self.mines:
            self.board[r][c] = '*'



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper")
    app = MinesweeperApp(root)
    root.mainloop()
