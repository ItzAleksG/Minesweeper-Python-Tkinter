import tkinter as tk # Library for creating the interface
from tkinter import ttk # Library for creating a pop-up menu
from idlelib.tooltip import Hovertip # Library for creating a drop-down menu on hovering

from random import randint # Library for generating a random number from a range
from threading import Thread # Library for starting a function without interrupting the execution of the rest of the program
from time import sleep # Library for stopping script/function execution for a certain period of time

ELEMENTS = { # Creating a global variable: Symbols of some elements
            'mines': '💣', # Mines
            'flags': '🚩', # Flag
            'fakeflags': 'X', # Flag without mine
            'nothing': '', # Nothing
            'emoji': { # Smileys for button
                'default': '🙂', # Normal
                'fail': '💀', # Defeat
                'win': '😎' # Victory
            }
        }

COLORS = { # Creating a global variable: colors
    'nums': { # Colors for numbers
        1: '#0000ff',
        2: '#008000',
        3: '#ff0000',
        4: '#00008b',
        5: '#8b0000',
        6: '#008b8b',
        7: '#000000',
        8: '#778899'
    },
    'flag': '#F23607', # Flag color
    'fakeflag': 'lightblue', # Flag background color without mine on defeat
    'water': 'lightblue', # Water color when winning
    'closed': ['#AAD751', '#A2D149'], # Colors of cells on the field
    'opened': ['#E5C29F', '#E2B488'], # Colors of open cells on the field ['empty', 'with digit']
    'background': '#87AF3A', # Field Background
    'panel': '#4A752C' # Panel background
}

DIFFICULTIES = { # Difficulty levels
            'easy': { # Simple
                'name': 'Easy',
                'width': 10, # Field length
                'height': 8, # Field height
                'mines': 10 # Number of mins
            },
            'medium': { # Medium
                'name': 'Medium',
                'width': 18, # Field length
                'height': 14, # Field height
                'mines': 40 # Number of mins
            },
            'hard': { # Difficult
                'name': 'Hard',
                'width': 30, # Field length
                'height': 16, # Field height
                'mines': 100 # Number of mins
            }
        }

