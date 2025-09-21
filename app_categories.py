# app_categories.py

import random, re, difflib, math
import streamlit as st
from question_bank import QUESTIONS

# link other categories to pop culture
CATEGORY_FOLD = {
    # existing
    "Celebrities": "Pop Culture",
    "Fashion and Trends": "Pop Culture",
    "Tech": "Pop Culture",
    "Sports and Athletes": "Pop Culture",
    "Video Games": "Pop Culture",
    "Literature and Books": "Pop Culture",
    "Comics and Superheroes": "Pop Culture",

    # new: make all these count as Pop Culture
    "Movies": "Pop Culture",
    "Film": "Pop Culture",
    "Television": "Pop Culture",
    "TV": "Pop Culture",
    "TV Shows": "Pop Culture",
    "Anime": "Pop Culture",
    "K-Pop and Dramas": "Pop Culture",
    "K-Pop": "Pop Culture",
    "Korean Dramas": "Pop Culture",
    "Social Media": "Pop Culture",
    "Music": "Pop Culture",
    "Pop culture trivia questions and answers": "Pop Culture",
}

# case/whitespace tolerant fold
_FOLD_NORM = {k.lower(): v for k, v in CATEGORY_FOLD.items()}
def fold(cat: str) -> str:
    key = (cat or "").strip()
    return _FOLD_NORM.get(key.lower(), key)

def _tokenize_options(s: str):
    # split on "and", commas, slashes, semicolons
    parts = re.split(r"\s*(?:\band\b|,|/|;)\s*", s.strip(), flags=re.I)
    return [p for p in parts if p]

def answers_match(user: str, correct: str) -> bool:
    u = user.strip().lower()
    c = correct.strip().lower()
    if u == c:  # exact quick pass
        return True
    u_parts = _tokenize_options(u)
    c_parts = _tokenize_options(c)
    if len(c_parts) > 1:
        return sorted(u_parts) == sorted(c_parts)
    return difflib.SequenceMatcher(None, u, c).ratio() >= 0.85

# ---------- Settings ----------
PASS_THRESHOLD = 0.70  # 70%
MIX_LABEL = "All Categories (Mix)"

