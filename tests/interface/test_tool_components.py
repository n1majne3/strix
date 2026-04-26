import pytest
from rich.text import Text

from strix.interface.tool_components.browser_renderer import BrowserRenderer
from strix.interface.tool_components.file_edit_renderer import StrReplaceEditorRenderer, ListFilesRenderer, SearchFilesRenderer
from strix.interface.tool_components.terminal_renderer import TerminalRenderer

def test_browser_renderer_partial_args():
    # Empty args
    BrowserRenderer.render({"args": {}})
    
    # Partial action
    BrowserRenderer.render({"args": {"action": None}})
    
    # Partial keys
    BrowserRenderer.render({"args": {"action": "type", "text": None}})
    BrowserRenderer.render({"args": {"action": "execute_js", "js_code": None}})
    BrowserRenderer.render({"args": {"action": "launch", "url": None}})
    
def test_file_edit_renderer_partial_args():
    # Empty args
    StrReplaceEditorRenderer.render({"args": {}})
    
    # Partial keys
    StrReplaceEditorRenderer.render({"args": {"command": None, "path": None, "old_str": None, "new_str": None, "file_text": None}})
    StrReplaceEditorRenderer.render({"args": {"command": "str_replace", "path": "test.py", "old_str": None, "new_str": None}})

def test_terminal_renderer_partial_args():
    # Empty args
    TerminalRenderer.render({"args": {}})
    
    # Partial command
    TerminalRenderer.render({"args": {"command": None, "is_input": None}})

def test_list_files_renderer_partial_args():
    ListFilesRenderer.render({"args": {}})
    ListFilesRenderer.render({"args": {"path": None}})

def test_search_files_renderer_partial_args():
    SearchFilesRenderer.render({"args": {}})
    SearchFilesRenderer.render({"args": {"path": None, "regex": None}})
