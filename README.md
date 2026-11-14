# Pacer + mylang  v0.9.0 — "COBOL Workload Edition"

> **Pacer** is a production-ready dark-themed code editor with a built-in interpreter for
> **mylang** — a custom scripting language designed for maths, statistics, electrical
> engineering, cryptography, data analysis, **exact financial arithmetic, COBOL-style
> statements, fixed-width business records, and business file I/O**.
> Press **F5** and your `.ml` file runs instantly. No separate compiler needed.
>
> **0.9.0 adds Phase 2 + Phase 3 of the COBOL workload:** `evaluate`, `perform`,
> `add/subtract/multiply/divide`, `compute`, `string`/`unstring`/`inspect`,
> slices, 88-level record conditions, and `file.*` fixed-record/CSV I/O.
> Everything is soft-keyword sugar, so 0.8.0 programs keep running unchanged.

---

## Quick Start

### 1. Install dependencies

```bash
pip install PyQt5 anthropic
```

Optional — install only if you plan to use those AI providers:

```bash
pip install openai                  # for OpenAI GPT, Groq, and OpenRouter
pip install google-generativeai     # for Google Gemini
pip install cryptography            # AES-256-GCM for crypto.encrypt_aes()
```

Pacer runs without `cryptography`; the crypto namespace then falls back to an
authenticated encrypt-then-MAC construction (AES is replaced by SHA-256 CTR
with an HMAC tag). Both formats decrypt transparently.

### 2. Set your API key (for AI features)

Pacer supports **five AI providers**. Set the key for whichever you use:

```bash
# macOS / Linux  — add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-..."

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

Or add any key directly inside Pacer via **Settings → Preferences (Ctrl+,) → AI tab**.

### 3. Project file layout

```
your-project/
├── Pacer_mylang.pyw         ← launch this (no console window)
├── fix_pyw_association.bat  ← run once on Windows to link .pyw to pythonw
├── run_pacer.bat            ← Windows double-click launcher
├── install.bat              ← Windows one-click setup
├── install.sh               ← macOS / Linux setup
├── build_exe.ps1            ← build a standalone Pacer.exe
├── build_msi.ps1            ← build a Windows MSI installer
├── MYLANG_DOCS.md           ← full language reference (opens inside Pacer)
├── COMMANDS.md              ← command reference: CLI, REPL, Pacer, AI, syntax
├── CHANGELOG.md             ← release history
├── SECURITY.md              ← security model, limits, reporting
├── RELEASE_NOTES.md         ← what's new in 0.9.0
├── README.md                ← this file
├── requirements.txt         ← pinned dependency versions
├── pacer_logo.png           ← your app icon (optional)
│
├── mylang/                  ← language engine (do not modify unless extending)
│   ├── lexer.py             Tokeniser: source text → token list
│   ├── ast_nodes.py         AST node dataclasses
│   ├── parser.py            Parser: tokens → abstract syntax tree
│   ├── interpreter.py       Interpreter: AST → execution
│   ├── stdlib.py            Standard library (math, stats, ee, crypto, image, csv, html, file)
│   ├── main.py              CLI entry point and REPL
│   ├── setup.py             pip install -e . support
│   ├── tests.py             215 automated tests
│   └── examples/
│       ├── hello.ml
│       ├── fibonacci.ml
│       ├── fizzbuzz.ml
│       ├── arrays.ml
│       ├── showcase.ml
│       ├── functions.ml
│       ├── math_stats.ml
│       ├── ee_showcase.ml
│       ├── complex_matrix.ml
│       ├── new_features.ml            ← crypto, image, csv, complex literals
│       ├── records.ml                 ← records, PIC, pack/unpack
│       ├── decimals.ml                ← exact decimal arithmetic
│       ├── cobol_statements.ml        ← evaluate/perform/verbs/slices/conditions
│       ├── payroll.ml                 ← fixed-record payroll workload
│       ├── business_files.ml          ← records, lines, CSV, housekeeping
│       ├── sudoku.ml                  ← backtracking constraint solver
│       ├── sudoku_html.ml             ← solver with HTML output
│       ├── html_quadratic_solver.ml   ← quadratic equation → HTML page
│       └── html_auto_render.ml        ← html.render() type showcase
│
├── games/
│   └── sudoku_game.html     ← standalone playable Sudoku (difficulties, sign-in, animations)
│
├── mylang-vscode/           ← VS Code extension (syntax highlighting + snippets)
│   ├── package.json
│   ├── extension.js
│   ├── language-configuration.json
│   ├── syntaxes/
│   │   └── mylang.tmLanguage.json
│   └── snippets/
│       └── mylang.json
│
└── installer/               ← WiX MSI build inputs
    ├── Pacer.wxs
    ├── Pacer.wixproj
    └── License.rtf
