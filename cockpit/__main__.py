"""python -m cockpit                          worry list, then ask questions until a blank line
python -m cockpit ask "question" [--as-of D]  one answer
python -m cockpit worry [--as-of D]           ranked worry list
D is YYYY-MM-DD (end of that day, IST) or YYYY-MM-DDTHH:MM; the default is now."""
import argparse

from .answer import ask
from .worry import worries


def show_worries(as_of):
    items = worries(as_of)
    print(f"What to worry about ({len(items)}):" if items else "Nothing to worry about on the records released so far.")
    for i, w in enumerate(items, 1):
        print(f"{i}. {w}")


p = argparse.ArgumentParser(prog="cockpit")
p.add_argument("command", nargs="?", choices=["ask", "worry"])
p.add_argument("question", nargs="*")
p.add_argument("--as-of")
args = p.parse_args()

if args.command == "ask":
    print(ask(" ".join(args.question), args.as_of))
elif args.command == "worry":
    show_worries(args.as_of)
else:
    show_worries(args.as_of)
    while True:
        try:
            q = input("\nAsk (blank line to quit): ").strip()
        except EOFError:
            break
        if not q:
            break
        print(ask(q, args.as_of))
