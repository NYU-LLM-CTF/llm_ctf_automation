import codecs
import io
import os
from pathlib import Path
import select
import subprocess
import socket
import json
import argparse
import threading
import time
import uuid
import docker
import pyte
from rich.text import Text
import tarfile
import traceback as tb
from urllib.parse import urlparse

from ..ctflogging import status
from ..challenge import CTFChallenge, get_asi_name, get_canonical_name
from .testutils import (
    screen_to_richtext,
    docker_stream_decode,
    tarline,
    parse_netstat_output
)

SCRIPT_PATH = Path(__file__).resolve().parent

class TestContainer:
    def __init__(
            self,
            image,
            network,
            volume=None,
            name=None,
            rows=40, cols=100,
            output_wait=0.1,
            startup_wait=1.0,
            log_dir=None):
        super().__init__()

        self.container_image = image
        self.client = docker.from_env()
        # Make sure the container is up to date by building it
        status.debug_message(f"Ensuring test client container {self.container_image} is up to date...")
        self.client.images.build(
            path=str(SCRIPT_PATH),
            tag=self.container_image,
            rm=True,
        )
        status.debug_message(f"Finished docker build")

        if name is None:
            # Generate a random suffix for the container name
            name = f"{image}_{uuid.uuid4().hex[:8]}"
        self.container_name = name
        self.log_dir = log_dir
        self.network = network
        self.volume = volume if volume is not None else {}
        self.container = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.startup_wait = startup_wait
        self.output_wait = output_wait
        # Screen to feed the output into
        self.cols = cols
        self.rows = rows
        self.screen = pyte.HistoryScreen(cols, rows, 10000)
        self.screen_stream = pyte.ByteStream(self.screen)
        # Asciinema log events
        self.log_file = None
        self.log_start_time = None
        self.output_log = []
        self.stdout_decoder = codecs.getincrementaldecoder('UTF-8')('replace')
        # Condition var for the monitor thread
        self.monvar = threading.Condition()
        self.output_done = True
        self.running = False

    def __enter__(self):
        status.debug_message(f"Starting client container {self.container_name}...")
        self.container = self.client.containers.create(
            image=self.container_image,
            name=self.container_name,
            command='bash',
            stdin_open=True,
            tty=True,
            network=self.network,
            volumes=self.volume,
            auto_remove=True,
            environment={'TERM': 'xterm-256color'},
        )
        for k in 'stdin', 'stdout', 'stderr':
            sock = self.client.api.attach_socket(
                self.container.id,
                params={k: 1, 'stream': 1},
            )
            if k == 'stdin':
                # stdin needs to be writable, but the socket Docker returns is not
                self.stdin = socket.SocketIO(sock._sock, 'wb')
            else:
                setattr(self, k, sock)

        # Start the container
        self.container.start()
        self.start_time = time.time()
        event_filters = {
            'event': ['start', 'die'],
            'container': [self.container.id],
        }
        self.container_events = self.client.events(
            decode=True,
            filters=event_filters,
            since=int(self.start_time),
            until=int(self.start_time+self.startup_wait),
        )
        for event in self.container_events:
            if event['status'] == 'start' and event['id'] == self.container.id:
                break
            # Check if the container failed to start
            if event['status'] == 'die' and event['id'] == self.container.id:
                raise Exception("Container failed to start")

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_output)
        self.monitor_thread.start()

        return self

    def monitor_output(self):
        """Monitor the container's output and add to buffer."""
        last_update = time.time()
        while self.running:
            rlist, _, _ = select.select([self.stdout], [], [], 0.1)
            if rlist:
                buf = self.stdout.read(1024)
                if buf:
                    last_update = time.time()
                    self.output_done = False
                    self.screen_stream.feed(buf)
                    decoded = self.stdout_decoder.decode(buf)
                    if self.output_log:
                        self.output_log.append(
                            (time.time()-self.log_start_time, "o", decoded)
                        )
            if time.time() - last_update > self.output_wait:
                with self.monvar:
                    self.output_done = True
                    self.monvar.notify_all()

    def __exit__(self, exc_type, exc_value, traceback):
        status.debug_message(f"Stopping client container {self.container_name}...")
        self.running = False
        self.container_events.close()
        self.monitor_thread.join()
        try:
            self.container.stop()
            self.container.wait()
        except Exception as e:
            pass
        if self.output_log and self.log_file:
            with open(self.log_file, 'w') as f:
                for line in self.output_log:
                    f.write(json.dumps(line) + '\n')

    def write(self, data: str):
        if self.output_log:
            self.output_log.append(
                (time.time()-self.log_start_time, "i", data)
            )
        self.stdin.write(data.encode())
        self.stdin.flush()

    def display(self, border=True):
        if border:
            status.print('+' + '-'*self.screen.columns + '+')
            borderchar = Text('|')
        for line in screen_to_richtext(self.screen):
            status.print(borderchar + line + borderchar)
        if border:
            status.print('+' + '-'*self.screen.columns + '+')

    def wait_output(self):
        self.output_done = False
        with self.monvar:
            while not self.output_done:
                self.monvar.wait()

    def start_logging(self, log_file):
        self.log_file = log_file
        self.log_start_time = time.time()
        self.output_log = []
        self.output_log.append(
            {
                "version": 2,
                "width": self.cols,
                "height": self.rows,
                "timestamp": int(self.log_start_time),
                "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
            }
        )

    def exec(self, cmd, timeout=5.0, **kwargs):
        exec_instance = self.client.api.exec_create(self.container.id, cmd)
        output = b''
        start_time = time.time()
        timed_out = False
        exec_sock = self.client.api.exec_start(exec_instance['Id'], socket=True, **kwargs)
        while True:
            elapsed = time.time() - start_time
            remain = timeout - elapsed
            if remain <= 0:
                timed_out = True
                break
            exec_sock._sock.settimeout(remain)
            try:
                buf = exec_sock.read(1024)
                if not buf:
                    break
                output += docker_stream_decode(buf)
            except socket.timeout:
                timed_out = True
                break
        if not timed_out:
            returncode = self.client.api.exec_inspect(exec_instance['Id'])['ExitCode']
        else:
            returncode = None
        return returncode, output

    def copy_from_container(self, src, dest, extract=True, strip_components=0, remove_after=False):
        parts, get_stat = self.container.get_archive(src)
        tardata = b''
        for part in parts:
            tardata += part
        if not extract:
            if os.path.isdir(dest):
                dest = os.path.join(dest, os.path.basename(src)) + '.tar'
            with open(dest, 'wb') as f:
                f.write(tardata)
            status.debug_message(f"Copied {self.container_name}:{src} to {dest}")
            if remove_after:
                self.exec(f'rm -rf {src}')
            return True, { 'stat': get_stat, 'extracted_files': [dest] }
        # extract the tarball
        status.debug_message(f"Extracting {self.container_name}:{src} to {dest}")
        extracted_files = []
        with tarfile.open(fileobj=io.BytesIO(tardata)) as tar:
            for member in tar.getmembers():
                new_name = str(Path(*Path(member.name).parts[strip_components:]))
                new_member = member.replace(name=new_name)
                status.debug_message(tarline(new_member))
                tar.extract(new_member, path=dest)
                extracted_files.append(os.path.join(dest, new_name))
        if remove_after:
            self.exec(f'rm -rf {src}')
        return True, {'stat': get_stat, 'extracted_files': extracted_files}

