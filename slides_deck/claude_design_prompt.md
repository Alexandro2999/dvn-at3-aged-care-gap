# Claude Design Prompt — AT3 Pitch Deck (11 slides)

**How to use:** Copy the **Master prompt** below into Claude (with Canva design tools enabled), then append **one per-slide brief** at a time. Save each returned PNG to the filename indicated.

**Compositing order in Canva (bottom → top):**
1. Claude design from `slides_deck/images/claude_designs/S{N}_*.png` (background + chrome)
2. Chart PNG from `slides_deck/assets/S{N}_*.png` (if applicable — S3, S4, S5, S6, S7, S8, S11)
3. Dashboard screencap from `slides_deck/images/dashboard_screencaps/` (S9, S10 only)
4. Headline + body text (composed natively in Canva — never bake text into PNGs)

---

## Master prompt

```
You are designing one 1920×1080 slide background for an academic data-storytelling pitch deck.

# Project
"Australia's Aged Care Gap" — DVN AT3, UTS MDSI Autumn 2026.
A 5-minute live pitch using the "Detective Arc": Map → Cause → Reveal → Tool → Verdict.
Stakeholder lens: CEO of a Not-For-Profit aged-care provider, asking "where to expand?"

# Locked design system (do NOT deviate)
Palette — use a maximum of 3 of these hex values per slide:
- Navy        #1B3F6E    primary brand / dark backgrounds
- Navy-deep   #122B4E    inset blocks on navy slides
- Teal        #00A79D    government / solution / demo accent
- Gold        #F5C842    annotation / mandate / transition / highlight
- Red         #D94F3D    for-profit / urgency / crisis
- Blue-mid    #4A7FC1    not-for-profit
- Blue-lite   #E3F1FA    soft section background
- Red-lite    #FDECEA    pale red accent
- Teal-lite   #E0F5F3    pale teal accent

Typography — Montserrat Bold 800 for heads, Inter 400/600 for body.
**DO NOT render any text in the design.** Headlines and body copy are composed natively in Canva afterwards.

Border-accent system (every slide carries one 6–8 px accent bar on left edge):
- Navy accent → S1, S3, S4, S10, S11
- Teal accent → S5, S9
- Gold accent → S2
- Red  accent → S6, S7, S8

# Hard constraints
1. Exact 1920×1080 px (16:9), PNG.
2. No text, no axes, no chart elements, no numbers.
3. No stock photography or AI-generated photographic imagery of people.
4. No clichéd corporate imagery: handshakes, lightbulbs, gears, generic elderly stock photos, jigsaw pieces, growth arrows.
5. No emoji.
6. Minimum 40% negative space. One focal idea per slide.
7. If using human figures: silhouettes only, no faces, no skin tones.
8. Asymmetric composition preferred over centered.
9. Editorial restraint: prefer 1 strong shape over 5 decorative ones.

# Per-slide brief
[paste the per-slide brief from below here]
```

---

## Per-slide briefs — paste ONE at a time under the master prompt

### S1 — Title hero

```
- Slide: S1 (title)
- Border accent: Gold (8px left edge)
- Background fill: Navy #1B3F6E full-bleed
- Mood: opening, sober, slightly ominous
- Overlay later: headline text only
- Brief: Generate a single Australia continent silhouette in Teal #00A79D at 8% opacity,
  positioned 30% right-of-centre, 50% vertical scale. Subtle radial Gold #F5C842 glow
  fading from bottom-left quadrant to mid-canvas at 15% intensity. Nothing else.
- Reserved zones: top 40% empty (headline), bottom 18% empty (footer band).
- Filename: S1_title.png
```

### S2 — Stakeholder hat persona card

```
- Slide: S2 (persona)
- Border accent: Gold
- Background fill: Blue-lite #E3F1FA
- Mood: confident, leadership
- Overlay later: persona Navy card + 3 Teal audience cards (composed in Canva)
- Brief: A single minimalist top-hat silhouette in Gold #F5C842, drawn as a clean
  6px stroke line-art outline, ~360×280 px, positioned 50% horizontal, 32% vertical.
  No face, no body. Behind the hat, a faint Teal #00A79D abstract halo at 6% opacity.
- Reserved zones: top 18% empty, bottom 55% empty (where 3 cards go).
- Filename: S2_stakeholder.png
```

