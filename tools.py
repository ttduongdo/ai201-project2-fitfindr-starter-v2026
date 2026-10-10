"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re

STOPWORDS = {"a", "an", "the", "and", "or", "for", "in", "of", "to", "with", "some", "looking", "want", "need"}
def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))

# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
    query = _words(description) - STOPWORDS
    size = _words(size) if size else None

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size and not size <= _words(listing["size"]):
            continue

        keywords = _words(" ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
            listing["brand"] if listing["brand"] else "" 
        ]))
        score = len(query & keywords)
        if score > 0:
            scored.append((score, listing))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [listing for score, listing in scored[:config.SEARCH_RESULT_LIMIT]]


def _format_wardrobe(items: list[dict]) -> str:
    lines = []
    for item in items:
        colors = ", ".join(item.get("colors", []))
        tags = ", ".join(item.get("style_tags", []))
        lines.append(f"-  {item['name']} ({item.get('category')}; {colors}; tags: {tags})")
    return "\n".join(lines)

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    tags = [t for t in new_item.get("style_tags", [])]
    item_desc = f"{new_item['title']} ({new_item.get('category')}; {', '.join(new_item['colors'])}; tags: {', '.join(tags)})"

    items = wardrobe.get("items", [])
    if not items:
        prompt = f"""
        You are a professional fashion stylist. For this item: {item_desc}, give some general styling ideas including the following:
        - How to style it with other wardrobe staples.
        - Suitable occasions or settings.
        - Color coordination and layering tips.
        Output: plain text only, no markdown. Start directly with the first outfit. Label each one "Idea 1: " / "Idea 2:". Give each 2-3 sentences covering the pieces, why they work, and an occasion.
        """
    else:
        wardrobe_str = _format_wardrobe(items)
        prompt = f"""
        You are a professional fashion stylist. 
        For this new item: {item_desc}
        and the user's wardrobe:
        {wardrobe_str}

        Suggest 1-2 outfit combinations strictly using these wardrobe items based on the following rules:
        - Pair complementary categories, such as a top with a bottom or a layer over a top.
        - Prefer pieces that share style tags and/or colors with the new item.
        - Consider color coordination and layering.
        - Mention suitable occasions or settings for each outfit.
        - Do not invent pieces the user doesn't own.
        Output: plain text only, no markdown. Start directly with the first outfit. Label each one "Outfit 1: " / "Outfit 2:". Give each 2-3 sentences covering the pieces, why they work, and an occasion.
        """

    reply = generate(prompt)
    if not reply or not reply.strip():
        return "Couldn't generate outfit ideas for this item. Try again."
    return reply.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "Couldn't create a fit card because the outfit is empty."

    price = f"${new_item['price']:.2f}"
    brand = new_item.get('brand')
    brand_line = f"Brand: {brand}" if brand else ""
    tags = ", ".join(new_item.get("style_tags", []))

    prompt = f"""
    You just bought some new clothing and you're posting about your haul.

    Item: {new_item['title']}
    Bought for: {price}
    Bought on: {new_item['platform']}
    {brand_line}
    Style tags: {tags}

    Outfit idea:
    {outfit}

    Write a two-to-four sentence caption you'd actually post about this find.
    - Mention the item, its price, and the platform once each.
    - Sound like a real person's post, not a product description.
    - Be specific about the vibe, using details from the outfit idea.
    - If the outfit idea has more than one outfit, base the caption on the first one.
    - End with 2-4 hashtags based on the style tags.
    - Plain text only. No intro like "Here's a caption", and no quotation marks around it.
    """

    reply = generate(prompt)
    if not reply or not reply.strip():
        return "Couldn't generate a fit card for this outfit. Try again."
    return reply.strip()
