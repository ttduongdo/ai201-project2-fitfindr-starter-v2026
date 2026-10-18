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

- **What it does:** Compares the selected item's price to the median price of other listings in the same category, and labels it as below/near/above typical
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
- If the catalog is empty (`load_listings() = None`): 
     - Set `session["error"]` to "No listings are available right now." and return the session.
     - No tool is called.
- If `search_listings` returns `[]`: 
     - Set `session["error"]` to a message that says what to change (raise the price cap/drop the size/use fewer descriptive words) and return the session. 
     - `compare_prices`, `suggest_outfit` and `create_fit_card` are never called/
     -  `session["price_check"] = None`, `session["fit_card"] = None`.
- Otherwise:
     - Set `session["selected_item"] = session["search_results"][0]`. 
     - Call `compare_prices` with it and store the result in `session["price_check"]`. Then call `suggest_outfit` with the item and the wardrobe and store the string in `session["outfit_suggestion"]`. Finally call `create_fit_card` with that string, the same item, and a price note (built from `session["price_check"]`, and store the caption in `session["fit_card"]`. The price check never ends a run or changes which tools run; it only changes what the caption can say.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> Regex:
- `max_price` is the number after `$` OR after "under" or "below" (float),
- `size` is the token after the word "size" (str),
- `description` is whatever text is left after removing those two phrases and stray punctuation,
- No price or size means no filter (None)

**What moves through the session:** <!-- which fields, in what order -->
1. `session["query"]`: the raw user text
2. `session["parsed"]`: `description`, `size`, `max_price`
3. `session["search_results"]`: the full list from `search_listings`
4. `session["selected_item"]`: `search_results[0]`, set only when results are non-empty
5. `session["price_check"]`: the dict from `compare_prices` (`median`, `diff`, `verdict`, `n`), set right after an item is selected
6. `session["outfit_suggestion"]`: the string from `suggest_outfit`
7. `session["fit_card"]`: the caption string from `create_fit_card`
8. `session["error"]`: set only when the run ends early

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'looking for a vintage graphic tee size M under $30'

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

```
$ python app.py ask "designer ballgown size XXS under $5"

  Nothing matched "designer ballgown" in size XXS under $5.0. Try removing the size filter or raising your budget or using different keywords.

```
---

## Stretch Feature: Price Comparison Tool

I'm adding a fourth tool `compare_prices` that checks whether the selected item is priced above or below similar listings. It runs in `agent.py::run_agent` after an item is selected and before `suggest_outfit`. Its result is stored in `session["price_check"]`, and the fit card mentions how the price compares to typical, worded to match the verdict.

### Sample Run
```
$ python app.py ask 'looking for a vintage graphic tee size M under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Pair the new Y2K Baby Tee with the baggy straight-leg dark wash jeans and the chunky white sneakers for a quintessential 2000s streetwear look. The fitted silhouette of the graphic baby tee balances the oversized denim, while the white sneakers tie in the crisp tones of the butterfly print. This nostalgic combination is perfect for a casual weekend hangout or running errands in the city.

  Outfit 2: Layer the vintage black denim jacket over the Y2K Baby Tee, paired with the wide-leg khaki trousers and black combat boots for an edgy, mixed-aesthetic ensemble. The black outerwear and boots adda grunge contrast to the sweet cottagecore and vintage vibes of the pink and purple butterfly graphic.This outfit is ideal for a casual day at a record store, a weekend concert, or grabbing coffee with friends.

  Fit card: Scored this adorable butterfly Y2K baby tee on depop for $18, which is about what these usually go for. I can't wait to style it with some baggy dark wash jeans and chunky white sneakers for the ultimate 2000s weekend look. 

  #y2k #vintagestyle #graphictee

```
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
| 1. Matching query completes | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops early | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| empty wardrobe _(diagnostic — not one of your five)_ | n/a | PASS | PASS | PASS | PASS | PASS | 5/5 |
| 3. Selected item is carried through | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card is postable | ≥4/5 | FAIL (312) | FAIL (362) | FAIL (378) | FAIL (355) | PASS (273) | MISSED (1/5) |
| 5. Price cap is respected | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
$ python run_eval.py --label before
Cache is OFF for this run — that's deliberate.

matching query completes  (example wardrobe)
  query: vintage graphic tee under $30
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    cap: 30.0, prices: [18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0]
[3] select
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    took item id lst_002
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: dict with keys: median, diff, verdict, n
      →    verdict: typical, median: 21.5, n: 14
[5] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Outfit 1: Pair the new Y2K baby tee with the baggy dark wash jeans and chunky white sneakers, adding the black…
      →    received item id lst_002
[6] create_fit_card
      in:  dict with keys: price_note
      out: scored this butterfly y2k baby tee on depop for $18, which is about typical for these. I'm obsessed with pairi…
      →    received item id lst_002
  try 1: completed — fit card 298 chars
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
| 1 | Matching query completes | 4/5 | MET (5/5) | "vintage graphic tee under $30" never stopped early |
| 2 | Impossible query stops early | 5/5 | MET (5/5) | "designer ballgown size XXS under $5" stopped at the no-results branch on all 5 tries |
| 3 | Selected item is carried through | 5/5 | MET (5/5) | On all 5 tries the trace shows `took item id lst_002` at select, then `received item id lst_002` at both `suggest_outfit` and `create_fit_card`|
| 4 | Fit card is postable | 4/5 | MISSED (1/5) | All 5 cards passed the price and hashtag checks BUT lengths were 312, 362, 378, 355 and 273, so only Try 5 passed |
| 5 | Price cap is respected | 5/5 | MET (5/5) | "tee under $20" showed `cap: 20.0, prices: [18.0, 15.0, 19.0]` on all 5 tries |


**Diagnoses**

**Criterion 4**
`create_fit_card` tool worked but its prompt never said the caption had to stay within 280 characters. The model followed the instructions of 3-4 sentences with a price clause and hashtags which comes out around 300–380 characters.

-> Fix the prompt: ask for 2-3 short sentences and state that the whole caption, hashtags included, must be 280 characters or fewer. If the model still goes over, add a retry-once guard.


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
$ python app.py ask 'looking for a vintage graphic tee size M under $30' --trace
[1] parse_query
      in:  looking for a vintage graphic tee size M under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[3] select
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    took search_results[0]
[4] compare_prices
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: dict with keys: median, diff, verdict, n
      →    verdict: typical, median: 21.5, n: 14
[5] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Outfit 1: Pair the new Y2K Baby Tee with the baggy straight-leg dark wash jeans and chunky white sneakers. Thi…
[6] create_fit_card
      in:  dict with keys: price_note
      out: Managed to snag this adorable Y2K butterfly baby tee on Depop for $18, which is pretty typical for these. Can'…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Pair the new Y2K Baby Tee with the baggy straight-leg dark wash jeans and chunky white sneakers. This combination nails the nostalgic Y2K streetwear aesthetic by balancing the fitted butterfly top with relaxed denim, tied together with the black crossbody bag. It is a trendy yet effortless look ideal for casual weekend hangouts or running errands.

  Outfit 2: Layer the vintage black denim jacket over the Y2K Baby Tee, paired with the wide-leg khaki trousers and chunky white sneakers. The earth tones of the trousers complement the pink and purple hues of the butterfly print, while the black denim adds a cool, vintage edge. This stylish ensemble is perfect for a casual daytime date or meeting friends at a coffee shop.

  Fit card: Managed to snag this adorable Y2K butterfly baby tee on Depop for $18, which is pretty typical for these. Can't wait to style it with some baggy dark wash jeans, chunky white sneakers, and a crossbody bag for the ultimate effortless weekend look. 

  #y2k #vintage #graphictee
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    no results, stopping before compare_prices / suggest_outfit / create_fit_card

  Nothing matched "designer ballgown" in size XXS under $5.0. Try removing the size filter or raising your budget or using different keywords.
```

**On the MCP move:** I moved `search_listings` onto an MCP server and changed `run_agent` to call it through `mcp_client.call_tool`. It returned the same top item and kept the no-results exit.
<!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** `create_fit_card` prompt in `tools.py`. I replaced the "two-to-four sentences" instruction to "two to three short sentences" and added a rule that the whole caption, hashtags included, must be 280 characters or fewer.


**Which failure it was meant to fix:** All 5 cards had the price and 3 trailing hashtags, but 4 were over 280 characters (312, 362, 378 and 355). 

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| empty wardrobe _(diagnostic — not one of your five)_ | n/a | PASS | PASS | PASS | PASS | PASS | 5/5 |
| 3. selected item is carried through | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card is postable | ≥4/5 | PASS (264) | PASS (276) | PASS (278) | PASS (245) | PASS (260) | MET (5/5) |
| 5. price cap is respected | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:** Yes. Criterion 4 went from MISSED (1/5) to MET (5/5), and the other four criteria stayed at their before-run results, so the change didn't break anything.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

**Criteria check form, not quality.** Some captions in the runs are generic ("perfect weekend fit"), and a few drop the platform or reword the price. It probably needs a human or a second model to judge, and I only had time to build word count check.

**The `compare_prices` price note is weakest for accessories.** The dataset has only 3 accessories, so the typical price falls back to all other listings, and the note can be misleading for that category.

**The agent always takes `search_results[0]`.** There's no ranking beyond the order `search_listings` returns, and the keyword match is loose. For "tee under $20", the results included a mesh long-sleeve top next to the tees. I'd add ranking, or ask the user which result they want.

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
