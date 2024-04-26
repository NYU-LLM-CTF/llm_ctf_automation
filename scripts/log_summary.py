import json
import os
from pathlib import Path
import itertools as it
from tabulate import tabulate

getsubdirs = lambda d: filter(lambda p: p.is_dir(), d.iterdir())
getconvos = lambda d: filter(lambda p: p.suffix == ".json", d.iterdir())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Log summary")
    parser.add_argument("-l", "--log-dir", required=True, help="Logs directory")
    args = parser.parse_args()

    table = []

    logdir = Path(args.log_dir)
    if not logdir.is_dir():
        print("ERROR:", logdir, "is not a directory.")
        exit(1)

    chals = (chal for year in getsubdirs(logdir) for event in getsubdirs(year)
                  for cat in getsubdirs(event) for chal in getsubdirs(cat))
    success = 0
    total = 0
    for chal in chals:
        convos = list(getconvos(chal))
        if len(convos) == 0:
            # No logs
            continue

        total += 1
        solved = ""
        reason = set()
        exception = set()
        for cjson in convos:
            with cjson.open() as f:
                convo = json.load(f)
                if convo["solved"]:
                    solved = "Yes"
                    reason.clear()
                    exception.clear()
                    success += 1
                    break
                else:
                    reason.add(convo["finish_reason"])
                    if convo["finish_reason"] == "exception":
                        exptype = convo["exception_info"]["exception_type"]
                        if exptype == "BadRequestError" and \
                                "context_length_exceeded" in convo["exception_info"]["exception_message"]:
                            exptype = "ContextLengthExceeded"
                        exception.add(exptype)
        table.append([str(chal), solved, ", ".join(list(reason)), ", ".join(list(exception))])

    print(tabulate(table, headers=["Challenge", "Solved", "Reason", "Exception"]))
    print(f"Success: {success}/{total} {success/total*100:.2f}%")
