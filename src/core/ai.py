
import random
from typing import Tuple, Optional, List
from .board import Board, Piece

def find_all_moves(board:Board, color:str) -> List[Tuple[Tuple[int,int], Tuple[int,int], int]]:
    moves = []
    for x in range(board.w):
        for y in range(board.h):
            p = board.get(x,y)
            if p and p.color == color:
                legals = board.legal_moves_for(x,y)
                for (xx,yy) in legals:
                    score = 0
                    t = board.get(xx,yy)
                    if t:
                        # prefer captures
                        pv = {'P':1,'N':3,'B':3,'R':5,'Q':9,'A':12,'K':100}.get(t.kind,0)
                        score = 10 + pv
                    # bonus if move gives check
                    kpos = board.locate_king('w' if color=='b' else 'b')
                    if kpos:
                        b2 = board.clone()
                        b2.move_and_promote(x,y,xx,yy)
                        if b2.is_attacked(kpos[0],kpos[1], color):
                            score += 5
                    moves.append(((x,y),(xx,yy),score))
    return moves

def choose_move(board:Board, color:str) -> Optional[Tuple[Tuple[int,int], Tuple[int,int]]]:
    moves = find_all_moves(board, color)
    if not moves:
        return None
    # pick weighted by score
    maxs = max(m[2] for m in moves)
    # bias to higher score
    top = [m for m in moves if m[2] >= maxs-2]
    return random.choice(top)[:2]
