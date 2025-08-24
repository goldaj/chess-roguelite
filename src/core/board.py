
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional

SLIDERS = {'B','R','Q'}
DIRS = {
    'N': [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)],
    'K': [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)],
    'B': [(1,1),(-1,1),(1,-1),(-1,-1)],
    'R': [(1,0),(-1,0),(0,1),(0,-1)],
    'Q': [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
}

@dataclass
class Piece:
    kind: str
    color: str

class Board:
    def __init__(self, w:int, h:int):
        self.w=w; self.h=h
        self.grid=[[None for _ in range(h)] for __ in range(w)]
    def in_bounds(self,x:int,y:int)->bool:
        return 0<=x<self.w and 0<=y<self.h
    def get(self,x:int,y:int):
        if not self.in_bounds(x,y): return None
        return self.grid[x][y]
    def set(self,x:int,y:int,p):
        if self.in_bounds(x,y): self.grid[x][y]=p
    def locate_king(self,color:str):
        for x in range(self.w):
            for y in range(self.h):
                p=self.get(x,y)
                if p and p.kind=='K' and p.color==color: return (x,y)
        return None
    def clone(self):
        b=Board(self.w,self.h)
        for x in range(self.w):
            for y in range(self.h):
                p=self.grid[x][y]
                if p: b.grid[x][y]=Piece(p.kind,p.color)
        return b
    def is_attacked(self,x:int,y:int, by_color:str)->bool:
        # Knights + Amazon knight
        for dx,dy in DIRS['N']:
            p=self.get(x+dx,y+dy)
            if p and p.color==by_color and p.kind in ('N','A'): return True
        # King
        for dx,dy in DIRS['K']:
            p=self.get(x+dx,y+dy)
            if p and p.color==by_color and p.kind=='K': return True
        # Sliders
        def ray(dirs, allowed):
            for dx,dy in dirs:
                xx,yy=x+dx,y+dy
                while self.in_bounds(xx,yy):
                    t=self.get(xx,yy)
                    if t:
                        if t.color==by_color and t.kind in allowed: return True
                        break
                    xx+=dx; yy+=dy
            return False
        if ray(DIRS['B'],('B','Q','A')): return True
        if ray(DIRS['R'],('R','Q','A')): return True
        # Pawns
        if by_color=='w':
            for dx in (-1,1):
                p=self.get(x+dx,y-1)
                if p and p.color=='w' and p.kind=='P': return True
        else:
            for dx in (-1,1):
                p=self.get(x+dx,y+1)
                if p and p.color=='b' and p.kind=='P': return True
        return False
    def legal_moves_for(self,x:int,y:int):
        p=self.get(x,y)
        if not p: return []
        moves=[]
        if p.kind=='N':
            for dx,dy in DIRS['N']:
                xx,yy=x+dx,y+dy
                if not self.in_bounds(xx,yy): continue
                t=self.get(xx,yy)
                if not t or t.color!=p.color: moves.append((xx,yy))
        elif p.kind=='K':
            for dx,dy in DIRS['K']:
                xx,yy=x+dx,y+dy
                if not self.in_bounds(xx,yy): continue
                t=self.get(xx,yy)
                if not t or t.color!=p.color: moves.append((xx,yy))
        elif p.kind in ('B','R','Q'):
            dirs = DIRS['B'] if p.kind=='B' else DIRS['R'] if p.kind=='R' else DIRS['Q']
            for dx,dy in dirs:
                xx,yy=x+dx,y+dy
                while self.in_bounds(xx,yy):
                    t=self.get(xx,yy)
                    if t:
                        if t.color!=p.color: moves.append((xx,yy))
                        break
                    moves.append((xx,yy)); xx+=dx; yy+=dy
        elif p.kind=='A':
            # Queen rays
            for dx,dy in DIRS['Q']:
                xx,yy=x+dx,y+dy
                while self.in_bounds(xx,yy):
                    t=self.get(xx,yy)
                    if t:
                        if t.color!=p.color: moves.append((xx,yy))
                        break
                    moves.append((xx,yy)); xx+=dx; yy+=dy
            # Knight jumps
            for dx,dy in DIRS['N']:
                xx,yy=x+dx,y+dy
                if not self.in_bounds(xx,yy): continue
                t=self.get(xx,yy)
                if not t or t.color!=p.color: moves.append((xx,yy))
        elif p.kind=='P':
            diry = -1 if p.color=='w' else 1
            fx,fy=x,y+diry
            if self.in_bounds(fx,fy) and not self.get(fx,fy):
                moves.append((fx,fy))
            for dx in (-1,1):
                cx,cy=x+dx,y+diry
                if self.in_bounds(cx,cy):
                    t=self.get(cx,cy)
                    if t and t.color!=p.color: moves.append((cx,cy))
        # filter self-check
        km=self.locate_king(p.color)
        legal=[]
        for (xx,yy) in moves:
            b2=self.clone()
            b2.move_and_promote(x,y,xx,yy)
            kp=b2.locate_king(p.color)
            if kp and not b2.is_attacked(kp[0],kp[1], 'w' if p.color=='b' else 'b'):
                legal.append((xx,yy))
        return legal
    def move_and_promote(self,x1,y1,x2,y2):
        p=self.get(x1,y1)
        self.set(x1,y1,None)
        if p and p.kind=='P':
            if (p.color=='w' and y2==0) or (p.color=='b' and y2==self.h-1):
                p=Piece('Q',p.color)
        self.set(x2,y2,p)