# Optional: paste your big ALIASES dict here if you want (can be empty)
ALIASES = {
    # example aliases – expand as you like
    "uk": {"united kingdom", "great britain", "britain"},
    "netherlands": {"holland", "the netherlands"},
    "robert downey jr": {"rdj", "robert downey junior"},
    "pokemon go": {"pokémon go", "pokemon-go"},
    "stranger things": {"strangerthings"},
    "united states": {"usa", "u s a", "u.s.", "us", "u.s.a", "united states of america"},
    "new york city": {"nyc", "new york", "ny"},
    "007": {"james bond", "bond"},
    "bible": {"the bible", "holy bible"},
    "Alabama": {"AL"},
    "Alaska": {"AK"},
    "Arizona": {"AZ"},
    "Arkansas": {"AR"},
    "California": {"CA"},
    "Colorado": {"CO"},
    "Connecticut": {"CT"},
    "Delaware": {"DE"},
    "Florida": {"FL"},
    "Georgia": {"GA"},
    "Hawaii": {"HI"},
    "Idaho": {"ID"},
    "Illinois": {"IL"},
    "Indiana": {"IN"},
    "Iowa": {"IA"},
    "Kansas": {"KS"},
    "Kentucky": {"KY"},
    "Louisiana": {"LA"},
    "Maine": {"ME"},
    "Maryland": {"MD"},
    "Massachusetts": {"MA"},
    "Michigan": {"MI"},
    "Minnesota": {"MN"},
    "Mississippi": {"MS"},
    "Missouri": {"MO"},
    "Montana": {"MT"},
    "Nebraska": {"NE"},
    "Nevada": {"NV"},
    "New Hampshire": {"NH"},
    "New Jersey": {"NJ"},
    "New Mexico": {"NM"},
    "New York": {"NY"},
    "North Carolina": {"NC"},
    "North Dakota": {"ND"},
    "Ohio": {"OH"},
    "Oklahoma": {"OK"},
    "Oregon": {"OR"},
    "Pennsylvania": {"PA"},
    "Rhode Island": {"RI"},
    "South Carolina": {"SC"},
    "South Dakota": {"SD"},
    "Tennessee": {"TN"},
    "Texas": {"TX"},
    "Utah": {"UT"},
    "Vermont": {"VT"},
    "Virginia": {"VA"},
    "Washington": {"WA"},
    "West Virginia": {"WV"},
    "Wisconsin": {"WI"},
    "Wyoming": {"WY"},
    # DC (normalize() strips punctuation)
    "Washington, DC": {"DC", "Washington DC", "District of Columbia"},
    # Countries / blocs
    "United Kingdom": {"UK", "U.K.", "Great Britain", "Britain"},
    "United Arab Emirates": {"UAE"},
    "Soviet Union": {"USSR", "Union of Soviet Socialist Republics"},
    "European Union": {"EU"},
    "United Nations": {"UN"},
    "Ivory Coast": {"Cote d'Ivoire", "Côte d'Ivoire"},
    "Netherlands": {"Holland", "The Netherlands"},
    "Myanmar": {"Burma"},
    "Czechia": {"Czech Republic"},
    "Eswatini": {"Swaziland"},
    "Cape Verde": {"Cabo Verde"},
    "East Timor": {"Timor-Leste", "Timor Leste"},
    "South Korea": {"ROK", "Republic of Korea"},
    "North Korea": {"DPRK", "Democratic People's Republic of Korea"},

    # Major cities (common nicknames/abbr.)
    "Los Angeles": {"LA", "L.A."},
    "San Francisco": {"SF", "S.F.", "San Fran"},
    "Philadelphia": {"Philly"},
    "Las Vegas": {"Vegas"},
    "New Orleans": {"NOLA"},
    "Atlanta": {"ATL"},
    "Saint Louis": {"St Louis", "St. Louis"},
    "Saint Petersburg": {"St Petersburg", "St. Petersburg"},

    # People / initials
    "John F. Kennedy": {"JFK"},
    "Franklin D. Roosevelt": {"FDR"},
    "Martin Luther King Jr.": {"MLK", "Dr Martin Luther King Jr", "Dr. Martin Luther King Jr"},

    # Entertainment shorthands
    "Lord of the Rings": {"LOTR"},
    "Game of Thrones": {"GOT"},
    "Harry Potter": {"HP"},
    "Back to the Future": {"BTTF"},
    "AC/DC": {"ACDC"},
}

def alias_equiv(u_norm: str, correct_raw: str) -> bool:
    return alias_match(u_norm, correct_raw)

# ---------- Helpers ----------
# Number helpers (allow "six" == 6, "twenty one" == 21, etc.)
_NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000,
}
_NUM_TOKEN_RE = re.compile(
    r"\b(?:(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|"
    r"million|billion)(?:[\s-]+|$))+",
    flags=re.I
)

def _words_to_int(phrase: str):
    words = [w for w in re.split(r"[\s-]+", phrase.strip().lower()) if w]
    if not words or not all(w in _NUM_WORDS for w in words):
        return None
    total, current = 0, 0
    for w in words:
        val = _NUM_WORDS[w]
        if val < 100:
            current += val
        elif val == 100:
            current = (current or 1) * 100
        else:
            total += (current or 1) * val
            current = 0
    return total + current

def _replace_number_words(text: str) -> str:
    def _sub(m):
        n = _words_to_int(m.group(0))
        return str(n) if n is not None else m.group(0)
    return _NUM_TOKEN_RE.sub(_sub, text)

def _extract_numbers(s: str):
    return [int(x) for x in re.findall(r"\d+", s)]

