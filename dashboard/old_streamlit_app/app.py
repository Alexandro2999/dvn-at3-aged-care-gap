import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aged Care Gap — Australia",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

MANDATE_DATE = "2023-10-01"
MANDATE_TS   = pd.Timestamp(MANDATE_DATE).timestamp() * 1000

MMM_LABELS = {
    "MM1": "MM1 Major city",
    "MM2": "MM2 Regional centre",
    "MM3": "MM3 Large rural",
    "MM4": "MM4 Medium rural",
    "MM5": "MM5 Small rural",
    "MM6": "MM6 Remote",
    "MM7": "MM7 Very remote",
}
ORG_COLOURS = {
    "profit":       "#F58518",
    "not_for_profit":"#4C78A8",
    "government":   "#72B7B2",
}

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_master():
    df = pd.read_csv("../data/clean/master_sa3.csv")
    df["mmm_label"] = df["mmm_code"].map(MMM_LABELS).fillna(df["mmm_code"])
    return df

@st.cache_data
def load_ratings():
    df = pd.read_csv("../data/clean/star_ratings_by_facility.csv",
                     parse_dates=["snapshot_date"])
    df["org_type"] = df["Purpose"].map({
        "For profit":     "profit",
        "Not for profit": "not_for_profit",
        "Government":     "government",
    }).fillna("unknown")
    df["mmm_num"]   = df["mmm_code"].str.extract(r"(\d)").astype(float)
    df["sa3_key"]   = pd.to_numeric(df["sa3_code"], errors="coerce")
    df = df[df["sa3_key"].notna()].copy()
    df["sa3_key"]   = df["sa3_key"].astype(int).astype(str)
    df["mmm_label"] = df["mmm_code"].map(MMM_LABELS).fillna(df["mmm_code"])
    return df

@st.cache_data
def load_supply():
    return pd.read_csv("../data/clean/service_supply_by_sa3.csv")

@st.cache_data
def load_users():
    return pd.read_csv("../data/clean/service_users_by_sa3.csv")

master  = load_master()
ratings = load_ratings()
supply  = load_supply()
users   = load_users()

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.title("Filters")

all_states = sorted(master["state"].dropna().unique())
sel_states = st.sidebar.multiselect("State / Territory", all_states, default=all_states)

all_years = sorted(master["year"].unique())
sel_year  = st.sidebar.selectbox("Year (SA3 metrics)", all_years, index=len(all_years) - 1)

all_mmm = [v for k, v in MMM_LABELS.items() if k in master["mmm_label"].values or
           v in master["mmm_label"].values]
all_mmm = sorted(master["mmm_label"].dropna().unique(),
                 key=lambda x: int(x[2]) if len(x) > 2 and x[2].isdigit() else 9)
sel_mmm = st.sidebar.multiselect("Remoteness (MMM)", all_mmm, default=all_mmm)

# Filtered slices
m_yr  = master[(master["year"] == sel_year) &
               (master["state"].isin(sel_states)) &
               (master["mmm_label"].isin(sel_mmm))]
