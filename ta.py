#!/home/golem/projects/llm-venice/venv/bin/python
#ta.p
import argparse
from llm_venice import VeniceChat

def main():
    parser = argparse.ArgumentParser(description="Standalone wrapper for VeniceChat")
    parser.add_argument("-m", "--model", default="llama-3.2-3b", help="Specify the model to use (default: llama-3.2-3b)")
    args = parser.parse_args()
    
    chat_instance = VeniceChat(model_id=f"venice/{args.model}")
    print(f"Initialized VeniceChat with model: {args.model}")

if __name__ == "__main__":
    main()
