"""
mylang Interpreter  — Stage C of the pipeline.
Tree-walks the AST and executes nodes directly using Python as the host.
Uses an Environment (scope chain) to track variable bindings.
"""

from ast_nodes import *
import re
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from stdlib import (
    register_stdlib, MylangComplex, MylangMatrix, MylangNamespace,
)



# ── Exceptions ────────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    """Non-error control-flow: unwinds call stack to the call site."""
    def __init__(self, value):
        self.value = value

class MylangThrowSignal(Exception):
    """Raised by throw — caught by try/catch."""
    def __init__(self, value): self.value = value


class RuntimeError(Exception):
    pass


class SizeError(RuntimeError):
    """A value does not fit the PICTURE clause of a record field."""
    pass


# Safety limits — keep runaway programs from exhausting memory.
MAX_RANGE_ELEMENTS  = 10_000_000
MAX_LOOP_ITERATIONS = 10_000_000


# ── Runtime value types ───────────────────────────────────────────────────────

class MylangArray:
    def __init__(self, elements: list):
        self.elements = list(elements)

    def __repr__(self):
        return "[" + ", ".join(_str(e) for e in self.elements) + "]"


class MylangHash:
    def __init__(self, pairs: dict = None):
        self.pairs: dict = pairs if pairs is not None else {}

    def __repr__(self):
        items = ", ".join(f"{_str(k)}: {_str(v)}"
                          for k, v in self.pairs.items())
        return "{" + items + "}"


# ── COBOL-style fixed-width records ──────────────────────────────────────────

class PicSpec:
    """Parsed PICTURE clause: x(n) / 9(n) / 9(n)v9(m) / s9(n)."""
    __slots__ = ("kind", "length", "digits", "scale", "signed")

    def __init__(self, kind, length=0, digits=0, scale=0, signed=False):
        self.kind   = kind      # "str" | "int" | "dec"
        self.length = length    # for str
        self.digits = digits    # integer digits for int/dec
        self.scale  = scale     # fractional digits for dec
        self.signed = signed

    def width(self) -> int:
        if self.kind == "str":
            return self.length
        if self.kind == "int":
            return self.digits + (1 if self.signed else 0)
        return self.digits + self.scale + (1 if self.signed else 0)


def _count_nines(part: str) -> int:
    total, i = 0, 0
    while i < len(part):
        if part[i] == "9":
            if i + 1 < len(part) and part[i + 1] == "(":
                j = part.index(")", i)
                total += int(part[i + 2:j] or 0)
                i = j + 1
            else:
                total += 1
                i += 1
        else:
            raise RuntimeError(f"Unsupported PIC character {part[i]!r}")
    return total


def parse_pic(pic) -> PicSpec:
    s = str(pic).strip().lower().replace(" ", "")
    if not s:
        raise RuntimeError("Empty PIC specification")
    signed = s.startswith("s")
    if signed:
        s = s[1:]

    # Text fields: x(n), a(n), x
    m = re.fullmatch(r"([xa])(?:\((\d+)\))?", s)
    if m:
        return PicSpec("str", length=int(m.group(2) or 1))

    # Numeric fields: split on V or .
    for sep in ("v", "."):
        if sep in s:
            int_part, frac_part = s.split(sep, 1)
            digits = _count_nines(int_part) if int_part else 0
            scale  = _count_nines(frac_part)
            if digits + scale == 0:
                raise RuntimeError(f"Invalid PIC specification: {pic!r}")
            return PicSpec("dec", digits=digits, scale=scale, signed=signed)

    digits = _count_nines(s)
    if digits == 0:
        raise RuntimeError(f"Invalid PIC specification: {pic!r}")
    return PicSpec("int", digits=digits, signed=signed)


def _blank_for_pic(pic) -> object:
    spec = parse_pic(pic)
    if spec.kind == "str":
        return " " * spec.length
    if spec.kind == "int":
        return 0
    return Decimal(0).quantize(Decimal(1).scaleb(-spec.scale))


def _apply_pic(pic, value) -> object:
    """Coerce a value into a field, applying COBOL storage rules."""
    spec = parse_pic(pic)

    if spec.kind == "str":
        s = "" if value is None else (value if isinstance(value, str) else _str(value))
        return s[:spec.length].ljust(spec.length)

    if spec.kind == "int":
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise RuntimeError(f"Field {pic!r} requires a number")
        i = int(value)
        limit = 10 ** spec.digits
        if abs(i) >= limit:
            raise SizeError(f"Size error: {i} does not fit PIC {pic!r}")
        return i

    # decimal field: truncate toward zero (COBOL default MOVE behaviour)
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise RuntimeError(f"Field {pic!r} requires a number")
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    q = Decimal(1).scaleb(-spec.scale) if spec.scale else Decimal(1)
    d = d.quantize(q, rounding=ROUND_DOWN)
    if spec.digits and abs(int(d)) >= 10 ** spec.digits:
        raise SizeError(f"Size error: {d} does not fit PIC {pic!r}")
    return d