### S3 — Hook (Australia map with red/gold zones)

```
- Slide: S3 (hook reveal)
- Border accent: Gold
- Background fill: Navy #1B3F6E full-bleed + dark inset Navy-deep #122B4E bottom 35%
- Mood: confrontational, surprising
- Overlay later: assets/S3_australia_silhouette.png (the labelled map from notebook)
- Brief: Generate ONLY the slide chrome — the dark inset block at the bottom 35%
  filled Navy-deep #122B4E with a 2px Gold #F5C842 top divider. Mid-slide ~50%
  height empty (the labelled silhouette PNG goes there). Top 25% empty for headline.
  No additional decoration — the inserted map carries the visual weight.
- Filename: S3_hook.png
```

### S4 — Map payoff

```
- Slide: S4 (Ch1 reveal)
- Border accent: Navy (8px left)
- Background fill: White with subtle Blue-lite #E3F1FA at 20% opacity in lower-right quadrant
- Mood: analytical, factual
- Overlay later: assets/S4_choropleth_caregap_2024.png (left 55%) + table panel (right 45%, Canva-built)
- Brief: A clean white slide with one design element: a 4px Red #D94F3D horizontal alert
  strip at the very bottom 4% of slide. A vertical 1px Blue-mid #4A7FC1 divider at
  the 55% column break (separating map from table). Top 18% empty for headline bar.
- Filename: S4_map.png
```

### S5 — Correlation (3 ownership lines)

```
- Slide: S5 (Ch2 part 1)
- Border accent: Navy
- Background fill: very pale Grey-100 #F7F9FB
- Mood: analytical, steady
- Overlay later: 3 stat boxes (Canva) + assets/S5_ownership_trend_12q.png (full width, bottom 65%)
- Brief: A clean pale-grey slide. Three faint vertical guide lines at 12%, 50%, 88% horizontal
  (where the 3 stat boxes will sit), drawn in Teal #00A79D / Blue-mid #4A7FC1 / Red #D94F3D
  respectively at 4% opacity (almost invisible — they're alignment marks for Canva).
  Top 18% empty for headline.
- Filename: S5_correlation.png
```

### S6 — Funding paradox

```
- Slide: S6 (Ch2 part 2)
- Border accent: Red (4px top — urgency mode begins)
- Background fill: White
- Mood: confrontational, paradoxical
- Overlay later: Navy body card (Canva, left 45%) + assets/S6_funding_quality_scatter.png (right 55%)
- Brief: A clean white slide with a 4px Red #D94F3D top accent strip (signals shift to
  urgency tone). Behind the right 55% (where the scatter will be), a faint Red-lite
  #FDECEA gradient bleed at 30% opacity radiating from centre-right. Nothing else.
- Filename: S6_funding_paradox.png
```

### S7 — Human cost

```
- Slide: S7 (Ch3 part 1)
- Border accent: Red
- Background fill: White with Red-lite #FDECEA dominant on left 40%
- Mood: urgent, emotional
- Overlay later: huge "3.1 / 1 bed" callout (Canva text) + assets/S7_waitlist_top10_2024.png (right 55%)
- Brief: Split slide visually: left 40% filled Red-lite #FDECEA, right 60% white. At the
  vertical seam between them (~40% horizontal), a 2px Red #D94F3D vertical accent line
  extending top-to-bottom. In the left zone, draw 3 small silhouette figures of standing
  people (max 60px tall each) above 1 simple bed silhouette — all in Red #D94F3D outlines
  at 4px line weight, positioned ~50% vertical in the left zone. No faces.
- Filename: S7_human_cost.png
```

### S8 — Supply failure

