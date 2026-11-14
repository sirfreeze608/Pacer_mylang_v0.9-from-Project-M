"""
mylang AST Node definitions.
Plain dataclasses — easy to inspect, walk, and extend.
"""

from dataclasses import dataclass, field


# ── Expressions ──────────────────────────────────────────────────────────────

@dataclass
class NumberLiteral:
    value: float | int

@dataclass
class ComplexJLiteral:
    """Imaginary literal: 4j → complex(0, 4)"""
    imag: float

@dataclass
class StringLiteral:
    value: str

@dataclass
class BoolLiteral:
    value: bool

@dataclass
class NullLiteral:
    pass

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    op:    str
    left:  object
    right: object

@dataclass
class LogicalOp:
    op:    str      # "&&"  "||"
    left:  object
    right: object

@dataclass
class UnaryOp:
    op:      str    # "-"  "!"
    operand: object

@dataclass
class Assign:
    name:  str
    value: object

@dataclass
class ArrayLiteral:
    elements: list = field(default_factory=list)

@dataclass
class HashLiteral:
    """{ key: value, ... }"""
    pairs: list = field(default_factory=list)   # [(key_expr, val_expr), ...]

@dataclass
class IndexGet:
    """arr[index]  or  map[key]  or  namespace.CONST"""
    array: object
    index: object

@dataclass
class IndexSet:
    """arr[index] = value  or  map[key] = value"""
    array: object
    index: object
    value: object

@dataclass
class MethodCall:
    """expr.method(args)"""
    object: object
    method: str
    args:   list = field(default_factory=list)

@dataclass
class Call:
    """callee(args) - callee can be a name or any expression returning a function"""
    callee: object
    args:   list = field(default_factory=list)


@dataclass
class CallExpr:
    """callee(args) where callee is any expression — arr[0](x), h["fn"](y),
    make_adder(5)(10), etc."""
    callee: object
    args:   list = field(default_factory=list)

@dataclass
class FnExpr:
    """Anonymous function: fn(params) { body }"""
    params: list = field(default_factory=list)
    body:   object = None


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class VarDecl:
    name:        str
    initializer: object

@dataclass
class ExprStmt:
    expr: object

@dataclass
class PrintStmt:
    expr: object

@dataclass
class Block:
    statements: list = field(default_factory=list)

@dataclass
class IfStmt:
    condition:   object
    then_branch: object
    else_branch: object = None

@dataclass
class WhileStmt:
    condition: object
    body:      object

@dataclass
class ForStmt:
    """for (var in iterable) { body }"""
    var:      str
    iterable: object
    body:     object

@dataclass
class FnDecl:
    name:   str
    params: list = field(default_factory=list)
    body:   object = None

@dataclass
class ReturnStmt:
    value: object = None

@dataclass
class Program:
    statements: list = field(default_factory=list)

@dataclass
class DecimalLiteral:
    """Exact decimal: dec("123.45") — value is the inner expression node."""
    value: object

@dataclass
class CondDecl:
    """88-level style condition inside a record:
    cond active for status == "A";  →  e.active is a bool."""
    name:  str
    field: str          # documented anchor field
    expr:  object       # expression evaluated against the record's fields

@dataclass
class RecordDecl:
    """record Employee { name pic x(30); salary pic 9(7)v99; }"""
    name: str
    fields: list = field(default_factory=list) # list of (name, pic, default_value)
    conditions: list = field(default_factory=list)  # list of CondDecl

@dataclass
class TemplateLiteral:
    """Backtick string: `Hello ${name}!`
    segments: list of (is_expr: bool, value: str)
    Plain text segments have is_expr=False, value=the text.
    Expression segments have is_expr=True, value=the source string to parse."""
    segments: list = field(default_factory=list)

@dataclass
class ImportStmt:
    """import "path/to/file.ml"; — runs that file in the current scope."""
    path: str

@dataclass
class ThrowStmt:
    """throw expression; — raises a MylangRuntimeError."""
    value: object

@dataclass
class TryStmt:
    """try { body } catch (var) { handler }"""
    body:     object
    var:      str
    handler:  object


# ── COBOL-style statements (v0.9.0) ───────────────────────────────────────────

@dataclass
class SliceGet:
    """text[start:end] / arr[start:end] / record.pack()[start:end]"""
    array: object
    start: object = None
    end:   object = None

@dataclass
class WhenClause:
    """One `when …` arm of an evaluate statement.
    tests: [("eq", expr) | ("range", lo, hi), …]"""
    tests: list = field(default_factory=list)
    body:  object = None

@dataclass
class EvaluateStmt:
    """evaluate subject { when … { } when other { } }
    subject is None for the boolean form: evaluate { when cond { } }"""
    subject: object = None
    clauses: list = field(default_factory=list)   # [WhenClause]
    default: object = None                        # Block for `when other`

@dataclass
class PerformStmt:
    """perform until cond { … }
       perform varying i from 1 by 1 until i > 10 { … }
       perform 5 times { … }"""
    kind:      str                 # "until" | "varying" | "times"
    body:      object = None
    condition: object = None       # until test
    times:     object = None       # expression for "N times"
    var:       str    = ""         # varying loop variable
    start:     object = None
    step:      object = None

@dataclass
class ArithVerb:
    """add a to b / subtract a from b / multiply a by b / divide a by b
       [giving c] [remainder r] [on size error { … }]"""
    op:        str                 # "add" | "subtract" | "multiply" | "divide"
    left:      object
    right:     object
    giving:    object = None       # assignable target (Identifier | IndexGet)
    remainder: object = None       # assignable target for divide
    size_error: object = None      # Block run when a PIC size error occurs

@dataclass
class ComputeStmt:
    """compute total = expr [on size error { … }];"""
    target:     object
    expr:       object
    size_error: object = None

@dataclass
class StringStmt:
    """string a, b, c into target;"""
    parts:  list = field(default_factory=list)
    target: object = None

@dataclass
class UnstringStmt:
    """unstring text by "," into parts;"""
    source:    object = None
    delimiter: object = None
    target:    object = None

@dataclass
class InspectStmt:
    """inspect s replacing old with new [giving t];
       inspect s tallying needle giving count;"""
    source: object = None
    mode:   str    = "replace"     # "replace" | "tally"
    old:    object = None
    new:    object = None
    target: object = None
