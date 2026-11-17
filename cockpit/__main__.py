"""python -m cockpit                          top 3 worries, then ask questions ("more" = all worries)
python -m cockpit ask "question" [--as-of D]  one answer
python -m cockpit worry [--as-of D] [--all]   ranked worry list (top 3 unless --all)
python -m cockpit agent NAME "question"       interview one of the 14 people (agent --list for all)
D is YYYY-MM-DD (end of that day, IST) or YYYY-MM-DDTHH:MM; the default is now."""
import argparse
from datetime import datetime, timedelta

from .agents import interview, roster
from .answer import ask
from .db import IST, to_ist
from .worry import top, worries


def show_worries(as_of, everything=False):
    cut = datetime.fromisoformat(to_ist(as_of or datetime.now(IST), end_of_day=True))
    items = worries(cut.isoformat())
    before = {w.title for w in worries((cut - timedelta(days=1)).isoformat())}   # NEW = not on yesterday's list
    shown = items if everything else top(items)
    if not items:
        print("Nothing to worry about on the records released so far.")
    for i, w in enumerate(shown, 1):
        print(f"{i}. {'NEW ' if w.title not in before else ''}{w}")
    if len(shown) < len(items):
        print(f"... and {len(items) - len(shown)} more. Type 'more' to see them.")


p = argparse.ArgumentParser(prog="cockpit")
p.add_argument("command", nargs="?", choices=["ask", "worry", "agent"])
p.add_argument("question", nargs="*")
p.add_argument("--as-of")
p.add_argument("--all", action="store_true", help="show every worry, not just the top 3")
p.add_argument("--list", action="store_true", help="with agent: list the 14 people")
args = p.parse_args()

if args.command == "ask":
    print(ask(" ".join(args.question), args.as_of))
elif args.command == "worry":
    show_worries(args.as_of, args.all)
elif args.command == "agent":
    if args.list or not args.question:
        for eid, name, title in roster(args.as_of):
            print(f"{eid}  {name}, {title}")
    else:
        print(interview(args.question[0], " ".join(args.question[1:]), args.as_of))
else:
    show_worries(args.as_of)
    while True:
        try:
            q = input("\nAsk, or '@name question' to talk to someone (blank line to quit): ").strip()
        except EOFError:
            break
        if not q:
            break
        if q.lower() == "more":
            show_worries(args.as_of, everything=True)
            continue
        if q.startswith("@"):
            name, _, rest = q[1:].partition(" ")
            print(interview(name, rest, args.as_of))
            continue
        print(ask(q, args.as_of))