class MylangRecord:
    """Instance of a `record` declaration with fixed-width PIC fields."""

    def __init__(self, decl, values=None):
        self.decl = decl
        self.pics = {fname: pic for fname, pic, _ in decl.fields}
        self.conditions = {c.name: c
                           for c in getattr(decl, "conditions", [])}
        overlap = set(self.conditions) & set(self.pics)
        if overlap:
            raise RuntimeError(
                f"Record '{decl.name}': condition name(s) "
                f"{', '.join(sorted(overlap))} collide with field names")
        self.values = {}
        for fname, pic, _ in decl.fields:
            if values is not None and fname in values:
                self.values[fname] = _apply_pic(pic, values[fname])
            else:
                self.values[fname] = _blank_for_pic(pic)

    def __repr__(self):
        parts = []
        for fname, pic, _ in self.decl.fields:
            spec = parse_pic(pic)
            v = self.values[fname]
            if spec.kind == "str":
                parts.append(f'{fname}: "{str(v).rstrip()}"')
            else:
                parts.append(f"{fname}: {_str(v)}")
        return f"{self.decl.name}{{{', '.join(parts)}}}"

    def pack(self) -> str:
        """Serialize to a COBOL-style fixed-width character record."""
        out = []
        for fname, pic, _ in self.decl.fields:
            spec = parse_pic(pic)
            v = self.values[fname]
            if spec.kind == "str":
                out.append(str(v)[:spec.length].ljust(spec.length))
            elif spec.kind == "int":
                i = int(v)
                body = f"{abs(i):0{spec.digits}d}"
                out.append((("-" if i < 0 else "+") + body) if spec.signed else body)
            else:
                d = v if isinstance(v, Decimal) else Decimal(str(v))
                scaled = int((d * (10 ** spec.scale))
                             .to_integral_value(rounding=ROUND_DOWN))
                sign = ""
                if spec.signed:
                    sign = "-" if scaled < 0 else "+"
                    scaled = abs(scaled)
                out.append(sign + f"{scaled:0{spec.digits + spec.scale}d}")
        return "".join(out)

    def unpack(self, text: str):
        """Populate this record from a fixed-width character record."""
        if not isinstance(text, str):
            raise RuntimeError("unpack() expects a string")
        pos = 0
        for fname, pic, _ in self.decl.fields:
            spec = parse_pic(pic)
            width = spec.width()
            chunk = text[pos:pos + width]
            pos += width
            chunk = chunk.ljust(width)
            if spec.kind == "str":
                self.values[fname] = chunk
            elif spec.kind == "int":
                body = chunk.strip()
                self.values[fname] = int(body) if body not in ("", "+", "-") else 0
            else:
                body = chunk
                sign = ""
                if spec.signed and body[:1] in ("+", "-"):
                    sign, body = ("-" if body[0] == "-" else ""), body[1:]
                intpart = body[:spec.digits] or "0"
                frac    = body[spec.digits:] if spec.scale else ""
                self.values[fname] = Decimal(
                    sign + intpart + ("." + frac if frac else ""))
        return self



class Function:
    """Named user-defined function (FnDecl), captured with its closure."""
    def __init__(self, name: str, params: list, body, closure):
        self.name    = name
        self.params  = params
        self.body    = body
        self.closure = closure

    def __repr__(self):
        return f"<fn {self.name}>"


class AnonFunction:
    """Anonymous function value (FnExpr), captured with its closure."""
    def __init__(self, params: list, body, closure):
        self.params  = params
        self.body    = body
        self.closure = closure

    def __repr__(self):
        return "<fn>"


class BuiltinFunction:
    """Native function implemented in Python."""
    def __init__(self, name: str, arity, fn):
        self.name  = name
        self.arity = arity   # int or None (variadic)
        self.fn    = fn

    def __repr__(self):
        return f"<builtin {self.name}>"


# ── Stringify helpers (module-level so stdlib can use them) ───────────────────

def _str(value) -> str:
    if value is None:                      return "null"
    if isinstance(value, bool):            return "true" if value else "false"
    if isinstance(value, MylangArray):     return repr(value)
    if isinstance(value, MylangHash):      return repr(value)
    if isinstance(value, MylangRecord):    return repr(value)
    if isinstance(value, MylangComplex):   return repr(value)
    if isinstance(value, MylangMatrix):    return repr(value)
    if isinstance(value, MylangNamespace): return repr(value)
    if isinstance(value, Decimal):         return format(value, "f")
    if isinstance(value, float):
        t = str(value)
        return t[:-2] if t.endswith(".0") else t
    return str(value)


def _type_name(v) -> str:
    if v is None:                       return "null"
    if isinstance(v, bool):             return "bool"
    if isinstance(v, (int, float)):     return "number"
    if isinstance(v, Decimal):          return "decimal"
    if isinstance(v, str):              return "string"
    if isinstance(v, MylangArray):      return "array"
    if isinstance(v, MylangHash):       return "hash"
    if isinstance(v, MylangRecord):     return "record"
    if isinstance(v, MylangComplex):    return "complex"
    if isinstance(v, MylangMatrix):     return "matrix"
    if isinstance(v, MylangNamespace):  return "namespace"
    if isinstance(v, (Function, AnonFunction, BuiltinFunction)):
        return "function"
    return "unknown"


# ── Environment (lexical scope chain) ────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars:   dict = {}
        self.parent        = parent

    def define(self, name: str, value):
        self.vars[name] = value

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'")


# ── Core built-in functions ───────────────────────────────────────────────────

def _b_len(args):
    v = args[0]
    if isinstance(v, MylangArray):  return len(v.elements)
    if isinstance(v, MylangHash):   return len(v.pairs)
    if isinstance(v, MylangRecord): return len(v.values)
    if isinstance(v, str):          return len(v)
    raise RuntimeError(
        f"len() expects array, hash, string, or record — got {_type_name(v)}")

def _b_type(args):  return _type_name(args[0])
def _b_str(args):   return _str(args[0])

