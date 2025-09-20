# app_categories.py

import random, re, difflib, math
import streamlit as st
from question_bank import QUESTIONS, CATEGORIES

def _tokenize_options(s: str):
    # split on "and", commas, slashes, semicolons
    parts = re.split(r"\s*(?:\band\b|,|/|;)\s*", s.strip(), flags=re.I)
    return [p for p in parts if p]

def answers_match(user: str, correct: str) -> bool:
    u = user.strip().lower()
    c = correct.strip().lower()

    # exact quick pass
    if u == c:
        return True

    # order-insensitive for multi-part answers like "Nepal and China"
    u_parts = _tokenize_options(u)
    c_parts = _tokenize_options(c)
    if len(c_parts) > 1:
        return sorted(u_parts) == sorted(c_parts)

    # fuzzy fallback for minor typos (tune 0.8–0.9)
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
def normalize(s: str) -> str:
    """Lowercase, trim, unify symbols, drop punctuation, collapse spaces; strip leading 'the'."""
    s = s.lower().strip()
    s = s.replace("&", "and").replace("’", "'").replace("´", "'").replace("`", "'")
    # Optional: mt./st. → mount/saint (good for place names)
    s = re.sub(r"\bmt[\.]?\s+", "mount ", s)
    s = re.sub(r"\bst[\.]?\s+", "saint ", s)
    # Collapse dotted/spacey 2-letter abbrevs: "u.s."/"n y" -> "us"/"ny"
    s = re.sub(r"\b([a-z])[\.\s]+([a-z])\b", r"\1\2", s)

    s = re.sub(r"[^\w\s]", " ", s)         # remove punctuation
    s = re.sub(r"\s+", " ", s).strip()     # collapse spaces
    if s.startswith("the "):
        s = s[4:]
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
    - Accept any among 'or' / comma / slash / semicolon separated answers
    - Order-insensitive match for multi-part answers (e.g., 'Nepal and China')
    - Alias-aware comparisons (e.g., 'us' ≈ 'united states')
    - Fuzzy match for mild typos (len-adaptive threshold)
    """
    u = normalize(user or "")
    c = normalize(correct or "")
    if not u:
        return False

    # whole-answer alias (rare but cheap)
    if alias_equiv(u, correct):
        return True

    # --- order-insensitive multi-part check ---
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
                    break
            else:
                # loop didn’t break -> every token matched something
                return True
        # if counts differ, fall through to single-option logic

    # --- single-part / “any of these options” logic ---
    parts = re.split(r"\bor\b|,|/|;", c)
    parts = [p.strip() for p in parts if p.strip()] or [c]

    for p in parts:
        if u == p or alias_equiv(u, p):  # <-- alias check added here
            return True
        if len(p) <= 3:  # very short answers require exact match
            continue
        ratio = difflib.SequenceMatcher(None, u, p).ratio()
        thresh = 0.88 if len(p) <= 6 else 0.80
        if ratio >= thresh:
            return True

    return False

def pool_for_category(category: str):
    if category == MIX_LABEL:
        return QUESTIONS
    return [q for q in QUESTIONS if q["category"] == category]

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
    cats = [MIX_LABEL] + sorted(CATEGORIES)
    ss.category = st.selectbox("Choose a category", cats, index=0)
    pool = pool_for_category(ss.category)

    # ✅ Show how many questions are available in the chosen category
    st.caption(f"{len(pool)} question(s) available in **{ss.category}**.")

    if not pool:
        st.warning("No questions in this category yet.")
        st.stop()

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
            "- Numeric answers must be digits (e.g., `1985`).\n"
            "- If a correct answer lists options (e.g., `Green or red`), **any one** is accepted.\n"
            "- Click **Quit** anytime and start over.\n"
        )

    if st.button("Start"):
        # ✅ Use repeats or not based on the checkbox
        ss.order = (
            random.choices(pool, k=num_q)  # can exceed unique pool size
            if allow_repeats
            else random.sample(pool, k=num_q)  # unique questions only
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
