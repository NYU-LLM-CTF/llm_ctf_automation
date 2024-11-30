from .tool import Tool, ToolCall, ToolResult

# Tools
from .misc import SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool
from .run_command import RunCommandTool
from .editing import CreateFileTool
from .reversing import DisassembleTool, DecompileTool

ALLTOOLS = {RunCommandTool, SubmitFlagTool, GiveupTool, CreateFileTool,
            DelegateTool, FinishTaskTool,
            DisassembleTool, DecompileTool}
TOOLSETS = {
    "default": {RunCommandTool, CreateFileTool, SubmitFlagTool, GiveupTool},
    "planner": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
    "executor": {RunCommandTool, CreateFileTool, FinishTaskTool, DisassembleTool, DecompileTool} # TODO add other tools
}

