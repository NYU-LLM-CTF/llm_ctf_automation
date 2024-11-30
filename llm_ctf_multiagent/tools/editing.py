import subprocess
import tempfile
from pathlib import Path

from .tool import Tool

class CreateFileTool(Tool):
    NAME = "create_file"
    DESCRIPTION = "Create a file in the container environment with the given contents. You may overwrite existing files with this tool. Relative paths will be taken from the home directory."
    PARAMETERS = {
        "path": ("string", "the full path of the file to create"),
        "contents": ("string", "the file contents"),
    }
    REQUIRED_PARAMETERS = {"path", "contents"}

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    def call(self, path=None, contents=None):
        if path is None or contents is None:
            return {"error": "Path or contents not provided!"}
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(contents.encode("utf-8"))
        tmpf.close()
        created = self.environment.copy_into_container(tmpf.name, path)
        return {"success": True, "path": str(created)}

    def format_tool_call(self, tool_call):
        return f"**{self.NAME}**: `{tool_call.parsed_arguments['path']}`\n```\n{tool_call.parsed_arguments['contents']}\n```\n"

    def format_result(self, tool_result):
        if "error" in tool_result.result:
            return f"**{self.NAME}**: {tool_result.result['error']}" 
        else:
            return f"**{self.NAME}**: successfully created file!" 