```
- Slide: S8 (Ch3 part 2)
- Border accent: Red
- Background fill: White
- Mood: revealing, urgent
- Overlay later: 2 colour contrast cards (Red-lite left / Teal-lite right, Canva) + assets/S8_supply_divergence_indexed.png (bottom)
- Brief: A clean white slide split into top 35% (where the contrast cards will go) and
  bottom 65% (where the chart will go). At the seam between them, a 1px Gold #F5C842
  horizontal divider line. In the top 35%, two soft background zones: Red-lite #FDECEA
  on left half, Teal-lite #E0F5F3 on right half, with a 24px gap between them. Top 14%
  empty for headline.
- Filename: S8_supply_failure.png
```

### S9 — Tool demo (4 features)

```
- Slide: S9 (demo)
- Border accent: Teal (top 4px — solution mode)
- Background fill: Blue-lite #E3F1FA
- Mood: technical, confident, modern
- Overlay later: 4 dashboard screencaps in 2×2 grid (from images/dashboard_screencaps/)
- Brief: Generate a 2×2 grid frame ONLY — four empty rectangular containers (each ~720×370 px),
  arranged in a 2×2 layout with 32px gaps between them, positioned centred in the slide.
  Each container has a 3px Teal #00A79D border, 12px corner radius, and a small Gold
  #F5C842 filled circle (~40px diameter) in its top-right corner (with empty centre — the
  number 1/2/3/4 will be added in Canva). Add a 4px Gold #F5C842 horizontal accent strip
  at the very top edge of the slide. Top 18% empty for headline.
- Filename: S9_tool_demo.png
```

### S10 — Forecast (dual map)

```
- Slide: S10 (Ch5)
- Border accent: Navy
- Background fill: White
- Mood: analytical, forward-looking, transparent
- Overlay later: 2 dashboard screencaps (S10_LEFT, S10_RIGHT) + scenario radio + KPI strip
- Brief: A clean white slide with two reserved rectangular regions for the dual maps
  (each ~830×460 px), separated by a 24px gap at slide centre. In the centre gap,
  a large bold Gold #F5C842 right-arrow symbol (→), drawn as a single chunky filled
  shape ~80px wide and ~50px tall, vertically centred. At the bottom 18%, a faint
  Grey-100 #F7F9FB band (where the 3-cell KPI strip will be composed in Canva).
  Top 16% empty for headline.
- Filename: S10_forecast.png
```

### S11 — Verdict + CTA

```
- Slide: S11 (closing — bookends S1)
- Border accent: Navy (full slide)
- Background fill: Navy #1B3F6E full-bleed
- Mood: closing, decisive, hopeful
- Overlay later: 4 bullet block (Canva text, left 60%) + assets/S11_quality_timeline_oct2023.png (right 40%) + Teal CTA stripe
- Brief: Full-bleed Navy slide. At the bottom 22%, a solid Teal #00A79D horizontal band
  (this is where the CTA text goes in Canva — the band is the brightest object on the
  slide). Above it, the body region is plain Navy — only one design element: a 1px
  Gold #F5C842 vertical divider at the 60% horizontal mark (separating bullets from
  chart). Top 18% empty for headline.
- Filename: S11_verdict.png
```

---

## Iteration tips

1. **Start with S1 and S11** — they bookend the deck. If the tone is wrong on bookends, every other slide will feel off.
2. **One slide at a time.** Don't batch — Claude needs the per-slide context.
3. **If Claude inserts text** (sometimes happens against instruction): re-prompt with *"Remove all text from the design — text is composed in Canva separately."*
4. **If Claude uses default colours** instead of the locked palette: re-prompt with *"Use only these exact hex values: [paste palette]. Do not use any other colour."*
5. **Tone consistency check** — at the end, view all 11 designs in a 3×4 grid (Canva has "view all pages") and verify the palette and weight feel like one deck.

---

## Folder destinations

| Asset type | Folder |
|------------|--------|
| Code-generated chart PNGs (S3–S8, S11) | `slides_deck/assets/` ← already populated by `visual_for_slides.ipynb` |
| Claude design PNGs (S1–S11) | `slides_deck/images/claude_designs/` |
| Manual dashboard screencaps (S9, S10) | `slides_deck/images/dashboard_screencaps/` |
| Final Canva exports (PDF + PNG per slide) | `slides_deck/images/final_exports/` |
