#!/usr/bin/env python3
from .tool_modules import *
from .general_set import *
from .crypto_set import *
from .pwn_set import *
from .for_set import *
from .web_set import *
from .rev_set import *

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


# class WebSearch(Tool):
#     NAME = "web_search"
#     def __init__(self, challenge: "CTFChallenge"):
#         super().__init__()
#         self.challenge = challenge

#     def _get_webs(self, query, number=3, pause=2):
#         return [j for j in search(query=query, num=number, stop=number, pause=2)]

#     def search_web(self, query, number=3, pause=2, timeout=30):
#         web_contents = []
#         urls = self._get_webs(query, number, pause)
#         for i in urls:
#             web_body = self._parse_web(i, timeout)
#             if web_body:
#                 web_contents.append(web_contents)
#         return urls, web_contents

#     def _parse_web(self, url, timeout=30):
#         try:
#             res = requests.get(url, timeout=timeout)
#             soup  = bs4.BeautifulSoup(res.text, 'html.parser')
#             elems = re.sub(r'\n\n+', '\n', soup.find('body').get_text())
#             if elems:
#                 return elems
#             else:
#                 status.debug_message(f"No main body in {url}")
#                 return
#         except requests.exceptions.Timeout:
#             print(f"Timeout on {url}, skipping")
#             return

#     def __call__(self, query, number=3, pause=2, timeout=30):
#         urls, webs = self.search_web(query, number, pause, timeout)
#         return {"url": "\n".join(urls), "contents": "\n".join(webs)}


# Predefined sets of tools for different categories; this is
# generated automatically based on the CATEGORIES attribute of each tool
DEFAULT_TOOLSET = Tool.__subclasses__()
print(DEFAULT_TOOLSET)
categories = { "rev", "pwn", "crypto", "misc", "forensics", "web" }
TOOLSETS = {
    cat : [ t for t in DEFAULT_TOOLSET if t.CATEGORIES is ALL or cat in t.CATEGORIES ]
    for cat in CTFCategories
}
# print(TOOLSETS)
TOOLSETS["default"] = DEFAULT_TOOLSET

# if __name__ == "__main__":
    # import sys
    # from argparse import Namespace
    # from llm_ctf_solve import CTFChallenge
    # dis = Disassemble(
    #     CTFChallenge(Path(sys.argv[1]), Namespace(container_image="ubuntu:20.04"))
    # )
    # dis.disassemble(sys.argv[2], 'main')
    # print('\n'.join(dis._disasm_cache[sys.argv[2]].keys()))

    # dc = Decompile(
    #     CTFChallenge(Path(sys.argv[1]), Namespace(container_image="ubuntu:20.04"))
    # )
    # dc.decompile(sys.argv[2], 'main')
    # print('\n'.join(dc._decomp_cache[sys.argv[2]].keys()))