def normalize(s: str) -> str:
    """
    Lowercase, trim, unify symbols; convert number words to digits; strip leading 'the'.
    Also normalizes common number formats like '1,250' -> '1250' and '1 250' -> '1250'.
    """
    s = (s or "").lower().strip()
    s = s.replace("&", "and").replace("’", "'").replace("´", "'").replace("`", "'")

    # Remove thousands commas: '1,250' -> '1250'
    s = re.sub(r'(?<=\d),(?=\d{3}\b)', '', s)

    # mt./st. → mount/saint
    s = re.sub(r"\bmt[\.]?\s+", "mount ", s)
    s = re.sub(r"\bst[\.]?\s+", "saint ", s)

    # Collapse dotted/spacey abbreviations (u.s. -> us; n y -> ny)
    s = re.sub(r"\b([a-z])[\.\s]+([a-z])\b", r"\1\2", s)
    s = re.sub(r"\b([a-z])(?:[\.\s]+([a-z])){2,}\b",
               lambda m: re.sub(r"[\.\s]+", "", m.group(0)), s)

    # Punctuation to spaces; collapse
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # Merge spaces between digits: '1 250' -> '1250'
    s = re.sub(r"(?<=\d)\s+(?=\d)", "", s)

    # Tolerate leading article 'the '
    if s.startswith("the "):
        s = s[4:]

    # Convert number words to digits: 'six' -> '6'; 'twenty one' -> '21'
    s = _replace_number_words(s)

    return s

def alias_match(user_norm: str, correct_raw: str) -> bool:
    """If correct answer has a direct alias set, honor it."""
    c_norm = normalize(correct_raw)
    for key, variants in ALIASES.items():
        if normalize(key) == c_norm:
            if any(user_norm == normalize(v) for v in variants):
                return True
    return False

