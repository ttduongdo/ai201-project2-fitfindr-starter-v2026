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
The user describes a thrift find in plain language, like "vintage graphic tee size M under $30". FitFindr pulls out the item description, size and price cap, searches the listings, and picks the best match. It then suggests one or two outfits that pair the find with pieces from user's wardrobe (or general styling ideas if your wardrobe is empty) and writes a short, post-ready caption with hashtags. If nothing matches, it stops and tells the user what to change, such as dropping the size or raising the budget.


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

- **What it does:** Finds listings that match the description words, optionally filtered by size and a price cap
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None)
- **Returns:** a list of full listing dicts (`id, title, description, category, style_tags, size, condition, price, colors, brand, platform`), best match first, at most `config.SEARCH_RESULT_LIMIT`. The score is the number of distinct description words (minus filler words like "a", "for", "looking") found in the listing's title, description, category, style tags or brand. Ties keep the order they appear in the listings file. `max_price` is inclusive. A size matches when every word in it appears as a whole token in the listing's size, so "M" matches "S/M" but not "XL (oversized)"
- **When it has nothing:** `[]`

### `suggest_outfit`

- **What it does:** Prompts the model for 1–2 outfits that pair the new item with wardrobe pieces from complementary categories, preferring pieces that share style tags or colors with it
- **Inputs:** `new_item` (dict), `wardrobe` (dict with `items`: list of dicts)
- **Returns:** a non-empty plain-text `str`: "Outfit 1: …" and "Outfit 2: …", each naming wardrobe pieces by their exact `name`, why they work together, and an occasion
- **When it has nothing:** if `wardrobe["items"]` is empty, a `str` of general styling advice for the item that doesn't refer to a wardrobe. If the model returns an empty reply, a fixed fallback message. Never `""`

### `create_fit_card`

- **What it does:** Writes a caption based on the listing details of `new_item` and the vibe of the `outfit` it was paired into
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** a caption of 2-4 sentences with hashtags from `new_item[style_tags]` (str)
- **When it has nothing:** if `outfit` is empty/whitespace then it returns a message string

### Stretch Feature: `compare_price`

- **What it does:** Compares the selected item's price to the median price of other listings in the same category (all other listings if the category has fewer than 3 others), and labels it as below, near, or above typical
- **Inputs:** `item` (dict), `listings` (list of dicts)
- **Returns:** a dict `{"median": float, "diff": float, "verdict": str, "n": int}`. `median` is the median price of the comparison pool, `diff` is the item's price minus the median, `n` is the pool size, and `verdict` is "below typical" if the price is at most 80% of the median, "above typical" if at least 120%, otherwise "typical". The item itself is excluded from the pool
- **When it has nothing:** if there are no other listings, `{"median": None, "diff": None, "verdict": "not enough data", "n": 0}`

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
python app.py ask 'looking for a vintage graphic tee size M under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Pair the new Y2K Baby Tee with the baggy straight-leg dark wash jeans and chunky white sneakers. The fitted silhouette of the baby tee balances the voluminous denim for a classic 2000s streetwear look that ties in with the Y2K and vintage tags. This outfit is perfect for casual weekend hangouts or running errands in style.

Outfit 2: Layer the vintage black denim jacket over the Y2K Baby Tee, paired with the wide-leg khaki trousers and chunky white sneakers. The butterfly print pops against the neutral earth tones of the trousers, while the black jacket adds a cool contrasting edge. This effortless yet put-together ensemble is ideal for a casual daytime date or meeting friends for coffee.

  Fit card: Score! Snagged this butterfly baby tee on Depop for just $18. I am so obsessed with how the fitted silhouette looks paired with baggy dark wash jeans and chunky white sneakers for that ultimate 2000s streetwear vibe. Perfect fit for weekend errands or just hanging out. 

