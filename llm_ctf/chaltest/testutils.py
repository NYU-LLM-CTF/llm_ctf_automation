from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
import pyte
import struct
import tarfile
import stat
from datetime import datetime
from rich.text import Text

def is_hex_color(s):
    if len(s) != 6:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def char_to_richtext(char : pyte.screens.Char):
    style_map = {
        'italics': 'italic',
        'underscore': 'underline',
        'strikethrough': 'strike',
    }
    fg = char.fg if not is_hex_color(char.fg) else f'#{char.fg}'
    bg = char.bg if not is_hex_color(char.bg) else f'#{char.bg}'
    styles_set = [ style_map.get(s,s) for s in char._fields if getattr(char, s) == True ]
    style = f'{fg} on {bg}'
    if styles_set:
        style += ' ' + ' '.join(styles_set)
    return Text(char.data, style=style)

def screen_to_richtext(screen : pyte.Screen):
    for i in range(screen.lines):
        line = Text()
        for j in range(screen.columns):
            line.append(char_to_richtext(screen.buffer[i][j]))
        yield line

# See https://docs.docker.com/engine/api/v1.39/#tag/Container/operation/ContainerAttach
def docker_stream_decode(stream, want=None):
    out = b''
    while stream:
        kind, _, _, _, dlen = struct.unpack(">bbbbI", stream[:8])
        if want is None or want == kind:
            out += stream[8:+8+dlen]
        stream = stream[8+dlen:]
    return out

def modestr(m : tarfile.TarInfo):
    # Convert the tar type to a stat mode
    mode = m.mode
    if m.isdir():
        mode |= stat.S_IFDIR
    elif m.isfile():
        mode |= stat.S_IFREG
    elif m.islnk():
        mode |= stat.S_IFLNK
    elif m.ischr():
        mode |= stat.S_IFCHR
    elif m.isblk():
        mode |= stat.S_IFBLK
    elif m.isfifo():
        mode |= stat.S_IFIFO
    elif m.issym():
        mode |= stat.S_IFLNK
    return stat.filemode(mode)

def lrfill(a,b,w):
    return "{:<{}} {:>{}}".format(a, max(w - len(b) - 1,0), b, len(b))

def isodt(s):
    dt = datetime.fromtimestamp(s)
    date = dt.date().isoformat()
    tm = dt.time().isoformat('minutes')
    return date, tm

def tarline(m : tarfile.TarInfo):
    """Format a tarfile.TarInfo object as a string, in the same way as `tar tvf` does.

    A really unnecessary of fidelity here, I got carried away.
    """
    UGS_WIDTH = 19
    dt, tm = isodt(m.mtime)
    name = m.name
    if m.isdir():
        name += "/"
    elif m.issym():
        name += " -> " + m.linkname
    elif m.islnk():
        name += " link to " + m.linkname
    if m.isblk() or m.ischr():
        size_str = f"{m.devmajor},{m.devminor}"
    else:
        size_str = str(m.size)
    ug = f"{m.uname or m.uid}/{m.gname or m.gid}"
    ugs = lrfill(ug,size_str,UGS_WIDTH)
    return f"{modestr(m)} {ugs} {dt} {tm} {name}"

class SocketState(StrEnum):
    ESTABLISHED = "ESTABLISHED"
    SYN_SENT = "SYN_SENT"
    SYN_RECV = "SYN_RECV"
    FIN_WAIT1 = "FIN_WAIT1"
    FIN_WAIT2 = "FIN_WAIT2"
    TIME_WAIT = "TIME_WAIT"
    CLOSE = "CLOSE"
    CLOSE_WAIT = "CLOSE_WAIT"
    LAST_ACK = "LAST_ACK"
    LISTEN = "LISTEN"
    CLOSING = "CLOSING"
    UNKNOWN = "UNKNOWN"

_unspecified_addrs = { '0.0.0.0', '::' }
_localhost_addrs = { '127.0.0.1', '::1', 'localhost' }

@dataclass
class ListenPort:
    proto: str
    l_addr: str
    l_port: int|Literal['*']
    r_addr: str
    r_port: int|Literal['*']
    state: SocketState
    pid: int|None
    program: str

    def is_global_listen(self):
        """Return true if the port is LISTEN and the local address is all interfaces."""
        return self.state == SocketState.LISTEN and self.l_addr in _unspecified_addrs

    def is_local_listen(self):
        """Return true if the port is LISTEN and the local address is localhost."""
        return self.state == SocketState.LISTEN and self.l_addr in _localhost_addrs

# Looks like:
# Active Internet connections (only servers)
# Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
# tcp        0      0 100.125.113.43:37862    0.0.0.0:*               LISTEN      3503/tailscaled
# tcp        0      0 0.0.0.0:9091            0.0.0.0:*               LISTEN      4041/dockerd
# [...]
# tcp6       0      0 :::2049                 :::*                    LISTEN      -
# tcp6       0      0 :::80                   :::*                    LISTEN      4076/nginx: master
# tcp6       0      0 :::111                  :::*                    LISTEN      1/systemd
# tcp6       0      0 :::22                   :::*                    LISTEN      1/systemd
def parse_netstat_output(output):
    lines = output.split('\n')
    for line in lines[2:]:
        parts = line.strip().split(maxsplit=6)
        if len(parts) < 7:
            continue
        proto = parts[0].lower()
        l_addr, l_port = parts[3].rsplit(':', 1)
        r_addr, r_port = parts[4].rsplit(':', 1)
        if l_port != '*':
            l_port = int(l_port)
        if r_port != '*':
            r_port = int(r_port)
        state = parts[-2]
        if parts[-1] == '-':
            pid, program = None, "-"
        elif '/' in parts[-1]:
            pid, program = parts[-1].split('/', 1)
            pid = int(pid)
        else:
            pid, program = None, parts[-1]

        yield ListenPort(proto, l_addr, l_port, r_addr, r_port, SocketState(state), pid, program)
