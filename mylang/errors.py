"""
mylang error formatting  (v0.9.0)

Produces readable code-frame error messages:

    ParseError: Expected ';' after expression
      --> script.ml, line 5, col 12
       |
     4 |  let x = 10;
     5 |  let y = 20
       |             ^
       = help: every mylang statement must end with a semicolon

Usage:
    from errors import format_error
    print(format_error(source, exc, filename="script.ml"))
"""

# Contextual help hints keyed by substrings of the error message
_HINTS = [
    ("Expected ';'",          "every mylang statement must end with a semicolon"),
    ("Expected '{'",          "mylang blocks always use curly braces — no Python-style colons"),
    ("Expected '}'",          "check for a missing closing brace earlier in the file"),
    ("Expected ')'",          "check for unbalanced parentheses on this line"),
    ("Undefined variable",    "declare variables with 'let' before first use"),
    ("Unterminated string",   "strings use double quotes: \"like this\""),
    ("Unterminated template", "template literals use backticks: `like ${this}`"),
    ("Unexpected character",  "mylang identifiers use ASCII letters, digits, and _ only"),
    ("Division by zero",      "guard with: if (denominator != 0) { ... }"),
    ("not callable",          "check the name — is it a function, and is it spelled right?"),
    ("out of bounds",         "array indexes run from 0 to len(arr) - 1"),
    ("import: file not found","import paths are relative to where you run the script"),
    ("Uncaught throw",        "wrap throwing code in try/catch: try { ... } catch (e) { ... }"),
    ("only be used inside",   "'return' belongs inside an fn function body"),
    ("recursion depth",       "check for infinite recursion — does your fn always reach a stop condition?"),
]


def _hint_for(message: str):
    for needle, hint in _HINTS:
        if needle.lower() in message.lower():
            return hint
    return None


def format_error(source: str, exc: Exception, filename: str = "script") -> str:
    """Format any mylang exception into a code-frame message.
    Falls back to the plain message when no line info is available."""
    kind    = type(exc).__name__
    message = str(exc)
    line    = getattr(exc, "line", None)
    col     = getattr(exc, "col",  None)

    # Strip legacy "[line N]" prefixes if present, recover line number
    import re
    m = re.match(r"\[line (\d+)\]\s*(.*)", message)
    if m and line is None:
        line    = int(m.group(1))
        message = m.group(2)
    elif m:
        message = m.group(2)

    header = f"{kind}: {message}"
    if line is None:
        return header

    lines = source.splitlines()
    if not (1 <= line <= len(lines)):
        return f"{header}\n  --> {filename}, line {line}"

    out = [header]
    out.append(f"  --> {filename}, line {line}" +
               (f", col {col}" if col else ""))
    out.append("   |")

    # Show the previous line for context when it exists
    width = len(str(line))
    if line > 1:
        out.append(f" {str(line-1).rjust(width)} |  {lines[line-2]}")
    out.append(f" {str(line).rjust(width)} |  {lines[line-1]}")

    if col:
        out.append("   |  " + " " * (col - 1) + "^")
    else:
        out.append("   |")

    hint = _hint_for(message)
    if hint:
        out.append(f"   = help: {hint}")

    return "\n".join(out)
