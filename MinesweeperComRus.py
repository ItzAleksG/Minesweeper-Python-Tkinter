import tkinter as tk # Библеотека для создания интерфейса
from tkinter import ttk # Библеотека для создание выподающего меню
from idlelib.tooltip import Hovertip # Библеотека для вызова выпадающей надписи при наведений

from random import randint # Библеотека для генерация случайного числа из диапазона
from threading import Thread # Библеотека для запуска функции не прирывая выполнение остальной программы
from time import sleep # Библеотека для остановки выполнения скрипта/функции на определённое время

ELEMENTS = { # Создание глобальной переменной: Символы некоторых элементов
            'mines': '💣', # Мины
            'flags': '🚩', # Флаг
            'fakeflags': 'X', # Флаг без мины
            'nothing': '', # Ничего
            'emoji': { # Смайлики для кнопки
                'default': '🙂', # Обычный
                'fail': '💀', # Поражение
                'win': '😎' # Победа
            }
        }

COLORS = { # Создание глобальной переменной: цвета
    'nums': { # Цвета для цифр
        1: '#0000ff',
        2: '#008000',
        3: '#ff0000',
        4: '#00008b',
        5: '#8b0000',
        6: '#008b8b',
        7: '#000000',
        8: '#778899'
    },
    'flag': '#F23607', # Цвет флага
    'fakeflag': 'lightblue', # Цвет фона флага без мины при поражении
    'water': 'lightblue', # Цвет воды при победе
    'closed': ['#AAD751', '#A2D149'], # Цвета клеток на поле
    'opened': ['#E5C29F', '#E2B488'], # Цвета открытых клеток на поле ['пустая', 'с цифрой']
    'background': '#87AF3A', # Фон поля
    'panel': '#4A752C' # Фон панели
}

DIFFICULTIES = { # Уровни сложности
            'easy': { # Простой
                'name': 'Easy',
                'width': 10, # Длина поля
                'height': 8, # Высота поля
                'mines': 10 # Количество мин
            },
            'medium': { # Средний
                'name': 'Medium',
                'width': 18, # Длина поля
                'height': 14, # Высота поля
                'mines': 40 # Количество мин
            },
            'hard': { # Сложный
                'name': 'Hard',
                'width': 30, # Длина поля
                'height': 16, # Высота поля
                'mines': 100 # Количество мин
            }
        }

