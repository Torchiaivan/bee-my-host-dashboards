# Dark Mode Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign BeeMyHost Dashboards from light Airbnb style to dark mode analytics with lollipop charts and glowing KPI cards.

**Architecture:** Two files change — `app.py` (color constants, CSS, KPI card HTML, chart traces) and `.streamlit/config.toml` (dark theme base). No logic changes — `data_loader.py` and `ocupacion_calc.py` are untouched. All chart functions are replaced by a new `_lollipop_traces()` helper in `app.py`.

**Tech Stack:** Python 3.13, Streamlit, Plotly `graph_objects`

**Spec:** `docs/superpowers/specs/2026-04-15-dark-mode-redesign-design.md`

---

## Task 1: Dark theme base + color constants

**Files:**
- Modify: `.streamlit/config.toml`
- Modify: `app.py:15-25`

- [ ] **Step 1: Update config.toml to add dark theme**

Replace the full content of `.streamlit/config.toml` with:

```toml
[browser]
gatherUsageStats = false

[theme]
base = "dark"
primaryColor = "#FF385C"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"
```

- [ ] **Step 2: Replace color constants block in app.py**

Replace lines 15–25 (the `# ── Palette` block) with:

```python
# ── Palette (dark mode) ──────────────────────────────────────────────────────
C_PRIMARY    = "#FF385C"
C_PRIMARY_D  = "#E31C5F"
C_BG         = "#0f172a"
C_BG_SECTION = "#0f172a"
C_BG_CARD    = "#1e293b"
C_BG_SIDEBAR = "#0d1526"
C_TEXT       = "#f1f5f9"
C_TEXT_SEC   = "#64748b"
C_BORDER     = "#1e293b"
C_BORDER_MID = "#334155"
C_GREEN      = "#22c55e"
C_RED_SOFT   = "#f87171"
C_AMBER      = "#f59e0b"
C_BLUE       = "#38bdf8"
C_PURPLE     = "#a78bfa"
```

- [ ] **Step 3: Run the app to verify it starts without errors**

