from .modules import Tool, CTFCategories, ALL
from .tools import *

# Tools for the model to use when solving CTF challenges.
# A few notes for adding new tools:
# - Each tool must be a subclass of Tool, and implement the __call__ method.
# - Each tool must include:
#     - A NAME field with the tool name.
#     - Type hints in the __call__ method with the parameters described using
#       an Annotated type
#     - The return type should NOT be annotated; the schemas used by OpenAI
#       don't describe the return type, so it's not necessary and the schema
#       generator will raise an error if you try to annotate it.
#     - A docstring for __call__ giving the overall description of the tool
#   These are used to automatically generate the schema for the tool.
# - Backends usually do some validation of the parameters provided by the model
#   before invoking the tool, but you should still be prepared to handle invalid
#   input in the __call__ method and return a nice error message.
# - Return values should be a JSON-serializable dictionary; if an error occurs,
#   then the only key should be "error" and the value should be a string.

# Predefined sets of tools for different categories; this is
# generated automatically based on the CATEGORIES attribute of each tool
DEFAULT_TOOLSET = Tool.__subclasses__()
TOOLSETS = {
    cat : [ t for t in DEFAULT_TOOLSET if t.CATEGORIES is ALL or cat in t.CATEGORIES ]
    for cat in CTFCategories
}
TOOLSETS["default"] = DEFAULT_TOOLSET
