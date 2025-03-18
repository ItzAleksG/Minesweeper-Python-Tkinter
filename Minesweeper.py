import tkinter as tk
from tkinter import ttk
from idlelib.tooltip import Hovertip

from random import randint
from threading import Thread
from time import sleep

ELEMENTS = {
            'mines': '💣',
            'flags': '🚩',
            'fakeflags': 'X',
            'nothing': '',
            'emoji': {
                'default': '🙂',
                'fail': '💀',
                'win': '😎'
            }
        }

COLORS = {
    'nums': {
        1: '#0000ff',
        2: '#008000',
        3: '#ff0000',
        4: '#00008b',
        5: '#8b0000',
        6: '#008b8b',
        7: '#000000',
        8: '#778899'
    },
    'flag': '#F23607',
    'fakeflag': 'lightblue',
    'water': 'lightblue',
    'closed': ['#AAD751', '#A2D149'],
    'opened': ['#E5C29F', '#E2B488'],
    'background': '#87AF3A',
    'panel': '#4A752C'
}

DIFFICULTIES = {
            'easy': {
                'name': 'Easy',
                'width': 10,
                'height': 8,
                'mines': 10
            },
            'medium': {
                'name': 'Medium',
                'width': 18,
                'height': 14,
                'mines': 40
            },
            'hard': {
                'name': 'Hard',
                'width': 30,
                'height': 16,
                'mines': 100
            }
        }