def _b_num(args):
    v = args[0]
    if isinstance(v, bool):
        raise RuntimeError("num() cannot convert a bool")
    if isinstance(v, Decimal): return v
    if isinstance(v, (int, float)): return v
    if isinstance(v, str):
        try:    return int(v)
        except ValueError:
            try: return float(v)
            except ValueError:
                raise RuntimeError(
                    f"num() cannot convert \"{v}\" to a number")
    raise RuntimeError(f"num() cannot convert {_type_name(v)}")

def _b_push(args):
    arr, val = args
    if not isinstance(arr, MylangArray):
        raise RuntimeError(f"push() expects array — got {_type_name(arr)}")
    arr.elements.append(val)
    return arr

def _b_pop(args):
    arr = args[0]
    if not isinstance(arr, MylangArray):
        raise RuntimeError(f"pop() expects array — got {_type_name(arr)}")
    if not arr.elements:
        raise RuntimeError("pop() called on empty array")
    return arr.elements.pop()

def _b_keys(args):
    h = args[0]
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"keys() expects hash — got {_type_name(h)}")
    return MylangArray(list(h.pairs.keys()))

def _b_values(args):
    h = args[0]
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"values() expects hash — got {_type_name(h)}")
    return MylangArray(list(h.pairs.values()))

def _b_has(args):
    h, key = args
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"has() expects hash — got {_type_name(h)}")
    return key in h.pairs

def _b_del(args):
    h, key = args
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"del() expects hash — got {_type_name(h)}")
    h.pairs.pop(key, None)
    return h

def _b_range(args):
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    else:
        start, stop, step = args
    for v in (start, stop, step):
        if not isinstance(v, (int, float, Decimal)):
            raise RuntimeError("range() arguments must be numbers")

    start_i, stop_i, step_i = int(start), int(stop), int(step)
    if step_i == 0:
        raise RuntimeError("range() step must not be zero")

    span = stop_i - start_i
    if (step_i > 0 and span <= 0) or (step_i < 0 and span >= 0):
        count = 0
    else:
        count = (abs(span) + abs(step_i) - 1) // abs(step_i)
    if count > MAX_RANGE_ELEMENTS:
        raise RuntimeError(
            f"range() would create {count} elements — "
            f"the limit is {MAX_RANGE_ELEMENTS}")
    return MylangArray(list(range(start_i, stop_i, step_i)))


BUILTINS = {
    "len":    BuiltinFunction("len",    1,    _b_len),
    "type":   BuiltinFunction("type",   1,    _b_type),
    "str":    BuiltinFunction("str",    1,    _b_str),
    "num":    BuiltinFunction("num",    1,    _b_num),
    "push":   BuiltinFunction("push",   2,    _b_push),
    "pop":    BuiltinFunction("pop",    1,    _b_pop),
    "keys":   BuiltinFunction("keys",   1,    _b_keys),
    "values": BuiltinFunction("values", 1,    _b_values),
    "has":    BuiltinFunction("has",    2,    _b_has),
    "del":    BuiltinFunction("del",    2,    _b_del),
    "range":  BuiltinFunction("range",  None, _b_range),
}


# ── String methods ────────────────────────────────────────────────────────────

def _string_method(obj: str, method: str, args: list):
    if method == "upper":      return obj.upper()
    if method == "lower":      return obj.lower()
    if method == "trim":       return obj.strip()
    if method == "split":
        sep = args[0] if args else " "
        if not isinstance(sep, str):
            raise RuntimeError("split() separator must be a string")
        return MylangArray(obj.split(sep))
    if method == "replace":
        if len(args) != 2:
            raise RuntimeError("replace(old, new) requires 2 arguments")
        old, new = args
        if not isinstance(old, str) or not isinstance(new, str):
            raise RuntimeError("replace() arguments must be strings")
        return obj.replace(old, new)
    if method == "contains":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("contains() requires a string argument")
        return args[0] in obj
    if method == "starts_with":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("starts_with() requires a string argument")
        return obj.startswith(args[0])
    if method == "ends_with":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("ends_with() requires a string argument")
        return obj.endswith(args[0])
    if method == "slice":
        if len(args) < 1:
            raise RuntimeError("slice(start[, end]) requires at least 1 argument")
        start = int(args[0])
        end   = int(args[1]) if len(args) > 1 else len(obj)
        return obj[start:end]
    if method == "index_of":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("index_of() requires a string argument")
        return obj.find(args[0])
    raise RuntimeError(f"String has no method '{method}'")


# ── Array methods ─────────────────────────────────────────────────────────────

def _array_method(obj: MylangArray, method: str, args: list, interp):
    if method == "push":
        if not args: raise RuntimeError("push() requires 1 argument")
        obj.elements.append(args[0]); return obj
    if method == "pop":
        if not obj.elements: raise RuntimeError("pop() on empty array")
        return obj.elements.pop()
    if method == "len":
        return len(obj.elements)
    if method == "slice":
        start = int(args[0]) if args else 0
        end   = int(args[1]) if len(args) > 1 else len(obj.elements)
        return MylangArray(obj.elements[start:end])
    if method == "contains":
        if not args: raise RuntimeError("contains() requires 1 argument")
        return args[0] in obj.elements
    if method == "index_of":
        if not args: raise RuntimeError("index_of() requires 1 argument")
        try:    return obj.elements.index(args[0])
        except ValueError: return -1
    if method == "reverse":
        return MylangArray(list(reversed(obj.elements)))
    if method == "join":
        sep = args[0] if args else ""
        if not isinstance(sep, str):
            raise RuntimeError("join() separator must be a string")
        return sep.join(_str(e) for e in obj.elements)
    if method == "map":
        if not args: raise RuntimeError("map() requires a function argument")
        fn = args[0]
        return MylangArray([interp._call_fn(fn, [e]) for e in obj.elements])
    if method == "filter":
        if not args: raise RuntimeError("filter() requires a function argument")
        fn = args[0]
        return MylangArray([e for e in obj.elements
                            if interp._is_truthy(interp._call_fn(fn, [e]))])
    if method == "reduce":
        if not args: raise RuntimeError("reduce(fn, init) requires arguments")
        fn    = args[0]
        items = obj.elements
        acc   = args[1] if len(args) > 1 else (items[0] if items else None)
        start = 1 if len(args) < 2 else 0
        for e in items[start:]:
            acc = interp._call_fn(fn, [acc, e])
        return acc
    raise RuntimeError(f"Array has no method '{method}'")