#y2k #vintage #graphictee

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{
     'id': 'lst_002', 
     'title': 'Y2K Baby Tee — Butterfly Print', 
     'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 
     'category': 'tops', 
     'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 
     'size': 'S/M', 
     'condition': 'excellent', 
     'price': 18.0, 
     'colors': ['white', 'pink', 'purple'], 
     'brand': None, 'platform': 'depop'
}, 
{
     'id': 'lst_006', 
     'title': 'Graphic Tee — 2003 Tour Bootleg Style', 
     'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 
     'category': 'tops', 
     'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 
     'size': 'L', 
     'condition': 'good', 
     'price': 24.0, 
     'colors': ['black'], 
     'brand': None, 
     'platform': 'depop'
}, 
{
     'id': 'lst_017', 
     'title': 'Mesh Long-Sleeve Top — Black', 
     'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 
     'category': 'tops', 
     'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 
     'size': 'S/M', 
     'condition': 'excellent', 
     'price': 15.0, 
     'colors': ['black'], 
     'brand': None, 
     'platform': 'depop'
}, 
{
     'id': 'lst_033', 
     'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 
     'category': 'tops', 
     'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 
     'size': 'L', 
     'condition': 'fair', 
     'price': 19.0, 'colors': ['grey', 'charcoal'], 
     'brand': None, 
     'platform': 'depop'
}, 
{
     'id': 'lst_011', 
     'title': 'Low-Rise Cargo Pants — Khaki', 
     'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 
     'category': 'bottoms', 
     'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 
     'size': 'W29', 
     'condition': 'fair', 
     'price': 27.0, 
     'colors': ['khaki', 'tan'], 
     'brand': None, 
     'platform': 'poshmark'
}, 
{
     'id': 'lst_015', 
     'title': 'Vintage Graphic Hoodie — Faded Black', 
     'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 
     'category': 'tops', 
     'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 
     'size': 'L', 
     'condition': 'fair', 
     'price': 26.0, 
     'colors': ['black', 'charcoal'], 
     'brand': None, 
     'platform': 'depop'
}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Outfit 1: Pair the new Vintage Levi's 501 Jeans with the white ribbed tank top and the black cropped zip hoodie layered on top, accessorized with the black crossbody bag and chunky white sneakers. This combination leans heavily into the streetwear and vintage tags shared by the jeans, creating an effortlessly cool silhouette by contrasting the fitted tank with the cropped hoodie. It is an ideal look for a casual weekend brunch, running errands, or meeting friends for coffee.

Outfit 2: Combine the new Vintage Levi's 501 Jeans with the oversized grey crewneck sweatshirt and the black combat boots, finished with the brown leather belt. The classic denim and the cozy, oversized grey crewneck share a timeless, streetwear-inspired aesthetic that looks effortlessly put-together while remaining incredibly comfortable. This outfit is perfect for casual Fridays at a creative workplace, a trip to the local record store, or an autumn afternoon walk.

```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Score on Depop! I just snagged these vintage Levi's 501 jeans for only $38.00 and they fit like a dream. Throwing them on with some fresh white sneakers for that ultimate effortless streetwear vibe. #vintage #classic #denim #streetwear
```

---

## Stretch Feature: Price Comparison Tool

I'm adding a fourth tool, `compare_prices`, that checks whether the selected item is priced above or below similar listings. It runs in `agent.py::run_agent` after an item is selected and before `suggest_outfit`. Its result is stored in `session["price_check"]`, and the fit card mentions the price only when the verdict is "below typical". I'll test it by computing one category's median by hand and matching the tool's output to it.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to help me scope how suggest_outfit should decide what goes with an item. My idea was to match it to wardrobe pieces by shared style_tags and similar colors, plus category rules (a top with a bottom, a layer over a top).
- *What came back:* Claude made an overcomplicated category-pairing system (top - bottom, top - layer, etc.) and brushed over the other rules such as matching colors or styles, which I thought wouldn't be actually helpful because anyone can pair a top to a bottom without an LLM. Claude also proposed ignoring the `vintage` tag when matching because it is present on a lot of items' style tags which didn't make sense.
- *What I changed:* I dropped the design and wrote it as a model prompt that returns a string. Style tags and colors became the pairing signal the model is told to prefer, which is where the model adds value over a lookup. I kept `vintage` as a usable tag to count toward the scoring system.


**Moment 2**

- *What I asked for:* Help making the fit card prompt produce something that reads like a real post instead of sounding like a seller.
- *What came back:* Review notes on my prompt: I pasted the whole listing dict (with the price and platform) so the caption read like a seller. The prompt also didn't say what to do when the outfit had two options.
- *What I changed:* I passed only the fields the caption needs, built the brand line in Python so it's empty when missing, told it to base the caption on the first outfit. To fix the seller tone I add some context: someone who just bought the item secondhand ("Bought for", "Bought on") and told it not to say it's selling. The next three runs read as a buyer.

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
