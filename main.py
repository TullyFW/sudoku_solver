import pandas as pd # I use the pandas dataframe library as a convenient way to index the board
from itertools import product as prod # itertools.product is a nice way to nest for loops
import math


class Cell: # the cell class is a class for each of the cells in the grid
    def __init__(self):
        '''
        cells are defined with a list of all of the
        possibilities that they could be. If a cell is 
        filled in, the list will only include one number
        '''
        self.cell = list(range(1,10))
        self.r = None
        self.c = None
        self.box = None
        self.unchecked = True
    
    @property
    def filled(self): # whether a cell has been completed or not
        return len(self.cell) == 1
    
    def remove(self,val): # remove a value from the possibilities of a cell
        self.cell.remove(val)
        
    def __len__(self): 
        return len(self.cell)
    
    def __repr__(self): # representation of the cell's contents-- useful in troubleshooting
        return f'r{self.r}c{self.c}: {self.cell}'
    
    def __str__(self): # representation of a cell seen in the final printed product
        return str(self.cell[0]) if self.filled else ''

class Board: # class for the puzzle's board
    def __init__(self):
        self.board = pd.DataFrame({int(x): [Cell() for _ in range(9)] for x in range(1,10)},index=list(range(1,10)))
        # the cells in the board are stored in a dataframe because standard sudoku indexing is like a dataframe (row, col)
        self.cells = sum(self.board.values.tolist(),[])
        # store cells as a list as well because you can't easily iterate through a dataframe
        
        '''
        The initialization of the board gives each cell a row, column, and box
        '''
        boxes_dict = {(1,1) : 1, (1,2) : 2, (1,3) : 3, (2,1) : 4, (2,2) : 5, (2,3) : 6, (3,1) : 7, (3,2) : 8, (3,3) : 9}
        for r,c in prod(range(1,10),range(1,10)):
            cell = self[r,c]
            cell.r = r
            cell.c = c
            cell.box = boxes_dict[(math.ceil(cell.r/3),math.ceil(cell.c/3))]
            
            
        self.rows = {n : [cell for cell in self.cells if cell.r == n] for n in range(1,10)}
        self.cols = {n : [cell for cell in self.cells if cell.c == n] for n in range(1,10)}
        self.boxes = {n : [cell for cell in self.cells if cell.box == n] for n in range(1,10)}
        
    def hits(self,cell):
        '''
        function that returns a list of all of the
        other cells that a cell touches by sudoku -
        everything in its row, column, and box
        '''
        hits = list(set(self.rows[cell.r]+self.cols[cell.c] + self.boxes[cell.box]))
        hits.remove(cell)
        return hits
    
    @property
    def filled_cells(self): # all of the filled in cells on the grid for iterating
        return [cell for cell in self.cells if cell.filled]
    
    def simple_check(self):
        '''
        This function iterates through each completed cell that hasn't been already
        checked and removes the number in it from the possibilities in all of the
        cells it hits (see Board.hit method)
        '''
        for cell in self.filled_cells:
            if cell.unchecked:
                for hit in self.hits(cell):
                    if cell.cell[0] in hit.cell:
                        hit.cell.remove(cell.cell[0])
                cell.unchecked = False
                
    def group_check(self):
        '''
        iterates through every row, column and box
        for each one, checks each number, and if only
        one cell in the box could have that number,
        then it must be that number
        '''
        for lis in [self.rows,self.cols,self.boxes]:
            for box,n in prod(lis.values(),range(1,10)):
                x = [cell for cell in box if n in cell.cell]
                if len(x) == 1: x[0].cell = [n]
    
    def solved(self): # check to see if the board is completed
        return [cell for cell in self.cells if cell.filled] == self.cells
    
    def __getitem__(self,key): 
        '''
        method of indexing in the form of row,column
        e.g. board[1,1] is the top left cell on the grid
        '''
        return self.board.at[key]
    
    def __repr__(self):
        '''
        ascii representation of the board to
        display initial and solved board
        '''
        text = ''
        for r in range(1,10):
            if r == 4 or r == 7:
                text += '------+-------+------\n'
            for i,c in enumerate(range(1,10)):
                cell = self[r,c]
                if cell.filled:
                    '''if cell in board.hits(board[1,6]):
                        text += 'X'
                    else:'''
                    text += f'{cell.cell[0]}'
                else:
                    text += '·'
                if i == 8:
                    text += '\n'
                else:
                    text += ' '
                if i == 2 or i == 5:
                    text += '| '
        return text
    
    def __setitem__(self, cell: tuple, value: list):
        '''
        __setitem__ to set a value in the board after
        indexing it in the same way as __getitem__ 
        '''
        self.board.at[cell].cell = value
        
    @property
    def setup_string(self): 
        '''
        return the string that would be inputted to make the board
        '''
        return "".join([str(cell.cell[0]) if cell.filled else "0" for cell in self.cells])
        
    def setup(self,text):
        '''
        setup the board when given a string of 81 digits (0 is empty)
        '''
        for fill,cell in zip(text,[self[x,y] for x,y in prod(range(1,10),range(1,10))]):
            if int(fill):
                cell.cell = [int(fill)]
        
board = Board()
# make the game board

# these are some board setups i used in the testing process
text = '310004069000000200008005040000000005006000017807030000590700006600003050000100002'
tetx = '305006000700050430000400020003008007680040100050000803400005300500209004162000008'
simple_test =  '123456780' + '0' * 72

board.setup(input('board: ')) # let user input a string of numbers to make the board


print(board) # display the initial board setup




def basic_checks(board):
    '''
    combines both methods of checking
    applies them over and over again
    until the function stops making 
    changes
    '''
    while True:
        prev_board = str(board.cells)
        while True:
            prev = str(board.cells)
            board.simple_check()
            if prev == str(board.cells): break
        while True:
            prev = str(board.cells)
            board.group_check()
            if prev == str(board.cells): break
        if prev_board == str(board.cells): break

def simple_brute_check(board):
    '''
    iterates through each cell in the 
    board with only two possibilities
    left. Try filling it in with one
    of the possibilities on a new
    board and apply the basic checks
    '''
    almost = [cell for cell in board.cells if len(cell) == 2]
    for cell in almost:
        try:
            new = Board()
            new.setup(board.setup_string)
            basic_checks(new)
            new[cell.r,cell.c] = [cell.cell[0]]
            basic_checks(new)
            print(f"no contradiction at r{cell.r}c{cell.c}")
        except IndexError:
            print("found contradiction")
            cell.cell = [cell.cell[1]]
            print(f"changed r{cell.r}c{cell.c}")


def solve():
    '''
    Use basic check and brute check
    over and over again until either
    the board is solved or it stops
    making changes (if it gets stuck)
    '''
    while True:
        prev = str(board.cells)
        basic_checks(board)
        if board.solved():
            print("Solved!")
            print(board)
            break
        else:
            simple_brute_check(board)
        print(board)
        if prev == str(board.cells): break

solve()
