# Changelog

All notable changes to **Pacer** and **mylang** are recorded here.
The project uses a simple `major.minor.patch` scheme; the format follows
[Keep a Changelog](https://keepachangelog.com/).

---

## [0.9.0] — 2026-11-13 — "COBOL Workload Edition"

Phase 2 (COBOL-style statements) and Phase 3 (business file I/O), plus a
security pass over crypto, networking, SVG/HTML output, the editor, and the
VS Code extension.

### Added — Phase 2: COBOL-style statements

All statement verbs are **soft keywords**: they remain valid identifiers and
function names outside the matching statement shape, so 0.8.0 code keeps
working.

- `evaluate` — subject form with `when a, b`, `when low thru high`, and
  `when other`; boolean form with `evaluate { when cond { } }`.
- `perform until`, `perform varying v from a by b until cond`, and
  `perform n times`.
- Arithmetic verbs: `add a to b`, `subtract a from b`, `multiply a by b`,
  `divide a by b [giving c] [remainder r]`, each with optional
  `on size error { }`.
- `compute target = expr [on size error { }]`.
- `string a, b into target`, `unstring s by delim into target`,
  `inspect s replacing old with new`, `inspect s tallying needle giving n`.
- Python-style slices on strings, arrays, and packed records:
  `s[a:b]`, `s[a:]`, `s[:b]`, negative indices.
- 88-level record conditions: `cond active for status == "A";` — read-only
  pseudo-fields evaluated live against the record's fields.
- New `SizeError` runtime error type, and per-statement `on size error`
  handling that leaves the target unchanged.
- Runaway-loop protection: `perform` is limited to 10,000,000 iterations;
  `range()` is limited to 10,000,000 elements; a zero `by` step is rejected.
- `--ast` output covers every new node, including record conditions.

### Added — Phase 3: Business file I/O

- `file.read_lines`, `file.write_lines`, `file.append_line`.
- `file.read_records`, `file.write_records`, `file.append_record`,
  `file.read_record`, `file.record_count`.
  - One packed record per line, or a true fixed-width sequential file with no
    separators (auto-detected when the length is an exact multiple of the
    record width).
  - Accepts a single record or an array for writes.
- `file.read_csv`, `file.write_csv`.
- `file.size`, `file.rename`, `file.touch`, `file.cwd`, `file.tempdir`.
- Optional text encodings on `read`, `write`, `append`, `read_lines`,
  `read_records`, and `read_csv`; names validated with `codecs.lookup`.
- Atomic writes (temp file + `os.replace`) and a 64 MB read cap.
- Path validation: non-empty strings, no NUL bytes, clear errors.

### Added — docs and tooling

- `COMMANDS.md` — CLI, REPL, Pacer shortcuts/menus, AI commands, statement and
  namespace reference, settings paths, and the error table.
- `SECURITY.md`, `CHANGELOG.md`, `RELEASE_NOTES.md`, `SHA256SUMS.txt`.
- Three runnable examples: `cobol_statements.ml`, `payroll.ml`,
  `business_files.ml`.
- Playground examples for COBOL statements and record conditions.
- VS Code grammar and snippets for the new statements.
- Pacer highlighter, completion, built-ins help, and About version updated.

### Security

- `crypto.encrypt_aes` replaced repeating-key XOR with authenticated
  AES-256-GCM (when `cryptography` is installed) or SHA-256 CTR +
  HMAC-SHA256, random nonce, `v2:` format; legacy hex decrypt remains.
- `crypto.secure_store` now uses authenticated encryption and constant-time
  tag comparison.
- `crypto.pbkdf2` iteration count capped at 10,000,000.
- `image.*` validates colours and escapes SVG attributes; `image.load`
  restricts URL schemes.
- `html.show` uses `mkstemp` (unpredictable names, `0600`) and `Path.as_uri()`.
- `http.*` restricts schemes, rejects embedded credentials, filters redirects
  (including HTTPS→HTTP downgrade), caps bodies at 10 MB, and rejects header
  injection.
- Pacer writes settings atomically with `0600` and tightens old files; browser
  launch uses `Path.as_uri()`.
- VS Code extension launches with `spawn(..., {shell:false})` instead of
  `terminal.sendText()`, removing command injection via file names.

### Changed

- Version bumped to 0.9.0 in the CLI, package metadata, editor, installer,
  playground, and VS Code extension.
- Test suite expanded from 148 to 215 tests.
- `dec()` scale is preserved through decimal arithmetic and `perform varying`
  (e.g. `2.0`, not `2`).

### Fixed

- `multiply price by 4` now targets `price` when the second operand is a
  literal (previously raised "needs a variable target").
- Optional trailing `;` after `on size error { }` blocks is accepted.
- `range()` rejects a zero step and oversized ranges with clear messages.
- `inspect … tallying` requires `giving` and reports the missing target.
- Record condition names may no longer collide with field names.

---

## [0.8.0] — "COBOL Workload Edition"

- `dec()` exact fixed-point decimals (int mixing, float rejection, explicit
  rounding/truncation methods).
- `record` declarations with PIC clauses (`x`, `a`, `9`, `s9`, `v`, `.`),
  default values, `pack()`, `unpack()`, `fields()`.
- Size errors on PIC overflow; truncation toward zero on assignment.
- Editor `RunWorker` on a background thread with a working **Stop** button.
- UTF-8-safe test output; expression callees; restored lost handlers.
- Documentation, examples, playground, and VS Code grammar for records and
  decimals.

## [0.7.0]

- `json.*`, `http.*`, `time.*`, `crypto.*`, `image.*`, `chart.*`, `html.*`
  namespaces.
- `chart.show()` and `html.show()` visual output in Pacer's panels/browser.
- Complex arithmetic, matrices, statistics, and EE libraries expanded.

## [0.6.0]

- Backtick template literals, `import`, `try`, `catch`, `throw`.
- Complex `j` literals and native complex arithmetic.
- First run of the Pacer editor and the browser playground.

## [0.5.0] and earlier

- Core language: `let`, `fn`, `if`, `while`, `for`, arrays, hashes, strings,
  math/statistics/EE built-ins, CLI, REPL, and the first Pacer prototype.
