
import random
from .board import Board

def find_all_moves(board:Board, color:str):
    moves=[]
    for x in range(board.w):
        for y in range(board.h):
            p=board.get(x,y)
            if p and p.color==color:
                for (xx,yy) in board.legal_moves_for(x,y):
                    score=0
                    t=board.get(xx,yy)
                    if t:
                        pv={'P':1,'N':3,'B':3,'R':5,'Q':9,'A':12,'K':100}.get(t.kind,0)
                        score=10+pv
                    moves.append(((x,y),(xx,yy),score))
    return moves

def choose_move(board:Board, color:str):
    moves=find_all_moves(board,color)
    if not moves: return None
    best=max(moves, key=lambda m:m[2])[2]
    pool=[m for m in moves if m[2]>=best-1]
    return random.choice(pool)[:2]
