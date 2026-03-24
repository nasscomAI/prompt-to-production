"""
Prompt-to-Production — All 4 Agents UI
Run: streamlit run ui.py
"""
import sys
import os
import csv
import io
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))

# ── load each agent module safely ─────────────────────────────────────────────
def _load(name, rel_path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, rel_path))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

uc0a = _load("uc0a", "uc-0a/classifier.py")
uc0b = _load("uc0b", "uc-0b/app.py")
uc0c = _load("uc0c", "uc-0c/app.py")
ucx  = _load("ucx",  "uc-x/app.py")

import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prompt to Production — Agents",
    page_icon="🤖",
    layout="wide",
)

DATA_DIR   = os.path.join(BASE, "data")
CITY_DIR   = os.path.join(DATA_DIR, "city-test-files")
POLICY_DIR = os.path.join(DATA_DIR, "policy-documents")
BUDGET_FILE = os.path.join(DATA_DIR, "budget", "ward_budget.csv")

st.title("🤖 Prompt-to-Production Agent Dashboard")
st.caption("NASSCOM Workshop — UC-0A · UC-0B · UC-0C · UC-X")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏙️ UC-0A  Complaint Classifier",
    "📄 UC-0B  Policy Summarizer",
    "📊 UC-0C  Budget Growth",
    "💬 UC-X   Ask My Documents",
])