class Minesweeper():
    def __init__(self):
        # Создание окна игры
        self.root = tk.Tk() # Создание
        self.root.title('Minesweeper') # Название
        self.root.resizable(0, 0) # Возможность менять размер
        self.root.config(bg=COLORS['panel']) # Задание цвета фона (панели)
        
        # Создание верхней панели
        self.panel = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['panel'])
        self.panel.grid(column=0, row=0)
        
        # Счётчик оставшихся мин
        self.mineCounter = tk.Label(self.panel, width=5)
        self.mineCounter.grid(column=0, row=0, padx=10)

        # Кнопка перезапуска
        self.restartBtn = tk.Button(self.panel, text=ELEMENTS['emoji']['default'], font='helv36', width=4, height=2, cursor='hand2', command=lambda: self.restart())
        self.restartBtn.grid(column=1, row=0, padx=10)
        Hovertip(self.restartBtn, 'Restart', 200) # Выпадающая надпись при наведении

        # Секундомер
        self.timeLabel = tk.Label(self.panel, text=f'⏰000', width=5)
        self.timeLabel.grid(column=2, row=0, padx=10)
        
        dif_var = tk.StringVar(value=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES][0]) # Получение названия первого уровня сложности для первичного вывода
        self.difficulty = ttk.Combobox(self.root, values=[DIFFICULTIES[i]['name'] for i in DIFFICULTIES], textvariable=dif_var, width=10, state='readonly') # Создание меню выбора сложности
        self.difficulty.grid(column=0, row=0, sticky='w', padx=10) # Расположение меню выбора сложности в интерфейсе
        self.difficulty.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected()) # Задание автоматического запуска скрипта при выборе сложности

        self.combobox_selected(False) # Запуск функции выбора сложности из скрипта
        self.create_board() # Генерация поля
        
        self.root.mainloop()
    
    def combobox_selected(self, combobox=True):
        ''' Смена уровней сложности '''
        # Получение выбранного уровня сложности
        if combobox: # Проверка на то является ли вызов данной функции из скрипта или пользователем
            selection = DIFFICULTIES[[i for i in DIFFICULTIES][[DIFFICULTIES[i]['name'] for i in DIFFICULTIES].index(self.difficulty.get())]] # Получение сложности исходя из выбора пользователя
        else: selection = DIFFICULTIES[[i for i in DIFFICULTIES][0]] # Получение первой сложности

        self.width = selection['width'] # Получение длины поля
        self.height = selection['height'] # Получение высоты поля
        self.mines = selection['mines'] # Получение количевства мин
        
        if combobox: self.restart() # Перезапуск игры для применения новых настроек
    
    def restart(self):
        ''' Запуск/перезапуск игры '''
        self.timerOff = True # Отключение таймера
        self.boardFrame.destroy() # Удаление поля
        self.timeLabel.config(text='⏰000') # Обнуление таймера
        self.restartBtn.config(text=ELEMENTS['emoji']['default']) # Возвращение смайлика на кнопку
        self.create_board() # Вывод нового поля
    
    def create_board(self):
        ''' Генерация поля '''
        self.board = [] # Создание пустой переменной которая будет содержать значения ячеек
        self.opened = [] # Создание глобальной переменной: Открытые клетки
        self.withflag = [] # Создание глобальной переменной: Клетки с флагом
        
        self.boardFrame = tk.Frame(self.root, padx=15, pady=15, bg=COLORS['background']) # Создание области под поле
        self.boardFrame.grid(column=0, row=1) # Размещение области поля в интерфесйсе
        self.mineCounter.config(text=f'{ELEMENTS["flags"]}{"0"*(3-len(str(self.mines)))}{self.mines}') # Вывод количевства мин на панель
        
        self.boardBtns = [[tk.Button(self.boardFrame) for x in range(self.width)] for y in range(self.height)] # Создание поля в виде списка списков
        for y in range(self.height): # Перебор всех строк в созданном поле
            for x in range(self.width): # Перебор всех столбцов в созданном поле
                self.boardBtns[y][x].config(command=lambda x=x, y=y: self.left_click(x, y), cursor='hand2', height=2, width=4,
                                            disabledforeground='black', fg=COLORS['flag'], bg=COLORS['closed'][(x+y)%2],
                                            relief=tk.FLAT, font='Courier 10', activebackground=COLORS['background']) # Первичная настройка кнопки
                self.boardBtns[y][x].grid(column=x, row=y) # Размещение кнопки в интерфейсе
                self.boardBtns[y][x].bind("<Button-3>", lambda event, x=x, y=y: self.right_click(x, y)) # Задание бинда на проверку нажатия правым кликом
    
    def generate_board(self):
        ''' Создание значений на поле и задание клеток с минами'''
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)] # Создание пустого поля в списке
        
        for _ in range(self.mines): # Цикл который повторяется столько раз, сколько должно быть мин
            while True: # Вечный цикл для исправление не желательных неисправностей
                py = randint(0, self.height-1) # Получение случайной строки
                px = randint(0, self.width-1) # Получение случайного столбца
                if self.opened[0] != (px, py) and self.board[py][px] != ELEMENTS['mines']: # Проверка открыта эта клетка первой или уже является миной
                    if self.width*self.height-self.mines >= 9: # Проверка возможно ли наличие пустой клетки
                        lst = [] # Пустой список
                        for dy in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних строк
                            for dx in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних столбцов
                                lst.append((dx+px, dy+py)) # Добавляем в список координаты всех клеток вокруг клетки с миной
                        if self.opened[0] in lst: continue # Если первая открытая клетка есть в этом списке то выбираем другую точку для мины
                    self.board[py][px] = ELEMENTS['mines'] # Делаем клетку миной
                    break # Завершаем вечный цикл
        
        for y in range(self.height): # Перебор всех строк
            for x in range(self.width): # Перебор всех столбцов
                if self.board[y][x] != ELEMENTS['mines']: # Проверка что клетка не является миной
                    for dy in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних строк
                        for dx in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних столбцов
                            if self.height > dy+y >= 0 and self.width > dx+x >= 0 and self.board[dy+y][dx+x] == ELEMENTS['mines']: # Проверка на существование клетки и что она является миной
                                self.board[y][x] += 1 # Прибовляем 1 к числу на оригинальной клетки
    
    def reveal_cell(self, x: int, y: int):
        ''' Открытие клеток без мин вокруг пустой клетки '''
        for dy in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних строк
            for dx in range(-1, 2): # Перебор слогаемых [-1, 0, 1] для перебора соседних столбцов
                if self.width > dx+x >= 0 and self.height > dy+y >= 0 and self.boardBtns[dy+y][dx+x]['state'] != tk.DISABLED: # Проверка на существование клетки и что она уже не отключена
                    self.left_click(x+dx, y+dy) # Открытие обнаруженной клетки
    
    def left_click(self, x: int, y: int):
        ''' Нажатие на клетку ЛКМ '''
        if (x, y) in self.withflag: return # Если на клетке есть флаг то отмена открытия
        self.opened.append((x, y)) # Добавление клетки в список открытых
        if len(self.opened) == 1: # Проверка на то первая ли это открыта клетка
            self.generate_board() # Cоздаётся поле
            Thread(target = self.timer).start() # Запуск таймера
        if self.board[y][x] == ELEMENTS['mines'] and (x, y) not in self.withflag: self.end(False) # Проверка что это клетка не является миной, иначе вызывать плохую концовку
        else:
            self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow', # Отключение клетки
                                        text=self.board[y][x] if self.board[y][x] else ELEMENTS['nothing'], # Задание текста на клетке
                                        bg=COLORS['opened'][1] if self.board[y][x] else COLORS['opened'][0], # Задание цвета фона клетки
                                        disabledforeground=COLORS['nums'][self.board[y][x]] if self.board[y][x] in [i for i in COLORS['nums']] else 'black') # Задание цвета символа
            if self.board[y][x] == 0: self.reveal_cell(x, y) # Запуск перебора и открытия соседних клеток если вокруг этой нет мин
            if self.width*self.height-self.mines == len(self.opened): self.end(True) # Провека открыты ли все возможные клетки, если да то вызвается хорошая концовка
    
    def right_click(self, x: int, y: int):
        ''' Нажатие на клетку ПКМ '''
        if (x, y) not in self.withflag and (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED: # Проверка на наличие флага и открыта ли клетка
            self.withflag.append((x, y)) # Добавление клетки в список клеток с флагом
            self.boardBtns[y][x].config(text=ELEMENTS['flags']) # Добавление флага на клетку
        elif (x, y) not in self.opened and self.boardBtns[y][x]['state'] != tk.DISABLED: # Проверка на то закрыта и включена ли клетка
            self.withflag.remove((x, y)) # Уборка клетки из списка клеток с флагом
            self.boardBtns[y][x].config(text='') # Уборка флага с клетки
        self.mineCounter.config(text=f'{ELEMENTS["flags"]}{"0"*(3-len(str(self.mines-len(self.withflag))))}{self.mines-len(self.withflag)}') # Измененение счётчика флагов
    
    def end(self, win: bool):
        ''' Концовка игра '''
        self.timerOff = True # Отключение таймера
        if win: # Проверка на победу
            self.restartBtn.config(text=ELEMENTS['emoji']['win']) # Задание смайлика на кнопку перезапуска
            for y in range(self.height): # Перебор всех строк
                for x in range(self.width): # Перебор всех столбцов
                    self.boardBtns[y][x].config(text=ELEMENTS['nothing'], state=tk.DISABLED, cursor='arrow') # Отключение всех клеток
                    if self.board[y][x] != ELEMENTS['mines']: self.boardBtns[y][x]['bg'] = COLORS['water'] # Заполнение всех клеток без мин водой
        else: # Проверка на поражение
            self.restartBtn.config(text=ELEMENTS['emoji']['fail']) # Задание смайлика на кнопку перезапуска
            for y in range(self.height): # Перебор всех строк
                for x in range(self.width): # Перебор всех столбцов
                    self.boardBtns[y][x].config(state=tk.DISABLED, cursor='arrow') # Отключение всех клеток
                    if self.board[y][x] == ELEMENTS['mines']: # проверка на то что это клетка мина
                        self.boardBtns[y][x].config(text=ELEMENTS['mines'], bg='red') # Задание цвета и надписи на клетке с миной
                        if (x, y) in self.withflag: # Проверка на наличие флага
                            self.boardBtns[y][x]['bg'] = 'yellow' # задание цвета фона жёлтым
                    elif (x, y) in self.withflag: # Проверяется клетка без мины на наличие флага
                        self.boardBtns[y][x].config(text=ELEMENTS['fakeflags'], bg=COLORS['fakeflag']) # Пометка клетки как лишний флаг
    def timer(self):
        ''' Секундомер для игры '''
        sec = 0 # Нулевая секунда
        self.timerOff = False # Не отключать таймер
        while not self.timerOff: # Цикл который закончится при надобности
            sec += 1 # Прибовляем еденицу
            self.timeLabel.config(text=f'⏰{'0'*(3-len(str(sec)))}{sec}') # Выводим время на табло
            sleep(1) # Ожидание пока пройдёт 1 секунда

if __name__ == '__main__':
    Minesweeper()
