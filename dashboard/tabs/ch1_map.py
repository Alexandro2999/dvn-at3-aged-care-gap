import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from tabs.utils import C, MMM_COLOURS, theme
from tabs import fullmap as pg_fullmap

MMM_ORDER  = ['MM1', 'MM2', 'MM3', 'MM4', 'MM5', 'MM6', 'MM7']
MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Small Rural', 'MM6': 'Remote Community', 'MM7': 'Very Remote',
}

# (col_name, worst_is_high, fmt, suffix, color)
_RANK_METRICS = {
    'Care Gap Index': ('care_gap_index', True,  ':.2f', '',   C['red']),
    'Quality Score':  ('quality_score',  False, ':.2f', '★',  C['teal']),
    'Residential Access Rate': ('access_rate', False, ':.1f', '%', '#4A7FC1'),
}


def render(df, gdf, supply, population, ratings, service_users=None) -> None:
    st.markdown('<div class="sec-h1">Where do the patterns live?</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">Zoom into state and remoteness patterns, then trace the '
        'structural supply decline. The interactive map and SA3 search live on the '
        '<a href="?page=home" target="_self">Home</a> page.</p>',
        unsafe_allow_html=True,
    )

    tab_a, tab_b = st.tabs([
        "📊 The Overview",
        "📉 The Decline",
    ])

    # ════════════════════════════════════════════════════════════════════════════
    # TAB A — Overview: care gap · quality · access × state / MMM + Top N rankings
    # ════════════════════════════════════════════════════════════════════════════
    with tab_a:
        year_sel = st.radio(
            "Year", [2023, 2024], index=1, horizontal=True, key="a_year",
        )
        df_yr = df[df['year'] == year_sel].copy()

        if df_yr.empty:
            st.info("No data for current filter.")
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
                ('access_rate',    f'Residential Access — {year_sel}',  '#4A7FC1',  '%{text:.1f}%'),
            ]
            c1, c2, c3 = st.columns(3)
            for widget_col, (metric, title, color, text_fmt) in zip([c1, c2, c3], bar_specs):
                agg = plot_df.groupby(grp, observed=True)[metric].mean().reset_index()
                if grp == 'mmm_code':
                    agg['x_label'] = agg[grp].map(MMM_LABELS).fillna(agg[grp].astype(str))
                    label_order = [MMM_LABELS.get(k, k) for k in ref_order]
                    agg['x_label'] = pd.Categorical(agg['x_label'], categories=label_order, ordered=True)
                    agg = agg.sort_values('x_label')
                    y_col = 'x_label'
                else:
                    agg[grp] = pd.Categorical(agg[grp], categories=ref_order, ordered=True)
                    agg = agg.sort_values(grp)
                    y_col = grp
                fig = px.bar(
                    agg, x=metric, y=y_col, orientation='h',
                    color_discrete_sequence=[color], text=metric,
                    title=title, labels={metric: '', y_col: ''},
                )
                fig.update_traces(
                    texttemplate=text_fmt, textposition='outside',
                    textfont=dict(size=11),
                )
                theme(fig, height=420)
                widget_col.plotly_chart(fig, use_container_width=True, key=f"a_bar_{metric}")

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

            fig_rank = px.bar(
                ranked, x=col_name, y='label', orientation='h',
                color_discrete_sequence=[bar_color], text=col_name,
                title=f'Top {n_top} {rank_dir} — {rank_metric} ({year_sel})',
                labels={col_name: rank_metric, 'label': ''},
            )
            fig_rank.update_traces(
                texttemplate=f'%{{text{fmt_str}}}{suffix}', textposition='outside',
                textfont=dict(size=11),
            )
            theme(fig_rank, height=max(400, n_top * 48))
            st.plotly_chart(fig_rank, use_container_width=True, key="a_rank")


    # ════════════════════════════════════════════════════════════════════════════
    # TAB B — The Decline: beds/1k + n_facilities (State or MMM)
    # ════════════════════════════════════════════════════════════════════════════
    with tab_b:
        st.info(
            "Beds per 1,000 elderly **fell in every state** while the total number of facilities "
            "consolidated year on year. Supply is shrinking as the elderly population grows."
        )

        # ── Build state-level supply (2019–2025) ──────────────────────────────
        state_supply = supply.merge(
            population[['sa3_code', 'year', 'pop_65_plus', 'state']],
            on=['sa3_code', 'year'], how='inner',
        )
        state_supply = (
            state_supply.groupby(['state', 'year'], as_index=False)
            .agg(
                residential_places=('residential_places', 'sum'),
                pop_65_plus=('pop_65_plus', 'sum'),
                n_facilities=('n_facilities', 'sum'),
            )
        )
        state_supply = state_supply[state_supply['pop_65_plus'] > 0].copy()
        state_supply['beds_per_1k'] = (
            state_supply['residential_places'] / state_supply['pop_65_plus'] * 1000
        )

        # ── Build MMM-level supply ─────────────────────────────────────────────
        # mmm_code is treated as static per SA3 — join without year constraint
        # so all supply years (2019–2025) are included, not just df years (2023–2024)
        sa3_mmm = (
            df[['sa3_code', 'mmm_code']].dropna()
            .drop_duplicates('sa3_code', keep='last')
        )
        mmm_supply_src = supply.merge(
            population[['sa3_code', 'year', 'pop_65_plus']],
            on=['sa3_code', 'year'], how='inner',
        ).merge(sa3_mmm, on='sa3_code', how='inner')
        mmm_supply_src = mmm_supply_src[mmm_supply_src['pop_65_plus'] > 0].copy()
        mmm_supply_src['beds_per_1k'] = (
            mmm_supply_src['residential_places'] / mmm_supply_src['pop_65_plus'] * 1000
        )
        mmm_beds = mmm_supply_src.groupby(['mmm_code', 'year'], as_index=False)['beds_per_1k'].mean()
        mmm_fac  = mmm_supply_src.groupby(['mmm_code', 'year'], as_index=False)['n_facilities'].sum()

        # ── View toggle ───────────────────────────────────────────────────────
        view_b = st.radio("View by", ["By State", "By MMM"], horizontal=True, key="decline_view")

        ch1, ch2 = st.columns(2)

        def _index_to_base(df_long, grp_col, val_col, base_year=2019):
            """Return a copy with val_col re-expressed as % change from base_year (base = 0%)."""
            base = (
                df_long[df_long['year'] == base_year][[grp_col, val_col]]
                .rename(columns={val_col: '_base'})
            )
            out = df_long.merge(base, on=grp_col, how='left')
            out[val_col] = (out[val_col] - out['_base']) / out['_base'] * 100
            return out.drop(columns='_base')

        if view_b == "By State":
            beds_idx = _index_to_base(state_supply, 'state', 'beds_per_1k')
            fac_idx  = _index_to_base(state_supply, 'state', 'n_facilities')

            with ch1:
                fig_beds = px.line(
                    beds_idx.sort_values('year'),
                    x='year', y='beds_per_1k', color='state', markers=True,
                    title='Beds per 1,000 elderly — % change from 2019 by State',
                    labels={'beds_per_1k': '% change vs 2019', 'year': '', 'state': ''},
                )
                fig_beds.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                theme(fig_beds, height=380)
                st.plotly_chart(fig_beds, use_container_width=True, key="b_beds_state")
            with ch2:
                fig_fac = px.line(
                    fac_idx.sort_values('year'),
                    x='year', y='n_facilities', color='state', markers=True,
                    title='Number of Facilities — % change from 2019 by State',
                    labels={'n_facilities': '% change vs 2019', 'year': '', 'state': ''},
                )
                fig_fac.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                theme(fig_fac, height=380)
                st.plotly_chart(fig_fac, use_container_width=True, key="b_fac_state")
        else:
            mmm_beds_idx = _index_to_base(mmm_beds, 'mmm_code', 'beds_per_1k')
            mmm_fac_idx  = _index_to_base(mmm_fac,  'mmm_code', 'n_facilities')
            # Add full labels and preserve sort order
            label_order = [MMM_LABELS[m] for m in MMM_ORDER if m in mmm_beds_idx['mmm_code'].values]
            label_colours = {MMM_LABELS[k]: v for k, v in MMM_COLOURS.items()}
            for _df in [mmm_beds_idx, mmm_fac_idx]:
                _df['mmm_label'] = pd.Categorical(
                    _df['mmm_code'].map(MMM_LABELS),
                    categories=label_order, ordered=True,
                )

            with ch1:
                fig_beds = px.line(
                    mmm_beds_idx.sort_values(['mmm_label', 'year']),
                    x='year', y='beds_per_1k', color='mmm_label',
                    color_discrete_map=label_colours, markers=True,
                    title='Beds per 1,000 elderly — % change from 2019 by Remoteness',
                    labels={'beds_per_1k': '% change vs 2019', 'year': '', 'mmm_label': ''},
                )
                fig_beds.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                theme(fig_beds, height=380)
                st.plotly_chart(fig_beds, use_container_width=True, key="b_beds_mmm")
            with ch2:
                fig_fac = px.line(
                    mmm_fac_idx.sort_values(['mmm_label', 'year']),
                    x='year', y='n_facilities', color='mmm_label',
                    color_discrete_map=label_colours, markers=True,
                    title='Number of Facilities — % change from 2019 by Remoteness',
                    labels={'n_facilities': '% change vs 2019', 'year': '', 'mmm_label': ''},
                )
                fig_fac.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
                theme(fig_fac, height=380)
                st.plotly_chart(fig_fac, use_container_width=True, key="b_fac_mmm")

        sup_grp = supply.groupby('year').agg(
            n_fac=('n_residential', 'sum'),
            n_bed=('residential_places', 'sum'),
        )
        sup_y0, sup_y1 = int(sup_grp.index.min()), int(sup_grp.index.max())
        fac_delta = int(sup_grp.loc[sup_y1, 'n_fac'] - sup_grp.loc[sup_y0, 'n_fac'])
        bed_delta = int(sup_grp.loc[sup_y1, 'n_bed'] - sup_grp.loc[sup_y0, 'n_bed'])

        ss_piv = state_supply.pivot(index='state', columns='year', values='beds_per_1k')
        ss_y0, ss_y1 = int(ss_piv.columns.min()), int(ss_piv.columns.max())
        ss_piv['delta'] = ss_piv[ss_y1] - ss_piv[ss_y0]
        n_lost = int((ss_piv['delta'] < 0).sum())
        n_states = len(ss_piv)
        worst2 = ss_piv['delta'].nsmallest(2)
        coverage_lead = (
            "Every state" if n_lost == n_states
            else f"{n_lost} of {n_states} states/territories"
        )

        nat_grp = state_supply.groupby('year').agg(
            rp=('residential_places', 'sum'),
            pp=('pop_65_plus', 'sum'),
        )
        nat_grp['b1k'] = nat_grp['rp'] / nat_grp['pp'] * 1000
        nat_y0, nat_y1 = int(nat_grp.index.min()), int(nat_grp.index.max())
        nat_pct = (nat_grp.loc[nat_y0, 'b1k'] - nat_grp.loc[nat_y1, 'b1k']) / nat_grp.loc[nat_y0, 'b1k'] * 100

        st.warning(
            f"**Supply consolidation:** {sup_y0}→{sup_y1} saw "
            f"**{fac_delta:+d} facilities** but **{bed_delta:+,} beds** nationally. "
            f"{coverage_lead} lost beds per 1,000 elderly — "
            f"{worst2.index[0]} and {worst2.index[1]} fell the most "
            f"({worst2.iloc[0]:.1f} and {worst2.iloc[1]:.1f}). "
            f"Beds per 1,000 elderly dropped from **{nat_grp.loc[nat_y0, 'b1k']:.1f}** ({nat_y0}) to "
            f"**{nat_grp.loc[nat_y1, 'b1k']:.1f}** ({nat_y1}), a **{nat_pct:.1f}% decline** "
            f"over {nat_y1 - nat_y0} years (denominator: pop 65+)."
        )

