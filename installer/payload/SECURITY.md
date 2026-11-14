# Security Policy — Pacer + mylang 0.9.0

## Supported versions

| Version | Supported |
|---|---|
| 0.9.x | ✅ current |
| 0.8.x and earlier | ❌ upgrade — 0.9.0 contains security fixes |

## Reporting a vulnerability

Open a private security advisory on the project repository, or contact the
maintainers directly. Please include:

- the mylang/Pacer version (`mylang --version`),
- the smallest `.ml` program or UI action that reproduces the issue,
- the platform and Python version,
- what an attacker gains (read? write? code execution?).

Do not publish a working exploit before a fix is available. We aim to
acknowledge reports within 5 working days.

---

## Threat model

mylang is a **local scripting language**. Running a `.ml` file is equivalent to
running a Python script: the program can read and write files the user can
access and can make outbound HTTP requests. Do not run untrusted `.ml` files.

The hardening in 0.9.0 focuses on:

1. **Input from a program must not become code or markup.**
2. **Ciphertext must be authenticated** (no silent tampering).
3. **Network access must not be redirected into local files or plaintext.**
4. **Generated files and settings must not be world-readable or predictable.**
5. **The editor must not interpolate file names into shell commands.**

---

## What 0.9.0 fixed

### 1. `crypto.encrypt_aes` was repeating-key XOR

**Before:** `encrypt_aes` hashed the key and XORed it across the plaintext,
returning hex. There was no nonce, no authentication, and identical plaintexts
produced identical ciphertexts. An attacker could flip bits undetected.

**Now:** authenticated encryption with a random per-message nonce and a
versioned format:

```
v2:<base64( mode || nonce || ciphertext || tag )>
```

| Mode byte | Construction |
|---|---|
| `0x01` | AES-256-GCM (used when the `cryptography` package is installed) |
| `0x02` | SHA-256 counter-mode keystream + HMAC-SHA256 tag (always available) |

Decryption verifies the tag with `hmac.compare_digest` and raises on a wrong
key, a modified ciphertext, or a truncated payload. Old 0.8.x hex values are
still accepted for migration, but are **not** authenticated — re-encrypt stored
values at the first opportunity.

`crypto.secure_store` / `secure_retrieve` use the same authenticated
construction with a fresh process-lifetime key, so a vault entry cannot be
silently altered.

### 2. `crypto.pbkdf2` accepted unbounded iterations

A program could pass `10**12` and pin a CPU core for hours (denial of service).
Iterations are now limited to **10,000,000** and must be ≥ 1.

### 3. `image.*` interpolated unescaped colours into SVG

A colour such as `red" onclick="alert(1)` produced attacker-controlled SVG
attributes. Colours are now validated against a strict grammar (`#rgb`,
`#rrggbb`, `#rrggbbaa`, `rgb(...)`/`rgba(...)`, or a CSS colour name) and
rejected otherwise. Text is attribute-escaped, and `image.load` accepts only
`http://`, `https://`, and `data:image/` URLs.

### 4. `html.show` wrote predictable files

Rendered pages used a timestamp-only name in a shared directory, so another
local user could pre-create or read them. Pages are now created with
`tempfile.mkstemp` (unpredictable name, `0600` permissions) and opened through
`Path.as_uri()`.

### 5. `http.*` followed arbitrary redirects and buffered arbitrary bodies

- Only `http://` and `https://` URLs are accepted.
- URLs containing `user:password@` are rejected, so credentials cannot be
  smuggled into a request or a log.
- Redirects are filtered: non-HTTP schemes are refused and an HTTPS request may
  never be downgraded to HTTP.
- Responses are capped at **10 MB**; header names/values containing CR, LF, or
  NUL are rejected.
- Error bodies are capped by the same limit.

### 6. Pacer stored API keys in a world-readable settings file

`~/.pacer_settings.json` is now written atomically with `0600` permissions
(existing files are tightened on load). The file is never printed in the output
panel, and AI error messages do not echo keys.

### 7. Pacer built `file://` URLs by string concatenation

`webbrowser.open("file://" + path)` mishandles spaces, `#`, `?`, and non-ASCII
paths and can point at the wrong file. It now uses
`Path(path).resolve().as_uri()`.

### 8. VS Code extension interpolated the file path into a shell command

The old run command used `terminal.sendText()` with a quoted file path. A file
name containing shell metacharacters could execute arbitrary commands. The
extension now:

- resolves the `mylang` CLI or a Python interpreter with `spawnSync` probe
  calls that never use user-controlled arguments,
- launches with `child_process.spawn(..., { shell: false })`,
- refuses `.cmd`/`.bat` shims that would require a shell,
- writes output to a dedicated Output channel.

### 9. File I/O hardening

- Paths must be non-empty strings with no NUL byte.
- Reads are capped at **64 MB**.
- Writes are atomic (temp file + `os.replace`) except appends.
- Encoding names are validated with `codecs.lookup`.
- Generated record/line/CSV files obey the same rules.

### 10. Runaway program limits

- `range()` may not create more than **10,000,000** elements.
- `perform` loops stop at **10,000,000** iterations.
- Recursion remains bounded by Python's configured limit with a clean error.

---

## Known limitations

| Area | Note |
|---|---|
| `html.raw(...)` | Inserts markup verbatim **by design**. Never pass untrusted input without escaping it. |
| Legacy `decrypt_aes` hex values | Accepted for compatibility; not authenticated. Re-encrypt to `v2:`. |
| `file.*` sandbox | There is no sandbox: a program can touch any file the user can. Run only trusted scripts. |
| `http.*` | No certificate pinning and no proxy hardening beyond Python's defaults. TLS verification is on by default. |
| Settings file | Protected by OS file permissions, not a master password. A process running as the same user can read it. |
| Playground | Runs entirely in the browser via Pyodide; it has no filesystem access to your real machine. |

---

## Dependency notes

| Package | Needed for | Security note |
|---|---|---|
| `PyQt5` | Pacer editor | Pin the tested version in `requirements.txt`. |
| `anthropic` | Claude AI provider | Optional; keys come from settings or env. |
| `openai` | OpenAI / Groq / OpenRouter | Optional. |
| `google-generativeai` | Gemini | Optional. |
| `cryptography` | AES-256-GCM in `crypto.encrypt_aes` | Optional; a built-in authenticated fallback is used when absent. |
| `pyinstaller` | Building `Pacer.exe` | Build-time only. |

Install from a trusted index, and prefer a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```
