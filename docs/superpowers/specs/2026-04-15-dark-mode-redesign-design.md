# Design Spec — BeeMyHost Dashboards Dark Mode Redesign
**Date:** 2026-04-15  
**Status:** Approved

---

## Summary

Full visual redesign of the BeeMyHost Dashboards Streamlit app from a light Airbnb-style theme to a dark mode "analytics control room" aesthetic. Scope covers color palette, KPI cards, charts, sidebar, tabs, and tables. No functional changes — data logic, calculations, and tab structure remain untouched.

---

## Design Decisions (user-selected)

| Element | Choice |
|---|---|
| Visual direction | Dark Mode — `#0f172a` base, neon accents |
| KPI cards | Glow + emoji icons, colored border per card |
| Chart type | Lollipop (line + glowing dot, horizontal) |
| Navigation | Keep Streamlit sidebar, dark-styled |

---

## Color Palette

| Token | Old | New |
|---|---|---|
| `C_BG` | `#FFFFFF` | `#0f172a` |
| `C_BG_SECTION` | `#F7F7F7` | `#0f172a` |
| `C_BG_CARD` | `#FFFFFF` | `#1e293b` |
| `C_BG_SIDEBAR` | `#FFFFFF` | `#0d1526` |
| `C_TEXT` | `#222222` | `#f1f5f9` |
| `C_TEXT_SEC` | `#717171` | `#64748b` |
| `C_BORDER` | `#EBEBEB` | `#1e293b` |
| `C_PRIMARY` | `#FF385C` | `#FF385C` (unchanged) |
| `C_GREEN` | `#16a34a` | `#22c55e` |
| `C_AMBER` | `#f59e0b` | `#f59e0b` (unchanged) |
| `C_RED_SOFT` | `#ef4444` | `#f87171` |

New tokens needed:
- `C_BG_CARD = "#1e293b"` — card surface
- `C_BG_SIDEBAR = "#0d1526"` — sidebar surface
- `C_BORDER_SUBTLE = "#334155"` — widget borders inside sidebar

---

## KPI Cards

Each card:
- Background: `C_BG_CARD` (`#1e293b`)
- Border: `1px solid {color}33` (color at 20% opacity)
- Box-shadow: `0 0 12px {color}22` (subtle glow)
- Emoji icon above the metric value
- Value: `#f1f5f9`, font-size `2rem`, font-weight `700`
- Label: `#64748b`, font-size `0.82rem`
- Delta (where applicable): `#22c55e` positive / `#f87171` negative

**Tab 1 — Ocupación General (4 cards):**
| Card | Color | Emoji |
|---|---|---|
| Ocupación promedio | `#FF385C` | 🏠 |
| Propiedades con reservas | `#38bdf8` | 📋 |
| Al 100% | `#22c55e` | ✅ |
| ≥ 70% | `#a78bfa` | 🎯 |

**Tab 2 — Reporte Individual (4 performance cards):**
| Card | Color | Emoji |
|---|---|---|
| Ocupación promedio | `#FF385C` | 🏠 |
| Propiedades a cargo | `#38bdf8` | 📋 |
| Excelente (≥70%) | `#22c55e` | ✅ |
| Revisar (<40%) | `#f87171` | ⚠️ |

**Tab 2 — Cobro del mes (3 cards):**
| Card | Color | Emoji |
|---|---|---|
| Sueldo base | `#64748b` | 💰 |
| Bono por ocupación | `#a78bfa` | 🎁 |
| Total a cobrar | `#22c55e` | 💵 |

---

## Charts — Lollipop Horizontal

Replace all `go.Bar` traces with a two-trace lollipop pattern:

```python
# Trace 1: horizontal line (stem)
go.Scatter(
    x=[0, value],
    y=[name, name],
    mode="lines",
    line=dict(color=color, width=2),
    opacity=0.4,
    showlegend=False,
)

# Trace 2: endpoint dot
go.Scatter(
    x=[value],
    y=[name],
    mode="markers",
    marker=dict(
        color=color,
        size=12,
        line=dict(color=color, width=2),
    ),
    text=f"{value:.1f}%",
    textposition="middle right",
    showlegend=False,
)
```

Each property gets its own pair of traces. Color per performance threshold (green/amber/red) is unchanged.

**Negative deltas (comparativa chart):** `x=[0, delta]` works correctly with negative values — Plotly draws the line leftward. Color logic stays: green if delta > 0.01, red if delta < -0.01, `C_BORDER_SUBTLE` otherwise.

**Helper function:** Extract `_lollipop_traces(df, x_col, y_col, color_col, text_col)` returning a list of traces. Used by all 4 chart sections.

**Chart backgrounds:**
- `plot_bgcolor = "#0f172a"`
- `paper_bgcolor = "#0f172a"`
- Grid lines: `#1e293b`
- Axis text: `#94a3b8`

**Reference line (70% goal):** `add_vline` with `line_color="#334155"`, `line_dash="dash"`, annotation in `#64748b`.

Applies to all charts:
1. % Ocupación por propiedad (Tab 1)
2. Comparativa mes anterior (Tab 1)
3. Por responsable (Tab 1)
4. Ocupación individual (Tab 2)
5. Comparativa individual (Tab 2)

---

## Sidebar

```css
[data-testid="stSidebar"] {
  background: #0d1526 !important;
  border-right: 1px solid #1e293b;
}
/* All text inside sidebar */
[data-testid="stSidebar"] p, label, span, div, small { color: #94a3b8 !important; }
/* Selectboxes */
[data-testid="stSidebar"] [data-baseweb="select"] {
  background-color: #1e293b !important;
  border: 1px solid #334155 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
  background-color: #1e293b !important;
  color: #f1f5f9 !important;
}
/* Refresh button — unchanged red */
[data-testid="stSidebar"] button {
  background-color: #FF385C !important;
  color: #ffffff !important;
}
```

---

## Tabs

```css
.stTabs [data-baseweb="tab"] { color: #475569 !important; }
.stTabs [aria-selected="true"] { color: #FF385C !important; border-bottom: 3px solid #FF385C !important; }
.stTabs [data-baseweb="tab-highlight"] { background: #FF385C !important; }
```

---

## Tables

Set `base = "dark"` in `.streamlit/config.toml` so Streamlit's dataframes inherit dark mode automatically:

```toml
[theme]
base = "dark"
primaryColor = "#FF385C"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"
```

This replaces manual CSS overrides for tables.

---

## Section Titles

Update `.section-title` CSS:
```css
.section-title {
  color: #f1f5f9;
  border-bottom: 2px solid #FF385C;
}
```

---

## Performance Badge Pills

Update background/text for dark contrast:
```css
.perf-excelente { background: #14532d; color: #22c55e; }
.perf-ajustar   { background: #78350f; color: #fbbf24; }
.perf-mejorar   { background: #7c2d12; color: #fb923c; }
.perf-revisar   { background: #7f1d1d; color: #f87171; }
```

---

## Files Changed

| File | Change |
|---|---|
| `app.py` | Color constants, CSS block, KPI card HTML, chart traces |
| `.streamlit/config.toml` | Add `[theme]` section for dark base |

No changes to `data_loader.py`, `ocupacion_calc.py`, or `requirements.txt`.

---

## Out of Scope

- Tab Ingresos (future)
- Layout change (sidebar stays as-is)
- Any functional/calculation changes
