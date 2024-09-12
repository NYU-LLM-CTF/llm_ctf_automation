import json
import os
from pathlib import Path
import itertools as it
from tabulate import tabulate

getsubdirs = lambda d: filter(lambda p: p.is_dir(), d.iterdir())
def getconvos(d, model=None):
    for p in d.iterdir():
        if p.suffix != ".json":
            continue
        if model and model not in p.parts[-1]:
            continue
        yield p

def filter_chals(args, year, event, cat, chal):
    if len(args.year) > 0 and year not in args.year:
        return False
    if len(args.event) > 0 and event not in args.event:
        return False
    if len(args.cat) > 0 and cat not in args.cat:
        return False
    if len(args.chal) > 0 and chal not in args.chal:
        return False
    return True

def check_for_mistakes(convo):
    mistakes = set()
    for msg in convo["messages"]:
        cont = msg[1].get("content", msg[1].get("text"))
        if not cont:
            continue
        if "{PORT}" in cont:
            mistakes.add("PortMissing")
        if "{port}" in cont:
            mistakes.add("PortMissing")
        if "{box}" in cont or "nc None" in cont:
            mistakes.add("ServerMissing")
    return mistakes


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Log summary")
    parser.add_argument("-l", "--log-dir", required=True, help="Logs directory")
    parser.add_argument("-y", "--year", default=[], nargs="+", help="Years to select, space separated")
    parser.add_argument("-e", "--event", default=[], nargs="+", help="Events to select, space separated")
    parser.add_argument("-t", "--cat", default=[], nargs="+", help="Categories to select, space separated")
    parser.add_argument("-c", "--chal", default=[], nargs="+", help="Challenges to select, space separated")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo-1106", help="Full name of model to select")
    args = parser.parse_args()

    table = []

    logdir = Path(args.log_dir)
    if not logdir.is_dir():
        print("ERROR:", logdir, "is not a directory.")
        exit(1)

    chals = (chal for year in getsubdirs(logdir) for event in getsubdirs(year)
                  for cat in getsubdirs(event) for chal in getsubdirs(cat)
                  if filter_chals(args, year.parts[-1], event.parts[-1], cat.parts[-1], chal.parts[-1]))
    success = set()
    total = 0
    for chal in chals:
        convos = list(getconvos(chal, args.model))
        if len(convos) == 0:
            # No logs
            print("No logs for challenge:", chal, "model:", args.model)
            continue

        total += 1
        solved = 0
        reason = set()
        mistakes = set()
        for cjson in convos:
            with cjson.open() as f:
                try:
                    convo = json.load(f)
                except:
                    reason.add("invalid_json")
                    print("WARN: invalid json", cjson)
                    continue
                mistakes |= check_for_mistakes(convo)
                if convo["solved"]:
                    solved += 1
                    success.add(str(chal))
                else:
                    if convo["finish_reason"] == "exception":
                        exptype = convo["exception_info"]["exception_type"]
                        if exptype == "BadRequestError" and \
                                ("context_length_exceeded" in convo["exception_info"]["exception_message"] \
                                or "string_above_max_length" in convo["exception_info"]["exception_message"]):
                            exptype = "context_length"
                        if exptype == "RateLimitError":
                            exptype = "rate_limit"
                        reason.add(exptype)
                    else:
                        reason.add(convo["finish_reason"])

        chalname = f"{chal.parts[-1]}({chal.parts[-4]}{'f' if 'Final' in chal.parts[-3] else 'q'})"
        table.append([chalname, f"{solved}/{len(convos)}", ", ".join(list(mistakes)), ", ".join(list(reason))])

    if total == 0:
        print("No challenges!")
        exit(2)

    print(tabulate(table, headers=["Challenge", "Solved", "Mistakes", "Reason"], tablefmt='tsv'))
    print(f"Success: {len(success)}/{total} {len(success)/total*100:.2f}%")

