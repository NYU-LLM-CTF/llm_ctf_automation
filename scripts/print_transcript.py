import json

from nyuctf_multiagent.logging import logger

def print_msg(msg):
    if msg["role"] == "MessageRole.SYSTEM":
        logger.system_message(msg["content"])
    elif msg["role"] == "MessageRole.USER":
        logger.user_message(msg["content"])
    elif msg["role"] == "MessageRole.ASSISTANT":
        logger.assistant_thought(msg["content"])
        if "tool_call" in msg and msg["tool_call"] is not None:
            action = f"**{msg['tool_call']['name']}**:\n\n"
            for arg, val in msg["tool_call"]["parsed_args"].items():
                action += f"- {arg}:\n\n```\n{val}\n```\n\n"
        else:
            action = None
        logger.assistant_action(action)
    elif msg["role"] == "MessageRole.OBSERVATION":
        if "tool_result" in msg and msg["tool_result"] is not None:
            result = f"**{msg['tool_result']['name']}**:\n\n"
            if type(msg["tool_result"]["result"]) == dict:
                for arg, val in msg["tool_result"]["result"].items():
                    result += f"- {arg}:\n\n```\n{val}\n```\n\n"
            else:
                result += f"\n```\n{msg['tool_result']['result']}\n```\n"
            logger.observation_message(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Pretty print the multi-agent transcript.")
    parser.add_argument("-t", "--transcript", required=True, help="Transcript JSON file")
    args = parser.parse_args()
    
    with open(args.transcript,  "r") as f:
        transcript = json.load(f)
    
    if "autoprompter" in transcript and transcript["autoprompter"] is not None:
        logger.print("=============== AUTOPROMPTER ================", style="bold")
        for msg in transcript["autoprompter"]:
            print_msg(msg)

    if "planner" in transcript and transcript["planner"] is not None:
        logger.print("=============== PLANNER =====================", style="bold")
        exec_count = 0
        for msg in transcript["planner"]:
            print_msg(msg)
            if "tool_call" in msg and msg["tool_call"]["name"] == "delegate":
                logger.print(f"=============== EXECUTOR {exec_count+1} =================", style="bold")
                for msg in transcript["executors"][exec_count]:
                    print_msg(msg)
                logger.print(f"=============== EXECUTOR DONE =================", style="bold")
                exec_count += 1
