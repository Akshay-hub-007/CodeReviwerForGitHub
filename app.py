import streamlit as st
from graphs.Gitgraph import workflow, ReviewOutput
from typing import List

# ── Helpers ───────────────────────────────────────────────────────────────────

SEVERITY_CONFIG = {
    "critical": {"icon": "🔴", "color": "#ff4b4b", "label": "Critical"},
    "high":     {"icon": "🟠", "color": "#ff8c00", "label": "High"},
    "medium":   {"icon": "🟡", "color": "#ffd700", "label": "Medium"},
    "low":      {"icon": "🟢", "color": "#00c853", "label": "Low"},
}

def score_color(score: float) -> str:
    if score >= 8: return "#00c853"
    if score >= 6: return "#ffd700"
    if score >= 4: return "#ff8c00"
    return "#ff4b4b"

def render_issues(issues, severity_key: str):
    cfg = SEVERITY_CONFIG[severity_key]
    if not issues:
        st.caption(f"No {cfg['label']} issues found ✅")
        return
    for issue in issues:
        with st.expander(f"{cfg['icon']} **{issue.title}** — `{issue.location}`"):
            col1, col2 = st.columns(2)
            col1.markdown(f"**Category:** {issue.category}")
            col2.markdown(f"**Severity:** {issue.severity}")
            st.markdown(f"**Description:** {issue.description}")
            st.warning(f"⚠️ **Impact:** {issue.impact}")
            st.success(f"✅ **Fix:** {issue.fix}")

def render_bullet_list(items: List[str]):
    for item in items:
        st.markdown(f"- {item}")

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .score-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 2rem;
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🔍 AI Code Reviewer")
    st.caption("Powered by Gemini 2.5 Flash + LangGraph")
    st.divider()

    url = st.text_input(
        "GitHub File URL",
        placeholder="https://github.com/owner/repo/blob/main/file.py",
    )
    run = st.button("▶ Run Review", type="primary", use_container_width=True)

    st.divider()
    st.markdown("**What gets reviewed:**")
    for item in ["Architecture & Design", "Code Quality", "Security",
                 "Performance", "Error Handling", "Testing", "Documentation"]:
        st.caption(f"✓ {item}")

# ── Main ──────────────────────────────────────────────────────────────────────

if not run:
    st.markdown("## Paste a GitHub file URL in the sidebar and click **Run Review**")
    st.info("Supports any public GitHub file — Python, Java, TypeScript, Go, etc.")
    st.stop()

if not url.strip():
    st.error("Please enter a GitHub URL first.")
    st.stop()

# Run agent
with st.status("Running agent…", expanded=True) as status:
    st.write("📥 Fetching source code from GitHub…")
    try:
        result = workflow.invoke({"url": url.strip()})
        st.write("🤖 LLM review complete!")
        status.update(label="✅ Review ready!", state="complete", expanded=False)
    except Exception as e:
        status.update(label="❌ Error", state="error")
        st.exception(e)
        st.stop()

review: ReviewOutput = result["review"]

# Score banner
col_score, col_summary = st.columns([1, 3])
with col_score:
    color = score_color(review.final_score)
    st.markdown(
        f'<div class="score-badge" style="background:{color}">'
        f'{review.final_score:.1f}<span style="font-size:1rem">/10</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Overall Quality Score")
with col_summary:
    st.subheader("Summary")
    st.write(review.summary)

st.divider()

# Strengths
with st.expander("✨ Strengths", expanded=True):
    render_bullet_list(review.strengths)

# Issues
st.subheader("🐛 Issues Found")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔴 Critical", len(review.critical_issues))
c2.metric("🟠 High",     len(review.high_priority_issues))
c3.metric("🟡 Medium",   len(review.medium_priority_issues))
c4.metric("🟢 Low",      len(review.low_priority_issues))

tab_c, tab_h, tab_m, tab_l = st.tabs(["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"])
with tab_c: render_issues(review.critical_issues,       "critical")
with tab_h: render_issues(review.high_priority_issues,  "high")
with tab_m: render_issues(review.medium_priority_issues,"medium")
with tab_l: render_issues(review.low_priority_issues,   "low")

st.divider()

# Detailed feedback
col_a, col_b = st.columns(2)
with col_a:
    if review.architecture_feedback:
        with st.expander("🏗️ Architecture Feedback"):
            render_bullet_list(review.architecture_feedback)
    if review.security_feedback:
        with st.expander("🔒 Security Review"):
            render_bullet_list(review.security_feedback)
    if review.code_smells:
        with st.expander("👃 Code Smells"):
            render_bullet_list(review.code_smells)

with col_b:
    if review.performance_feedback:
        with st.expander("⚡ Performance Review"):
            render_bullet_list(review.performance_feedback)
    if review.testing_feedback:
        with st.expander("🧪 Testing Recommendations"):
            render_bullet_list(review.testing_feedback)

st.divider()
st.subheader("💡 Recommendation")
st.info(review.recommendation)