# ══════════════════════════════════════════════════════════════════════════════
# UC-0A — Complaint Classifier
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("🏙️ Civic Complaint Classifier")
    st.markdown("Classifies citizen complaints → **category · priority · reason · flag**")

    city_files = {
        "Pune":      os.path.join(CITY_DIR, "test_pune.csv"),
        "Hyderabad": os.path.join(CITY_DIR, "test_hyderabad.csv"),
        "Kolkata":   os.path.join(CITY_DIR, "test_kolkata.csv"),
        "Ahmedabad": os.path.join(CITY_DIR, "test_ahmedabad.csv"),
    }

    city = st.selectbox("Select city", list(city_files.keys()), key="uc0a_city")

    if st.button("▶ Run Classifier", key="run_uc0a"):
        with st.spinner("Classifying complaints..."):
            results = uc0a.batch_classify(city_files[city])

        urgent  = [r for r in results if r["priority"] == "Urgent"]
        reviews = [r for r in results if r["flag"] == "NEEDS_REVIEW"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(results))
        m2.metric("🔴 Urgent", len(urgent))
        m3.metric("🟡 Standard", sum(1 for r in results if r["priority"] == "Standard"))
        m4.metric("⚠️ Needs Review", len(reviews))

        st.subheader("All Results")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        if urgent:
            st.subheader("🔴 Urgent Complaints")
            for r in urgent:
                st.error(f"**[{r['complaint_id']}]** `{r['category']}` — {r['reason']}")

        if reviews:
            st.subheader("⚠️ Flagged for Review")
            for r in reviews:
                st.warning(f"**[{r['complaint_id']}]** `{r['category']}` — {r['reason']}")

        out = io.StringIO()
        csv.DictWriter(out, fieldnames=["complaint_id","category","priority","reason","flag"]).writeheader()
        # re-write properly
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=["complaint_id","category","priority","reason","flag"])
        w.writeheader(); w.writerows(results)
        st.download_button("⬇ Download CSV", out.getvalue(),
                           file_name=f"results_{city.lower()}.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# UC-0B — Policy Summarizer
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("📄 Policy Summarizer")
    st.markdown("Summarizes policy documents — **preserves all binding obligations, no clause dropped**")

    policy_files = {
        "HR Leave Policy":              os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
        "IT Acceptable Use Policy":     os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
        "Finance Reimbursement Policy": os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
    }

    selected_policy = st.selectbox("Select policy document", list(policy_files.keys()), key="uc0b_policy")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("📖 Show Source Document", key="show_source"):
            with open(policy_files[selected_policy], encoding="utf-8") as f:
                st.text_area("Source Document", f.read(), height=450)

    with col_b:
        if st.button("▶ Generate Summary", key="run_uc0b"):
            with st.spinner("Summarizing policy..."):
                policy = uc0b.retrieve_policy(policy_files[selected_policy])
                summary = uc0b.summarize_policy(policy)

            if "VERIFIED ✓" in summary:
                st.success("✅ All critical clauses verified in source document")
            elif "10/10" in summary:
                st.success("✅ 10/10 critical clauses confirmed")
            else:
                st.warning("⚠️ Some clauses could not be verified — check output")

            st.text_area("Summary Output", summary, height=450)
            st.download_button("⬇ Download Summary", summary,
                               file_name="policy_summary.txt", mime="text/plain")


# ══════════════════════════════════════════════════════════════════════════════
# UC-0C — Budget Growth Calculator
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("📊 Budget Growth Calculator")
    st.markdown("Computes **MoM / YoY growth** per ward per category — formula shown per row, nulls flagged")

    @st.cache_data
    def load_budget():
        return uc0c.load_dataset(BUDGET_FILE)

    clean_rows, null_rows = load_budget()
    wards      = sorted(set(r["ward"] for r in clean_rows))
    categories = sorted(set(r["category"] for r in clean_rows))

    col1, col2, col3 = st.columns(3)
    with col1:
        ward = st.selectbox("Ward", wards, key="uc0c_ward")
    with col2:
        category = st.selectbox("Category", categories, key="uc0c_cat")
    with col3:
        growth_type = st.selectbox("Growth Type", ["MoM", "YoY"], key="uc0c_gt")

    if null_rows:
        with st.expander(f"⚠️ {len(null_rows)} NULL rows excluded from calculation"):
            for r in null_rows:
                st.caption(f"• {r['period']}  |  {r['ward']}  |  {r['category']}  →  {r.get('notes','')}")

    if st.button("▶ Calculate Growth", key="run_uc0c"):
        with st.spinner("Calculating..."):
            results = uc0c.compute_growth(clean_rows, ward, category, growth_type)

        st.subheader(f"{growth_type} Growth — {ward}  |  {category}")
        df = pd.DataFrame(results)

        def colour_growth(val):
            if isinstance(val, str) and val.startswith("-"):
                return "color: red; font-weight: bold"
            elif isinstance(val, str) and "%" in val:
                return "color: green; font-weight: bold"
            return ""

        st.dataframe(
            df.style.applymap(colour_growth, subset=["growth_pct"]),
            use_container_width=True,
        )

        out = io.StringIO()
        df.to_csv(out, index=False)
        st.download_button("⬇ Download CSV", out.getvalue(),
                           file_name="growth_output.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# UC-X — Ask My Documents
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("💬 Ask My Documents")
    st.markdown("RAG Q&A over **3 CMC policy documents** — single-source answers, refuses if not found")

    if "ucx_docs" not in st.session_state:
        with st.spinner("Loading policy documents..."):
            st.session_state.ucx_docs = ucx.retrieve_documents()
        st.session_state.ucx_chat = []

    docs = st.session_state.ucx_docs
    st.success(f"✅ {len(docs)} documents loaded: HR Leave · IT Acceptable Use · Finance Reimbursement")

    st.markdown("**Quick questions — click to ask:**")
    sample_qs = [
        "Can I carry forward unused annual leave?",
        "Who approves leave without pay?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I claim DA and meal receipts on the same day?",
        "What is the company view on flexible working culture?",
        "Can I use my personal phone to access work files?",
    ]
    cols = st.columns(2)
    for i, q in enumerate(sample_qs):
        if cols[i % 2].button(q, key=f"sq_{i}"):
            st.session_state.ucx_pending = q

    st.divider()

    user_q = st.chat_input("Type your policy question here...")
    if user_q:
        st.session_state.ucx_pending = user_q

    if st.session_state.get("ucx_pending"):
        q = st.session_state.ucx_pending
        with st.spinner("Searching policy documents..."):
            answer = ucx.answer_question(q, docs, use_llm=False)
        st.session_state.ucx_chat.append({"q": q, "a": answer})
        st.session_state.ucx_pending = None

    for msg in reversed(st.session_state.get("ucx_chat", [])):
        with st.chat_message("user"):
            st.write(msg["q"])
        with st.chat_message("assistant"):
            if "not covered in the available policy" in msg["a"]:
                st.warning(msg["a"])
            else:
                st.info(msg["a"])

    if st.session_state.get("ucx_chat"):
        if st.button("🗑 Clear Chat", key="clear_chat"):
            st.session_state.ucx_chat = []
            st.rerun()

