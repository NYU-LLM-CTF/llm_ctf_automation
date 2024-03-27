import tiktoken

def count_token(string: str, enc: str) -> int:
    encoding = tiktoken.get_encoding(enc)
    return len(encoding.encode(string))