def is_correct(user: str, correct: str) -> bool:
    """
    Flexible match:
    - Case/whitespace/punctuation-insensitive
    - Optional leading 'The' (e.g., 'The Daily Planet' == 'Daily Planet')
    - Number word ↔ digit equivalence ('six' == '6', 'twenty one' == '21')
    - Accept any among 'or' / comma / slash / semicolon separated answers
    - Order-insensitive for multi-part answers (e.g., 'Blue and Gold' == 'gold, blue')
    - Alias-aware comparisons (e.g., 'us' ≈ 'united states')
    - Fuzzy match for mild typos (length-adaptive threshold)
    - If both sides contain digits, the numeric sequences must match (units/words can differ)
    """
    u = normalize(user or "")
    c = normalize(correct or "")
    if not u:
        return False

    # Exact or alias quick pass
    if u == c or alias_equiv(u, correct):
        return True

    # If both contain digits, compare just the numbers (ignore units/extra words)
    if re.search(r"\d", u) and re.search(r"\d", c):
        if _extract_numbers(u) == _extract_numbers(c):
            return True

    # Order-insensitive multi-part check (split on and/commas/slashes/semicolons)
    u_parts = _tokenize_options(u)
    c_parts = _tokenize_options(c)
    if len(c_parts) > 1:
        if len(u_parts) == len(c_parts):
            def close(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio() >= 0.88
            used = [False] * len(c_parts)
            for a in u_parts:
                matched = False
                for j, b in enumerate(c_parts):
                    if used[j]:
                        continue
                    if a == b or alias_equiv(a, b) or close(a, b):
                        used[j] = True
                        matched = True
                        break
                if not matched:
                    return False
            return True  # all tokens matched in some order

    # Single-part / “any of these options” logic
    parts = re.split(r"\bor\b|,|/|;", c)
    parts = [p.strip() for p in parts if p.strip()] or [c]

    for p in parts:
        if u == p or alias_equiv(u, p):
            return True
        if len(p) <= 3:  # very short answers require exact match
            continue
        ratio = difflib.SequenceMatcher(None, u, p).ratio()
        thresh = 0.88 if len(p) <= 6 else 0.80
        if ratio >= thresh:
            return True

    return False

def pool_for_category(category: str):
    cat = fold(category)
    if cat == MIX_LABEL:
        return QUESTIONS
    return [q for q in QUESTIONS if fold(q["category"]) == cat]

# ---------- UI ----------
st.set_page_config(page_title="Trivia (Categories)", page_icon="🧠", layout="centered")
st.title("🧠 Trivia — Categories")
st.caption("Build: 2025-09-20")

# Session state
ss = st.session_state
if "started" not in ss: ss.started = False
if "idx" not in ss: ss.idx = 0
if "order" not in ss: ss.order = []         # list of question dicts in play order
if "history" not in ss: ss.history = []     # dicts: {q, user, correct, is_correct}
if "category" not in ss: ss.category = MIX_LABEL

# Start screen
if not ss.started:
    cats = [MIX_LABEL] + sorted({fold(q["category"]) for q in QUESTIONS})
    ss.category = st.selectbox("Choose a category", cats, index=0)
    pool = pool_for_category(ss.category)

    if not pool:
        st.warning("No questions in this category yet.")
        st.stop()

    # ✅ Show how many questions are available in the chosen category
    st.caption(f"{len(pool)} question(s) available in **{ss.category}**.")

    # ✅ Let users allow repeats; this also changes the slider’s max
    allow_repeats = st.checkbox("Allow repeats (sample with replacement)", value=False)

    MAX_BASE = 50
    max_q = MAX_BASE if allow_repeats else min(MAX_BASE, len(pool))
    num_default = min(10, max_q)
    num_q = st.slider(
        "How many questions?",
        min_value=5, max_value=max_q, value=num_default, step=1
    )

    with st.expander("📋 Rules & Tips", expanded=True):
        st.markdown(
            "- Answers are **case-insensitive**; basic typos are tolerated.\n"
            "- Numbers can be **words or digits** (e.g., `six` or `6`).\n"
            "- If a correct answer lists options (e.g., `Green or red`), **any one** is accepted.\n"
            "- Click **Quit** anytime and start over.\n"
        )

    if st.button("Start"):
        ss.order = (
            random.choices(pool, k=num_q) if allow_repeats
            else random.sample(pool, k=num_q)
        )
        ss.history = []
        ss.idx = 0
        ss.started = True
        st.rerun()

# Game flow
else:
    i = ss.idx
    total = len(ss.order)

    if i < total:
        qobj = ss.order[i]
        qtext, ans_correct = qobj["q"], qobj["a"]

        st.subheader(f"Question {i + 1} of {total} — {ss.category}")
        st.write(qtext)

        # ✅ Image display goes HERE (optional per-question)
        if qobj.get("image"):
            st.image(qobj["image"], use_column_width=True)

        user_ans = st.text_input("Your answer:", key=f"ans_{i}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit", key=f"submit_{i}"):
                if not user_ans.strip():
                    st.warning("Please type an answer.")
                else:
                    ok = is_correct(user_ans, ans_correct)
                    ss.history.append({
                        "q": qtext,
                        "user": user_ans,
                        "correct": ans_correct,
                        "is_correct": ok
                    })
                    ss.idx += 1
                    st.rerun()
        with col2:
            if st.button("Quit"):
                ss.started = False
                ss.idx = 0
                ss.order = []
                ss.history = []
                st.rerun()

        st.progress(i / total if total else 0.0)

    else:
        # End screen
        right = sum(1 for h in ss.history if h["is_correct"])
        needed = math.ceil(total * PASS_THRESHOLD)
        pct = (right / total) * 100 if total else 0.0

        st.success(f"Game over! Your score: **{right}/{total}** ({pct:.2f}%)")

        if right >= needed:
            st.info("🌟 Nice work!")
        else:
            st.warning(f"😬 You needed at least **{needed}/{total}** ({int(PASS_THRESHOLD*100)}%).")

        st.markdown("### Review answers")
        st.write(f"✅ Correct: {right} ❌ Incorrect: {total - right}")

        for idx, h in enumerate(ss.history, start=1):
            icon = "✅" if h["is_correct"] else "❌"
            st.markdown(
                f"**Q{idx} {icon}**  \n"
                f"{h['q']}  \n"
                f"**Your answer:** {h['user']}  \n"
                f"**Correct answer:** {h['correct']}"
            )

        if st.button("Play again"):
            ss.started = False
            ss.idx = 0
            ss.order = []
            ss.history = []
            st.rerun()
