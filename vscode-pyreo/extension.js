const { LanguageClient, TransportKind } = require("vscode-languageclient/node");
const vscode = require("vscode");
const fs = require("fs");
const path = require("path");

let client;
let outputChannel;

function findWorkspacePython() {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders) return null;

  const root = folders[0].uri.fsPath;
  const isWin = process.platform === "win32";
  const candidates = [
    path.join(root, ".venv", isWin ? "Scripts" : "bin", isWin ? "python.exe" : "python"),
    path.join(root, "venv", isWin ? "Scripts" : "bin", isWin ? "python.exe" : "python"),
  ];

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function resolvePython(configured) {
  if (configured) return configured;

  const venvPython = findWorkspacePython();
  if (venvPython) return venvPython;

  return process.platform === "win32" ? "python" : "python3";
}

function activate(context) {
  const config = vscode.workspace.getConfiguration("pyreo");
  const pythonPath = resolvePython(config.get("pythonPath"));
  const keywordsPath = config.get("keywordsPath");

  outputChannel = vscode.window.createOutputChannel("PyReo Language Server");
  outputChannel.appendLine(`Using Python: ${pythonPath}`);

  const args = ["-m", "pyreo.server"];
  if (keywordsPath) {
    args.push("--keywords", keywordsPath);
    outputChannel.appendLine(`Using keywords: ${keywordsPath}`);
  }

  const serverOptions = {
    command: pythonPath,
    args,
    transport: TransportKind.stdio,
  };

  const clientOptions = {
    documentSelector: [{ scheme: "file", language: "pyreo" }],
    outputChannel,
  };

  client = new LanguageClient(
    "pyreo",
    "PyReo Language Server",
    serverOptions,
    clientOptions
  );

  client.start().catch((err) => {
    const msg = `PyReo language server failed to start: ${err.message}`;
    outputChannel.appendLine(msg);
    vscode.window
      .showErrorMessage(msg, "Open Output", "Install Guide")
      .then((choice) => {
        if (choice === "Open Output") outputChannel.show();
        if (choice === "Install Guide") {
          vscode.env.openExternal(
            vscode.Uri.parse("https://github.com/b-j-karl/pyreo#quickstart")
          );
        }
      });
  });
}

function deactivate() {
  if (outputChannel) outputChannel.dispose();
  if (client) return client.stop();
}

module.exports = { activate, deactivate };
