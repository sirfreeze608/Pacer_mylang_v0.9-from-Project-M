"""
mylang Lexer  — v0.6.0
New: backtick template literals, import, try, catch, throw keywords.
"""
from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    NUMBER=auto(); STRING=auto(); TEMPLATE=auto(); BOOL=auto(); COMPLEX_J=auto()
    IDENTIFIER=auto(); LET=auto(); IF=auto(); ELSE=auto(); WHILE=auto()
    FOR=auto(); IN=auto(); FN=auto(); RETURN=auto(); PRINT=auto()
    TRUE=auto(); FALSE=auto(); NULL=auto()
    IMPORT=auto(); TRY=auto(); CATCH=auto(); THROW=auto(); RECORD=auto()
    PLUS=auto(); MINUS=auto(); STAR=auto(); SLASH=auto(); PERCENT=auto()
    EQ=auto(); EQ_EQ=auto(); BANG_EQ=auto(); LT=auto(); LT_EQ=auto()
    GT=auto(); GT_EQ=auto(); BANG=auto(); AND=auto(); OR=auto()
    LPAREN=auto(); RPAREN=auto(); LBRACE=auto(); RBRACE=auto()
    LBRACKET=auto(); RBRACKET=auto(); COMMA=auto(); SEMICOLON=auto()
    DOT=auto(); COLON=auto(); EOF=auto()

KEYWORDS = {
    "let":TokenType.LET,"if":TokenType.IF,"else":TokenType.ELSE,
    "while":TokenType.WHILE,"for":TokenType.FOR,"in":TokenType.IN,
    "fn":TokenType.FN,"return":TokenType.RETURN,"print":TokenType.PRINT,
    "true":TokenType.TRUE,"false":TokenType.FALSE,"null":TokenType.NULL,
    "import":TokenType.IMPORT,"try":TokenType.TRY,
    "catch":TokenType.CATCH,"throw":TokenType.THROW, "record":TokenType.RECORD,
}

@dataclass
class Token:
    type:TokenType; value:object; line:int; col:int=0
    def __repr__(self): return f"Token({self.type.name},{self.value!r},line={self.line},col={self.col})"

class LexerError(Exception): pass

