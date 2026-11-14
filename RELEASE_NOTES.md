# mylang 0.9.0 — Release Notes

**COBOL Workload Edition — Phase 2 & Phase 3 complete**

mylang 0.9.0 turns the language into a practical business-programming
workload: COBOL-style statements, 88-level conditions, and fixed-width
business file I/O, all inside the Pacer editor. Everything is additive and
soft-keyword based — **your 0.8.0 programs run unchanged**.

---

## Highlights

### COBOL statements, the mylang way

```mylang
evaluate grade {
    when 90 thru 100 { print("A"); }
    when 80 thru 89  { print("B"); }
    when other       { print("Below B"); }
}

perform varying i from 1 by 1 until i > 10 {
    print(i);
}

add dec("25.50") to balance;
divide 10 by 3 giving share remainder rem;
compute invoice = dec("19.99") * 3 + dec("4.95");

string "Ada", " ", "Lovelace" into full;
unstring "red,green,blue" by "," into parts;
inspect text replacing "  " with "_";
```

The verbs are *soft* keywords. `let string = 5;`, `fn add(a, b)`, and
`perform(9)` keep working exactly as before. Mix statement style and
expression style freely.

### 88-level conditions

```mylang
record Employee {
    status pic x(1);
    cond active for status == "A";
}

let e = Employee();
e.status = "A";
print(e.active);     // true — evaluated live
```

Read-only pseudo-fields, always current, no refresh call.

### Business file I/O

```mylang
file.write_records("output/payroll.dat", staff);
let rows = file.read_records("output/payroll.dat", Employee);
print(file.record_count("output/payroll.dat", Employee));

file.write_lines("output/notes.txt", ["one", "two"]);
file.append_line("output/notes.txt", "three");
file.write_csv("output/report.csv", rows);
```

- One packed record per line, or true fixed-width sequential files with no
  separators — auto-detected by record width.
- Atomic writes (temp file + rename), 64 MB read cap, optional encodings.
- Same fixed-width layout COBOL jobs produce, so legacy data works directly.

### Slices

```mylang
"COBOL workload"[0:5]      // COBOL
[10, 20, 30, 40][1:3]      // [20, 30]
record.pack()[-7:]         // last 7 characters
```

---

## Security

0.9.0 closes nine concrete issues; see [`SECURITY.md`](SECURITY.md) for the
full write-up.

| Area | Before | Now |
|---|---|---|
| `crypto.encrypt_aes` | repeating-key XOR, no nonce, no auth | AES-256-GCM or SHA-256 CTR + HMAC, random nonce, `v2:` format |
| `crypto.secure_store` | XOR vault | authenticated encryption, constant-time check |
| `crypto.pbkdf2` | unbounded work factor | capped at 10,000,000 |
| `image.*` | SVG attribute injection via colours | strict colour validation, escaped attributes |
| `image.load` | any URL scheme | `http(s)` and `data:image/` only |
| `html.show` | predictable temp files | `mkstemp`, `0600`, `Path.as_uri()` |
| `http.*` | arbitrary redirects, unbounded bodies | scheme/credential checks, redirect filter, 10 MB cap |
| Pacer settings | plaintext keys in a world-readable file | atomic write + `0600` |
| VS Code run | `terminal.sendText` command injection | `spawn(..., {shell:false})` |

Legacy `decrypt_aes` hex values still decrypt for migration, but are not
authenticated — re-encrypt them to `v2:` when convenient.

---

## Documentation

- **[`MYLANG_DOCS.md`](MYLANG_DOCS.md)** — new sections 17 (COBOL statements)
  and 18 (business file I/O); TOC and quick reference updated.
- **[`COMMANDS.md`](COMMANDS.md)** — new: CLI, REPL, every Pacer shortcut and
  menu, AI commands, statement grammar, namespaces, settings paths, error table.
- **`README.md`** — 0.9.0 overview, examples, file layout.
- **VS Code extension** — grammar and 12 new snippets.
- **Playground** — new COBOL Statements and Record Conditions examples.

---

## New example programs

| File | Shows |
|---|---|
| `examples/cobol_statements.ml` | every new statement, slices, conditions |
| `examples/payroll.ml` | fixed-record payroll with `evaluate`/`perform`/`compute` |
| `examples/business_files.ml` | records, line files, CSV, housekeeping |

Run them in Pacer with **F5**:

```bash
python mylang/main.py mylang/examples/payroll.ml
```

---

## Compatibility

| Item | Status |
|---|---|
| 0.8.0 `.ml` programs | ✅ unchanged behaviour |
| Identifiers named `add`, `string`, `perform`, `evaluate`, `compute`, `inspect` | ✅ still valid |
| `decrypt_aes` on 0.8.x hex values | ✅ still decrypts (unauthenticated legacy path) |
| `record` keyword | unchanged (hard keyword since 0.8.0) |
| Test suite | **215/215 passing** |

---

## Upgrading

1. Replace the old folder with the 0.9.0 archive.
2. Re-run `install.bat` (Windows) or `install.sh` (Unix) to pick up the new
   optional `cryptography` dependency.
3. Optional: `pip install cryptography` for hardware-accelerated AES-GCM.
   Without it, mylang uses its built-in authenticated CTR+HMAC fallback.
4. Open Pacer and press **F5** on `examples/payroll.ml` to verify the install.

---

## Known limitations

- A COBOL **source transpiler** is not part of 0.9.0; it is planned for 1.0.0.
- `html.raw()` inserts markup verbatim by design — never pass untrusted input.
- `file.*` is not sandboxed; run only trusted scripts.
- The settings file is protected by OS permissions, not a master password.

---

## Thanks

Built and tested on Windows with Python 3.13 and PyQt5 5.15.11. The test suite
covers the language engine, the new statement family, business file I/O, and
the security hardening described above.

MIT licensed — see `README.md`.
