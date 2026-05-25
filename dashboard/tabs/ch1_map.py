"""Chapter 1 — The Gap: where the worst regions are.

Advanced feature implemented here:
    Forecast scenario toggle (Tab A, year radio with 📈 Forecast option)
    User flips between real years and a 2025 projection that respects the
    scenario picked in the sidebar (Baseline / Aggressive aging / Stagnation).
    The shared `_project_df_to_2025` helper keeps Home, fullmap, and this
    chapter aligned on the same forecast surface.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tabs.utils import C, MMM_COLOURS, SCENARIO_GROWTH_RATES, chapter_breadcrumb, chapter_closer, project_pop_65_2025, theme, data_caption
from tabs import fullmap as pg_fullmap
from tabs.fullmap import _project_df_to_2025

MMM_ORDER  = ['MM1', 'MM2', 'MM3', 'MM4', 'MM5', 'MM6', 'MM7']
MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Small Rural', 'MM6': 'Remote Community', 'MM7': 'Very Remote',
}

# (col_name, worst_is_high, fmt, suffix, color)
_RANK_METRICS = {
    'Care Gap Index': ('care_gap_index', True,  ':.2f', '',   C['red']),
    'Quality Score':  ('quality_score',  False, ':.2f', '★',  C['teal']),
    'Residential Access Rate': ('access_rate', False, ':.1f', '%', '#3D6FA0'),
}


def render(df, gdf, supply, population, ratings, service_users=None) -> None:
    st.markdown(chapter_breadcrumb(1), unsafe_allow_html=True)
    st.markdown('<div class="sec-h1">Where do the patterns live?</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">Zoom into state and remoteness patterns, then trace the '
        'structural supply decline. The interactive map and SA3 search live on the '
        '<a href="?page=home" target="_self">Home</a> page.</p>',
        unsafe_allow_html=True,
    )

    tab_a, tab_b = st.tabs([
        "📊 Snapshot",
        "📉 Trend",
    ])

    # ════════════════════════════════════════════════════════════════════════════
    # TAB A — Overview: care gap · quality · access × state / MMM + Top N rankings
    # ════════════════════════════════════════════════════════════════════════════
    with tab_a:
        # Project to 2025 (idempotent if 2025 already present) — same pattern
        # as Home Find-My-Area so the scenario picker stays a single source of truth.
        if service_users is not None and supply is not None and population is not None:
            scenario = st.session_state.get('fm_scenario', list(SCENARIO_GROWTH_RATES.keys())[0])
            with st.spinner("Recomputing 2025 forecast..."):
                df = _project_df_to_2025(df, supply, service_users, ratings, population, scenario)

        _years = sorted(int(y) for y in df['year'].dropna().unique())
        _year_label = {y: (f"📈 Forecast {y}" if y == 2025 else str(y)) for y in _years}
        year_sel = st.radio(
            "Year",
            options=_years,
            format_func=lambda y: _year_label[y],
            index=len(_years) - 1,
            horizontal=True,
            key="a_year",
        )
        df_yr = df[df['year'] == year_sel].copy()

        if df_yr.empty:
            st.warning(
                "**No SA3s match your sidebar filter for this year.** "
                "Try expanding State or Remoteness in the left panel."
            )
        else:
            # ── KPI cards ──────────────────────────────────────────────────────
            k1, k2, k3 = st.columns(3)
            k1.metric("Avg Care Gap Index", f"{df_yr['care_gap_index'].mean():.2f}",
                      help="Higher = more underserved")
            k2.metric("Avg Quality Score", f"{df_yr['quality_score'].mean():.2f} ★",
                      help="Out of 5.0")
            k3.metric("Avg Residential Access", f"{df_yr['access_rate'].mean():.1f}%",
                      help="% of 65+ in residential care")

            top10 = df_yr.nlargest(10, 'care_gap_index')[
                ['sa3_name', 'state', 'mmm_code', 'care_gap_index']
            ]
            n_mm1 = int((top10['mmm_code'] == 'MM1').sum())
            nat_avg_cg = float(df_yr['care_gap_index'].mean())
            if not top10.empty and nat_avg_cg > 0:
                worst = top10.iloc[0]
                ratio = worst['care_gap_index'] / nat_avg_cg
                mm1_lead = (
                    f"All **{n_mm1} of the top 10** worst-performing SA3s are **MM1 — major city**. "
                    if n_mm1 == 10 else
                    f"**{n_mm1} of the top 10** worst-performing SA3s are **MM1 — major city**. "
                )
                st.warning(
                    mm1_lead +
                    f"{worst['sa3_name']} ({worst['state']}) has a care gap of "
                    f"**{worst['care_gap_index']:.2f}** — **{ratio:.1f}× the national average** "
                    f"in {year_sel}. The crisis is in the suburbs, not the outback."
                )

            # ── View toggle ────────────────────────────────────────────────────
            view_a = st.radio(
                "View by", ["By State", "By Remoteness (MMM)"],
                horizontal=True, key="a_view",
            )

            if view_a == "By State":
                grp = 'state'
                grp_label = 'State'
                plot_df = df_yr.copy()
            else:
                grp = 'mmm_code'
                grp_label = 'Remoteness'
                plot_df = df_yr.copy()
                plot_df['mmm_code'] = pd.Categorical(
                    plot_df['mmm_code'], categories=MMM_ORDER, ordered=True
                )

            # ── 3 metric bar charts — shared y-axis order (worst care gap at top) ─
            ref_order = (
                plot_df.groupby(grp, observed=True)['care_gap_index']
                .mean().sort_values(ascending=True)  # ascending = worst floats to top in horizontal bars
                .index.tolist()
            )
            bar_specs = [
                ('care_gap_index', f'Care Gap Index — {year_sel}',      C['red'],   '%{text:.2f}'),
                ('quality_score',  f'Quality Score — {year_sel}',       C['teal'],  '%{text:.2f}★'),
                ('access_rate',    f'Residential Access — {year_sel}',  '#3D6FA0',  '%{text:.1f}%'),
            ]

            # Build a single subplot figure with shared Y-axis (states/MMM listed once on left)
            if grp == 'mmm_code':
                y_categories = [MMM_LABELS.get(k, k) for k in ref_order]
            else:
                y_categories = ref_order

            fig = make_subplots(
                rows=1, cols=3, shared_yaxes=True,
                subplot_titles=[title for (_, title, _, _) in bar_specs],
                horizontal_spacing=0.04,
            )

            for col_idx, (metric, _, color, text_fmt) in enumerate(bar_specs, start=1):
                agg = plot_df.groupby(grp, observed=True)[metric].mean().reset_index()
                if grp == 'mmm_code':
                    agg['x_label'] = agg[grp].map(MMM_LABELS).fillna(agg[grp].astype(str))
                    agg['x_label'] = pd.Categorical(agg['x_label'], categories=y_categories, ordered=True)
                    agg = agg.sort_values('x_label')
                    y_vals = agg['x_label'].astype(str).tolist()
                else:
                    agg[grp] = pd.Categorical(agg[grp], categories=y_categories, ordered=True)
                    agg = agg.sort_values(grp)
                    y_vals = agg[grp].astype(str).tolist()

                fig.add_trace(
                    go.Bar(
                        x=agg[metric].tolist(),
                        y=y_vals,
                        orientation='h',
                        marker=dict(color=color),
                        text=agg[metric].tolist(),
                        texttemplate=text_fmt,
                        textposition='outside',
                        textfont=dict(size=14),
                        showlegend=False,
                        hovertemplate='%{y}: %{x:.2f}<extra></extra>',
                    ),
                    row=1, col=col_idx,
                )

            theme(fig, height=440)
            fig.update_layout(
                margin=dict(l=0, r=16, t=64, b=16),
                bargap=0.28,
                title_text="",
            )
            # Pad each x-axis a bit so the outside labels don't get clipped
            for col_idx in range(1, 4):
                fig.update_xaxes(automargin=True, row=1, col=col_idx)
            fig.update_yaxes(categoryorder='array', categoryarray=y_categories)

            st.plotly_chart(fig, use_container_width=True, key="a_bar_combined")
            st.markdown(data_caption("ABS Population SA3 2023–2024 · ACQSC Star Ratings (Feb 2026) · AIHW GEN residential"), unsafe_allow_html=True)

            mmm_q = (
                df_yr.dropna(subset=['mmm_code', 'quality_score'])
                .groupby('mmm_code')['quality_score'].mean()
            )
            state_acc = (
                df_yr.dropna(subset=['state', 'access_rate'])
                .groupby('state')['access_rate'].mean()
            )
            parts = []
            if len(mmm_q) >= 2:
                best_mmm = mmm_q.idxmax()
                worst_mmm = mmm_q.idxmin()
                parts.append(
                    f"**Remote paradox:** {MMM_LABELS.get(best_mmm, best_mmm)} ({best_mmm}) averages "
                    f"**{mmm_q[best_mmm]:.2f}★**, the highest of all bands, vs "
                    f"{MMM_LABELS.get(worst_mmm, worst_mmm)} ({worst_mmm}) at "
                    f"**{mmm_q[worst_mmm]:.2f}★**. "
                    "The remote disadvantage is **access**, not quality. "
                )
            if len(state_acc) >= 2:
                top_st = state_acc.idxmax()
                parts.append(
                    f"{top_st} has the highest access rate "
                    f"(**{state_acc[top_st]:.2f}%**) — driven by demand, not better supply."
                )
            if parts:
                st.info(''.join(parts))

            # Single-state context callout
            selected_states = df_yr['state'].dropna().unique()
            if len(selected_states) == 1:
                s = selected_states[0]
                s_cgi = df_yr['care_gap_index'].mean()
                nat_cgi = df[df['year'] == year_sel]['care_gap_index'].mean()
                direction = "above" if s_cgi > nat_cgi else "below"
                diff = abs(s_cgi - nat_cgi)
                st.info(
                    f"**{s}:** care gap index is **{s_cgi:.2f}** — "
                    f"{diff:.2f} pts {direction} the national average of {nat_cgi:.2f}."
                )

            # ── SA3 Rankings ───────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 🏆 SA3 Rankings")
            st.caption("⚠ Red bars = worst direction · ✓ Teal bars = best direction. Icons mean the same as colour — readable without seeing the hue.")

            rk1, rk2, rk3 = st.columns(3)
            with rk1:
                n_top = st.slider("Top N", 5, 30, 10, 5, key="rank_n")
            with rk2:
                rank_metric = st.selectbox(
                    "Metric", list(_RANK_METRICS.keys()), key="rank_metric",
                )
            with rk3:
                rank_dir = st.radio("Direction", ["Worst", "Best"], horizontal=True, key="rank_dir")

            col_name, worst_is_high, fmt_str, suffix, _ = _RANK_METRICS[rank_metric]
            use_largest = (rank_dir == "Worst") == worst_is_high
            bar_color = C['red'] if rank_dir == "Worst" else C['teal']

            if use_largest:
                ranked = df_yr.nlargest(n_top, col_name)[['sa3_name', 'state', col_name]].copy()
                ranked = ranked.sort_values(col_name)
            else:
                ranked = df_yr.nsmallest(n_top, col_name)[['sa3_name', 'state', col_name]].copy()
                ranked = ranked.sort_values(col_name, ascending=False)
            ranked['label'] = ranked['sa3_name'] + ' (' + ranked['state'] + ')'
            # Icon prefix on bar text so direction reads without colour.
            icon = '⚠ ' if rank_dir == 'Worst' else '✓ '
            ranked['text_with_icon'] = (
                icon + ranked[col_name].map(lambda v: f"{v:{fmt_str.lstrip(':')}}" + suffix)
            )

            fig_rank = px.bar(
                ranked, x=col_name, y='label', orientation='h',
                color_discrete_sequence=[bar_color], text='text_with_icon',
                title=f'Top {n_top} {rank_dir} — {rank_metric} ({year_sel})',
                labels={col_name: rank_metric, 'label': ''},
            )
            fig_rank.update_traces(
                texttemplate='%{text}', textposition='outside',
                textfont=dict(size=14),
            )
            theme(fig_rank, height=max(400, n_top * 48))
            st.plotly_chart(fig_rank, use_container_width=True, key="a_rank")
            st.markdown(data_caption(), unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════════
    # TAB B — The Decline: beds/1k + n_facilities (State or MMM)
    # ════════════════════════════════════════════════════════════════════════════
    with tab_b:
        st.caption("📍 *National context — these trends show all states and remoteness bands regardless of the sidebar filter.*")

        # ── Build state-level supply (2023–2025) ─────────────────────────────
        # n_facilities is REAL data for all 3 years (no pop dependency).
        # beds_per_1k = residential_places / pop_65_plus × 1000 — ABS pop only
        # goes to 2024, so we project pop_65 forward to 2025 using the sidebar
        # scenario so the line reaches 2025 (forecast for the 2024→2025 segment).
        DASH_MIN_YEAR = 2023
        _scenario = st.session_state.get('fm_scenario', list(SCENARIO_GROWTH_RATES.keys())[0])
        _pop_2025_wide = project_pop_65_2025(population, _scenario)
        _pop_2025 = _pop_2025_wide[['sa3_code', 'state', 'pop_65_plus_2025']].rename(
            columns={'pop_65_plus_2025': 'pop_65_plus'}
        )
        _pop_2025['year'] = 2025
        _population_full = pd.concat(
            [population[['sa3_code', 'year', 'pop_65_plus', 'state']], _pop_2025],
            ignore_index=True,
        )

        # Facilities frame — pure supply, no pop dependency (real 2023→2025)
        # supply.csv has no 'state' column — pull it from the master df (sa3→state map).
        _sa3_state = (
            df[['sa3_code', 'state']].dropna()
            .drop_duplicates('sa3_code')
        )
        state_facilities = (
            supply.merge(_sa3_state, on='sa3_code', how='inner')
            .groupby(['state', 'year'], as_index=False)
            .agg(n_facilities=('n_facilities', 'sum'))
        )

        # Beds-per-1k frame — needs pop (projected for 2025)
        state_supply = supply.merge(
            _population_full[['sa3_code', 'year', 'pop_65_plus', 'state']],
            on=['sa3_code', 'year'], how='inner',
        )
        state_supply = (
            state_supply.groupby(['state', 'year'], as_index=False)
            .agg(
                residential_places=('residential_places', 'sum'),
                pop_65_plus=('pop_65_plus', 'sum'),
            )
        )
        state_supply = state_supply[state_supply['pop_65_plus'] > 0].copy()
        state_supply['beds_per_1k'] = (
            state_supply['residential_places'] / state_supply['pop_65_plus'] * 1000
        )
        # Merge real facility counts back so both charts share the same frame
        state_supply = state_supply.merge(state_facilities, on=['state', 'year'], how='left')

        # ── Data-driven intro callout ─────────────────────────────────────────
        # Compute worst-mover state for each metric so the intro references the
        # exact states the reader sees on the charts below.
        _yr_base, _yr_end = 2023, int(state_supply['year'].max())
        _piv_beds = state_supply.pivot(index='state', columns='year', values='beds_per_1k')
        _piv_fac  = state_supply.pivot(index='state', columns='year', values='n_facilities')
        if _yr_base in _piv_beds.columns and _yr_end in _piv_beds.columns:
            _beds_pct = ((_piv_beds[_yr_end] - _piv_beds[_yr_base]) / _piv_beds[_yr_base] * 100).dropna()
            _fac_pct  = ((_piv_fac[_yr_end]  - _piv_fac[_yr_base])  / _piv_fac[_yr_base]  * 100).dropna()
            _beds_worst = _beds_pct.idxmin()
            _fac_worst  = _fac_pct.idxmin()
            _fac_best   = _fac_pct.idxmax()
            _n_fac_up   = int((_fac_pct > 0).sum())
            _n_fac_dn   = int((_fac_pct < 0).sum())
            st.info(
                f"📉 **Beds per 1,000 elderly fell in every state** from {_yr_base} → {_yr_end} "
                f"(worst: **{_beds_worst} {_beds_pct[_beds_worst]:+.1f}%**). "
                f"**Facility counts** moved in different directions — "
                f"**{_n_fac_up}** states added providers (led by **{_fac_best} {_fac_pct[_fac_best]:+.1f}%**) "
                f"while **{_n_fac_dn}** lost them (worst: **{_fac_worst} {_fac_pct[_fac_worst]:+.1f}%**). "
                f"Supply is shrinking *relative to the 65+ population*, not in raw facility count."
            )

        # ── Build MMM-level supply (2023–2025) ────────────────────────────────
        sa3_mmm = (
            df[['sa3_code', 'mmm_code']].dropna()
            .drop_duplicates('sa3_code', keep='last')
        )
        # MMM facilities — pure supply, no pop dependency
        mmm_fac_src = supply.merge(sa3_mmm, on='sa3_code', how='inner')
        mmm_fac = mmm_fac_src.groupby(['mmm_code', 'year'], as_index=False)['n_facilities'].sum()

        # MMM beds-per-1k — needs pop (projected for 2025)
        mmm_supply_src = supply.merge(
            _population_full[['sa3_code', 'year', 'pop_65_plus']],
            on=['sa3_code', 'year'], how='inner',
        ).merge(sa3_mmm, on='sa3_code', how='inner')
        mmm_supply_src = mmm_supply_src[mmm_supply_src['pop_65_plus'] > 0].copy()
        mmm_supply_src['beds_per_1k'] = (
            mmm_supply_src['residential_places'] / mmm_supply_src['pop_65_plus'] * 1000
        )
        mmm_beds = mmm_supply_src.groupby(['mmm_code', 'year'], as_index=False)['beds_per_1k'].mean()

        # ── View toggle (default State — matches the warning callout below) ──
        view_b = st.radio(
            "View by", ["By State", "By MMM"],
            horizontal=True, index=0, key="decline_view",
        )

        ch1, ch2 = st.columns(2)

        def _index_to_base(df_long, grp_col, val_col, base_year=DASH_MIN_YEAR):
            """Return a copy with val_col re-expressed as % change from base_year (base = 0%)."""
            base = (
                df_long[df_long['year'] == base_year][[grp_col, val_col]]
                .rename(columns={val_col: '_base'})
            )
            out = df_long.merge(base, on=grp_col, how='left')
            out[val_col] = (out[val_col] - out['_base']) / out['_base'] * 100
            return out.drop(columns='_base')

        def _force_year_ticks(fig, years):
            """Force integer year ticks — Plotly auto-inserts '2023.5' style
            half-ticks when there are only 2–3 data points."""
            yrs = sorted(int(y) for y in years)
            fig.update_xaxes(
                tickmode='array', tickvals=yrs,
                ticktext=[str(y) for y in yrs],
            )

        if view_b == "By State":
            beds_idx = _index_to_base(state_supply, 'state', 'beds_per_1k')
            fac_idx  = _index_to_base(state_supply, 'state', 'n_facilities')
            _yrs = beds_idx['year'].unique()

            with ch1:
                fig_beds = px.line(
                    beds_idx.sort_values('year'),
                    x='year', y='beds_per_1k', color='state', markers=True,
                    title='Beds per 1,000 elderly — % change from 2023 by State<br><sup>📈 2025 uses projected pop_65 (Baseline scenario)</sup>',
                    labels={'beds_per_1k': '% change vs 2023', 'year': '', 'state': ''},
                )
                fig_beds.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                _force_year_ticks(fig_beds, _yrs)
                theme(fig_beds, height=380)
                st.plotly_chart(fig_beds, use_container_width=True, key="b_beds_state")
                st.markdown(data_caption("AIHW GEN Aged Care Service List, 2023–2025 · ABS Population SA3"), unsafe_allow_html=True)
            with ch2:
                fig_fac = px.line(
                    fac_idx.sort_values('year'),
                    x='year', y='n_facilities', color='state', markers=True,
                    title='Number of Facilities — % change from 2023 by State',
                    labels={'n_facilities': '% change vs 2023', 'year': '', 'state': ''},
                )
                fig_fac.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                _force_year_ticks(fig_fac, _yrs)
                theme(fig_fac, height=380)
                st.plotly_chart(fig_fac, use_container_width=True, key="b_fac_state")
                st.markdown(data_caption("AIHW GEN Aged Care Service List, 2023–2025"), unsafe_allow_html=True)
        else:
            mmm_beds_idx = _index_to_base(mmm_beds, 'mmm_code', 'beds_per_1k')
            mmm_fac_idx  = _index_to_base(mmm_fac,  'mmm_code', 'n_facilities')
            label_order = [MMM_LABELS[m] for m in MMM_ORDER if m in mmm_beds_idx['mmm_code'].values]
            label_colours = {MMM_LABELS[k]: v for k, v in MMM_COLOURS.items()}
            for _df in [mmm_beds_idx, mmm_fac_idx]:
                _df['mmm_label'] = pd.Categorical(
                    _df['mmm_code'].map(MMM_LABELS),
                    categories=label_order, ordered=True,
                )
            _yrs = mmm_beds_idx['year'].unique()

            with ch1:
                fig_beds = px.line(
                    mmm_beds_idx.sort_values(['mmm_label', 'year']),
                    x='year', y='beds_per_1k', color='mmm_label',
                    color_discrete_map=label_colours, markers=True,
                    title='Beds per 1,000 elderly — % change from 2023 by Remoteness<br><sup>📈 2025 uses projected pop_65 (Baseline scenario)</sup>',
                    labels={'beds_per_1k': '% change vs 2023', 'year': '', 'mmm_label': ''},
                )
                fig_beds.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                _force_year_ticks(fig_beds, _yrs)
                theme(fig_beds, height=380)
                st.plotly_chart(fig_beds, use_container_width=True, key="b_beds_mmm")
                st.markdown(data_caption("AIHW GEN Aged Care Service List, 2023–2025 · ABS MMM remoteness"), unsafe_allow_html=True)
            with ch2:
                fig_fac = px.line(
                    mmm_fac_idx.sort_values(['mmm_label', 'year']),
                    x='year', y='n_facilities', color='mmm_label',
                    color_discrete_map=label_colours, markers=True,
                    title='Number of Facilities — % change from 2023 by Remoteness',
                    labels={'n_facilities': '% change vs 2023', 'year': '', 'mmm_label': ''},
                )
                fig_fac.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                _force_year_ticks(fig_fac, _yrs)
                theme(fig_fac, height=380)
                st.plotly_chart(fig_fac, use_container_width=True, key="b_fac_mmm")
                st.markdown(data_caption("AIHW GEN Aged Care Service List, 2023–2025 · ABS MMM remoteness"), unsafe_allow_html=True)

        # National beds-per-1k delta — used by the chapter_closer takeaways
        nat_grp = state_supply.groupby('year').agg(
            rp=('residential_places', 'sum'),
            pp=('pop_65_plus', 'sum'),
        )
        nat_grp['b1k'] = nat_grp['rp'] / nat_grp['pp'] * 1000
        nat_y0, nat_y1 = int(nat_grp.index.min()), int(nat_grp.index.max())
        nat_pct = (nat_grp.loc[nat_y0, 'b1k'] - nat_grp.loc[nat_y1, 'b1k']) / nat_grp.loc[nat_y0, 'b1k'] * 100

    # ── Chapter closer: takeaways + next chapter CTA ──────────────────────────
    st.markdown(
        chapter_closer(1, [
            "The worst care gaps cluster in <b>major cities</b>, not the outback — "
            "all top-10 worst SA3s are MM1 metro suburbs.",
            "Remote bands (MM5–MM7) actually score the <b>highest</b> on quality — "
            "the rural penalty is access, not care quality.",
            f"Beds per 1,000 elderly fell <b>{nat_pct:.1f}%</b> nationally "
            f"({nat_y0}→{nat_y1}) — supply is contracting while demand grows.",
        ]),
        unsafe_allow_html=True,
    )

