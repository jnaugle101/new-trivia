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
    "united states": {"usa", "us", "u.s.a", "u s a", "u.s."},
    "uk": {"united kingdom", "great britain", "britain"},
}

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
    - Fuzzy match for mild typos (len-adaptive threshold)
    """
    u = normalize(user or "")
    c = normalize(correct or "")
    if not u:
        return False
    if alias_match(u, correct):
        return True

    # --- NEW: order-insensitive multi-part check ---
    u_parts = _tokenize_options(u)
    c_parts = _tokenize_options(c)
    if len(c_parts) > 1:
        if len(u_parts) == len(c_parts):
            # exact token set match
            if sorted(u_parts) == sorted(c_parts):
                return True
            # fuzzy per-token (all tokens must find a close match)
            def close(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio() >= 0.88
            used = [False] * len(c_parts)
            all_matched = True
            for a in u_parts:
                hit = False
                for j, b in enumerate(c_parts):
                    if not used[j] and (a == b or close(a, b)):
                        used[j] = True
                        hit = True
                        break
                if not hit:
                    all_matched = False
                    break
            if all_matched:
                return True
        # if user didn’t provide same number of parts, fall through to single-part logic

    # --- Single-part logic: accept any one of the listed options ---
    parts = re.split(r"\bor\b|,|/|;", c)
    parts = [p.strip() for p in parts if p.strip()] or [c]

    for p in parts:
        if u == p:
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
