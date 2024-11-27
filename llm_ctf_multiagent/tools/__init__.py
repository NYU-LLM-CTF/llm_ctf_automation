from .tool import ToolCall, ToolResult
from .run_command import RunCommandTool
from .misc import SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool

ALLTOOLS = {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool, FinishTaskTool}
TOOLSETS = {
    "default": {RunCommandTool, SubmitFlagTool, GiveupTool},
    "planner": {RunCommandTool, SubmitFlagTool, GiveupTool, DelegateTool},
    "executor": {RunCommandTool, FinishTaskTool} # TODO add other tools
}