class Lexer:
    def __init__(self,source):
        self.source=source; self.pos=0; self.line=1; self.col=1; self.tokens=[]
        self._tok_col=1
    def peek(self,o=0):
        i=self.pos+o; return self.source[i] if i<len(self.source) else "\0"
    def advance(self):
        ch=self.source[self.pos]; self.pos+=1
        if ch=="\n": self.line+=1; self.col=1
        else: self.col+=1
        return ch
    def match(self,e):
        if self.peek()==e: self.advance(); return True
        return False
    def emit(self,t,v=None): self.tokens.append(Token(t,v,self.line,self._tok_col))
    def tokenize(self):
        while self.pos<len(self.source): self._scan_token()
        self.emit(TokenType.EOF); return self.tokens
    def _scan_token(self):
        self._tok_col=self.col
        ch=self.advance()
        if ch in " \t\r\n": return
        if ch=="/" and self.peek()=="/":
            while self.peek() not in("\n","\0"): self.advance()
            return
        S={"(":TokenType.LPAREN,")":TokenType.RPAREN,
           "{":TokenType.LBRACE,"}":TokenType.RBRACE,
           "[":TokenType.LBRACKET,"]":TokenType.RBRACKET,
           ",":TokenType.COMMA,";":TokenType.SEMICOLON,
           ".":TokenType.DOT,":":TokenType.COLON,
           "+":TokenType.PLUS,"*":TokenType.STAR,
           "/":TokenType.SLASH,"%":TokenType.PERCENT}
        if ch in S: self.emit(S[ch]); return
        if ch=="-": self.emit(TokenType.MINUS)
        elif ch=="=": self.emit(TokenType.EQ_EQ if self.match("=") else TokenType.EQ)
        elif ch=="!": self.emit(TokenType.BANG_EQ if self.match("=") else TokenType.BANG)
        elif ch=="<": self.emit(TokenType.LT_EQ if self.match("=") else TokenType.LT)
        elif ch==">": self.emit(TokenType.GT_EQ if self.match("=") else TokenType.GT)
        elif ch=="&" and self.match("&"): self.emit(TokenType.AND)
        elif ch=="|" and self.match("|"): self.emit(TokenType.OR)
        elif ch=='"': self._scan_string()
        elif ch=="`": self._scan_template()
        elif ch.isdigit(): self._scan_number(ch)
        elif ch.isalpha() or ch=="_": self._scan_identifier(ch)
        else:
            err = LexerError(f"Unexpected character: {ch!r}")
            err.line = self.line; err.col = max(1, self.col - 1)
            raise err
    def _scan_string(self):
        sl=self.line; buf=[]
        while self.peek() not in('"',"\0"):
            c=self.advance()
            if c=="\\" and self.peek() in('"',"\\","n","t","r"):
                esc=self.advance(); buf.append({"n":"\n","t":"\t","r":"\r",'"':'"',"\\":"\\"}[esc])
            else: buf.append(c)
        if self.peek()=="\0":
            err = LexerError("Unterminated string literal"); err.line=sl; err.col=1; raise err
        self.advance(); self.emit(TokenType.STRING,"".join(buf))
    def _scan_template(self):
        """Backtick template: `Hello ${name}!` → TEMPLATE token with segment list."""
        sl=self.line; segs=[]; buf=[]
        while self.peek() not in("`","\0"):
            c=self.advance()
            if c=="\\" and self.peek() in("`","\\","n","t","$"):
                esc=self.advance(); buf.append({"n":"\n","t":"\t","`":"`","$":"$","\\":"\\"}[esc])
            elif c=="$" and self.peek()=="{":
                if buf: segs.append((False,"".join(buf))); buf=[]
                self.advance()  # {
                depth=1; eb=[]
                while depth>0 and self.peek()!="\0":
                    ec=self.advance()
                    if ec=="{": depth+=1
                    elif ec=="}":
                        depth-=1
                        if depth==0: break
                    eb.append(ec)
                segs.append((True,"".join(eb).strip()))
            else: buf.append(c)
        if self.peek()=="\0":
            err = LexerError("Unterminated template literal"); err.line=sl; err.col=1; raise err
        self.advance()
        if buf: segs.append((False,"".join(buf)))
        self.emit(TokenType.TEMPLATE,segs)
    def _scan_number(self,first):
        buf=[first]
        while self.peek().isdigit(): buf.append(self.advance())
        if self.peek()=="." and self.peek(1).isdigit():
            buf.append(self.advance())
            while self.peek().isdigit(): buf.append(self.advance())
        if self.peek() in("e","E"):
            nxt=self.peek(1)
            if nxt.isdigit() or nxt in("+","-"):
                buf.append(self.advance())
                if self.peek() in("+","-"): buf.append(self.advance())
                while self.peek().isdigit(): buf.append(self.advance())
                if self.peek()=="j":
                    self.advance(); self.emit(TokenType.COMPLEX_J,float("".join(buf))); return
                self.emit(TokenType.NUMBER,float("".join(buf))); return
        if self.peek()=="j":
            self.advance(); self.emit(TokenType.COMPLEX_J,float("".join(buf))); return
        t="".join(buf); self.emit(TokenType.NUMBER,float(t) if "." in t else int(t))
    def _scan_identifier(self,first):
        buf=[first]
        while self.peek().isalnum() or self.peek()=="_": buf.append(self.advance())
        word="".join(buf); tt=KEYWORDS.get(word,TokenType.IDENTIFIER)
        if tt==TokenType.TRUE: self.emit(TokenType.BOOL,True)
        elif tt==TokenType.FALSE: self.emit(TokenType.BOOL,False)
        elif tt==TokenType.NULL: self.emit(tt,None)
        else: self.emit(tt,word)
