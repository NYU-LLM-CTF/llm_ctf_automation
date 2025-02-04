from functools import partial
from typing import Any, Callable, List, Literal, Tuple, Optional, NamedTuple, Union
from ..ctflogging import status
import re
from rich.syntax import Syntax
import re
import json
from pathlib import Path
import os
import backoff

PythonSyntax = partial(Syntax, lexer="python", theme=status.THEME, line_numbers=False)

# Mixtral has an unfortunate habit of escaping underscores in its
# XML tag names. Fix that here:
XML_TAG_REGEX = re.compile(r'<[^>]*?>')
def fix_xml_tag_names(s : str) -> str:
    # Process each XML tag separately to handle multiple escaped underscores
    def unescape_underscores(match : re.Match):
        # Replace all escaped underscores within the tag
        return match.group(0).replace(r'\_', '_')
    # Find all XML tags and apply the unescape function
    return XML_TAG_REGEX.sub(unescape_underscores, s)

def parse_models(model_info=None):
    if not model_info:
        model_info = Path(__file__).resolve().parent / "model_info.json"
    with open(model_info, 'r') as m:
        data = json.load(m)
    return data

def parse_keys(key_path=None):
    file_path = Path(__file__).resolve()
    keys = {}
    if not key_path:
        key_path = file_path.parent.parent.parent / "keys.cfg"
    try:
        with open(key_path, 'r') as k:
            for line in k:
                line = line.split(":")
                keys[line[0].strip()] = line[1].strip()
        return keys
    except FileExistsError:
        return None

def fix_xml_seqs(seqs : List[str]) -> List[str]:
    return list(set(seqs +[fix_xml_tag_names(seq) for seq in seqs]))

class ModelQuirks(NamedTuple):
    """Model-specific quirks for the VLLM backend."""
    # Whether the model supports system messages
    supports_system_messages: bool
    # Whether the model needs tool use demonstrations (most do)
    needs_tool_use_demonstrations: bool = True
    # Function to run to clean up the model's content output
    clean_content: Optional[Callable[[str], str]] = None
    # Function to run to clean up the model's tool output
    clean_tool_use: Optional[Callable[[str], str]] = None
    # Function to run to augment the stop sequences from the formatter
    augment_stop_sequences: Optional[Callable[[List[str]], List[str]]] = None
    # Function to run to augment the start sequences from the formatter
    augment_start_sequences: Optional[Callable[[List[str]], List[str]]] = None

NO_QUIRKS = ModelQuirks(supports_system_messages=True)
KEYS = parse_keys()
MODEL_INFO = parse_models()
