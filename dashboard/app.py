import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Inject custom CSS ─────────────────────────────────────────────────────────
with open("dashboard/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    path = "data/jobs_processed.csv" if os.path.exists("data/jobs_processed.csv") else "data/sample_jobs.csv"
    df = pd.read_csv(path)
    def parse_skills(val):
        if isinstance(val, str) and val:
            return [s.strip() for s in val.split(",") if s.strip()]
        return []
    df["skills_found"] = df["skills_str"].apply(parse_skills)
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🔎 Filters")
all_terms = ["All"] + sorted(df["search_term"].dropna().unique().tolist())
selected_term = st.sidebar.selectbox("Job Category", all_terms)
all_locations = ["All"] + sorted(df["location"].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("Location", all_locations)

filtered_df = df.copy()
if selected_term != "All":
    filtered_df = filtered_df[filtered_df["search_term"] == selected_term]
if selected_location != "All":
    filtered_df = filtered_df[filtered_df["location"] == selected_location]

def get_skill_counts(dataframe, top_n=20):
    all_skills = []
    for skills in dataframe["skills_found"]:
        all_skills.extend(skills)
    counts = Counter(all_skills)
    return pd.DataFrame(counts.most_common(top_n), columns=["Skill", "Count"])

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem;'>
        <h1 style='font-size:2.8rem; font-weight:800;
                   background: linear-gradient(90deg, #00d4ff, #ffffff);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;'>
            📊 Job Market Intelligence
        </h1>
        <p style='color:rgba(255,255,255,0.5); font-size:1rem; margin-top:-0.5rem;'>
            Real-time skill demand analysis from live job postings
        </p>
    </div>
""", unsafe_allow_html=True)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Overview",
    "🔍 Skill Explorer",
    "⚖️ Role Comparison",
    "🎯 Skill Gap Analyser"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs Scraped",   len(df))
    col2.metric("Jobs in View",         len(filtered_df))
    col3.metric("Unique Companies",     filtered_df["company"].nunique())
    col4.metric("Avg Skills / Posting", f"{filtered_df['skill_count'].mean():.1f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top 20 In-Demand Skills")
        skill_df = get_skill_counts(filtered_df, 20)
        if not skill_df.empty:
            fig = px.bar(
                skill_df, x="Count", y="Skill",
                orientation="h",
                color="Count",
                color_continuous_scale="Blues",
                title="Skill Frequency in Job Postings"
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                height=500,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skill data for this filter.")

    with col_right:
        st.subheader("Jobs by Category")
        cat_counts = df["search_term"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig2 = px.pie(
            cat_counts, values="Count", names="Category",
            title="Distribution of Job Categories",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Top Hiring Companies")
        top_companies = (filtered_df["company"]
                         .value_counts()
                         .head(10)
                         .reset_index())
        top_companies.columns = ["Company", "Openings"]
        st.dataframe(top_companies, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — SKILL EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🔍 Explore a Specific Skill")
    st.markdown("Pick any skill to see which roles demand it most.")

    all_skills_flat = []
    for s in df["skills_found"]:
        all_skills_flat.extend(s)
    unique_skills = sorted(set(all_skills_flat))

    selected_skill = st.selectbox("Choose a skill", unique_skills)

    if selected_skill:
        skill_jobs = df[df["skills_found"].apply(lambda x: selected_skill in x)]

        col1, col2 = st.columns(2)
        col1.metric("Jobs requiring this skill", len(skill_jobs))
        col2.metric("% of all jobs", f"{len(skill_jobs)/len(df)*100:.1f}%")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Top roles asking for this skill**")
            role_counts = skill_jobs["search_term"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]
            fig3 = px.bar(
                role_counts, x="Role", y="Count",
                color="Count",
                color_continuous_scale="Blues"
            )
            fig3.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col_b:
            st.markdown("**Skills most often paired with this skill**")
            paired = []
            for skills in skill_jobs["skills_found"]:
                for s in skills:
                    if s != selected_skill:
                        paired.append(s)
            paired_df = pd.DataFrame(
                Counter(paired).most_common(10),
                columns=["Paired Skill", "Count"]
            )
            fig4 = px.bar(
                paired_df, x="Count", y="Paired Skill",
                orientation="h",
                color="Count",
                color_continuous_scale="Teal"
            )
            fig4.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("**Sample job postings requiring this skill**")
        sample = skill_jobs[["title", "company", "location", "skills_str"]].head(10)
        st.dataframe(sample, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ROLE COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("⚖️ Compare Two Job Roles Side by Side")

    roles = sorted(df["search_term"].dropna().unique().tolist())
    col1, col2 = st.columns(2)
    role_a = col1.selectbox("Role A", roles, index=0)
    role_b = col2.selectbox("Role B", roles, index=1)

    df_a = df[df["search_term"] == role_a]
    df_b = df[df["search_term"] == role_b]

    skills_a = Counter()
    skills_b = Counter()
    for s in df_a["skills_found"]: skills_a.update(s)
    for s in df_b["skills_found"]: skills_b.update(s)

    top_a = dict(skills_a.most_common(15))
    top_b = dict(skills_b.most_common(15))
    all_keys = sorted(set(list(top_a.keys()) + list(top_b.keys())))

    compare_df = pd.DataFrame({
        "Skill": all_keys,
        role_a:  [top_a.get(k, 0) for k in all_keys],
        role_b:  [top_b.get(k, 0) for k in all_keys],
    })

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        name=role_a, x=compare_df["Skill"],
        y=compare_df[role_a], marker_color="#00d4ff"
    ))
    fig5.add_trace(go.Bar(
        name=role_b, x=compare_df["Skill"],
        y=compare_df[role_b], marker_color="#ff7f0e"
    ))
    fig5.update_layout(
        barmode="group",
        title="Skill Demand Comparison",
        xaxis_tickangle=-45,
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig5, use_container_width=True)

    set_a = set(top_a.keys())
    set_b = set(top_b.keys())
    overlap = set_a & set_b
    only_a  = set_a - set_b
    only_b  = set_b - set_a

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**✅ Shared skills ({len(overlap)})**")
    c1.write(", ".join(sorted(overlap)) or "None")
    c2.markdown(f"**🔵 Only in {role_a} ({len(only_a)})**")
    c2.write(", ".join(sorted(only_a)) or "None")
    c3.markdown(f"**🟠 Only in {role_b} ({len(only_b)})**")
    c3.write(", ".join(sorted(only_b)) or "None")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — SKILL GAP ANALYSER
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("🎯 Your Personal Skill Gap Analyser")
    st.markdown("Enter the skills you already have and pick a target role "
                "— we'll show you exactly what you're missing.")

    your_skills_input = st.text_area(
        "Enter your skills (comma separated)",
        placeholder="e.g. python, sql, excel, machine learning, git"
    )

    target_role = st.selectbox("Target Role", roles)

    if st.button("Analyse My Skill Gap 🚀") and your_skills_input:
        your_skills = {s.strip().lower()
                       for s in your_skills_input.split(",") if s.strip()}

        role_df = df[df["search_term"] == target_role]
        role_skill_counts = Counter()
        for s in role_df["skills_found"]:
            role_skill_counts.update(s)

        top_role_skills = dict(role_skill_counts.most_common(20))

        have    = {s for s in top_role_skills if s in your_skills}
        missing = {s for s in top_role_skills if s not in your_skills}

        col1, col2 = st.columns(2)
        col1.metric("Skills you already have", f"{len(have)} / 20")
        col2.metric("Skills to learn",          len(missing))

        st.progress(len(have) / 20)
        st.caption(f"You match {len(have)/20*100:.0f}% of top skills "
                   f"for **{target_role}** roles")

        col_have, col_miss = st.columns(2)

        with col_have:
            st.markdown("### ✅ Skills You Have")
            for skill in sorted(have):
                demand = top_role_skills[skill]
                st.success(f"**{skill}** — mentioned in {demand} postings")

        with col_miss:
            st.markdown("### ❌ Skills to Learn")
            missing_sorted = sorted(
                missing, key=lambda x: top_role_skills[x], reverse=True)
            for skill in missing_sorted:
                demand = top_role_skills[skill]
                st.error(f"**{skill}** — mentioned in {demand} postings")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Data sourced from RemoteOK API · Built with Python, spaCy & Streamlit")