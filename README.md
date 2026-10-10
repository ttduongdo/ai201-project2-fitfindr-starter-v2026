# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Search the listings file for items matching the description, optionally filtered by size and/or price cap 
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" --> `description` (str), `size` (str|None), `max_price` (float|None)
- **Returns:** a list of listing dicts `[item01: {id, title, description, category, style_tags, size, condition, price, colors, brand, platform}, item02, ...]`. Filtered by `size` and `max_price`. Sorted by best score calculated from (number of description word present, style_tags, category). At most `config.SEARCH_RESULT_LIMIT` values
- **When it has nothing:** []

### `suggest_outfit`

- **What it does:** Prompts the model to pair an item with wardrobe items from complementary categories that share at least one `style_tags`, ranked by number of shared tags and color match
- **Inputs:** `new_item` (dict), `wardrobe` (dict with `items: [dict]`)
- **Returns:** A (str) describing the outfit and naming the wardrobe pieces by `name`
- **When it has nothing:** If no `wardrobe` item fits, or `items` is empty, a str of general styling advice for the item. Never "".

### `create_fit_card`

- **What it does:** Writes a caption based on the listing details of `new_item` and the vibe of the `outfit` it was paired into
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** a caption of 2-4 sentences with hashtags from `new_item[style_tags]` (str)
- **When it has nothing:** if `outfit` is empty/whitespace then it returns a message string
---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** 
- If `search_listings` returns `[]`: set `session["error"]` to a message that names the query and says what to change (raise the price cap, drop the size, or use fewer descriptive words), then return the session. `suggest_outfit` and `create_fit_card` are never called and `session["fit_card"]` stays `None`. 
- Otherwise set `session["selected_item"] = session["search_results"][0]`, call `suggest_outfit` with it and the wardrobe, store the string in `session["outfit_suggestion"]`, pass that same string and the selected item to `create_fit_card`, and store the caption in `session["fit_card"]`.
**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> Regex:
- `max_price` is the number after `$` OR after "under" or "below" (float),
- `size` is the token after the word "size" (str),
- `description` is whatever text is left after removing those two phrases and stray punctuation,
- If no price or size is found, it means no filter (None)
**What moves through the session:** <!-- which fields, in what order -->
1. `session["query"]`: the raw user text
2. `session["parsed"]`: `description`, `size`, `max_price`
3. `session["search_results"]`: the full list from `search_listings`
4. `session["selected_item"]`: `search_results[0]`, set only when results are non-empty
5. `session["outfit_suggestion"]`: the string from `suggest_outfit`
6. `session["fit_card"]`: the caption string from `create_fit_card`
7. `session["error"]`: set only when the run ends early

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
(.venv) dothuyduong@Dos-MacBook-Pro-1546 ai201-project2-fitfindr-starter-v2026 % python -c "from tools import search_listings as s; print([r['id'] for r in s('graphic tee', max_price=30)])"
['lst_002', 'lst_006', 'lst_017', 'lst_033', 'lst_011', 'lst_015']

```

```
$ python -c "from tools import suggest_outfit; ..."
(.venv) dothuyduong@Dos-MacBook-Pro-1546 ai201-project2-fitfindr-starter-v2026 % python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit 1: Pair the new Vintage Levi's 501 Jeans with the white ribbed tank top and the black cropped zip hoodie layered on top, accessorized with the black crossbody bag and chunky white sneakers. This combination leans heavily into the streetwear and vintage tags shared by the jeans, creating an effortlessly cool silhouette by contrasting the fitted tank with the cropped hoodie. It is an ideal look for a casual weekend brunch, running errands, or meeting friends for coffee.

Outfit 2: Combine the new Vintage Levi's 501 Jeans with the oversized grey crewneck sweatshirt and the black combat boots, finished with the brown leather belt. The classic denim and the cozy, oversized grey crewneck share a timeless, streetwear-inspired aesthetic that looks effortlessly put-together while remaining incredibly comfortable. This outfit is perfect for casual Fridays at a creative workplace, a trip to the local record store, or an autumn afternoon walk.

```

```
$ python -c "from tools import create_fit_card; ..."
(.venv) dothuyduong@Dos-MacBook-Pro-1546 ai201-project2-fitfindr-starter-v2026 % python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Absolute thrift store miracle finding these vintage Levi's 501 jeans in the absolute best medium wash. Just tossed them up on depop for $38 because they deserve a better home than my crowded closet. They look insane paired with a crisp pair of fresh white sneakers for that effortless off-duty streetwear look. 

#vintage #classic #denim #streetwear

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
