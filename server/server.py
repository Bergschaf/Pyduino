import json
import os.path
from json import JSONDecodeError
from lsprotocol.types import (TEXT_DOCUMENT_DID_CHANGE,
                              TEXT_DOCUMENT_DID_OPEN)
from lsprotocol.types import (Diagnostic, DidChangeTextDocumentParams,
                              DidOpenTextDocumentParams, Position, Range)
from pygls.server import LanguageServer
from server.transpiler.transpiler import Transpiler

COUNT_DOWN_START_IN_SECONDS = 10
COUNT_DOWN_SLEEP_IN_SECONDS = 1

CWD = os.getcwd().replace("\\","\\\\")
SETTINGS_JSON = """
{
    "actionButtons": {
        "reloadButton": null,
        "loadNpmCommands": false,
        "commands": [
            {
                "name": "$(triangle-right) Run Pyduino",
                "cwd": \"""" + CWD + """\",
                "command": "env/Scripts/python.exe run.py ${file}",
                "singleInstance": true,
                "focus": true
            },
            { 
                "name": "$(sync) Refresh Port",
                "cwd":  \"""" + CWD + """\",
                "command": "rm temp/port.txt",
                "singleInstance": true
            }
        ]
    },
    "files.autoSave": "onFocusChange"
}"""

class PyduinoLanguageServer(LanguageServer):

    def __init__(self, *args):
        super().__init__(*args)


pyduino_server = PyduinoLanguageServer('Pyduino', 'v0.1')


def get_diagnostics(ls, params):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    source = text_doc.source
    errors = Transpiler.get_diagnostics(source.splitlines())
    return errors


def _validate(ls, params):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    print("enter valiudate")
    diagnostics = get_diagnostics(ls, params)    
    print("diagnostics", diagnostics)

    ls.publish_diagnostics(text_doc.uri, diagnostics)



"""
@json_server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=[',']))
def completions(params: Optional[CompletionParams] = None) -> CompletionList:
    ""Returns completion items.""
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(label='"'),
            CompletionItem(label='['),
            CompletionItem(label=']'),
            CompletionItem(label='{'),
            CompletionItem(label='}'),
        ]
    )
"""


@pyduino_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@pyduino_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Pyduino activated')

    text_doc = ls.workspace.get_document(list(ls.workspace.documents.keys())[0])
    base_path = os.path.dirname(text_doc.path)
    if not os.path.exists(base_path + "\\\\.vscode"):
        os.mkdir(base_path + "\\\\.vscode")

    with open(base_path + "\\\\.vscode/settings.json", "w") as f:
        f.write(SETTINGS_JSON) # TODO keep settings

    ls.show_message('Pyduino Running')

    _validate(ls, params)