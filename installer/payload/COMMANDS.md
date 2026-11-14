# mylang 0.9.0 — Command Reference

> The complete command book for **Pacer** and **mylang 0.9.0 "COBOL Workload
> Edition"**: the command line, the REPL, every Pacer shortcut and AI command,
> and a compact grammar reference for every statement and namespace.
>
> Canonical language guide: [`MYLANG_DOCS.md`](MYLANG_DOCS.md) ·
> Release history: [`CHANGELOG.md`](CHANGELOG.md)

---

## Contents

1. [Command-line interface](#1-command-line-interface)
2. [REPL](#2-repl)
3. [Pacer keyboard shortcuts](#3-pacer-keyboard-shortcuts)
4. [Pacer menus](#4-pacer-menus)
5. [Pacer AI commands](#5-pacer-ai-commands)
6. [Launchers and installers](#6-launchers-and-installers)
7. [Statement reference](#7-statement-reference)
8. [Operators and expressions](#8-operators-and-expressions)
9. [Built-in functions](#9-built-in-functions)
10. [Namespaces](#10-namespaces)
11. [Methods](#11-methods)
12. [Types](#12-types)
13. [Settings, files, environment](#13-settings-files-environment)
14. [Error reference](#14-error-reference)

---

## 1. Command-line interface

### Forms

```bash
# Run a file (module entry point)
python main.py program.ml

# Installed console script (after `pip install -e mylang/`)
mylang program.ml

# REPL
mylang --repl
python main.py --repl

# Debug views
mylang --tokens program.ml      # print token stream, then run
mylang --ast    program.ml      # print pretty AST, then run

# Version
mylang --version
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | program ran to completion |
| `1` | lexer, parser, or runtime error; file missing; usage error |

### Output streams

| Stream | Content |
|---|---|
| stdout | `print()` output |
| stderr | formatted errors — `LexerError`, `ParseError`, `RuntimeError`, `InternalError` |

Errors are rendered with a source excerpt, a caret at the failing column, and a
hint where one is available:

```
RuntimeError: Division by zero
  → 4 | let x = 10 / 0;
                 ^
```

### Flags

| Flag | Effect |
|---|---|
| `--tokens` | dump every token (`Token(TYPE, value, line, col)`) before running |
| `--ast` | dump the pretty-printed AST before running |
| `--repl` | interactive session; takes priority over file names |
| `--version` | print `mylang 0.9.0` and exit |
| *no args* | starts the REPL |

Flags may appear anywhere; only the first non-flag argument is executed.

---

## 2. REPL

```bash
python main.py --repl
```

```
mylang 0.9.0 REPL
Type 'exit' to quit, '.tokens' / '.ast' to toggle debug output.

>>> let x = 21;
>>> print(x * 2);
42
```

| Input | Effect |
|---|---|
| `exit` | leave the REPL (Ctrl+D / Ctrl+C also work) |
| `.tokens` | toggle token dumps for each following entry |
| `.ast` | toggle AST dumps for each following entry |
| *blank line* | ignored |

Behaviour notes:

- State persists across entries — variables and functions stay alive.
- A missing trailing `;` is added automatically, and `}` also terminates input.
- Each entry must be complete on one logical line; there is no multi-line
  continuation prompt.
- Errors are printed and the session continues; nothing aborts the REPL.

---

## 3. Pacer keyboard shortcuts

Defaults (every shortcut can be rebound in **Settings → Keybindings**; changes
apply after a restart).

| Action | Default |
|---|---|
| New mylang file (`.ml`) | **Ctrl+N** |
| New file of another type | **Ctrl+Shift+N** |
| Open file | **Ctrl+O** |
| Open folder (set project root) | **Ctrl+K Ctrl+O** |
| Save | **Ctrl+S** |
| Save As | **Ctrl+Shift+S** |
| Run current file | **F5** |
| Settings / Preferences | **Ctrl+,** |
| Zoom in | **Ctrl+=** |
| Zoom out | **Ctrl+-** |
| Reset zoom | **Ctrl+0** |

Editor gestures:

| Gesture | Effect |
|---|---|
| **Tab** / **Shift+Tab** | indent / outdent selection |
| **Enter** inside `{ }` | auto-indent one level |
| **Ctrl+Mouse wheel** | zoom (where supported by Qt) |
| Tab drag | reorder open files |
| Middle-click tab | close tab |

Running:

| Control | Effect |
|---|---|
| **F5** / **▶ Run** / `/run` | run the current file |
| **■ Stop** | stop the run (mylang: between statements; subprocesses: terminated) |
| **Run → Clear Output** | empty the output panel |

`.ml` files run in-process on a background thread. `.py` runs `python -u`,
`.js` runs `node`, and `.html` / `.xml` open in the default browser.

---

## 4. Pacer menus

| Menu | Items |
|---|---|
| **File** | New mylang File (.ml) · New File (choose type)… · Open · Open Folder… · Save · Save As · Exit |
| **Run** | Run File · Clear Output |
| **View** | Theme ▸ (Dark / Light / High Contrast) · Mode ▸ (Editor Only / Editor + Output / Editor + Visual Panel / Editor + Browser Panel / Full Screen) · Toggle Output Panel · Toggle AI Assistant Panel · Toggle Visual Panel · Toggle Browser Panel · Toggle Example Gallery · Toggle File Tree · Zoom In/Out/Reset |
| **mylang** | Show Built-ins Reference · Open Documentation |
| **Settings** | Preferences… |

Explorer right-click: Open · Set as Project Folder · Reveal in File Explorer ·
Rename · Delete · New mylang File Here… · New Folder…

---

## 5. Pacer AI commands

Type these in the command bar at the bottom of the window and press Enter.

| Command | What it does |
|---|---|
| `/run` | Run the current `.ml` file |
| `/debug` | AI reviews the file and explains each bug |
| `/fix` | AI repairs the file and offers to apply the result |
| `/complete` | AI finishes the code at the cursor / end of file |
| `/explain` | AI explains the file step by step |
| `/mylang <question>` | Ask any mylang question in natural language |
| `/settings` | Open the Settings dialog |
| `/help` | Print the command list into the output panel |

Notes:

- AI commands automatically receive the mylang syntax reference, so answers use
  mylang (`fn`, `let`, `{}`, `;`), not Python or JavaScript.
- A provider and key must be configured first — **Settings → AI**. Keys set via
  environment variables are used when the settings field is empty.
- Provider keys are stored per provider, so switching never overwrites another
  key. See [`SECURITY.md`](SECURITY.md) for how they are protected.

| Provider | Environment variable |
|---|---|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google Gemini | `GOOGLE_API_KEY` |
| Groq | `GROQ_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |

---

## 6. Launchers and installers

| Script | Platform | Purpose |
|---|---|---|
| `Pacer_mylang.pyw` | all | launch Pacer without a console window |
| `run_pacer.bat` | Windows | double-click launcher |
| `fix_pyw_association.bat` | Windows | link `.pyw` to `pythonw.exe` |
| `install.bat` | Windows | install dependencies, create shortcuts |
| `install.sh` | macOS / Linux | install dependencies, create launcher |
| `build_exe.ps1` | Windows | build `dist\Pacer.exe` (PyInstaller) |
| `build_msi.ps1` | Windows | build `installer\bin\Release\Pacer-Setup.msi` (WiX) |

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
powershell -ExecutionPolicy Bypass -File .\build_msi.ps1
```

---

## 7. Statement reference

Every statement ends with `;`. Blocks always use `{ }`. Words marked *soft* are
only keywords in the shape shown — they remain usable as identifiers and
function names.

### Core

| Statement | Syntax |
|---|---|
| Variable | `let name = expr;` |
| Reassign | `name = expr;` · `arr[i] = v;` · `h["k"] = v;` · `rec.field = v;` |
| Print | `print(expr);` |
| If | `if (cond) { } else if (cond) { } else { }` |
| While | `while (cond) { }` |
| For-in | `for (item in iterable) { }` |
| Function | `fn name(a, b) { return expr; }` |
| Anonymous function | `let f = fn(x) { return x * 2; };` |
| Return | `return expr;` / `return;` |
| Comment | `// one line` |
| Import | `import "file.ml";` |
| Try / catch | `try { } catch (e) { }` |
| Throw | `throw expr;` |

### Records (0.8.0)

```mylang
record Name {
    field  pic x(20);
    amount pic 9(7)v99 = dec("0.00");
    cond active for amount > dec("0");
}

let r = Name();
r.field = "Ada";
print(r.pack());
print(r.fields());
r.unpack(line);
print(r.active);
```

### COBOL-style statements (0.9.0, soft keywords)

| Statement | Syntax |
|---|---|
| evaluate | `evaluate subj { when a, b { } when lo thru hi { } when other { } }` |
| evaluate (boolean) | `evaluate { when cond { } when other { } }` |
| perform until | `perform until cond { }` |
| perform varying | `perform varying i from a by b until cond { }` |
| perform times | `perform n times { }` |
| add | `add a to b [giving t] [on size error { }];` |
| subtract | `subtract a from b [giving t] [on size error { }];` |
| multiply | `multiply a by b [giving t] [on size error { }];` |
| divide | `divide a by b [giving t] [remainder r] [on size error { }];` |
| compute | `compute target = expr [on size error { }];` |
| string | `string a, b, c into target;` |
| unstring | `unstring s by delim into target;` |
| inspect replace | `inspect s replacing old with new [giving t];` |
| inspect tally | `inspect s tallying needle giving count;` |
| slice | `text[a:b]` · `text[a:]` · `text[:b]` · `text[-n:]` |

`on size error { }` may be followed by `;` or not.

### Business file I/O (0.9.0)

```mylang
file.read_records(path, Record [, encoding])   // array of Record
file.write_records(path, recordOrArray)
file.append_record(path, record)
file.read_record(path, Record, index)
file.record_count(path, Record)
```

See [section 10](#file--business-io) for the full list.

---

## 8. Operators and expressions

Highest to lowest precedence:

| Level | Operators |
|---|---|
| Postfix | `()` call · `[]` index/slice · `.` field/method |
| Unary | `-` · `!` |
| Multiplicative | `*` `/` `%` |
| Additive | `+` `-` |
| Comparison | `<` `<=` `>` `>=` |
| Equality | `==` `!=` |
| Logical AND | `&&` |
| Logical OR | `\|\|` |
| Assignment | `=` (statement level) |

Literals:

| Kind | Examples |
|---|---|
| Number | `42`, `3.14`, `-7`, `1e-6`, `4.7e-12` |
| String | `"text"`, `'text'` |
| Template | `` `Hello, ${name}!` `` |
| Bool | `true`, `false` |
| Null | `null` |
| Complex | `3 + 4j`, `2j`, `1.5e-3j`, `complex(3, 4)` |
| Array | `[1, 2, 3]`, `[]` |
| Hash | `{"key": value}` |
| Decimal | `dec("19.99")` |
| Matrix | `matrix([[1,2],[3,4]])` |

Strings support concatenation with `+`; arrays concatenate with `+` as well.
`==` compares decimal value and string content.

---

## 9. Built-in functions

Global, always available:

| Function | Returns |
|---|---|
| `len(x)` | length of string, array, hash, or record field count |
| `type(x)` | `"number"`, `"string"`, `"bool"`, `"null"`, `"array"`, `"hash"`, `"function"`, `"complex"`, `"matrix"`, `"decimal"`, `"record"` |
| `str(x)` | string form of any value |
| `num(x)` | number from a numeric string |
| `push(arr, v)` | append to array |
| `pop(arr)` | remove and return last element |
| `range(n)` / `range(a,b)` / `range(a,b,step)` | array of integers (max 10,000,000 elements) |
| `keys(h)` / `values(h)` | hash keys / values |
| `has(h,k)` / `del(h,k)` | test / remove a hash key |
| `complex(r,i)` | complex number |
| `real(z)` / `imag(z)` / `complex_abs(z)` | complex parts |
| `matrix(rows)` / `mat_zeros(r,c)` / `mat_identity(n)` | matrices |
| `dec("1.23")` | exact decimal (special syntax, not a function value) |

---

## 10. Namespaces

### math

```
abs  cbrt  pow  floor  ceil  round  sign  clamp
sin  cos  tan  asin  acos  atan  atan2  sinh  cosh  tanh
deg  rad  exp  log  log2  log10
factorial  gcd  lcm  comb  perm
random  rand_int  rand_seed  quadratic
```

Constants: `PI E TAU PHI INF NAN` — also available as bare names.

### stats

```
mean  median  mode  stdev  pstdev  variance  pvariance
min  max  sum  data_range
percentile  quartiles  correlation  covariance  linreg
normalize  zscore  histogram
normal_pdf  normal_cdf
```

### ee

```
voltage  current  resistance  power  power_r  power_v
series  parallel  cap_series  cap_parallel  ind_series  ind_parallel
xc  xl  impedance_rc  impedance_rl  impedance_rlc
resonant_freq  q_factor  bandwidth  rc_tau  rl_tau
rc_charge  rc_discharge  to_db  to_db_power  from_db  from_db_power
vrms  vpeak  phasor  phasor_mag  phasor_angle
complex_add  complex_mul  complex_div  complex_conj
voltage_divider  current_divider  thevenin  norton
energy_cap  energy_ind  charge
```

Constants: `ee.EPSILON0 ee.MU0 ee.C_LIGHT ee.PLANCK ee.BOLTZMANN ee.ELECTRON`

### crypto

```
sha256(text)                     hex digest
hmac(text, key)                  hex MAC
pbkdf2(password, salt[, iter])   derived key (iterations capped at 10,000,000)
encrypt_aes(text, key)           authenticated ciphertext, "v2:" prefix
decrypt_aes(ciphertext, key)     plaintext
secure_store(key, value)         memory vault write
secure_retrieve(key)             memory vault read
secure_wipe(key)                 erase one vault entry
```

`encrypt_aes` uses AES-256-GCM when the `cryptography` package is installed and
an authenticated SHA-256 CTR + HMAC-SHA256 construction otherwise. Both
produce authenticated ciphertext with a random nonce.

### image (SVG)

```
blank(w, h)  rect  circle  line  text  load  show
```

`show(["panel"|"browser"|"file"])` displays the drawing.

### csv

```
csv.parse(text)        -> array of rows (numbers auto-coerced)
csv.stringify(rows)    -> CSV text
```

### html

```
page  heading  text  result  kv  table  list  code  raw  divider
render(value [, label])  show(["browser"|"file"|"panel"])
```

### chart

```
page  line  multi_line  bar  area  scatter  pie  histogram  show
```

### json

```
json.parse(text)        -> value
json.stringify(value)   -> compact JSON
json.pretty(value)      -> indented JSON
```

### file — business I/O

```
read(path [, enc])              write(path, text [, enc])
append(path, text [, enc])      read_lines(path [, enc])
write_lines(path, lines)        append_line(path, text)
read_records(path, Record [, enc])   write_records(path, records)
append_record(path, record)     read_record(path, Record, index)
record_count(path, Record)      read_csv(path [, enc])
write_csv(path, rows)           exists(path)
size(path)                      delete(path)
list(dir)                       mkdir(path)
copy(src, dst)                  rename(src, dst)
touch(path)                     cwd()
tempdir()
```

Limits: reads cap at 64 MB; writes are atomic except appends; paths must be
non-empty strings with no NUL byte.

---

## 11. Methods

| Type | Methods |
|---|---|
| Array | `.map(fn)` `.filter(fn)` `.reduce(fn, init)` `.push(v)` `.pop()` `.len()` `.reverse()` `.join(sep)` `.slice(a,b)` `.contains(v)` `.index_of(v)` |
| String | `.upper()` `.lower()` `.trim()` `.split(sep)` `.replace(a,b)` `.contains(s)` `.starts_with(s)` `.ends_with(s)` `.slice(a,b)` `.index_of(s)` |
| Hash | `.keys()` `.values()` `.has(k)` `.del(k)` `.len()` |
| Complex | `.real()` `.imag()` `.abs()` `.conj()` `.angle()` |
| Matrix | `.det()` `.trace()` `.transpose()` `.shape()` |
| Decimal | `.round(places)` `.truncate(places)` `.abs()` |
| Record | `.pack()` `.unpack(text)` `.fields()` |

Slicing works on strings, arrays, and `record.pack()` via `[a:b]`.

---

## 12. Types

`number` (`int`/`float`), `decimal`, `string`, `bool`, `null`, `array`, `hash`,
`complex`, `matrix`, `record`, `function`, `namespace`.

Decimals are exact fixed-point values. Arithmetic with integers is allowed;
arithmetic with floats is rejected unless converted with `dec(str(x))`.

Records are fixed-width structs with PIC-checked fields. Assigning a value that
does not fit raises a **size error**, which `on size error { }` can intercept.

---

## 13. Settings, files, environment

| Path | Content |
|---|---|
| `~/.pacer_settings.json` | editor, theme, keys, AI provider, model, keybindings |
| `~/.pacer_backups/` (default) | timed `.bak` snapshots |
| `output/` | `html.show(["file"])`, charts, and example output |
| `<project>/` | Explorer root; persists across restarts |

Environment variables: the five provider keys in
[section 5](#5-pacer-ai-commands), plus `PYTHONIOENCODING=utf-8` on Windows
consoles for correct Unicode output.

Settings tabs: **Editor** (font, tab width, wrap, indent, line numbers,
highlight), **Appearance** (theme, accent), **AI** (provider, key, model, max
tokens), **Run** (auto-save, clear output), **Files** (save dir, auto-backup,
interval, folder), **Keybindings**, **About** (versions, paths, configured
providers, engine status).

`~/.pacer_settings.json` is written with owner-only permissions (`0o600`).
API keys are never printed in the output panel or logs.

---

## 14. Error reference

| Message | Cause | Fix |
|---|---|---|
| `ParseError at 'x': Expected ';'` | Missing semicolon | End every statement with `;` |
| `ParseError at 'x': Expected expression` | Empty value | Check `let x = ;` |
| `ParseError at '=': Expected '('` | `fn name =` | Use `fn name(...)` |
| `LexerError: Unexpected character '@'` | Illegal char | Identifiers use letters, digits, `_` |
| `Undefined variable 'x'` | Not declared | Add `let x = ...;` |
| `'foo' is not callable` | Calling a non-function | Check the name/spelling |
| `Index 5 out of bounds (length 3)` | Index too large | Guard with `len()` |
| `Division by zero` | Divisor `0` | Check before dividing |
| `Size error: … does not fit PIC …` | Value too large for a field | Shrink it or handle `on size error` |
| `perform N times: repeat count must be a number` | Non-numeric count | Pass a number |
| `perform varying: 'by' step must not be zero` | Zero step | Use a non-zero step |
| `evaluate: 'thru' ranges need a subject value` | `thru` in boolean form | Give `evaluate` a subject |
| `inspect tallying: add 'giving <counter>'` | Missing target | Add `giving n` |
| `file.read: path must be a non-empty string` | Empty path | Pass a real path |
| `file.read_records: expected a record type` | Passed an instance | Use `Employee`, not `Employee()` |
| `file.read_record: index N out of range` | Bad index | Check `file.record_count(...)` |
| `Record condition 'active' is read-only` | Assigned to a `cond` | Set the field instead |
| `Maximum recursion depth exceeded` | Infinite recursion | Add a base case |
| `Uncaught throw: …` | `throw` outside `try` | Wrap in `try { } catch (e) { }` |
| `InternalError: …` | Host bug | Report with the source and traceback |