class Minesweeper():
    def __init__(self):
        # Creating a game window
        self.root = tk.Tk() # Creation
        self.root.title('Minesweeper') # Title
        self.root.resizable(0, 0) # Ability to change the size
        self.root.config(bg=COLORS['panel']) # Setting background color (panel)
        
        # Creating the top panel
        self.panel = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['panel'])
        self.panel.grid(column=0, row=0)
        
        # Counter of remaining minutes
        self.mineCounter = tk.Label(self.panel, width=5)
        self.mineCounter.grid(column=0, row=0, padx=10)

        # Restart button
        self.restartBtn = tk.Button(self.panel, text=ELEMENTS['emoji']['default'], font='helv36', width=4, height=2, cursor='hand2', command=lambda: self.restart())
        self.restartBtn.grid(column=1, row=0, padx=10)
        Hovertip(self.restartBtn, 'Restart', 200) # Drop-down inscription on hovering

        # Stopwatch
        self.timeLabel = tk.Label(self.panel, text=f'⏰000', width=5)
        self.timeLabel.grid(column=2, row=0, padx=10)
        
        dif_var = tk.StringVar(value=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES][0]) # Getting the name of the first difficulty level for the initial output
        self.difficulty = ttk.Combobox(self.root, values=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES], textvariable=dif_var, width=10, state='readonly') # Creating a difficulty selection menu
        self.difficulty.grid(column=0, row=0, sticky='w', padx=10) # Locating the complexity selection menu in the interface
        self.difficulty.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected()) # Setting the script to start automatically when a difficulty is selected

        self.combobox_selected(False) # Starting the complexity selection function from the script
        self.create_board() # Field generation
        
        self.root.mainloop()
    
    def combobox_selected(self, combobox=True):
        ''' Changing difficulty levels '''
        # Getting the selected difficulty level
        if combobox: # Checking whether this function is called from the script or by the user
            selection = DIFFICULTIES[[i for i in DIFFICULTIES][[DIFFICULTIES[i]['name'] for i in DIFFICULTIES].index(self.difficulty.get())]] # Getting the complexity based on the user's choice
        else: selection = DIFFICULTIES[[i for i in DIFFICULTIES][0]] # Getting the first difficulty

        self.width = selection['width'] # Getting the field length
        self.height = selection['height'] # Getting the height of the field
        self.mines = selection['mines'] # Getting the number of mins
        
        if combobox: self.restart() # Restarting the game to apply new settings
    
    def restart(self):
        ''' Start/restart the game '''
        self.timerOff = True # Disabling the timer
        self.boardFrame.destroy() # Deleting a field
        self.timeLabel.config(text='⏰000') # Resetting the timer
        self.restartBtn.config(text=ELEMENTS['emoji']['default']) # Returning the smiley face to the button
        self.create_board() # Displaying a new field
    
    def create_board(self):
        ''' Field generation '''
        self.board = [] # Creating an empty variable that will contain cell values
        self.opened = [] # Creating a global variable: Open cells
        self.withflag = [] # Creating a global variable: Flagged cells
        
        self.boardFrame = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['background']) # Creating a field area
        self.boardFrame.grid(column=0, row=1) # Placing the field area in the interface
        self.mineCounter.config(text=f'{ELEMENTS["flags"]}{"0"*(3-len(str(self.mines)))}{self.mines}') # Displaying the number of mines on the panel
        
        self.boardBtns = [[tk.Button(self.boardFrame) for x in range(self.width)] for y in range(self.height)] # Creating a field as a list of lists
        for y in range(self.height): # Searching all rows in the created field
            for x in range(self.width): # Searching all columns in the created field
                self.boardBtns[y][x].config(command=lambda x=x, y=y: self.left_click(x, y), cursor='hand2', height=2, width=4,
                                            disabledforeground='black', fg=COLORS['flag'], bg=COLORS['closed'][(x+y)%2],
                                            relief=tk.FLAT, font='Courier 10', activebackground=COLORS['background']) # Initial button configuration
                self.boardBtns[y][x].grid(column=x, row=y) # Placing the button in the interface
                self.boardBtns[y][x].bind("<Button-3>", lambda event, x=x, y=y: self.right_click(x, y)) # Setting a bind to check the right-click pressed button
    
    def generate_board(self):
        ''' Creating values on the field and setting cells with mines '''
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)] # Creating an empty field in the list
        
        for _ in range(self.mines): # Cycle that repeats as many times as there should be mins
            while True: # Perpetual loop to fix unwanted faults
                py = randint(0, self.height-1) # Getting a random row
                px = randint(0, self.width-1) # Getting a random column
                if self.opened[0] != (px, py) and self.board[py][px] != ELEMENTS['mines']: # Check if this cell is open first or is already a mine
                    if self.width*self.height-self.mines >= 9: # Check if an empty cell is possible
                        lst = [] # Empty list
                        for dy in range(-1, 2): # Parsing syllables [-1, 0, 1] to enumerate neighboring rows
                            for dx in range(-1, 2): # Enumerating syllables [-1, 0, 1] to enumerate neighboring columns
                                lst.append((dx+px, dy+py)) # Add to the list the coordinates of all cells around the cell with mine
                        if self.opened[0] in lst: continue # If the first open cell is in this list, choose another point for the mine.
                    self.board[py][px] = ELEMENTS['mines'] # Make the cell a mine
                    break # End the eternal loop
        
        for y in range(self.height): # Going through all rows
            for x in range(self.width): # Sifting all columns
                if self.board[y][x] != ELEMENTS['mines']: # Check that the cell is not a mine
                    for dy in range(-1, 2): # Parsing syllables [-1, 0, 1] to enumerate neighboring rows
                        for dx in range(-1, 2): # Enumerating syllables [-1, 0, 1] to enumerate neighboring columns
                            if self.height > dy+y >= 0 and self.width > dx+x >= 0 and self.board[dy+y][dx+x] == ELEMENTS['mines']: # Checking for the existence of a cell and that it is a mine
                                self.board[y][x] += 1 # Add 1 to the number on the original cell
    
    def reveal_cell(self, x: int, y: int):
        ''' Opening cells without mines around an empty cell '''
        for dy in range(-1, 2): # Parsing syllables [-1, 0, 1] to enumerate neighboring rows
            for dx in range(-1, 2): # Enumerating syllables [-1, 0, 1] to enumerate neighboring columns
                if self.width > dx+x >= 0 and self.height > dy+y >= 0 and self.boardBtns[dy+y][dx+x]['state'] != tk.DISABLED: # Checking that the cell exists and that it is not already disconnected
                    self.left_click(x+dx, y+dy) # Opening a detected cell
    
    def left_click(self, x: int, y: int):
        ''' Clicking on a cell with the LKM '''
        if (x, y) in self.withflag: return # If there is a flag on the cell, cancel the opening
        self.opened.append((x, y)) # Adding the cell to the list of opened cells
        if len(self.opened) == 1: # Checking if this is the first cell to be opened
            self.generate_board() # A field is created
            Thread(target = self.timer).start() # Starting the timer
        if self.board[y][x] == ELEMENTS['mines'] and (x, y) not in self.withflag: self.end(False) # Checking that this cage is not a mine, otherwise cause a bad ending.
        else:
            self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow', # Disabling the cell
                                        text=self.board[y][x] if self.board[y][x] else ELEMENTS['nothing'], # Setting the text on the cage
                                        bg=COLORS['opened'][1] if self.board[y][x] else COLORS['opened'][0], # Setting the background color of the cell
                                        disabledforeground=COLORS['nums'][self.board[y][x]] if self.board[y][x] in [i for i in COLORS['nums']] else 'black') # Set symbol color
            if self.board[y][x] == 0: self.reveal_cell(x, y) # Starting the search and opening neighboring cells if there are no mines around this cell
            if self.width*self.height-self.mines == len(self.opened): self.end(True) # Checking if all possible squares are open, if so, a good ending is triggered
    
    def right_click(self, x: int, y: int):
        ''' Clicking on a cell PCM '''
        if (x, y) not in self.withflag and (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED: # Checking for a flag and if a cell is open
            self.withflag.append((x, y)) # Adding a cell to the list of cells with a flag
            self.boardBtns[y][x].config(text=ELEMENTS['flags']) # Adding a flag to a cell
        elif (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED: # Checking if the cell is closed and on
            self.withflag.remove((x, y)) # Removing a cell from the list of flagged cells
            self.boardBtns[y][x].config(text='') # Removing a flag from a cell
        self.mineCounter.config(text=f'{ELEMENTS["flags"]}{"0"*(3-len(str(self.mines-len(self.withflag))))}{self.mines-len(self.withflag)}') # Changing the flag counter
    
    def end(self, win: bool):
        ''' End game '''
        self.timerOff = True # Disabling the timer
        if win: # Checking for a win
            self.restartBtn.config(text=ELEMENTS['emoji']['win']) # Setting a smiley face on the restart button
            for y in range(self.height): # Going through all rows
                for x in range(self.width): # Sifting all columns
                    self.boardBtns[y][x].config(text=ELEMENTS['nothing'], state=tk.DISABLED, cursor='arrow') # Disabling all cells
                    if self.board[y][x] != ELEMENTS['mines']: self.boardBtns[y][x]['bg'] = COLORS['water'] # Filling all cells without mines with water
        else: # Checking for defeat
            self.restartBtn.config(text=ELEMENTS['emoji']['fail']) # Setting a smiley face on the restart button
            for y in range(self.height): # Going through all rows
                for x in range(self.width): # Sifting all columns
                    self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow') # Disabling all cells
                    if self.board[y][x] == ELEMENTS['mines']: # Check if it is a mine cell
                        self.boardBtns[y][x].config(text=ELEMENTS['mines'], bg='red') # Setting the color and writing on the mine cell
                        if (x, y) in self.withflag: # Checking for a flag
                            self.boardBtns[y][x]['bg'] = 'yellow' # Setting the background color to yellow
                    elif (x, y) in self.withflag: # Checking a cell without a mine for a flag.
                        self.boardBtns[y][x].config(text=ELEMENTS['fakeflags'], bg=COLORS['fakeflag']) # Marking the cell as an extra flag
    def timer(self):
        ''' Stopwatch for the game '''
        sec = 0 # Zero second
        self.timerOff = False # Do not disable the timer
        while not self.timerOff: # Cycle that will end if needed
            sec += 1 # Add a unit
            self.timeLabel.config(text=f'⏰{'0'*(3-len(str(sec)))}{sec}') # Display the time on the scoreboard
            sleep(1) # Waiting for 1 second to elapse

if __name__ == '__main__':
    Minesweeper()