def get_container_info(container_id):
    client = docker.from_env()
    chal_container = client.containers.get(container_id)
    info = client.api.inspect_container(chal_container.id)
    return info

def get_listening_ports_netstat(container_id):
    info = get_container_info(container_id)
    pid = info['State']['Pid']
    try:
        listen_ports_output = subprocess.check_output(
            ['sudo', 'nsenter', '-t', str(pid), '-n', 'netstat', '-Wplnt'],
            text=True,
        )
        return listen_ports_output
    except subprocess.CalledProcessError as e:
        status.debug_message(f"Error occurred: {e}")
        status.debug_message(f"Standard Output:\n{e.stdout}")
        status.debug_message(f"Standard Error:\n{e.stderr}")
        return None

def wait_for_container_port(tester : TestContainer, host : str, port : int, timeout=5.0):
    if port is None:
        return None
    status.debug_message(f"Waiting up to {timeout:.1f}s for port {port} to be open on {host}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        returncode, output = tester.exec(f'nc -zv -w1 -W1 {host} {port}', timeout=timeout)
        if returncode == 0:
            startup_time = time.time()-start_time
            status.debug_message(f"Server port came up in {startup_time:.2f}s")
            return startup_time
        time.sleep(0.1)
    return float('inf')

def get_docker_ports(container_id):
    netstat_ports = get_listening_ports_netstat(container_id)
    status.print(f"Netstat ports: {netstat_ports}")
    return netstat_ports

def run_test(cmd, tester: TestContainer, test_name, timeout=5.0, retries=3):
    status.print(f"[{test_name}] {cmd}")
    for i in range(retries):
        status.print(f"[{test_name}] Attempt {i+1}/{retries}...")
        returncode, output = tester.exec(cmd, timeout=timeout)
        if returncode == 0:
            status.print(f"[green bold]{test_name} test passed![/green bold]", markup=True)
            rv = True
            break
    else:
        ret = returncode if returncode is not None else 'timeout'
        status.print(f"[red bold]{test_name} test failed (ret={ret})![/red bold]", markup=True)
        rv = False
    status.print("Output:")
    output_dec = output.decode(errors='replace')
    status.print(output_dec)
    return rv, { 'cmd': cmd, 'returncode': returncode, 'output': output_dec }

def test_nc(tester: TestContainer, host : str, port : int, retries=3):
    # Use nc to connect to the challenge server's port
    success, extra = run_test(
        f"nc -zv -w1 -W1 {host} {port}",
        tester,
        "Network",
        timeout=5.0,
        retries=retries,
    )
    return success, { 'nc_test': extra }

def test_web(tester: TestContainer, url : str, retries=3):
    # Use curl to connect to the challenge server's port
    success, extra = run_test(
        f"curl --fail-with-body -L --connect-timeout 1 -s -v -I -X GET {url}",
        tester,
        "Web server",
        timeout=5.0,
        retries=retries,
    )
    return success, { 'web_test': extra }

def url_to_name(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(':','_')
    path = parsed.path[1:].replace('/', '_')
    name = netloc
    if path:
        name += '_' + path
    return name

def take_web_screenshot(tester : TestContainer, url : str, name : str):
    status.print(f"Taking a screenshot of {url} -> {name}...")
    returncode, output = tester.exec(f"python webtester.py {url} {name}", timeout=30.0)
    status.print(output.decode(errors='replace'))
    # Copy the logs out of the container
    outdir = output.decode(errors='replace').strip()
    _, extracted_files = tester.copy_from_container(outdir, tester.log_dir, strip_components=1, remove_after=True)
    return returncode == 0, { 'web_screenshot_files': extracted_files }

def take_nc_screencast(tester : TestContainer, host : str, port : int, name : str):
    status.print(f"Taking a screencast of {host}:{port}...")
    cast_filename = tester.log_dir / f'{name}.cast'
    tester.start_logging(cast_filename)
    tester.write(f"nc -v {host} {port}\n")
    tester.wait_output()
    return True, { 'nc_screencast_filename': str(cast_filename) }

_port_cache = {}
def port_is_ssl(tester: TestContainer, host, port):
    global _port_cache
    if (host, port) in _port_cache:
        return _port_cache[(host, port)]
    cmd = f'bash -c "openssl s_client -connect {host}:{port} < /dev/null"'
    returncode, output = tester.exec(cmd, timeout=5.0)
    output = output.decode(errors='replace')
    status.debug_message(f"Output from openssl s_client:\n{output}", truncate=False)
    _port_cache[(host, port)] = (returncode == 0)
    return returncode == 0, { 'ssl_test_output': output }

def test_network(chal : CTFChallenge, tester : TestContainer, port : int|None = None):
    net_test_res = {}
    # If the challenge has no server, consider it a pass
    if chal.get_server_type() is None:
        net_test_res[-1] = {
            'net_ok': True,
        }
        return net_test_res
    if chal.challenge_port is None:
        status.print(f"[red]No challenge port specified for {chal.asiname}[/red]", markup=True)
        net_test_res[-1] = {
            'net_ok': False,
        }
        return net_test_res
    if port is None:
        port = chal.challenge_port
        if isinstance(port, list):
            net_test_res = {}
            for p in port:
                net_test_res[p] = test_network(chal, tester, p)
            return net_test_res
        else:
            return { port: test_network(chal, tester, port) }
    # Test network connectivity
    # Assume not ok by default
    net_test_res['net_ok'] = False
    status.print(f"[bold]Testing network connectivity on {port}...[/bold]", markup=True)
    net_test_res['nc'] = {}
    nc_res, extra = test_nc(tester, chal.challenge_server_name, port)
    net_test_res['nc']['success'] = nc_res
    net_test_res['nc'].update(extra)
    if not nc_res:
        return net_test_res
    elif chal.get_server_type() == "web":
        net_test_res['web'] = {}
        is_ssl, extra = port_is_ssl(tester, chal.challenge_server_name, port)
        net_test_res.update(extra)
        scheme = "https" if is_ssl else "http"
        url = f"{scheme}://{chal.challenge_server_name}:{port}"
        status.debug_message(f"Testing URL: {url}")
        net_test_res['web']['ssl'] = is_ssl
        net_test_res['web']['url'] = url
        web_res, extra = test_web(tester, url)
        net_test_res['web']['success'] = web_res
        net_test_res['web'].update(extra)
        net_test_res['web']['web_screenshot'] = []
        if web_res:
            net_test_res['net_ok'] = True
            # Take a screenshot of the web page
            web_sc_res, extra = take_web_screenshot(tester, url, f"{chal.asiname}_{url_to_name(url)}")
            net_test_res['web']['web_screenshot'] = [{'success': web_sc_res, 'url': url, **extra}]
        # Take a screenshot of any other URLs listed in the challenge info
        for url in chal.challenge.get('urls', []):
            status.debug_message(f"Testing additional URL: {url}")
            # If any of these succeed, web is ok
            web_res, extra = test_web(tester, url, retries=5)
            if web_res:
                net_test_res['web']['success'] = True
                net_test_res['net_ok'] = True
            web_sc_res, extra = take_web_screenshot(tester, url, f"{chal.asiname}_{url_to_name(url)}")
            net_test_res['web']['web_screenshot'].append({'success': web_sc_res, 'url': url, **extra})
        return net_test_res
    else:
        # nc style challenge, and it works
        net_test_res['net_ok'] = True
        nc_cast_res, extra = take_nc_screencast(tester, chal.challenge_server_name, port, f"{chal.asiname}_{port}")
        net_test_res['nc']['nc_cast'] = { 'success': nc_cast_res, **extra }
        return net_test_res

def test_solver(chal : CTFChallenge, tester : TestContainer, skip_labels=None):
    # Load metadata if it exists
    if (chal.chaldir/'test_solver'/'metadata.json').exists():
        with open(chal.chaldir/'test_solver'/'metadata.json') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    timeout = metadata.get('timeout', 300)
    if skip_labels is not None:
        skip_labels = set(skip_labels)
        labels = set(metadata.get('labels', []))
        if labels & skip_labels:
            status.debug_message(f"Skipping solver test for {chal.asiname} due to labels: {labels & skip_labels}")
            return None, None
    status.debug_message(f"Running solver test for {chal.asiname} with timeout={timeout}...")
    res, output = run_test("bash /chaltest_solver/test.sh", tester, "Solver", timeout=timeout, retries=1)
    res = chal.check_flag(output['output'])
    return res, { 'solver_output': output }

def main():
    parser = argparse.ArgumentParser(
        description="Test that a challenge is working correctly",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("challenge_jsons", nargs='+', help="path to the JSON file describing the challenge")
    parser.add_argument("-q", "--quiet", action="store_true", help="don't print messages to the console")
    parser.add_argument("-d", "--debug", action="store_true", help="print debug messages")
    parser.add_argument("-C", "--container-image", default="chaltest", help="the Docker image to use for the CTF test environment")
    parser.add_argument("-n", "--container-name", default=None, help="the Docker container name to set for the CTF test environment")
    parser.add_argument("-N", "--network", default="ctfnet", help="the Docker network to use for the CTF environment")
    parser.add_argument("-w", "--wait", type=float, default=2.0, help="time to wait before running network test")
    parser.add_argument("-L", "--log-dir", default=None, help="direcotry where output logs go")
    parser.add_argument("--rm", action="store_true", help="remove the global log file before starting")
    args = parser.parse_args()
    status.set(quiet=args.quiet, debug=args.debug)

    # This is needed for the challenge class but it doesn't make much sense for us
    args.disable_docker = False

    # Log directory
    if args.log_dir is None:
        args.log_dir = Path('chaltest_logs')
    else:
        args.log_dir = Path(args.log_dir)
    args.log_dir.mkdir(exist_ok=True)
    global_log_file = args.log_dir / 'chaltest.jsonl'
    if args.rm:
        global_log_file.unlink(missing_ok=True)
    all_ok = None
    # Open the global log file with line buffering (flush after every newline)
    with open(global_log_file, 'a', buffering=1) as global_log:
        for challenge_json in args.challenge_jsons:
            challenge_json = Path(challenge_json).resolve()
            compose_files = list(challenge_json.parent.glob('**/docker-compose.y*ml'))
            asiname = get_asi_name(challenge_json.parent)
            ociname = get_canonical_name(challenge_json.parent)
            oci_archive = challenge_json.parent / f"{ociname}.tar"
            chal_logdir = args.log_dir / asiname
            chal_logdir.mkdir(exist_ok=True)
            chaltest_result = {
                "name": asiname,
                "challenge_json": str(challenge_json),
                "success": False,
                "log": str(chal_logdir),
                "server_start_time": None,
                "test_timestamp": None,
                "network_tests": None,
                "server_logs": None,
                "server_ports": None,
                "server_ports_raw": None,
                "solver_output": None,
                "solver_success": None,
                "canonical_oci_name": oci_archive.name,
                "canonical_oci_exists": oci_archive.exists(),
                "compose_files": [str(cf) for cf in compose_files],
                "exception_info": None,
            }
            if compose_files:
                status.debug_message(f"docker-compose.yml found in {challenge_json.parent}, test will probably fail", truncate=False)
            try:
                with CTFChallenge(challenge_json, args) as chal:
                    volume = {}
                    if (chal.chaldir/'test_solver').is_dir():
                        volume[str((chal.chaldir/'test_solver'))] = {'bind': '/chaltest_solver', 'mode': 'rw'}
                    if chal.has_files:
                        volume[chal.tmpdir] = {'bind': '/home/ctfplayer/ctf_files', 'mode': 'rw'}
                    with TestContainer(
                        args.container_image,
                        args.network,
                        name=args.container_name,
                        startup_wait=args.wait,
                        log_dir=chal_logdir,
                        volume=volume,
                    ) as tester:
                        test_timestamp = time.time()
                        chaltest_result['test_timestamp'] = test_timestamp
                        status.debug_message(f"Testing challenge {chal.asiname} ({chal.name})...")
                        startup_time = wait_for_container_port(tester, chal.challenge_server_name, chal.challenge_port, timeout=args.wait)
                        if startup_time is None:
                            status.debug_message(f"Server port did not come up in time, but will try anyway")
                        chaltest_result['server_start_time'] = startup_time
                        net_results = test_network(chal, tester)
                        net_ok = all([v['net_ok'] for v in net_results.values()])
                        chaltest_result["network_tests"] = net_results
                        chaltest_result["success"] = net_ok
                        if (chal.chaldir/'test_solver').is_dir():
                            solver_ok, solver_output = test_solver(chal, tester)
                            chaltest_result["solver_output"] = solver_output
                            chaltest_result["solver_success"] = solver_ok
                            chaltest_result["success"] = net_ok and solver_ok
                        if -1 in net_results:
                            if all_ok is None:
                                all_ok = chaltest_result["success"]
                            else:
                                all_ok = all_ok and chaltest_result["success"]
                            # No server, skip the rest
                            global_log.write(json.dumps(chaltest_result) + '\n')
                            continue
                        server_logs = chal.get_server_logs()
                        status.debug_message(f"Server output:\n{server_logs}", truncate=False)
                        chaltest_result["server_logs"] = server_logs
                        if chal.challenge_container:
                            server_ports = get_docker_ports(chal.challenge_container)
                            chaltest_result["server_ports_raw"] = server_ports
                            try:
                                server_ports = parse_netstat_output(server_ports)
                                chaltest_result["server_ports"] = [vars(lp) for lp in server_ports]
                            except Exception as e:
                                status.debug_message(f"Error parsing netstat output: {e}")
                        if all_ok is None:
                            all_ok = chaltest_result["success"]
                        else:
                            all_ok = all_ok and chaltest_result["success"]
                        global_log.write(json.dumps(chaltest_result) + '\n')
            except Exception as e:
                all_ok = False
                # Extracting traceback details
                tb_list = tb.format_tb(e.__traceback__)
                tb_string = ''.join(tb_list)
                status.debug_message(f"{type(e).__name__} loading {challenge_json}: {e}")
                status.debug_message(f"Traceback:\n{tb_string}", truncate=False)
                # Constructing the JSON object
                exception_info = {
                    "exception_type": str(type(e).__name__),
                    "exception_message": str(e),
                    "traceback": tb_string
                }
                chaltest_result["exception_info"] = exception_info
                global_log.write(json.dumps(chaltest_result) + '\n')
                continue

    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())