```

### 4. Launch Pacer

**Windows — no console window (recommended):**
```
Double-click run_pacer.bat
  — or —
Double-click Pacer_mylang.pyw
```

> If double-clicking `.pyw` does nothing, run `fix_pyw_association.bat` once to register
> the file type. This writes a registry entry linking `.pyw` → `pythonw.exe`.

**macOS / Linux:**
```bash
python3 Pacer_mylang.pyw
```

**After dependencies are installed:**
Pacer opens with a fresh `Untitled-1.ml` tab ready to go.

---

## Running Files

Pacer runs every language it edits, on a background thread so the UI never
freezes:

| File type | How Pacer runs it |
|---|---|
| `.ml` | built-in mylang interpreter (no Python subprocess needed) |
| `.py` | `python -u <file>` |
| `.js` | `node <file>` (Node.js must be on `PATH`) |
| `.html` / `.xml` | opens the file in your default browser |
| `.jsx` / `.tsx` / `.ts` | not runnable without a bundler — Pacer explains this |

Press **F5**, click **▶ Run**, or type `/run`. **■ Stop** terminates the running
program (mylang runs are stopped between statements; Python/Node processes are
terminated).

| Method | Command |
|--------|---------|
| Inside Pacer | Press **F5**, or type `/run` in the command bar |
| Terminal | `python mylang/main.py yourfile.ml` |
| Global CLI (after `pip install -e .`) | `mylang yourfile.ml` |
| Interactive REPL | `mylang --repl` |
| Dump token stream | `mylang --tokens yourfile.ml` |
| Dump AST | `mylang --ast yourfile.ml` |

---

## Pacer Features

### Editor

| Feature | Detail |
|---------|--------|
| New mylang file | **Ctrl+N** — opens a `.ml` tab with Hello World template |
| New other types | **Ctrl+Shift+N** — pick Python, JS, JSX, HTML, XML, plain text |
| Open Folder | **File → Open Folder… (Ctrl+K Ctrl+O)** — sets the Explorer root |
| Unsaved indicator | `●` dot in tab name; clears on save |
| Auto-save before run | Configurable in Settings → Run |
| Run any file type | `.ml` (interpreter), `.py` (python), `.js` (node), `.html`/`.xml` (browser) |
| Background runner | Runs never block the UI; **■ Stop** kills long programs |
| Syntax highlighting | mylang, Python, JavaScript, React/JSX, HTML, XML |
| Line numbers | Gutter with current-line highlight (toggleable) |
| Auto-indent | Enter inside `{` blocks indents to match scope |
| Word wrap | Toggleable in Settings → Editor |
| Font control | Family, size, tab width — all in Settings → Editor |
| Zoom | **Ctrl+=** / **Ctrl+-** / **Ctrl+0** — live across all open tabs |
| Auto-backup | Timed `.bak` snapshots — configure interval and folder in Settings → Files |

### File Explorer Panel

| Feature | Detail |
|---------|--------|
| Project root | Shows folder name as header; persists across restarts |
| Navigate up | **⬆** button in the Explorer header |
| Refresh | **⟳** button forces a re-read of the current folder |
| Right-click menu | Open, Set as Project Folder, Reveal in File Explorer, Rename, Delete |
| New file here | Right-click → New mylang File Here… (pre-filled with template) |
| New folder | Right-click → New Folder… |

### View / Theme / Mode Menu

| Feature | Detail |
|---------|--------|
| **View → Theme** | Dark (default) · Light · High Contrast — live, no restart |
| **View → Mode** | Editor Only · Editor + Output · Editor + Visual Canvas · Full Screen |
| **View → Toggle panels** | Output · AI Assistant · Visual Panel · File Tree — individual toggles |
| Visual Panel | Auto-opens when `image.show()` or `html.show(["panel"])` is called |

### AI Assistant

| Command | Action |
|---------|--------|
| `/run` | Run the current `.ml` file |
| `/debug` | Ask AI to find bugs in the current file |
| `/fix` | Ask AI to repair errors (offers to apply the result) |
| `/complete` | Ask AI to finish incomplete code |
| `/explain` | Ask AI to explain what the code does line by line |
| `/mylang <q>` | Ask any mylang language question in natural language |
| `/settings` | Open the Settings dialog |
| `/help` | Show all commands |

**Supported AI providers** (switch in Settings → AI):

| Provider | Models included |
|----------|----------------|
| Anthropic (Claude) | claude-sonnet-4-6, claude-haiku-4-5, claude-opus-4-6 |
| OpenAI (GPT) | gpt-4.1, gpt-4.1-mini, gpt-4o, o3-mini |
| Google (Gemini) | gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash |
| Groq | llama-3.3-70b, mixtral-8x7b, gemma2-9b |
| OpenRouter | anthropic/claude-sonnet-4.6, openai/gpt-4.1, meta-llama/llama-3.3-70b |

Each provider has its own stored API key — switching providers never overwrites another key.

### Settings (Ctrl+,)

Seven tabs persist all preferences to `~/.pacer_settings.json`:

| Tab | What it controls |
|-----|-----------------|
| Editor | Font family, size, tab width, word wrap, auto-indent, line numbers, line highlight |
| Appearance | Theme (dark/light/high contrast), accent colour picker |
| AI | Provider selector, API key per provider (masked), model, max tokens |
| Run | Auto-save before run, clear output before each run |
| Files | Default save directory, auto-backup on/off, interval, backup folder |
| Keybindings | Edit any shortcut (changes take effect after restart) |
| About | Python version, all file paths, configured providers, mylang engine status |

---

## Building a Standalone Executable

### `.exe` only (no installer)

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Output: `dist\Pacer.exe` — fully self-contained, no Python needed on the target machine.
The mylang engine, documentation, and logo are bundled inside the `.exe`.

### MSI installer (Start Menu + Add/Remove Programs + uninstaller)

Requires the .NET SDK (free, from [dotnet.microsoft.com](https://dotnet.microsoft.com/download)):

```powershell
powershell -ExecutionPolicy Bypass -File .\build_msi.ps1
```

Output: `installer\bin\Release\Pacer-Setup.msi`  
Installs to Program Files, creates a Start Menu shortcut, a Desktop shortcut,
and registers a working uninstaller in Add/Remove Programs.  
The VS Code extension is bundled and optionally installed if VS Code is detected.

---

## mylang in 90 Seconds

```ml
// ── Core syntax ───────────────────────────────────────────────────────────
let name = "World";
let x    = 42;
print("Hello, " + name + "!");       // Hello, World!

fn square(n) { return n * n; }
print(square(x));                    // 1764

// ── Arrays and loops ─────────────────────────────────────────────────────
let nums = [1, 2, 3, 4, 5];
let squares = nums.map(fn(n) { return n * n; });
print(squares);                      // [1, 4, 9, 16, 25]

// ── Hash maps ─────────────────────────────────────────────────────────────
let person = {"name": "Alice", "age": 30};
print(person["name"]);               // Alice

// ── Math ──────────────────────────────────────────────────────────────────
print(sqrt(144));                    // 12
print(quadratic(1, -5, 6));          // [3, 2]

// ── Statistics ────────────────────────────────────────────────────────────
let data = [10, 20, 30, 40, 50];
print(stats.mean(data));             // 30
print(stats.stdev(data));            // 15.811...

// ── Electrical engineering ────────────────────────────────────────────────
print(ee.voltage(2, 100));           // 200
print(ee.parallel([100, 100]));      // 50
print(ee.resonant_freq(10e-3, 1e-6));// 1591.55 Hz

// ── Complex numbers (literal j syntax) ────────────────────────────────────
let z1 = 3 + 4j;
let z2 = 1 - 2j;
print(z1 + z2);                      // 4+2j  (native arithmetic)
print(z1.abs());                     // 5.0
print(z1.angle());                   // 53.13...°

// ── Cryptography ──────────────────────────────────────────────────────────
let hash = crypto.sha256("hello");
let enc  = crypto.encrypt_aes("secret", "key");   // authenticated, random nonce
let dec  = crypto.decrypt_aes(enc, "key");
print(dec);                          // secret

// ── HTML output ───────────────────────────────────────────────────────────
html.page("My Results");
html.heading("Quadratic solver", 1);
html.result("Roots", quadratic(1, -5, 6));
html.kv("Discriminant", 1);
html.show(["browser"]);              // opens a styled HTML page in your browser
```

---

## Language Overview

| Feature | Syntax |
|---------|--------|
| Variable | `let x = value;` |
| Reassign | `x = new_value;` (no `let` on reassignment) |
| Function | `fn name(a, b) { return a + b; }` |
| Anonymous fn | `let f = fn(x) { return x * 2; };` |
| Closure | Functions capture their parent scope |
| If / else if / else | `if (cond) { } else if (cond) { } else { }` |
| While | `while (cond) { }` |
| For-in | `for (item in array) { }` — works on arrays, strings, hashes, range() |
| Array | `[1, 2, 3]` · `arr[0]` · `arr[1] = v` |
| Hash | `{"key": val}` · `h["key"]` · `h["k"] = v` |
| Complex literal | `3 + 4j` · `2j` · `1.5e-3j` |
| Complex function | `complex(3, 4)` |
| Matrix | `matrix([[1,2],[3,4]])` |
| Scientific notation | `1e-6`, `4.7e-12`, `1e6` |
| Comment | `// single-line` |
| Semicolons | **Mandatory** at end of every statement |
| Braces | **Mandatory** around all blocks — no Python-style colons |
| Slice | `s[1:4]` · `arr[2:]` · `text[:3]` · `record.pack()[2:6]` |
| Evaluate | `evaluate x { when 1, 2 { } when 3 thru 5 { } when other { } }` |
| Perform | `perform until cond { }` · `perform varying i from 1 by 1 until … { }` · `perform n times { }` |
| Arithmetic verbs | `add a to b;` · `subtract a from b;` · `multiply a by b;` · `divide a by b giving c remainder r;` |
| Compute | `compute total = a * b + c;` (supports `on size error { }`) |
| String verbs | `string a, b into t;` · `unstring s by "," into parts;` · `inspect s replacing a with b;` |
| Record condition | `cond active for status == "A";` inside a `record` |

### Standard Library Namespaces

| Namespace | Size | Key functions |
|-----------|------|---------------|
| `math.*` | 40+ | sqrt, trig, log, exp, factorial, gcd, comb, perm, random, quadratic, clamp |
| `stats.*` | 20 | mean, median, mode, stdev, variance, linreg, normalize, zscore, normal_pdf/cdf, histogram |
| `ee.*` | 35 | Ohm's law, series/parallel, impedance, RC/RL, resonance, phasors, dB, Thevenin/Norton |
| `crypto.*` | 8 | sha256, hmac, pbkdf2, encrypt_aes, decrypt_aes, secure_store, secure_retrieve, secure_wipe |
| `image.*` | 7 | blank, rect, circle, line, text, show, load — SVG canvas rendering |
| `csv.*` | 2 | parse, stringify — auto-coerces numbers |
| `html.*` | 12 | page, heading, text, result, kv, table, list, code, raw, divider, render, show |
| `file.*` | 24 | read/write/lines, fixed-width records, CSV, size/rename/touch/cwd/tempdir |

All math functions also available as bare names: `sin(x)` = `math.sin(x)`.

**Constants:** `PI  E  TAU  PHI  INF  NAN`  
**EE constants:** `ee.EPSILON0  ee.MU0  ee.ELECTRON  ee.BOLTZMANN  ee.PLANCK  ee.C_LIGHT`

### Array Methods
`.map(fn)` `.filter(fn)` `.reduce(fn, init)` `.push(v)` `.pop()` `.len()`  
`.reverse()` `.join(sep)` `.slice(a,b)` `.contains(v)` `.index_of(v)`

### String Methods
`.upper()` `.lower()` `.trim()` `.split(sep)` `.replace(a,b)` `.contains(s)`  
`.starts_with(s)` `.ends_with(s)` `.slice(a,b)` `.index_of(s)`

### Hash Methods
`.keys()` `.values()` `.has(k)` `.del(k)` `.len()`

### Complex Methods
`.real()` `.imag()` `.abs()` `.conj()` `.angle()`  
Native arithmetic: `z1 + z2` `z1 - z2` `z1 * z2` `z1 / z2`

### Matrix Functions
`matrix()` `mat_zeros(r,c)` `mat_identity(n)` `mat_add` `mat_sub` `mat_mul`  
`mat_scale` `mat_transpose` `mat_det` `mat_trace` `mat_get` `mat_set` `mat_shape`  
Also available as methods: `M.det()` `M.transpose()` `M.shape()` etc.

---

## Exact Decimals & COBOL-Grade Records (v0.8.0)

### Money that adds up — `dec()`

Floating point is fine for physics, not for payroll. `dec()` gives you exact
fixed-point arithmetic:

```mylang
let price = dec("19.99");
let total = price * 3;
print(total);          // 59.97
print(total / 3);      // 19.99
print(type(total));    // decimal
```

Decimals mix with integers automatically. Mixing a decimal with a float is
rejected, so a cent can never silently become `0.30000000000000004`.

### Records with PICTURE clauses

```mylang
record Employee {
    name   pic x(30);        // 30-character text field
    salary pic 9(7)v99;      // 7 integer digits + 2 decimals
    dept   pic x(10) = "SALES";
}

let e = Employee();
e.name   = "Ada Lovelace";
e.salary = dec("5400.50");

print(e.salary + dec("100.00"));   // 5500.50
print(e);                          // Employee{name: "Ada Lovelace", ...}
```

### Legacy file layouts

Records serialize to the same fixed-width character format COBOL uses, so
existing data files can be read and written directly:

```mylang
let line = e.pack();       // 30 + 9 + 10 = 49 characters
print(len(line));          // 49

let f = Employee();
f.unpack(line);
print(f.salary);           // 5400.50
```

Numeric fields are zero-padded, text fields are space-padded, and values are
truncated (not rounded) when they exceed a field's PIC — exactly COBOL's default
`MOVE` behaviour. See `MYLANG_DOCS.md` for the full PIC reference.

## COBOL-Style Statements (v0.9.0)

All statement keywords are **soft**: `let string = 5;` and `fn add(a,b)`
continue to work exactly as before. A word only becomes a verb when the
statement matches its shape.

```mylang
// evaluate — multi-value, ranges, default, or boolean arms
evaluate grade {
    when 90 thru 100 { print("A"); }
    when 80 thru 89  { print("B"); }
    when other       { print("Below B"); }
}

// perform — until / varying / N times
perform until i >= 3 { i = i + 1; }
perform varying n from 1 by 1 until n > 5 { print(n); }
perform 3 times { print("tick"); }

// arithmetic verbs — PIC rules and size errors apply
add dec("25.50") to balance;
subtract dec("10.00") from balance;
multiply qty by 7;
divide 10 by 3 giving share remainder rem;

// compute
compute invoice = dec("19.99") * 3 + dec("4.95");

// string verbs
string "Ada", " ", "Lovelace" into full;
unstring "red,green,blue" by "," into parts;
inspect text replacing "  " with "_";

// slices
print("COBOL workload"[0:5]);     // COBOL

// 88-level conditions
record Employee {
    status pic x(1);
    cond active for status == "A";
}
```

`on size error { … }` runs instead of aborting when a value does not fit the
target's PIC — the target is left untouched.

## Business File I/O (v0.9.0)

`file.*` reads and writes the sequential formats COBOL jobs produce. Writes are
atomic (temp file + rename), reads are capped at 64 MB, and encodings are
optional.

```mylang
record Employee {
    emp_no pic 9(4);
    name   pic x(20);
    gross  pic 9(7)v99;
}

file.write_records("output/payroll.dat", staff);   // one packed record per line
let rows = file.read_records("output/payroll.dat", Employee);
let one  = file.read_record("output/payroll.dat", Employee, 0);
print(file.record_count("output/payroll.dat", Employee));

file.write_lines("output/notes.txt", ["line one", "line two"]);
file.append_line("output/notes.txt", "line three");
file.write_csv("output/report.csv", [["name", "score"], ["Ada", 10]]);
```

Files with no line separators whose length is an exact multiple of the record
width are read as true fixed-width sequential files — legacy COBOL data works
as-is. See `examples/payroll.ml` and `examples/business_files.ml`.

A complete command reference (CLI, REPL, Pacer shortcuts, AI commands) is in
[`COMMANDS.md`](COMMANDS.md).

## The html.* Namespace — Rich Output Pages

Scripts can produce fully styled HTML pages as output by calling `html.*` functions.
This is completely **opt-in** — scripts that never call `html.*` behave exactly as before.

```ml
html.page("My Report");              // start a fresh page
html.heading("Results", 1);          // <h1>
html.text("Analysis complete.");     // paragraph
html.result("Final answer", 42);     // big highlighted answer box
html.kv("Runtime", "0.003s");        // label : value row
html.table(headers, rows);           // data table from arrays
html.list(["item 1", "item 2"]);     // bullet list
html.code("let x = 5;");             // monospace code block
html.raw("<div>...</div>");          // inject raw HTML (for custom grids etc.)
html.divider();                      // horizontal rule
html.render(value, "label");         // smart auto-format by type
html.show(["browser","file","panel"]);// open in browser + save file + Pacer panel
```

`html.render()` inspects the value type and picks automatically:
- **number** → result box
- **complex** → styled badge
- **matrix** → grid table
- **array** → bullet list
- **hash** → kv rows

`html.show()` targets:
- `"browser"` — opens the generated page in your default browser
- `"file"` — saves a timestamped `.html` file to `output/` in your project folder
- `"panel"` — renders inside Pacer's Visual Panel dock

---

## VS Code Extension

Copy `mylang-vscode/` into `~/.vscode/extensions/` to get:
- Syntax highlighting for `.ml` files (all keywords, builtins, namespaces)
- 36 code snippets (`fn`, `for`, `let`, `record`, `evaluate`, `perform`,
  `readrec`, `writerec`, `statsum`, `ohms`, `linreg`, `rc`, etc.)
- **F5** run button in the editor title bar
- Status bar showing `▶ Run mylang`

---

## Security

0.9.0 is a security release. Highlights:

- `crypto.encrypt_aes` / `decrypt_aes` use **authenticated** encryption
  (AES-256-GCM when `cryptography` is installed, otherwise SHA-256 CTR +
  HMAC-SHA256) with a random nonce and a `v2:` prefix.
- `http.*` accepts only `http`/`https`, rejects `user:password@` URLs, filters
  redirects, and caps responses at 10 MB.
- `image.*` validates colours and escapes SVG attributes; `html.show` writes
  owner-only, unpredictably named files.
- Pacer stores API keys in a `0600` settings file written atomically.
- The VS Code extension launches the interpreter without a shell.

Full threat model, limits, and reporting instructions:
[`SECURITY.md`](SECURITY.md).

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `ParseError` | Missing `;` or `}` | Check every statement ends with `;`; all blocks use `{}` |
| `Undefined variable` | Used before `let` | Declare with `let` before first use |
| `Index out of bounds` | Index ≥ array length | Guard with `if (i < arr.len())` |
| `RuntimeError` | Division by zero, wrong argument type, etc. | Read the message — it names the function and what was passed |
| `LexerError` | Illegal character (`@`, `#`, `$`) | mylang uses clean ASCII identifiers only |

**Common mistakes from Python background:**
```ml
// WRONG                          // RIGHT
let x = 5                         let x = 5;           // semicolons mandatory
if (x > 0) print("yes")          if (x > 0) { print("yes"); }  // braces mandatory
def add(a, b): return a + b       fn add(a, b) { return a + b; }  // fn not def
```

---

## License

MIT — do whatever you like with it.  
Copyright (c) 2026 Pacer and MyLang Contributors