# ── Hash methods ──────────────────────────────────────────────────────────────

def _hash_method(obj: MylangHash, method: str, args: list):
    if method == "keys":   return MylangArray(list(obj.pairs.keys()))
    if method == "values": return MylangArray(list(obj.pairs.values()))
    if method == "has":
        if not args: raise RuntimeError("has() requires 1 argument")
        return args[0] in obj.pairs
    if method == "del":
        if not args: raise RuntimeError("del() requires 1 argument")
        obj.pairs.pop(args[0], None); return obj
    if method == "len":
        return len(obj.pairs)
    raise RuntimeError(f"Hash has no method '{method}'")


# ── Interpreter ───────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        for name, fn in BUILTINS.items():
            self.globals.define(name, fn)
        register_stdlib(self)          # math / stats / ee / matrix / complex
        self.env    = self.globals
        self.output: list[str] = []

    def run(self, program: Program):
        for stmt in program.statements:
            try:
                self._exec(stmt)
            except MylangThrowSignal as sig:
                e = RuntimeError(f"Uncaught throw: {_str(sig.value)}")
                self._attach_stmt_pos(e, stmt)
                raise e from None
            except ReturnSignal:
                e = RuntimeError("'return' can only be used inside a function")
                self._attach_stmt_pos(e, stmt)
                raise e from None

    def _attach_stmt_pos(self, e, stmt):
        """Give a top-level runtime error the source position of its statement."""
        if not hasattr(e, "line"):
            line = getattr(stmt, "_line", None)
            if line:
                e.line = line
                e.col = getattr(stmt, "_col", None)

    # ── dispatch ──────────────────────────────────────────────────────────────

    def _exec(self, node):
        m = getattr(self, "_exec_" + type(node).__name__, None)
        if m is None:
            raise RuntimeError(
                f"No exec handler for {type(node).__name__}")
        try:
            return m(node)
        except RuntimeError as e:
            # Attach source position from the statement node for error frames
            if not hasattr(e, "line") and hasattr(node, "_line"):
                e.line = node._line
                e.col  = getattr(node, "_col", None)
            raise

    def _eval(self, node):
        m = getattr(self, "_eval_" + type(node).__name__, None)
        if m is None:
            raise RuntimeError(
                f"No eval handler for {type(node).__name__}")
        return m(node)

    # ── statement handlers ────────────────────────────────────────────────────

    def _exec_VarDecl(self, node: VarDecl):
        self.env.define(node.name, self._eval(node.initializer))

    def _exec_FnDecl(self, node: FnDecl):
        self.env.define(node.name,
            Function(node.name, node.params, node.body, self.env))

    def _exec_RecordDecl(self, node: RecordDecl):
        self.env.define(node.name, node)

    def _exec_ExprStmt(self, node: ExprStmt):
        self._eval(node.expr)

    def _exec_PrintStmt(self, node: PrintStmt):
        text = _str(self._eval(node.expr))
        print(text)
        self.output.append(text)

    def _exec_Block(self, node: Block, env: Environment = None):
        prev     = self.env
        self.env = env or Environment(self.env)
        try:
            for stmt in node.statements:
                self._exec(stmt)
        finally:
            self.env = prev

    def _exec_IfStmt(self, node: IfStmt):
        if self._is_truthy(self._eval(node.condition)):
            self._exec(node.then_branch)
        elif node.else_branch:
            self._exec(node.else_branch)

    def _exec_WhileStmt(self, node: WhileStmt):
        while self._is_truthy(self._eval(node.condition)):
            self._exec(node.body)

    def _exec_ForStmt(self, node: ForStmt):
        iterable = self._eval(node.iterable)
        if isinstance(iterable, MylangArray):
            items = iterable.elements
        elif isinstance(iterable, str):
            items = list(iterable)
        elif isinstance(iterable, MylangHash):
            items = list(iterable.pairs.keys())
        else:
            raise RuntimeError(
                f"Cannot iterate over {_type_name(iterable)}")
        for item in items:
            loop_env = Environment(self.env)
            loop_env.define(node.var, item)
            self._exec_Block(node.body, env=loop_env)

    def _exec_ReturnStmt(self, node: ReturnStmt):
        raise ReturnSignal(
            self._eval(node.value) if node.value is not None else None)

    def _exec_ThrowStmt(self, node):
        val = self._eval(node.value)
        # Wrap in a runtime error to provide line/col info if it's not already a signal
        raise MylangThrowSignal(val)

    def _exec_TryStmt(self, node):
        try:
            self._exec(node.body)
        except MylangThrowSignal as sig:
            prev = self.env
            self.env = Environment(prev)
            self.env.define(node.var, sig.value)
            try:
                self._exec(node.handler)
            finally:
                self.env = prev
        except ReturnSignal:
            raise   # return is control flow, never an error to catch
        except Exception as e:
            # Any runtime failure is catchable — including native errors
            # raised by the stdlib (RecursionError, ZeroDivisionError, …).
            prev = self.env
            self.env = Environment(prev)
            self.env.define(node.var, str(e) or type(e).__name__)
            try:
                self._exec(node.handler)
            finally:
                self.env = prev

    def _exec_ImportStmt(self, node):
        """Run an external .ml file in the current global scope."""
        import os as _os
        from lexer import Lexer as _Lexer
        from parser import Parser as _Parser
        path = node.path
        # Resolve relative to the calling script if possible
        search = [path, _os.path.join(_os.getcwd(), path)]
        for candidate in search:
            if _os.path.isfile(candidate):
                src = open(candidate, encoding="utf-8").read()
                tokens = _Lexer(src).tokenize()
                ast    = _Parser(tokens).parse()
                # Run in current scope so imported functions/vars are available
                saved_env = self.env
                self.env  = self.globals
                try:
                    for stmt in ast.statements:
                        self._exec(stmt)
                finally:
                    self.env = saved_env
                return
        raise RuntimeError(f"import: file not found: {path!r}")

    # ── COBOL-style statement handlers (v0.9.0) ───────────────────────────────

    def _exec_EvaluateStmt(self, node: EvaluateStmt):
        subject      = self._eval(node.subject) if node.subject is not None else None
        boolean_form = node.subject is None

        for clause in node.clauses:
            hit = False
            for test in clause.tests:
                if test[0] == "eq":
                    value = self._eval(test[1])
                    hit = (self._is_truthy(value) if boolean_form
                           else self._eq(subject, value))
                else:
                    if boolean_form:
                        raise RuntimeError(
                            "evaluate: 'thru' ranges need a subject value")
                    low, high = self._eval(test[1]), self._eval(test[2])
                    try:
                        hit = low <= subject <= high
                    except TypeError:
                        raise RuntimeError(
                            "evaluate: 'thru' range needs comparable values")
                if hit:
                    break
            if hit:
                self._exec(clause.body)
                return

        if node.default is not None:
            self._exec(node.default)

    def _exec_PerformStmt(self, node: PerformStmt):
        if node.kind == "until":
            while not self._is_truthy(self._eval(node.condition)):
                self._exec(node.body)
            return

        if node.kind == "times":
            count = self._eval(node.times)
            if not isinstance(count, (int, float, Decimal)):
                raise RuntimeError(
                    f"perform N times: repeat count must be a number "
                    f"— got {_type_name(count)}")
            n = int(count)
            if n > MAX_LOOP_ITERATIONS:
                raise RuntimeError(
                    f"perform {n} times exceeds the loop limit "
                    f"({MAX_LOOP_ITERATIONS})")
            for _ in range(max(0, n)):
                self._exec(node.body)
            return

        # varying
        start = self._eval(node.start)
        step  = self._eval(node.step)
        if isinstance(step, (int, float, Decimal)) and step == 0:
            raise RuntimeError("perform varying: 'by' step must not be zero")

        loop_env = Environment(self.env)
        loop_env.define(node.var, start)
        prev = self.env
        self.env = loop_env
        try:
            iterations = 0
            while not self._is_truthy(self._eval(node.condition)):
                self._exec_Block(node.body, env=loop_env)
                current = loop_env.get(node.var)
                loop_env.assign(node.var, self._apply_binop("+", current, step))
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise RuntimeError(
                        "perform varying: loop limit exceeded "
                        f"({MAX_LOOP_ITERATIONS} iterations)")
        finally:
            self.env = prev

    def _exec_ArithVerb(self, node: ArithVerb):
        left   = self._eval(node.left)
        right  = self._eval(node.right)
        target = node.giving

        if node.op == "add":
            result = self._apply_binop("+", left, right)
        elif node.op == "subtract":
            # COBOL: subtract a from b  →  b - a
            result = self._apply_binop("-", right, left)
        elif node.op == "multiply":
            result = self._apply_binop("*", left, right)
        else:  # divide
            if node.remainder is not None:
                for v in (left, right):
                    if not isinstance(v, (int, float, Decimal)):
                        raise RuntimeError(
                            "divide ... remainder requires numbers")
                if right == 0:
                    raise RuntimeError("Division by zero")
                quotient  = int(left / right)     # truncates toward zero
                remainder = left - quotient * right
                result = quotient
                self._store_target(node.remainder, remainder)
            else:
                result = self._apply_binop("/", left, right)

        try:
            self._store_target(node.giving or self._verb_target(node), result)
        except SizeError:
            if node.size_error is not None:
                self._exec(node.size_error)
                return
            raise

    def _verb_target(self, node: ArithVerb):
        """COBOL target rules, with a Mylang-friendly fallback.

        `add 5 to balance` / `subtract 3 from total` / `multiply 4 by price`
        direct the result into the second operand. When that operand is a
        literal (`multiply price by 4`), the first assignable operand is used
        instead, which is what a Mylang programmer expects.
        """
        if isinstance(node.right, (Identifier, IndexGet)):
            return node.right
        if isinstance(node.left, (Identifier, IndexGet)):
            return node.left
        raise RuntimeError(
            f"{node.op}: needs a variable target — use 'giving <target>'")

    def _exec_ComputeStmt(self, node: ComputeStmt):
        result = self._eval(node.expr)
        try:
            self._store_target(node.target, result)
        except SizeError:
            if node.size_error is not None:
                self._exec(node.size_error)
                return
            raise

    def _exec_StringStmt(self, node: StringStmt):
        text = "".join(_str(self._eval(part)) for part in node.parts)
        self._store_target(node.target, text)

    def _exec_UnstringStmt(self, node: UnstringStmt):
        source    = self._eval(node.source)
        delimiter = self._eval(node.delimiter)
        if not isinstance(delimiter, str) or delimiter == "":
            raise RuntimeError(
                "unstring: delimiter must be a non-empty string")
        text = source if isinstance(source, str) else _str(source)
        self._store_target(node.target, MylangArray(text.split(delimiter)))

    def _exec_InspectStmt(self, node: InspectStmt):
        source = self._eval(node.source)
        text   = source if isinstance(source, str) else _str(source)

        if node.mode == "replace":
            old = self._eval(node.old)
            new = self._eval(node.new)
            if not isinstance(old, str) or not isinstance(new, str):
                raise RuntimeError(
                    "inspect replacing: patterns must be strings")
            if old == "":
                raise RuntimeError(
                    "inspect replacing: search pattern must not be empty")
            target = node.target
            if target is None:
                target = self._assignable(node.source)
            if target is None:
                raise RuntimeError(
                    "inspect replacing: add 'giving <target>' or inspect a "
                    "variable directly")
            self._store_target(target, text.replace(old, new))
            return

        needle = self._eval(node.old)
        if not isinstance(needle, str) or needle == "":
            raise RuntimeError(
                "inspect tallying: search pattern must be a non-empty string")
        if node.target is None:
            raise RuntimeError(
                "inspect tallying: add 'giving <counter>'")
        self._store_target(node.target, text.count(needle))

    def _assignable(self, node):
        """Return node when it is a legal assignment target, else None."""
        if isinstance(node, (Identifier, IndexGet)):
            return node
        return None

    def _store_target(self, target, value):
        """Assign `value` to an Identifier or a record/array/hash element."""
        if isinstance(target, Identifier):
            self.env.assign(target.name, value)
            return value

        if isinstance(target, IndexGet):
            obj = self._eval(target.array)
            idx = self._eval(target.index)
            if isinstance(obj, MylangRecord):
                if not isinstance(idx, str) or idx not in obj.values:
                    raise RuntimeError(
                        f"Record '{obj.decl.name}' has no field {idx!r}")
                obj.values[idx] = _apply_pic(obj.pics[idx], value)
            elif isinstance(obj, MylangArray):
                self._check_index(obj, idx)
                obj.elements[int(idx)] = value
            elif isinstance(obj, MylangHash):
                obj.pairs[idx] = value
            else:
                raise RuntimeError(f"Cannot assign into {_type_name(obj)}")
            return value

        raise RuntimeError(
            "Assignment target must be a variable or a record field")

    def _eval_condition(self, record, cond):
        """Evaluate an 88-level condition against a record's field values."""
        env = Environment(self.env)
        for fname, value in record.values.items():
            env.define(fname, value)
        prev = self.env
        self.env = env
        try:
            return self._is_truthy(self._eval(cond.expr))
        finally:
            self.env = prev

    # ── expression handlers ───────────────────────────────────────────────────

    def _eval_NumberLiteral(self, n): return n.value
    def _eval_ComplexJLiteral(self, n): return MylangComplex(0.0, n.imag)
    def _eval_StringLiteral(self, n): return n.value
    def _eval_TemplateLiteral(self, n):
        parts = []
        for is_expr, val in n.segments:
            if is_expr:
                parts.append(_str(self._eval(val)))
            else:
                parts.append(val)
        return "".join(parts)
    def _eval_BoolLiteral(self,   n): return n.value
    def _eval_NullLiteral(self,   n): return None
    def _eval_DecimalLiteral(self, n):
        raw = n.value
        if not isinstance(raw, (str, int, float, Decimal)):
            raw = self._eval(raw)
        if isinstance(raw, bool):
            raise RuntimeError("dec() cannot convert a bool")
        try:
            return Decimal(str(raw))
        except Exception:
            raise RuntimeError(f"dec() cannot convert {raw!r} to a decimal")
    def _eval_Identifier(self,    n): return self.env.get(n.name)

    def _eval_FnExpr(self, node: FnExpr):
        return AnonFunction(node.params, node.body, self.env)

    def _eval_Assign(self, node: Assign):
        value = self._eval(node.value)
        self.env.assign(node.name, value)
        return value

    def _eval_ArrayLiteral(self, node: ArrayLiteral):
        return MylangArray([self._eval(e) for e in node.elements])

    def _eval_HashLiteral(self, node: HashLiteral):
        pairs = {}
        for k_expr, v_expr in node.pairs:
            key = self._eval(k_expr)
            if not isinstance(key, (str, int, float, bool, Decimal)):
                raise RuntimeError(
                    f"Hash key must be a string or number — got {_type_name(key)}")
            pairs[key] = self._eval(v_expr)
        return MylangHash(pairs)

    def _eval_IndexGet(self, node: IndexGet):
        obj   = self._eval(node.array)
        index = self._eval(node.index)
        if isinstance(obj, MylangRecord):
            if isinstance(index, str) and index in obj.values:
                return obj.values[index]
            if isinstance(index, str) and index in obj.conditions:
                return self._eval_condition(obj, obj.conditions[index])
            raise RuntimeError(
                f"Record '{obj.decl.name}' has no field {index!r}")
        if isinstance(obj, MylangNamespace):
            if not isinstance(index, str):
                raise RuntimeError("Namespace key must be a string")
            return obj.get_constant(index)
        if isinstance(obj, MylangArray):
            self._check_index(obj, index)
            return obj.elements[int(index)]
        if isinstance(obj, MylangHash):
            return obj.pairs.get(index, None)
        if isinstance(obj, str):
            if not isinstance(index, (int, float, Decimal)):
                raise RuntimeError("String index must be a number")
            i = int(index)
            if i < 0 or i >= len(obj):
                raise RuntimeError(f"String index {i} out of bounds")
            return obj[i]
        raise RuntimeError(f"Cannot index into {_type_name(obj)}")

    def _eval_IndexSet(self, node: IndexSet):
        obj   = self._eval(node.array)
        index = self._eval(node.index)
        value = self._eval(node.value)
        if isinstance(obj, MylangRecord):
            if not isinstance(index, str) or index not in obj.values:
                if isinstance(index, str) and index in obj.conditions:
                    raise RuntimeError(
                        f"Record condition '{index}' is read-only")
                raise RuntimeError(
                    f"Record '{obj.decl.name}' has no field {index!r}")
            obj.values[index] = _apply_pic(obj.pics[index], value)
        elif isinstance(obj, MylangArray):
            self._check_index(obj, index)
            obj.elements[int(index)] = value
        elif isinstance(obj, MylangHash):
            obj.pairs[index] = value
        else:
            raise RuntimeError(f"Cannot assign into {_type_name(obj)}")
        return value

    def _eval_SliceGet(self, node: SliceGet):
        obj   = self._eval(node.array)
        start = int(self._eval(node.start)) if node.start is not None else None
        end   = int(self._eval(node.end))   if node.end   is not None else None

        if isinstance(obj, MylangArray):
            return MylangArray(obj.elements[start:end])
        if isinstance(obj, str):
            return obj[start:end]
        if isinstance(obj, MylangRecord):
            return obj.pack()[start:end]
        raise RuntimeError(f"Cannot slice {_type_name(obj)}")

    def _eval_MethodCall(self, node: MethodCall):
        obj  = self._eval(node.object)
        args = [self._eval(a) for a in node.args]

        if isinstance(obj, MylangRecord):
            if node.method == "pack":
                return obj.pack()
            if node.method == "unpack":
                if not args:
                    raise RuntimeError("unpack() requires a record string")
                return obj.unpack(args[0])
            if node.method == "fields":
                return MylangArray([f for f, _, _ in obj.decl.fields])
            raise RuntimeError(f"Record has no method '{node.method}'")

        if isinstance(obj, MylangNamespace):
            return obj.call(node.method, args)
        if isinstance(obj, str):
            return _string_method(obj, node.method, args)
        if isinstance(obj, MylangArray):
            return _array_method(obj, node.method, args, self)
        if isinstance(obj, MylangHash):
            return _hash_method(obj, node.method, args)

        if isinstance(obj, MylangComplex):
            import cmath as _cm, math as _m
            if node.method == "real":  return obj.real
            if node.method == "imag":  return obj.imag
            if node.method == "abs":   return abs(obj.value)
            if node.method == "conj":  return MylangComplex(obj.real, -obj.imag)
            if node.method == "angle": return _m.degrees(_cm.phase(obj.value))
            raise RuntimeError(f"Complex has no method '{node.method}'")

        if isinstance(obj, Decimal):
            if node.method == "round":
                places = int(args[0]) if args else 0
                return obj.quantize(Decimal(1).scaleb(-places),
                                    rounding=ROUND_HALF_UP)
            if node.method == "truncate":
                places = int(args[0]) if args else 0
                return obj.quantize(Decimal(1).scaleb(-places),
                                    rounding=ROUND_DOWN)
            if node.method == "abs":
                return abs(obj)
            raise RuntimeError(f"Decimal has no method '{node.method}'")

        if isinstance(obj, MylangMatrix):
            from stdlib import (
                _mat_transpose, _mat_det, _mat_trace, _mat_get, _mat_set,
                _mat_shape, _mat_to_array, _mat_scale,
            )
            dispatch = {
                "transpose": _mat_transpose, "det":      _mat_det,
                "trace":     _mat_trace,     "get":      _mat_get,
                "set":       _mat_set,       "shape":    _mat_shape,
                "to_array":  _mat_to_array,  "scale":    _mat_scale,
            }
            if node.method in dispatch:
                return dispatch[node.method]([obj] + args)
            raise RuntimeError(f"Matrix has no method '{node.method}'")

        raise RuntimeError(
            f"Value of type {_type_name(obj)} has no method '{node.method}'")

    def _eval_UnaryOp(self, node: UnaryOp):
        v = self._eval(node.operand)
        if node.op == "-":
            if not isinstance(v, (int, float, Decimal)):
                raise RuntimeError(
                    f"Unary '-' requires a number — got {_type_name(v)}")
            return -v
        if node.op == "!":
            return not self._is_truthy(v)

    def _eval_BinaryOp(self, node: BinaryOp):
        return self._apply_binop(node.op,
                                 self._eval(node.left),
                                 self._eval(node.right))

    def _apply_binop(self, op, left, right):
        # Handle Decimal arithmetic (COBOL-style exact fixed point)
        if isinstance(left, Decimal) or isinstance(right, Decimal):
            def _to_d(v):
                if isinstance(v, Decimal): return v
                if isinstance(v, bool):
                    raise RuntimeError(f"Operator '{op}' cannot mix decimal with bool")
                if isinstance(v, (int, float)): return Decimal(str(v))
                raise RuntimeError(
                    f"Operator '{op}' cannot mix decimal with {_type_name(v)}")
            ld, rd = _to_d(left), _to_d(right)
            if op == "+": r = ld + rd
            elif op == "-": r = ld - rd
            elif op == "*": r = ld * rd
            elif op == "/":
                if rd == 0: raise RuntimeError("Decimal division by zero")
                r = ld / rd
            elif op == "%":
                if rd == 0: raise RuntimeError("Decimal modulo by zero")
                r = ld % rd
            elif op == "==": return ld == rd
            elif op == "!=": return ld != rd
            elif op == "<":  return ld <  rd
            elif op == "<=": return ld <= rd
            elif op == ">":  return ld >  rd
            elif op == ">=": return ld >= rd
            else: raise RuntimeError(
                f"Operator '{op}' not supported on decimals")
            return r

        # Native complex arithmetic: any operand being MylangComplex promotes both
        if isinstance(left, MylangComplex) or isinstance(right, MylangComplex):

            def _to_c(v):
                if isinstance(v, MylangComplex): return v.value
                if isinstance(v, (int, float)):  return complex(v)
                raise RuntimeError(
                    f"Operator '{op}' cannot mix complex with {_type_name(v)}")
            lc, rc = _to_c(left), _to_c(right)
            if op == "+": r = lc + rc
            elif op == "-": r = lc - rc
            elif op == "*": r = lc * rc
            elif op == "/":
                if rc == 0: raise RuntimeError("Complex division by zero")
                r = lc / rc
            elif op == "==": return lc == rc
            elif op == "!=": return lc != rc
            else: raise RuntimeError(
                f"Operator '{op}' not supported on complex numbers")
            return MylangComplex(r.real, r.imag)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return _str(left) + _str(right)
            self._nums(left, right, op)
            return left + right
        if op == "-":  self._nums(left, right, op); return left - right
        if op == "*":  self._nums(left, right, op); return left * right
        if op == "/":
            self._nums(left, right, op)
            if right == 0: raise RuntimeError("Division by zero")
            return left / right
        if op == "%":
            self._nums(left, right, op)
            if right == 0: raise RuntimeError("Modulo by zero")
            return left % right
        if op == "==": return self._eq(left, right)
        if op == "!=": return not self._eq(left, right)
        if op in ("<", "<=", ">", ">="):
            self._nums(left, right, op)
            return {"<": left < right, "<=": left <= right,
                    ">": left > right,  ">=": left >= right}[op]
        raise RuntimeError(f"Unknown operator '{op}'")

    def _eval_LogicalOp(self, node: LogicalOp):
        left = self._eval(node.left)
        if node.op == "||":
            return left if self._is_truthy(left) else self._eval(node.right)
        if node.op == "&&":
            return self._eval(node.right) if self._is_truthy(left) else left

    def _eval_Call(self, node: Call):
        callee = self._eval(node.callee)
        args   = [self._eval(a) for a in node.args]
        # We use a fallback name for error reporting if callee isn't a named function
        name = getattr(callee, "name", "<expr>")
        return self._dispatch_call(name, callee, args)

    def _eval_CallExpr(self, node: CallExpr):
        callee = self._eval(node.callee)
        args   = [self._eval(a) for a in node.args]
        return self._dispatch_call("<expr>", callee, args)

    # ── call helpers (reused by map / filter / reduce) ────────────────────────

    def _call_fn(self, fn, args: list):
        return self._dispatch_call("<anon>", fn, args)

    def _dispatch_call(self, name: str, callee, args: list):
        if isinstance(callee, RecordDecl):
            if args:
                raise RuntimeError(
                    f"Record '{callee.name}' takes no constructor arguments")
            defaults = {}
            for fname, _pic, default in callee.fields:
                if default is not None:
                    defaults[fname] = self._eval(default)
            return MylangRecord(callee, defaults)

        if isinstance(callee, BuiltinFunction):
            if callee.arity is not None and len(args) != callee.arity:
                raise RuntimeError(
                    f"'{callee.name}' expects {callee.arity} arg(s)"
                    f" — got {len(args)}")
            return callee.fn(args)

        if isinstance(callee, (Function, AnonFunction)):
            params  = callee.params
            body    = callee.body
            closure = callee.closure
            if len(args) != len(params):
                label = getattr(callee, "name", name)
                raise RuntimeError(
                    f"'{label}' expects {len(params)} arg(s)"
                    f" — got {len(args)}")
            call_env = Environment(closure)
            for p, a in zip(params, args):
                call_env.define(p, a)
            try:
                self._exec_Block(body, env=call_env)
            except ReturnSignal as r:
                return r.value
            return None

        raise RuntimeError(
            f"'{name}' is not callable — got {_type_name(callee)}")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _is_truthy(self, v) -> bool:
        if v is None or v is False: return False
        return True

    def _eq(self, a, b) -> bool:
        if a is None and b is None: return True
        if a is None or b is None:  return False
        return a == b

    def _nums(self, a, b, op: str):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise RuntimeError(
                f"Operator '{op}' requires numbers"
                f" — got {_type_name(a)} and {_type_name(b)}")

    def _check_index(self, arr: MylangArray, index):
        if not isinstance(index, (int, float, Decimal)):
            raise RuntimeError(
                f"Array index must be a number — got {_type_name(index)}")
        i = int(index)
        if i < 0 or i >= len(arr.elements):
            raise RuntimeError(
                f"Index {i} out of bounds (length {len(arr.elements)})")
