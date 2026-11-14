const vscode = require("vscode");
const path   = require("path");
const fs     = require("fs");
const cp     = require("child_process");

let output = null;
let running = null;

function getOutput() {
    if (!output) {
        output = vscode.window.createOutputChannel("mylang");
    }
    return output;
}

/** Locate the mylang CLI or a Python interpreter, without invoking a shell. */
function findRunner(filePath) {
    const isWin = process.platform === "win32";

    // 1. A directly executable `mylang` CLI (never a .cmd/.bat shim — those
    //    would require a shell, and a crafted path could inject commands).
    const locator = isWin ? "where" : "which";
    try {
        const probe = cp.spawnSync(locator, ["mylang"], {
            shell: false, encoding: "utf8", timeout: 5000
        });
        if (probe.status === 0 && probe.stdout) {
            const candidate = probe.stdout.split(/\r?\n/)[0].trim();
            const spawnable = isWin
                ? /\.(exe|com)$/i.test(candidate)
                : candidate.length > 0;
            if (spawnable && fs.existsSync(candidate)) {
                return { command: candidate, prefix: [] };
            }
        }
    } catch (_) { /* ignore and fall through */ }

    // 2. Python + the bundled engine, resolved from the .ml file location.
    const engines = [
        path.resolve(path.dirname(filePath), "..", "mylang", "main.py"),
        vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0]
            ? path.join(vscode.workspace.workspaceFolders[0].uri.fsPath,
                        "mylang", "main.py")
            : null
    ].filter(p => p && fs.existsSync(p));

    if (engines.length === 0) {
        return null;
    }

    const pythons = isWin ? ["python", "py"] : ["python3", "python"];
    for (const py of pythons) {
        try {
            const probe = cp.spawnSync(py, ["--version"], {
                shell: false, encoding: "utf8", timeout: 5000
            });
            if (probe.status === 0) {
                return { command: py, prefix: [engines[0]] };
            }
        } catch (_) { /* try the next interpreter */ }
    }
    return null;
}

function runFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage("mylang: No active file to run.");
        return;
    }
    const filePath = editor.document.fileName;
    if (!filePath.toLowerCase().endsWith(".ml")) {
        vscode.window.showErrorMessage("mylang: Not a .ml file.");
        return;
    }

    if (running) {
        running.kill();
        running = null;
    }

    editor.document.save().then(() => {
        const runner = findRunner(filePath);
        const channel = getOutput();
        channel.show(true);

        if (!runner) {
            channel.appendLine(
                "mylang: could not find the mylang CLI or a Python interpreter.\n" +
                "Install the CLI (pip install -e ./mylang) or make sure `python` " +
                "is on PATH and the mylang/ folder sits next to your project.");
            vscode.window.showErrorMessage(
                "mylang: no runner found (CLI or Python). See the Output panel.");
            return;
        }

        channel.appendLine(`\n▶ ${path.basename(filePath)}`);
        const args = [...runner.prefix, filePath];
        const child = cp.spawn(runner.command, args, {
            cwd: path.dirname(filePath),
            shell: false,
            windowsHide: true
        });
        running = child;

        child.stdout.on("data", d => channel.append(d.toString()));
        child.stderr.on("data", d => channel.append(d.toString()));
        child.on("error", err => {
            channel.appendLine(`mylang: failed to start ${runner.command}: ${err.message}`);
            running = null;
        });
        child.on("close", code => {
            channel.appendLine(code === 0
                ? "─ finished"
                : `─ exited with code ${code}`);
            running = null;
        });
    });
}

function activate(context) {
    const run = vscode.commands.registerCommand("mylang.runFile", runFile);

    context.subscriptions.push(run, getOutput());

    // Status bar item showing language
    const statusItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left, 100);
    statusItem.command = "mylang.runFile";

    const updateStatus = (editor) => {
        if (editor && editor.document.fileName.toLowerCase().endsWith(".ml")) {
            statusItem.text = "$(play) Run mylang";
            statusItem.tooltip = "Run this .ml file (F5)";
            statusItem.show();
        } else {
            statusItem.hide();
        }
    };

    vscode.window.onDidChangeActiveTextEditor(updateStatus, null, context.subscriptions);
    updateStatus(vscode.window.activeTextEditor);
    context.subscriptions.push(statusItem);
}

function deactivate() {
    if (running) {
        running.kill();
        running = null;
    }
}

module.exports = { activate, deactivate };