r_flt = ratings[(ratings["state"].isin(sel_states))]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🔍 The Aged Care Gap — Australia")
st.markdown(
    "**Which Australian regions have the worst gap between aged care quality and access — and why?**  \n"
    "*National overview → state comparison → SA3-level reveal*"
)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 National Snapshot",
    "📈 The Trend",
    "🔍 The Correlation",
    "⚠️ The Reveal",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — National Snapshot
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"National Snapshot — {sel_year}")

    latest_supply = supply[supply["year"] == sel_year]
    latest_users  = users[users["year"]   == sel_year]
    latest_rat    = ratings[ratings["snapshot_date"].dt.year == sel_year]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Residential facilities", f"{latest_supply['n_residential'].sum():,.0f}")
    c2.metric("Licensed beds",          f"{latest_supply['residential_places'].sum():,.0f}")
    c3.metric("Residential users",      f"{latest_users['total_residential'].sum():,.0f}")
    c4.metric("HCP high-needs (L3+L4)", f"{latest_users['hcp_high_needs'].sum():,.0f}")
    c5.metric("Avg quality score",      f"{latest_rat['quality_score'].mean():.2f} / 5")

    st.divider()
    col_a, col_b = st.columns(2)

    # Org type pie
    with col_a:
        org_counts = pd.DataFrame({
            "label": ["Not for profit", "Government", "Private"],
            "count": [latest_supply["n_nfp"].sum(),
                      latest_supply["n_government"].sum(),
                      latest_supply["n_private"].sum()],
        })
        fig = px.pie(
            org_counts, values="count", names="label",
            title="Facility ownership mix (latest year)",
            color="label",
            color_discrete_map={"Not for profit":"#4C78A8","Government":"#72B7B2","Private":"#F58518"},
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # HCP level breakdown
    with col_b:
        hcp_trend = users.groupby("year")[["hcp_level1","hcp_level2","hcp_level3","hcp_level4"]].sum().reset_index()
        hcp_melt  = hcp_trend.melt(id_vars="year", var_name="level", value_name="users")
        hcp_melt["level"] = hcp_melt["level"].str.replace("hcp_level","Level ")
        fig = px.bar(
            hcp_melt, x="year", y="users", color="level", barmode="stack",
            title="Home care users by HCP level (national)",
            labels={"users":"Users","year":"Year","level":"HCP Level"},
            color_discrete_sequence=px.colors.sequential.Blues[2:],
        )
        fig.update_layout(height=350, legend_title="HCP Level")
        st.plotly_chart(fig, use_container_width=True)

    # Demand explosion callout
    hcp_2023 = users[users["year"]==2023]["hcp_high_needs"].sum()
    hcp_late  = users[users["year"]==users["year"].max()]["hcp_high_needs"].sum()
    pct_change = (hcp_late - hcp_2023) / hcp_2023 * 100
    st.info(
        f"**Demand explosion:** HCP high-needs users (Level 3+4) grew "
        f"from **{hcp_2023:,.0f}** (2023) → **{hcp_late:,.0f}** ({users['year'].max()}) "
        f"— a **+{pct_change:.0f}%** increase in just {users['year'].max()-2023} year(s). "
        f"They now represent **{hcp_late/users[users['year']==users['year'].max()]['total_homecare'].sum()*100:.0f}%** "
        f"of all home care users."
    )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — The Trend
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Quality Over Time — Did the Oct 2023 Staffing Mandate Work?")

    subtab_a, subtab_b, subtab_c = st.tabs(["By state","By org type","Sub-dimensions"])

    with subtab_a:
        qual_time = (r_flt.groupby(["snapshot_date","state"])["quality_score"]
                     .mean().reset_index())
        fig = px.line(
            qual_time, x="snapshot_date", y="quality_score", color="state",
            title="Average quality score by state over time",
            labels={"quality_score":"Avg quality score","snapshot_date":"Quarter"},
            markers=True,
        )
        fig.add_vline(x=MANDATE_TS, line_dash="dash", line_color="red",
                      annotation_text="Oct 2023 staffing mandate",
                      annotation_position="top right")
        fig.update_layout(yaxis_range=[2.8, 4.5], height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Before / after bar
        MANDATE = pd.Timestamp(MANDATE_DATE)
        r_flt2 = r_flt.copy()
        r_flt2["period"] = r_flt2["snapshot_date"].apply(
            lambda d: "After mandate" if d >= MANDATE else "Before mandate")
        mandate_df = (r_flt2.groupby(["state","period"])["quality_score"]
                      .mean().reset_index())
        fig2 = px.bar(
            mandate_df, x="state", y="quality_score", color="period",
            barmode="group",
            title="Quality score before vs after Oct 2023 mandate",
            labels={"quality_score":"Avg quality score"},
            color_discrete_map={"Before mandate":"#aec7e8","After mandate":"#1f77b4"},
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

        before = r_flt2[r_flt2["period"]=="Before mandate"]["quality_score"].mean()
        after  = r_flt2[r_flt2["period"]=="After mandate"]["quality_score"].mean()
        st.success(
            f"**Mandate worked:** national avg quality rose from **{before:.2f} → {after:.2f}** "
            f"(+{after-before:.2f} pts, +{(after-before)/before*100:.1f}%) after Oct 2023."
        )

    with subtab_b:
        qual_org = (r_flt[r_flt["org_type"] != "unknown"]
                    .groupby(["snapshot_date","org_type"])["quality_score"]
                    .mean().reset_index())
        fig = px.line(
            qual_org, x="snapshot_date", y="quality_score", color="org_type",
            title="Quality score by org type over time",
            labels={"quality_score":"Avg quality score","snapshot_date":"Quarter","org_type":"Org type"},
            color_discrete_map=ORG_COLOURS, markers=True,
        )
        fig.add_vline(x=MANDATE_TS, line_dash="dash", line_color="red",
                      annotation_text="Oct 2023 mandate")
        fig.update_layout(yaxis_range=[2.5, 4.8], height=430)
        st.plotly_chart(fig, use_container_width=True)

        latest_snap = r_flt["snapshot_date"].max()
        latest_r    = r_flt[r_flt["snapshot_date"] == latest_snap]
        gov_q  = latest_r[latest_r["org_type"]=="government"]["quality_score"].mean()
        prof_q = latest_r[latest_r["org_type"]=="profit"]["quality_score"].mean()
        st.warning(
            f"**For-profit gap:** government facilities average **{gov_q:.2f}** vs "
            f"for-profit **{prof_q:.2f}** — a gap of **{gov_q-prof_q:.2f} pts** "
            f"({latest_snap.strftime('%B %Y')})."
        )

    with subtab_c:
        dims = ["residents_exp","staffing","compliance","quality_measures"]
        dim_labels = {
            "residents_exp":  "Residents experience",
            "staffing":       "Staffing",
            "compliance":     "Compliance",
            "quality_measures":"Quality measures",
        }
        MANDATE = pd.Timestamp(MANDATE_DATE)
        sub_records = []
        for d in dims:
            b = r_flt[r_flt["snapshot_date"] < MANDATE][d].mean()
            a = r_flt[r_flt["snapshot_date"] >= MANDATE][d].mean()
            sub_records.append({"dimension": dim_labels[d], "before": b, "after": a, "change": a - b})
        sub_df = pd.DataFrame(sub_records).sort_values("change", ascending=False)

        fig = px.bar(
            sub_df.melt(id_vars="dimension", value_vars=["before","after"],
                        var_name="period", value_name="score"),
            x="dimension", y="score", color="period", barmode="group",
            title="Sub-rating change before vs after Oct 2023 mandate",
            labels={"score":"Avg score","dimension":"Sub-rating"},
            color_discrete_map={"before":"#aec7e8","after":"#1f77b4"},
        )
        fig.update_layout(yaxis_range=[2.0, 5.0], height=400)
        st.plotly_chart(fig, use_container_width=True)

        staffing_delta = sub_df[sub_df["dimension"]=="Staffing"]["change"].values[0]
        qm_delta       = sub_df[sub_df["dimension"]=="Quality measures"]["change"].values[0]
        st.info(
            f"**Staffing was the target — and it moved.** Staffing sub-rating jumped "
            f"**+{staffing_delta:.2f} pts** — the largest gain of any dimension. "
            f"Quality measures barely changed ({qm_delta:+.3f} pts), suggesting the mandate "
            f"improved inputs (staff hours) but hasn't yet translated to better outcomes."
        )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — The Correlation
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Access Rate vs Quality — Where is the System Stretched?")

    scatter_data = m_yr.dropna(subset=["access_rate","avg_quality","pop_65_plus"])

    col1, col2 = st.columns([3, 1])
    with col2:
        colour_by = st.radio("Colour by", ["MMM remoteness","State","Org type mix"])

    if colour_by == "MMM remoteness":
        colour_col = "mmm_label"
        cat_order  = {"mmm_label": [v for v in MMM_LABELS.values() if v in scatter_data["mmm_label"].values]}
    elif colour_by == "State":
        colour_col = "state"
        cat_order  = {}
    else:
        scatter_data = scatter_data.copy()
        scatter_data["dominant_org"] = np.select(
            [scatter_data["n_private"] >= scatter_data[["n_nfp","n_government","n_private"]].max(axis=1),
             scatter_data["n_nfp"]     >= scatter_data[["n_nfp","n_government","n_private"]].max(axis=1)],
            ["Mostly private","Mostly NFP"], default="Mostly government"
        )
        colour_col = "dominant_org"
        cat_order  = {}

    with col1:
        fig = px.scatter(
            scatter_data,
            x="access_rate", y="avg_quality",
            size="pop_65_plus",
            color=colour_col,
            hover_name="sa3_name",
            hover_data={
                "state": True,
                "access_rate": ":.1f",
                "avg_quality": ":.2f",
                "pop_65_plus": ":,",
                "beds_per_1000_elderly": ":.1f",
            },
            trendline="ols",
            title=f"Access rate vs quality score by SA3 — {sel_year}",
            labels={
                "access_rate":  "Access rate (% of 65+ in residential care)",
                "avg_quality":  "Avg quality score",
                "pop_65_plus":  "65+ population",
            },
            opacity=0.7,
            **({} if not cat_order else {"category_orders": cat_order}),
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Quality by MMM band
    st.markdown("#### Quality by remoteness — the counterintuitive finding")
    mmm_order = [v for v in MMM_LABELS.values() if v in r_flt["mmm_label"].values]
    latest_r  = r_flt[r_flt["snapshot_date"] == r_flt["snapshot_date"].max()]
    fig2 = px.box(
        latest_r.dropna(subset=["mmm_label"]),
        x="mmm_label", y="quality_score", color="mmm_label",
        category_orders={"mmm_label": mmm_order},
        title=f"Quality score by remoteness class ({r_flt['snapshot_date'].max().strftime('%B %Y')})",
        labels={"quality_score":"Quality score","mmm_label":"Remoteness"},
        points="outliers",
    )
    fig2.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig2, use_container_width=True)

    city_q   = latest_r[latest_r["mmm_code"]=="MM1"]["quality_score"].mean()
    rural_q  = latest_r[latest_r["mmm_code"]=="MM5"]["quality_score"].mean()
    st.success(
        f"**Counterintuitive:** remote areas score *higher* than cities. "
        f"MM5 Small rural averages **{rural_q:.2f}** vs MM1 Major city **{city_q:.2f}**. "
        f"Reason: remote facilities are 100% government-run; cities skew for-profit. "
        f"The real remote penalty is **access** (fewer beds), not quality."
    )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — The Reveal
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("The Reveal — Which Communities Are Being Left Behind?")

    subtab_1, subtab_2, subtab_3 = st.tabs([
        "Top 20 worst SA3",
        "Waitlist pressure",
        "Supply change",
    ])

    with subtab_1:
        worst = (m_yr.dropna(subset=["care_gap_index"])
                 .nlargest(20, "care_gap_index")
                 .sort_values("care_gap_index"))
        fig = px.bar(
            worst, x="care_gap_index", y="sa3_name", orientation="h",
            color="state",
            hover_data={"access_rate":":.1f","avg_quality":":.2f","pop_65_plus":":,"},
            title=f"Top 20 SA3 regions by Care Gap Index — {sel_year}",
            labels={"care_gap_index":"Care Gap Index","sa3_name":""},
        )
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Sub-rating breakdown for these SA3s**")
        worst10 = worst.tail(10)["sa3_code"].tolist()
        worst_detail = (
            ratings[ratings["sa3_key"].isin(worst10)]
            .groupby("sa3_name")[["residents_exp","staffing","compliance","quality_measures"]]
            .mean().reset_index()
            .melt(id_vars="sa3_name", var_name="dimension", value_name="score")
        )
        if not worst_detail.empty:
            fig2 = px.bar(
                worst_detail, x="score", y="sa3_name", color="dimension",
                barmode="group", orientation="h",
                title="Sub-rating breakdown — top 10 worst SA3s by care gap",
                labels={"score":"Avg score","sa3_name":"SA3"},
            )
            fig2.update_layout(height=450)
            st.plotly_chart(fig2, use_container_width=True)

    with subtab_2:
        latest_m = master[master["year"] == master["year"].max()].copy()
        top_pressure = (latest_m.dropna(subset=["waitlist_pressure"])
                        .nlargest(20, "waitlist_pressure")
                        .sort_values("waitlist_pressure"))
        fig = px.bar(
            top_pressure, x="waitlist_pressure", y="sa3_name", orientation="h",
            color="state",
            hover_data={"hcp_high_needs":":,","residential_places":":,"},
            title="Top 20 SA3 regions by waitlist pressure (HCP L3+L4 per residential place)",
            labels={"waitlist_pressure":"HCP high-needs per residential place","sa3_name":""},
        )
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        worst_sa3 = top_pressure.iloc[-1]
        st.warning(
            f"**{worst_sa3['sa3_name']}** has **{worst_sa3['waitlist_pressure']:.0f}** "
            f"high-needs HCP users per residential place — meaning people who need "
            f"high-level care are stuck at home with almost no residential capacity nearby."
        )

    with subtab_3:
        supply_2019 = supply[supply["year"]==2019][["sa3_code","sa3_name","n_residential"]].rename(
            columns={"n_residential":"res_2019"})
        supply_late = supply[supply["year"]==supply["year"].max()][["sa3_code","sa3_name","n_residential"]].rename(
            columns={"n_residential":"res_latest"})
        supply_chg = supply_2019.merge(supply_late, on=["sa3_code","sa3_name"], how="inner")
        supply_chg["change"] = supply_chg["res_latest"] - supply_chg["res_2019"]

        lost   = supply_chg[supply_chg["change"] < 0].sort_values("change")
        gained = supply_chg[supply_chg["change"] > 0].sort_values("change", ascending=False)

        ca, cb, cc = st.columns(3)
        ca.metric("SA3s that LOST facilities",   len(lost),   delta=f"-{len(lost)}",  delta_color="inverse")
        cb.metric("SA3s that GAINED facilities", len(gained), delta=f"+{len(gained)}")
        cc.metric("SA3s unchanged",              len(supply_chg[supply_chg["change"]==0]))

        fig = px.bar(
            lost.head(20), x="change", y="sa3_name", orientation="h",
            title=f"Top 20 SA3 regions that lost the most residential facilities (2019 → {supply['year'].max()})",
            labels={"change":"Change in facilities","sa3_name":"SA3"},
            color="change", color_continuous_scale="Reds_r",
        )
        fig.update_layout(height=500, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
