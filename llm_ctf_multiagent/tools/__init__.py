from .tool import ToolCall, ToolResult
from .run_command import RunCommandTool
from .reversing import DisassembleTool, DecompileTool
from .misc import SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool

ALLTOOLS = {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool, DisassembleTool, DecompileTool}
TOOLSETS = {
    "default": {RunCommandTool, SubmitFlagTool, GiveupTool},
    "planner": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
    "executor": {RunCommandTool, FinishTaskTool, DisassembleTool, DecompileTool} # TODO add other tools
}
