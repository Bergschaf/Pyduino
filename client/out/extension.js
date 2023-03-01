/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: // www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------- */
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const net = require("net");
const path = require("path");
const vscode_1 = require("vscode");
const node_1 = require("vscode-languageclient/node");
const fs = require("fs");
const child_process_1 = require("child_process");
let client;
function getClientOptions() {
    return {
        documentSelector: [
            { scheme: "file", language: "pyduino" },
            { scheme: "untitled", language: "pyduino" },
        ],
        outputChannelName: "[pygls] PyduinoLanguageServer",
        synchronize: {
            // Notify the server about file changes to '.clientrc files contain in the workspace
            fileEvents: vscode_1.workspace.createFileSystemWatcher("**/.clientrc"),
        },
    };
}
function startLangServerTCP(addr) {
    const serverOptions = () => {
        return new Promise((resolve /*, reject */) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(addr, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };
    return new node_1.LanguageClient(`tcp lang server (port ${addr})`, serverOptions, getClientOptions());
}
function startLangServer(command, args, cwd) {
    const serverOptions = {
        args,
        command,
        options: { cwd },
    };
    return new node_1.LanguageClient(command, serverOptions, getClientOptions());
}
function activate(context) {
    if (false) { //if (context.extensionMode === ExtensionMode.Development) {
        // Development - Run the server manually
        client = startLangServerTCP(2087);
        console.log("Development mode");
        context.subscriptions.push(client.start());
    }
    else {
        const cwd = path.join(__dirname, "..", "..");
        const pythonPath = "env/Scripts/python.exe";
        (0, child_process_1.exec)("where python", (error, stdout, stderr) => {
            if (error) {
                console.log(`error: ${error.message}`);
                return;
            }
            if (stderr) {
                console.log(`stderr: ${stderr}`);
            }
            console.log(`stdout: ${stdout}`);
            const interpreter = stdout.split("\n")[0];
            // remove the python.exe from the path
            const cfg = "home = " + interpreter.substring(0, interpreter.length - 12) + "\ninclude-system-site-packages = false";
            fs.writeFileSync(path.join(cwd, "env/pyvenv.cfg"), cfg);
            client = startLangServer(pythonPath, ["-m", "server"], cwd);
            context.subscriptions.push(client.start());
        });
    }
}
exports.activate = activate;
function deactivate() {
    return client ? client.stop() : Promise.resolve();
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map