class Minesweeper():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Minesweeper')
        self.root.resizable(0, 0)
        self.root.config(bg=COLORS['panel'])
        
        self.panel = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['panel'])
        self.panel.grid(column=0, row=0)
        
        self.mineCounter = tk.Label(self.panel, width=5)
        self.mineCounter.grid(column=0, row=0, padx=10)

        self.restartBtn = tk.Button(self.panel, text=ELEMENTS['emoji']['default'], font='helv36', width=4, height=2, cursor='hand2', command=lambda: self.restart())
        self.restartBtn.grid(column=1, row=0, padx=10)
        Hovertip(self.restartBtn, 'Restart', 200)

        self.timeLabel = tk.Label(self.panel, text=f'⏰000', width=5)
        self.timeLabel.grid(column=2, row=0, padx=10)
        
        dif_var = tk.StringVar(value=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES][0])
        self.difficulty = ttk.Combobox(self.root, values=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES], textvariable=dif_var, width=10, state='readonly')
        self.difficulty.grid(column=0, row=0, sticky='w', padx=10)
        self.difficulty.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected())
        self.combobox_selected(False)
        
        self.create_board()
        
        self.root.mainloop()
    
    def combobox_selected(self, combobox=True):
        if combobox:
            selection = DIFFICULTIES[[i for i in DIFFICULTIES][[DIFFICULTIES[i]['name'] for i in DIFFICULTIES].index(self.difficulty.get())]]
        else: selection = DIFFICULTIES[[i for i in DIFFICULTIES][0]]

        self.width = selection['width']
        self.height = selection['height']
        self.mines = selection['mines']
        
        if combobox: self.restart()
    
    def restart(self):
        self.timerOff = True
        self.boardFrame.destroy()
        self.timeLabel.config(text='⏰000')
        self.restartBtn.config(text=ELEMENTS['emoji']['default'])
        self.create_board()
    
    def create_board(self):
        self.board = []
        self.opened = []
        self.withflag = []
        
        self.boardFrame = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['background'])
        self.boardFrame.grid(column=0, row=1)
        self.mineCounter.config(text=f'{ELEMENTS['flags']}{"0"*(3-len(str(self.mines)))}{self.mines}')
        
        self.boardBtns = [[tk.Button(self.boardFrame, fg=COLORS['flag'],bg=COLORS['closed'][(x+y)%2], cursor='hand2', height=2, width=4) for x in range(self.width)] for y in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                self.boardBtns[y][x].config(command=lambda x=x, y=y: self.left_click(x, y),
                                            disabledforeground='black',
                                            relief=tk.FLAT, font='Courier 10', activebackground=COLORS['background'])
                self.boardBtns[y][x].grid(column=x, row=y)
                self.boardBtns[y][x].bind("<Button-3>", lambda event, x=x, y=y: self.right_click(x, y))
    
    def generate_board(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for _ in range(self.mines):
            while True:
                py = randint(0, self.height-1)
                px = randint(0, self.width-1)
                if self.opened[0] != (px, py) and self.board[py][px] != ELEMENTS['mines']:
                    if self.width*self.height-self.mines >= 9:
                        lst = []
                        for dy in range(-1, 2):
                            for dx in range(-1, 2):
                                lst.append((dx+px, dy+py))
                        if self.opened[0] in lst: continue
                    self.board[py][px] = ELEMENTS['mines']
                    break
        
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != ELEMENTS['mines']:
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if self.height > dy+y >= 0 and self.width > dx+x >= 0 and self.board[dy+y][dx+x] == ELEMENTS['mines']:
                                self.board[y][x] += 1
    
    def reveal_cell(self, x: int, y: int):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if self.width > dx+x >= 0 and self.height > dy+y >= 0 and self.boardBtns[dy+y][dx+x]['state'] != tk.DISABLED:
                    self.left_click(x+dx, y+dy)
    
    def left_click(self, x: int, y: int):
        if (x, y) in self.withflag: return
        self.opened.append((x, y))
        if len(self.opened) == 1:
            self.generate_board()
            Thread(target = self.timer).start()
        if self.board[y][x] == ELEMENTS['mines'] and (x, y) not in self.withflag: self.end(False)
        else:
            self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow',
                                        text=self.board[y][x] if self.board[y][x] else ELEMENTS['nothing'],
                                        bg=COLORS['opened'][1] if self.board[y][x] else COLORS['opened'][0],
                                        disabledforeground=COLORS['nums'][self.board[y][x]] if self.board[y][x] in [i for i in COLORS['nums']] else 'black')
            if self.board[y][x] == 0: self.reveal_cell(x, y)
            if self.width*self.height-self.mines == len(self.opened): self.end(True)
    
    def right_click(self, x: int, y: int):
        if (x, y) not in self.withflag and (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED:
            self.withflag.append((x, y))
            self.boardBtns[y][x].config(text=ELEMENTS['flags'])
        elif (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED:
            self.withflag.remove((x, y))
            self.boardBtns[y][x].config(text='')
        self.mineCounter.config(text=f'{ELEMENTS['flags']}{"0"*(3-len(str(self.mines-len(self.withflag))))}{self.mines-len(self.withflag)}')
    
    def end(self, win: bool):
        self.timerOff = True
        if win:
            self.restartBtn.config(text=ELEMENTS['emoji']['win'])
            for y in range(self.height):
                for x in range(self.width):
                    self.boardBtns[y][x].config(text=ELEMENTS['nothing'], state=tk.DISABLED, cursor='arrow')
                    if self.board[y][x] != ELEMENTS['mines']: self.boardBtns[y][x]['bg'] = COLORS['water']
        else:
            self.restartBtn.config(text=ELEMENTS['emoji']['fail'])
            for y in range(self.height):
                for x in range(self.width):
                    self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow')
                    if self.board[y][x] == ELEMENTS['mines']:
                        self.boardBtns[y][x].config(text=ELEMENTS['mines'], bg='red')
                        if (x, y) in self.withflag:
                            self.boardBtns[y][x]['bg'] = 'yellow'
                    elif (x, y) in self.withflag:
                        self.boardBtns[y][x].config(text=ELEMENTS['fakeflags'], bg=COLORS['fakeflag'])
    def timer(self):
        sec = 0
        self.timerOff = False
        while not self.timerOff:
            sec += 1
            self.timeLabel.config(text=f'⏰{'0'*(3-len(str(sec)))}{sec}')
            sleep(1)

if __name__ == '__main__':
    Minesweeper()