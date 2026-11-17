# Response to T6a: "Just tell me what to worry about. Top three."

**Voice note (released 17 Nov):** "I won't type questions every morning, na. When I open it, it should just tell me what to worry about. Top three." (`T6a:#2`)

**Decision:** I made the change. I pushed back on three details of "top three" and kept the evidence.

## What changed

- When you open the cockpit (`./run.sh`), it shows the top three worries before anything else. You don't need to type a question.
- Each worry is marked **NEW** if it wasn't on the list the day before, so the morning view shows what changed and not just what's still true.
- Type `more` to see the rest of the list.

This is what you would have seen on 17 Nov:

```
1. [5/5, High] Atlas (routing engine v3) has slipped and there is no new GA date on record
2. [4/5, High] Backend hiring meant to de-risk Atlas is on hold, after a recruiter advance was paid
3. NEW [4/5, Medium] Engineering engagement fell from 3.9 to 3.1 in Jul-Sep 2026
... and 5 more. Type 'more' to see them.
```

## Where I pushed back

1. **A 5/5 is never cut to make three.** If more than three items are severity 5, all of them show. Three is the normal length of the list, not a cap on the worst news.
2. **No padding.** On a quiet day you may see one item. I won't fill the list with weak signals just to reach three.
3. **Every item keeps its evidence.** You asked not to have to type, not to drop the sources. A ranked list with nothing behind it is just one more opinion in your inbox, and that's what you said you wanted to get away from. The sources take one line per item.

The ranking is my judgement. Each rule in `cockpit/worry.py` has a severity from 1 to 5, and ties are broken by confidence. If you'd order something differently, say so; changing it is a one-line edit.

**Not built:** pushing the list to you on WhatsApp or by email. You said "when I open it", so opening the cockpit is the trigger.

## How to check it

- `./run.sh` opens on the top three. `python -m cockpit worry --as-of 2026-11-17 --all` shows the full list.
- Tests: `test_t6a_opens_on_top_three` and `test_t6a_never_cuts_a_five_or_pads` in `tests/test_cockpit.py`.