```bash
cd proyectos/bee-my-host-dashboards
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: app loads, background is dark, no Python errors in terminal.

- [ ] **Step 4: Commit**

```bash
git add .streamlit/config.toml app.py
git commit -m "feat: dark mode color constants and theme base"
```

---

## Task 2: CSS block rewrite

**Files:**
- Modify: `app.py:35-120` (the `st.markdown(f"""<style>...</style>""")` block)

- [ ] **Step 1: Replace the entire CSS st.markdown block**

Find the block starting with `st.markdown(f"""` and ending with `""", unsafe_allow_html=True)` (currently lines 35–120). Replace it entirely with:

```python
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
  [data-testid="stAppViewContainer"] {{ background: {C_BG}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: {C_BG_SIDEBAR} !important;
    border-right: 1px solid {C_BORDER} !important;
  }}
  [data-testid="stSidebar"] hr {{ border-color: {C_BORDER_MID}; }}
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div,
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] .stMarkdown,
  [data-testid="stSidebar"] .stCaption {{ color: {C_TEXT_SEC} !important; }}

  [data-testid="stSidebar"] [data-baseweb="select"] {{
    background-color: {C_BG_CARD} !important;
    border: 1px solid {C_BORDER_MID} !important;
    border-radius: 8px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] * {{
    background-color: {C_BG_CARD} !important;
    color: {C_TEXT} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] svg {{
    fill: {C_TEXT} !important;
  }}
  [data-testid="stSidebar"] button {{
    background-color: {C_PRIMARY} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
  }}

  h1, h2, h3 {{ color: {C_TEXT} !important; font-family: 'Inter', sans-serif !important; }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{ background: transparent; gap: 4px; }}
  .stTabs [data-baseweb="tab"] {{
    color: {C_TEXT_SEC} !important;
    font-weight: 600;
    font-size: 0.95rem;
    background: transparent;
    border-bottom: 3px solid transparent;
  }}
  .stTabs [aria-selected="true"] {{
    color: {C_PRIMARY} !important;
    border-bottom: 3px solid {C_PRIMARY} !important;
    background: transparent !important;
  }}
  .stTabs [data-baseweb="tab-highlight"] {{ background: {C_PRIMARY} !important; }}

  /* KPI cards */
  .bmh-card {{
    background: {C_BG_CARD};
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }}
  .bmh-val   {{ font-size: 2rem;  font-weight: 700; color: {C_TEXT};    line-height: 1.2; }}
  .bmh-icon  {{ font-size: 1.1rem; margin-bottom: 6px; }}
  .bmh-label {{ font-size: 0.82rem; color: {C_TEXT_SEC}; margin-top: 6px; }}
  .bmh-delta-pos {{ color: {C_GREEN};   font-size: 0.85rem; font-weight: 600; }}
  .bmh-delta-neg {{ color: {C_RED_SOFT}; font-size: 0.85rem; font-weight: 600; }}
  .bmh-delta-neu {{ color: {C_TEXT_SEC}; font-size: 0.85rem; }}

  /* Section titles */
  .section-title {{
    font-size: 1rem; font-weight: 600; color: {C_TEXT};
    margin: 32px 0 14px; padding-bottom: 6px;
    border-bottom: 2px solid {C_PRIMARY}; display: inline-block;
  }}

  /* Performance badge pills */
  .perf-excelente {{ background:#14532d; color:#22c55e; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-ajustar   {{ background:#78350f; color:#fbbf24; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-mejorar   {{ background:#7c2d12; color:#fb923c; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-revisar   {{ background:#7f1d1d; color:#f87171; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}

  .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)
```

- [ ] **Step 2: Run the app and verify visually**

```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: dark sidebar, dark background, red active tab, no light flickers on refresh.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: dark mode CSS — sidebar, tabs, cards, badges"
```

---

## Task 3: `_chart_layout` helper + `_lollipop_traces` helper

**Files:**
- Modify: `app.py` — replace `_chart_layout` and add `_lollipop_traces` in the `# ── Helpers` section (around line 122)

- [ ] **Step 1: Replace `_chart_layout` with dark version**

Find the existing `_chart_layout` function and replace it:

```python
def _chart_layout(height: int) -> dict:
    return dict(
        height=height,
        margin=dict(l=0, r=100, t=10, b=40),
        plot_bgcolor=C_BG,
        paper_bgcolor=C_BG,
        font=dict(family="Inter, sans-serif", color=C_TEXT_SEC),
    )
```

- [ ] **Step 2: Add `_lollipop_traces` helper immediately after `_chart_layout`**

```python
def _lollipop_traces(
    names: list[str],
    values: list[float],
    colors: list[str],
    suffix: str = "%",
) -> list:
    """
    Build a list of Plotly traces for a horizontal lollipop chart.
    Each entry produces two traces: a faint stem line + a glowing dot.
    `values` must already be in display units (e.g., multiply pct by 100 first).
    """
    traces = []
    for name, val, color in zip(names, values, colors):
        # Stem
        traces.append(go.Scatter(
            x=[0, val],
            y=[name, name],
            mode="lines",
            line=dict(color=color, width=2),
            opacity=0.35,
            showlegend=False,
            hoverinfo="skip",
        ))
        # Dot + label
        traces.append(go.Scatter(
            x=[val],
            y=[name],
            mode="markers+text",
            marker=dict(color=color, size=12, line=dict(color=color, width=0)),
            text=f"{val:.1f}{suffix}",
            textposition="middle right",
            textfont=dict(color=color, size=11, family="Inter, sans-serif"),
            hovertemplate=f"<b>{name}</b><br>{val:.1f}{suffix}<extra></extra>",
            showlegend=False,
        ))
    return traces
```

- [ ] **Step 3: Run the app to confirm no syntax errors**

```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: app loads cleanly. Charts still show as bars (helpers not yet wired up).

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: dark _chart_layout and _lollipop_traces helper"
```

---

## Task 4: KPI cards — Tab 1 (Ocupación general)

**Files:**
- Modify: `app.py` — the 4-column KPI block inside `with tab_ocup:` (around lines 226–240)

- [ ] **Step 1: Replace the 4-card loop with glow cards**

Find the block that starts with `c1, c2, c3, c4 = st.columns(4)` and the `for col, val, label, dh in [...]` loop inside `with tab_ocup:`. Replace it entirely:

```python
    c1, c2, c3, c4 = st.columns(4)
    cards_ocup = [
        (c1, f"{avg_act*100:.1f}%", "Ocupación promedio",       _delta_html(delta), "🏠", C_PRIMARY),
        (c2, str(n_deptos),         "Propiedades con reservas",  "",                 "📋", C_BLUE),
        (c3, str(n_full),           "Propiedades al 100%",       "",                 "✅", C_GREEN),
        (c4, str(n_over70),         "Propiedades ≥ 70%",         "",                 "🎯", C_PURPLE),
    ]
    for col, val, label, dh, icon, color in cards_ocup:
        with col:
            st.markdown(f"""
            <div class="bmh-card" style="border:1px solid {color}33; box-shadow:0 0 12px {color}22;">
              <div class="bmh-icon">{icon}</div>
              <div class="bmh-val" style="color:{color};">{val}</div>
              <div class="bmh-label">{label}</div>
              {dh}
            </div>""", unsafe_allow_html=True)
```

- [ ] **Step 2: Run the app and check Tab 1 KPI cards visually**

```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: 4 glowing cards with emoji icons. Ocupación in red, propiedades in blue, al 100% in green, ≥70% in purple.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: Tab 1 KPI cards — glow + emoji dark mode"
```

---

## Task 5: Charts Tab 1 — ocupación y responsable

**Files:**
- Modify: `app.py` — 3 chart sections inside `with tab_ocup:` (fig1, fig2, fig3)

- [ ] **Step 1: Replace fig1 (% ocupación por propiedad)**

Find the `fig1 = go.Figure(go.Bar(...))` block and replace it:

```python
        df_p = df_mes.sort_values("pct_ocupacion", ascending=True).copy()
        df_p["color"] = df_p["pct_ocupacion"].apply(_occ_color)
        vals   = (df_p["pct_ocupacion"] * 100).tolist()
        names  = df_p["nombre"].tolist()
        colors = df_p["color"].tolist()

        fig1 = go.Figure(_lollipop_traces(names, vals, colors, suffix="%"))
        fig1.add_vline(x=70, line_dash="dash", line_color=C_BORDER_MID,
                       annotation_text="meta 70%", annotation_position="top right",
                       annotation_font_color=C_TEXT_SEC)
        fig1.update_layout(
            xaxis=dict(title="% Ocupación", ticksuffix="%", range=[0, 130],
                       gridcolor=C_BORDER, zerolinecolor=C_BORDER_MID,
                       tickfont=dict(color=C_TEXT_SEC), title_font=dict(color=C_TEXT_SEC)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT_SEC)),
            **_chart_layout(max(420, len(df_p) * 32)),
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("🟢 ≥ 70% &nbsp;&nbsp; 🟡 50–70% &nbsp;&nbsp; 🔴 < 50%")
```

Note: delete the old `df_p` sort and `df_p["color"]` lines just above the old `fig1 = go.Figure(go.Bar(...))` if they appear separately — they are now included in the replacement block above.

- [ ] **Step 2: Replace fig2 (comparativa mes anterior)**

Find the `fig2 = go.Figure(go.Bar(...))` block and replace it:

```python
        df_c = df_comp.sort_values("delta", ascending=True).copy()
        df_c["color"] = df_c["delta"].apply(
            lambda x: C_GREEN if x > 0.01 else (C_RED_SOFT if x < -0.01 else C_BORDER_MID)
        )
        delta_vals = (df_c["delta"] * 100).tolist()
        names_c    = df_c["nombre"].tolist()
        colors_c   = df_c["color"].tolist()

        fig2 = go.Figure(_lollipop_traces(names_c, delta_vals, colors_c, suffix="pp"))
        # Add invisible hover-only scatter for rich tooltip (actual + anterior values)
        fig2.add_trace(go.Scatter(
            x=delta_vals,
            y=names_c,
            mode="markers",
            marker=dict(opacity=0, size=16),
            customdata=list(zip(
                (df_c["pct_actual"] * 100).round(1).astype(str) + "%",
                (df_c["pct_anterior"] * 100).round(1).astype(str) + "%",
            )),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{month_name}: %{{customdata[0]}}<br>"
                f"{prev_label}: %{{customdata[1]}}<br>"
                "Δ: %{x:.1f}pp<extra></extra>"
            ),
            showlegend=False,
        ))
        fig2.update_layout(
            xaxis=dict(title="Δ puntos porcentuales", ticksuffix="pp",
                       zeroline=True, zerolinecolor=C_TEXT_SEC, gridcolor=C_BORDER,
                       tickfont=dict(color=C_TEXT_SEC), title_font=dict(color=C_TEXT_SEC)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT_SEC)),
            **_chart_layout(max(420, len(df_c) * 32)),
        )
        st.plotly_chart(fig2, use_container_width=True)
```

Also delete the old `df_c` sort/color/label lines and `hover_actual`/`hover_anterior` lines that appear above the old `fig2 = go.Figure(go.Bar(...))`.

- [ ] **Step 3: Replace fig3 (por responsable)**

Find the `fig3 = go.Figure(go.Bar(...))` block and replace it:

```python
        df_r = df_resp.copy()
        df_r["avg_pct"] = (df_r["avg_ocupacion"] * 100).round(1)
        df_r["color"]   = df_r["avg_ocupacion"].apply(_occ_color)

        fig3 = go.Figure(_lollipop_traces(
            df_r["responsable"].tolist(),
            df_r["avg_pct"].tolist(),
            df_r["color"].tolist(),
            suffix="%",
        ))
        fig3.add_vline(x=70, line_dash="dash", line_color=C_BORDER_MID,
                       annotation_text="70%", annotation_position="top right",
                       annotation_font_color=C_TEXT_SEC)
        fig3.update_layout(
            xaxis=dict(title="% Ocupación promedio", ticksuffix="%",
                       range=[0, 130], gridcolor=C_BORDER,
                       tickfont=dict(color=C_TEXT_SEC), title_font=dict(color=C_TEXT_SEC)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT_SEC)),
            **_chart_layout(max(300, len(df_r) * 60)),
        )
        st.plotly_chart(fig3, use_container_width=True)
```

Delete the old `df_r` color/avg_pct lines that appeared above the old `fig3 = go.Figure(go.Bar(...))` if they're now duplicated.

- [ ] **Step 4: Run the app and verify Tab 1 charts visually**

```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: Tab 1 shows lollipop charts — faint stem lines with colored glowing dots at each property. Comparativa shows negative deltas going left. Reference line at 70%.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: Tab 1 lollipop charts — dark mode"
```

---

## Task 6: KPI cards + charts — Tab 2 (Reporte Individual)

**Files:**
- Modify: `app.py` — the full `with tab_ind:` block (from line ~376 to end of file)

- [ ] **Step 1: Replace the 4 performance KPI cards**

Find the `c1, c2, c3, c4 = st.columns(4)` block inside `with tab_ind:` (the one with `avg_ri`, `n_ri`, `n_excelente`, `n_revisar`). Replace:

```python
    c1, c2, c3, c4 = st.columns(4)
    cards_ind = [
        (c1, f"{avg_ri*100:.1f}%", "Ocupación promedio",    "🏠", C_PRIMARY),
        (c2, str(n_ri),            "Propiedades a cargo",    "📋", C_BLUE),
        (c3, str(n_excelente),     "Excelente (≥ 70%)",      "✅", C_GREEN),
        (c4, str(n_revisar),       "Revisar (< 40%)",        "⚠️", C_RED_SOFT),
    ]
    for col, val, label, icon, color in cards_ind:
        with col:
            st.markdown(f"""
            <div class="bmh-card" style="border:1px solid {color}33; box-shadow:0 0 12px {color}22;">
              <div class="bmh-icon">{icon}</div>
              <div class="bmh-val" style="color:{color};">{val}</div>
              <div class="bmh-label">{label}</div>
            </div>""", unsafe_allow_html=True)
```

- [ ] **Step 2: Replace the 3 cobro cards**

Find the `ca, cb, cc = st.columns(3)` block and the `for col, val, label in [...]` loop below it. Replace:

```python
    ca, cb, cc = st.columns(3)
    cards_cobro = [
        (ca, f"${sueldo_base:,.0f}", f"Sueldo base ({n_ri} deptos × $14.000)", "💰", C_TEXT_SEC),
        (cb, f"${total_bono:,.0f}",  "Bono por ocupación",                     "🎁", C_PURPLE),
        (cc, f"${total_mes:,.0f}",   "Total a cobrar en el mes",               "💵", C_GREEN),
    ]
    for col, val, label, icon, color in cards_cobro:
        with col:
            st.markdown(f"""
            <div class="bmh-card" style="border:1px solid {color}33; box-shadow:0 0 12px {color}22;">
              <div class="bmh-icon">{icon}</div>
              <div class="bmh-val" style="color:{color};">{val}</div>
              <div class="bmh-label">{label}</div>
            </div>""", unsafe_allow_html=True)
```

- [ ] **Step 3: Replace fig_ri (individual ocupación chart)**

Find `fig_ri = go.Figure(go.Bar(...))` and replace it:

```python
        df_ri_sorted = df_ri.sort_values("pct_ocupacion", ascending=True).copy()
        df_ri_sorted["color"] = df_ri_sorted["pct_ocupacion"].apply(_occ_color)

        fig_ri = go.Figure(_lollipop_traces(
            df_ri_sorted["nombre"].tolist(),
            (df_ri_sorted["pct_ocupacion"] * 100).tolist(),
            df_ri_sorted["color"].tolist(),
            suffix="%",
        ))
        fig_ri.add_vline(x=70, line_dash="dash", line_color=C_BORDER_MID,
                         annotation_text="meta 70%", annotation_position="top right",
                         annotation_font_color=C_TEXT_SEC)
        fig_ri.update_layout(
            xaxis=dict(title="% Ocupación", ticksuffix="%", range=[0, 130],
                       gridcolor=C_BORDER, zerolinecolor=C_BORDER_MID,
                       tickfont=dict(color=C_TEXT_SEC), title_font=dict(color=C_TEXT_SEC)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT_SEC)),
            **_chart_layout(max(320, len(df_ri_sorted) * 44)),
        )
        st.plotly_chart(fig_ri, use_container_width=True)
```

Delete the old `df_ri_sorted` sort and `df_ri_sorted["color"]` lines above the old `fig_ri` if they are now duplicated.

- [ ] **Step 4: Replace fig_rc (individual comparativa chart)**

Find `fig_rc = go.Figure(go.Bar(...))` inside the `if not df_ri_ant.empty:` block and replace it:

```python
            df_ri_c = df_ri_ant.sort_values("delta", ascending=True).copy()
            df_ri_c["color"] = df_ri_c["delta"].apply(
                lambda x: C_GREEN if x > 0.01 else (C_RED_SOFT if x < -0.01 else C_BORDER_MID)
            )
            delta_ri  = (df_ri_c["delta"] * 100).tolist()
            names_ri  = df_ri_c["nombre"].tolist()
            colors_ri = df_ri_c["color"].tolist()

            fig_rc = go.Figure(_lollipop_traces(names_ri, delta_ri, colors_ri, suffix="pp"))
            fig_rc.add_trace(go.Scatter(
                x=delta_ri,
                y=names_ri,
                mode="markers",
                marker=dict(opacity=0, size=16),
                customdata=list(zip(
                    (df_ri_c["pct_actual"] * 100).round(1).astype(str) + "%",
                    (df_ri_c["pct_anterior"] * 100).round(1).astype(str) + "%",
                )),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{month_name}: %{{customdata[0]}}<br>"
                    f"{prev_label}: %{{customdata[1]}}<br>"
                    "Δ: %{x:.1f}pp<extra></extra>"
                ),
                showlegend=False,
            ))
            fig_rc.update_layout(
                xaxis=dict(title="Δ puntos porcentuales", ticksuffix="pp",
                           zeroline=True, zerolinecolor=C_TEXT_SEC, gridcolor=C_BORDER,
                           tickfont=dict(color=C_TEXT_SEC), title_font=dict(color=C_TEXT_SEC)),
                yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT_SEC)),
                **_chart_layout(max(320, len(df_ri_c) * 44)),
            )
            st.plotly_chart(fig_rc, use_container_width=True)
```

Delete the old `df_ri_c` sort/color/label lines and old `fig_rc = go.Figure(go.Bar(...))` if now duplicated.

- [ ] **Step 5: Run the full app and verify Tab 2 visually**

```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Expected: Tab 2 shows glow cards (performance + cobro), lollipop charts for individual and comparativa. Select different responsables from the dropdown and confirm all render correctly.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat: Tab 2 dark mode — glow cards + lollipop charts"
```

---

## Task 7: Final visual pass + push

**Files:** None changed — review only.

- [ ] **Step 1: Open both tabs and verify the full dark mode experience**

Run:
```bash
C:/ProgramData/miniconda3/python.exe -m streamlit run app.py
```

Checklist:
- [ ] Background is `#0f172a` throughout
- [ ] Sidebar is `#0d1526` with dark selects
- [ ] All 4 KPI cards in Tab 1 show emoji + glow border
- [ ] All 3 KPI cards in Tab 1 (cobro) show emoji + glow border
- [ ] All charts in Tab 1 are lollipops with colored dots
- [ ] Comparativa chart handles negative deltas (line goes left)
- [ ] 70% reference line is visible as dashed grey
- [ ] Tab 2 individual report: same card and chart treatment
- [ ] Tables are dark (via Streamlit theme base)
- [ ] No white flash on page load
- [ ] Refresh button still red

- [ ] **Step 2: Commit final state**

```bash
git add -A
git commit -m "feat: BeeMyHost Dashboards dark mode redesign complete"
```
