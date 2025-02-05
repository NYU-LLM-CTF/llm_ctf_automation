from pathlib import Path
from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge
import json

def look_for_flag(logdata, chal):
    for message in logdata["planner"]:
        if "content" in message and message["content"] is not None:
            if chal.flag in message["content"]:
                return True

    for executor in logdata["executors"]:
        for message in executor:
            if "content" in message and message["content"] is not None: 
                if chal.flag in message["content"]:
                    return True

    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Check if flag was found in any of the messages")
    parser.add_argument("--logdir", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--dataset", default=None)
    
    args = parser.parse_args()

    if args.dataset is not None:
        ds = CTFDataset(dataset_json=args.dataset)
    else:
        ds = CTFDataset(split=args.split)

    logdir = Path(args.logdir)

    for log in logdir.glob("*.json"):
        logdata = log.open().read()
        logjson = json.loads(logdata)
        if logjson["success"]:
            continue
        chal = CTFChallenge(ds.get(log.stem), ds.basedir)
        # print("Checking", log.stem, chal.flag)
        if chal.flag in logdata or look_for_flag(logjson, chal):
            print("Flag found in messages:", log.stem)
