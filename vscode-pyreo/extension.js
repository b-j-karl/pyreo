const { LanguageClient, TransportKind } = require("vscode-languageclient/node");
const vscode = require("vscode");

let client;

function activate(context) {
  const config = vscode.workspace.getConfiguration("pyreo");
  const pythonPath = config.get("pythonPath") || "python";

  const serverOptions = {
    command: pythonPath,
    args: ["-m", "pyreo.server"],
    transport: TransportKind.stdio,
  };

  const clientOptions = {
    documentSelector: [{ scheme: "file", language: "pyreo" }],
  };

  client = new LanguageClient(
    "pyreo",
    "PyReo Language Server",
    serverOptions,
    clientOptions
  );

  client.start();
}

function deactivate() {
  if (client) {
    return client.stop();
  }
}

module.exports = { activate, deactivate };
