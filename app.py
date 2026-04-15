"""
BeeMyHost Dashboards — Ocupación
Streamlit app: occupation metrics by month, sourced from Google Sheets.
"""

import calendar
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import build_master
from ocupacion_calc import calc_ocupacion, calc_comparativa, resumen_por_responsable

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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BeeMyHost · Dashboards",
    page_icon="🐝",
    layout="wide",
)

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
  [data-testid="stAppViewContainer"] {{ background: {C_BG_SECTION}; }}

  /* Sidebar — white background, black text */
  [data-testid="stSidebar"] {{ background: {C_BG} !important; border-right: 1px solid {C_BORDER}; }}
  [data-testid="stSidebar"] hr {{ border-color: {C_BORDER}; }}
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div,
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] .stMarkdown,
  [data-testid="stSidebar"] .stCaption {{ color: {C_TEXT} !important; }}

  /* Selectbox & button widgets inside sidebar — white bg, black text */
  [data-testid="stSidebar"] [data-baseweb="select"] {{
    background-color: {C_BG} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 8px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] * {{
    background-color: {C_BG} !important;
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

  /* Tabs — always visible in dark text / red when active */
  .stTabs [data-baseweb="tab-list"] {{ background: transparent; gap: 4px; }}
  .stTabs [data-baseweb="tab"] {{
    color: {C_TEXT} !important;
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

  .bmh-card {{
    background: {C_BG};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .bmh-val   {{ font-size: 2rem;  font-weight: 700; color: {C_TEXT};    line-height: 1.2; }}
  .bmh-label {{ font-size: 0.82rem; color: {C_TEXT_SEC}; margin-top: 6px; }}
  .bmh-delta-pos {{ color: {C_GREEN};   font-size: 0.85rem; font-weight: 600; }}
  .bmh-delta-neg {{ color: {C_RED_SOFT}; font-size: 0.85rem; font-weight: 600; }}
  .bmh-delta-neu {{ color: {C_TEXT_SEC}; font-size: 0.85rem; }}

  .section-title {{
    font-size: 1rem; font-weight: 600; color: {C_TEXT};
    margin: 32px 0 14px; padding-bottom: 6px;
    border-bottom: 2px solid {C_PRIMARY}; display: inline-block;
  }}

  /* Performance badge pills */
  .perf-excelente {{ background:#dcfce7; color:#15803d; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-ajustar   {{ background:#fef9c3; color:#a16207; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-mejorar   {{ background:#ffedd5; color:#c2410c; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}
  .perf-revisar   {{ background:#fee2e2; color:#b91c1c; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:600; }}

  .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _delta_html(val: float) -> str:
    if abs(val) < 0.001:
        return f'<span class="bmh-delta-neu">sin cambio</span>'
    sign = "+" if val > 0 else ""
    cls  = "bmh-delta-pos" if val > 0 else "bmh-delta-neg"
    return f'<span class="{cls}">{sign}{val*100:.1f}pp vs mes ant.</span>'

def _occ_color(pct: float) -> str:
    if pct >= 0.70: return C_GREEN
    if pct >= 0.50: return C_AMBER
    return C_RED_SOFT

def _perf_label(pct: float) -> str:
    if pct >= 0.70: return "Excelente"
    if pct >= 0.50: return "Ajustar"
    if pct >= 0.40: return "Mejorar"
    return "Revisar"

def _calc_bono(pct: float) -> tuple[float, float]:
    """Returns (bono_base, bono_extra) for a single property."""
    bono_base  = 6000.0 if pct >= 0.70 else 0.0
    bono_extra = max(pct - 0.70, 0) * 33334.0
    return bono_base, bono_extra

def _chart_layout(height: int) -> dict:
    return dict(
        height=height,
        margin=dict(l=0, r=80, t=10, b=40),
        plot_bgcolor=C_BG,
        paper_bgcolor=C_BG_SECTION,
        font=dict(family="Inter, sans-serif", color=C_TEXT),
    )

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Cargando datos desde Google Sheets…")
def load_data() -> pd.DataFrame:
    return build_master(min_year=2025)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://beemyhost.com.ar/images/beemyhost-logo.webp",
        width=150,
    )
    st.markdown("---")
    st.markdown("**Período**")
    today = date.today()
    year  = st.selectbox("Año", list(range(today.year, 2024, -1)), index=0, label_visibility="collapsed")
    month = st.selectbox(
        "Mes", list(range(1, 13)), index=today.month - 1,
        format_func=lambda m: calendar.month_name[m].capitalize(),
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filtros**")
    show_zero = st.checkbox("Incluir deptos sin reservas", value=False)

    st.markdown("---")
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Datos cacheados 60 min · Fuente: Google Sheets")

# ── Compute ───────────────────────────────────────────────────────────────────
df_master = load_data()
df_mes    = calc_ocupacion(df_master, year, month)
df_comp   = calc_comparativa(df_master, year, month)
df_resp   = resumen_por_responsable(df_mes)

if not show_zero:
    df_mes  = df_mes[df_mes["dias_ocupados"] > 0].copy()
    df_comp = df_comp[df_comp["dias_actual"] > 0].copy()

month_name = calendar.month_name[month].capitalize()
if month == 1:
    prev_month     = 12
    prev_year      = year - 1
    prev_label     = f"Dic {year - 1}"
else:
    prev_month     = month - 1
    prev_year      = year
    prev_label     = f"{calendar.month_name[month - 1].capitalize()} {year}"

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ocup, tab_ind = st.tabs(["Ocupación", "Reporte Individual"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OCUPACIÓN GENERAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_ocup:
    st.markdown(f"## Ocupación · {month_name} {year}")
    st.caption(f"{df_mes['nombre'].nunique()} propiedades con reservas · datos desde Google Sheets")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    avg_act  = df_mes["pct_ocupacion"].mean() if not df_mes.empty else 0
    avg_ant  = df_comp["pct_anterior"].mean() if not df_comp.empty else 0
    delta    = avg_act - avg_ant
    n_full   = int((df_mes["pct_ocupacion"] >= 1.0).sum())
    n_over70 = int((df_mes["pct_ocupacion"] >= 0.70).sum())
    n_deptos = df_mes["nombre"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, dh in [
        (c1, f"{avg_act*100:.1f}%", "Ocupación promedio", _delta_html(delta)),
        (c2, str(n_deptos),         "Propiedades con reservas", ""),
        (c3, str(n_full),           "Propiedades al 100%", ""),
        (c4, str(n_over70),         "Propiedades ≥ 70%", ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="bmh-card">
              <div class="bmh-val">{val}</div>
              <div class="bmh-label">{label}</div>
              {dh}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart 1: % ocupación por propiedad ────────────────────────────────────
    st.markdown('<div class="section-title">% Ocupación por propiedad</div>', unsafe_allow_html=True)

    if df_mes.empty:
        st.info("Sin reservas para el período seleccionado.")
    else:
        df_p = df_mes.sort_values("pct_ocupacion", ascending=True).copy()
        df_p["color"] = df_p["pct_ocupacion"].apply(_occ_color)

        fig1 = go.Figure(go.Bar(
            x=df_p["pct_ocupacion"] * 100,
            y=df_p["nombre"],
            orientation="h",
            text=(df_p["pct_ocupacion"] * 100).round(1).astype(str) + "%",
            textposition="outside",
            marker_color=df_p["color"],
            hovertemplate="<b>%{y}</b><br>Ocupación: %{x:.1f}%<extra></extra>",
        ))
        fig1.update_layout(
            xaxis=dict(title="% Ocupación", ticksuffix="%", range=[0, 118],
                       gridcolor=C_BORDER, zerolinecolor=C_BORDER,
                       tickfont=dict(color=C_TEXT), title_font=dict(color=C_TEXT)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT)),
            **_chart_layout(max(420, len(df_p) * 26)),
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("🟢 ≥ 70% &nbsp;&nbsp; 🟡 50–70% &nbsp;&nbsp; 🔴 < 50%")

    # ── Chart 2: comparativa mes anterior ─────────────────────────────────────
    st.markdown(
        f'<div class="section-title">Comparativa {month_name} vs {prev_label}</div>',
        unsafe_allow_html=True,
    )

    if df_comp.empty:
        st.info("Sin datos para comparar.")
    else:
        df_c = df_comp.sort_values("delta", ascending=True).copy()
        df_c["color"] = df_c["delta"].apply(
            lambda x: C_GREEN if x > 0.01 else (C_RED_SOFT if x < -0.01 else C_BORDER)
        )
        df_c["label"] = df_c["delta"].apply(
            lambda x: f"+{x*100:.1f}pp" if x >= 0 else f"{x*100:.1f}pp"
        )
        hover_actual   = (df_c["pct_actual"] * 100).round(1).astype(str) + "%"
        hover_anterior = (df_c["pct_anterior"] * 100).round(1).astype(str) + "%"

        fig2 = go.Figure(go.Bar(
            x=df_c["delta"] * 100,
            y=df_c["nombre"],
            orientation="h",
            text=df_c["label"],
            textposition="outside",
            marker_color=df_c["color"],
            customdata=list(zip(hover_actual, hover_anterior)),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{month_name}: %{{customdata[0]}}<br>"
                f"{prev_label}: %{{customdata[1]}}<br>"
                "Δ: %{x:.1f}pp<extra></extra>"
            ),
        ))
        fig2.update_layout(
            xaxis=dict(title="Δ puntos porcentuales", ticksuffix="pp",
                       zeroline=True, zerolinecolor=C_TEXT_SEC, gridcolor=C_BORDER,
                       tickfont=dict(color=C_TEXT), title_font=dict(color=C_TEXT)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT)),
            **_chart_layout(max(420, len(df_c) * 26)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: por responsable ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Por responsable</div>', unsafe_allow_html=True)

    if not df_resp.empty:
        df_r = df_resp.copy()
        df_r["avg_pct"] = (df_r["avg_ocupacion"] * 100).round(1)
        df_r["color"]   = df_r["avg_ocupacion"].apply(_occ_color)

        fig3 = go.Figure(go.Bar(
            x=df_r["avg_pct"],
            y=df_r["responsable"],
            orientation="h",
            text=df_r["avg_pct"].astype(str) + "%",
            textposition="outside",
            marker_color=df_r["color"],
            hovertemplate="<b>%{y}</b><br>Ocup. promedio: %{x:.1f}%<extra></extra>",
        ))
        fig3.add_vline(x=70, line_dash="dash", line_color=C_TEXT_SEC,
                       annotation_text="70%", annotation_position="top right",
                       annotation_font_color=C_TEXT_SEC)
        fig3.update_layout(
            xaxis=dict(title="% Ocupación promedio", ticksuffix="%",
                       range=[0, 118], gridcolor=C_BORDER,
                       tickfont=dict(color=C_TEXT), title_font=dict(color=C_TEXT)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT)),
            **_chart_layout(max(300, len(df_r) * 52)),
        )
        st.plotly_chart(fig3, use_container_width=True)

        df_r_table = df_r[["responsable", "n_deptos", "avg_pct", "deptos_sobre_70"]].copy()
        df_r_table.columns = ["Responsable", "Deptos", "Ocup. promedio (%)", "Deptos ≥ 70%"]
        st.dataframe(df_r_table, use_container_width=True, hide_index=True)

    # ── Tabla detalle ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Detalle por propiedad</div>', unsafe_allow_html=True)

    if not df_mes.empty:
        df_t = df_mes[["nombre", "responsable",
                       "dias_ocupados", "dias_mes", "pct_ocupacion"]].copy()
        df_t["pct_ocupacion"] = (df_t["pct_ocupacion"] * 100).round(1)
        df_t = df_t.sort_values("pct_ocupacion", ascending=False).reset_index(drop=True)

        st.dataframe(
            df_t,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nombre":        st.column_config.TextColumn("Propiedad"),
                "responsable":   st.column_config.TextColumn("Responsable"),
                "dias_ocupados": st.column_config.NumberColumn("Días ocupados"),
                "dias_mes":      st.column_config.NumberColumn("Días mes"),
                "pct_ocupacion": st.column_config.ProgressColumn(
                    "Ocupación (%)",
                    min_value=0, max_value=100,
                    format="%.1f%%",
                ),
            },
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REPORTE INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_ind:
    # Responsable selector
    responsables = sorted(df_mes["responsable"].dropna().unique().tolist())
    if not responsables:
        st.info("Sin datos de responsables para el período seleccionado.")
        st.stop()

    resp_sel = st.selectbox(
        "Responsable",
        responsables,
        key="resp_ind",
    )

    # Filter data for selected responsable
    df_ri = df_mes[df_mes["responsable"] == resp_sel].copy()

    # df_comp has responsable only for rows that appear in the current month;
    # outer-join rows from prior month only won't have it. Filter safely.
    if "responsable" in df_comp.columns:
        df_ri_ant = df_comp[df_comp["responsable"].fillna("") == resp_sel].copy()
    else:
        df_ri_ant = pd.DataFrame()

    # Add performance category and bonus columns
    df_ri["performance"] = df_ri["pct_ocupacion"].apply(_perf_label)
    df_ri[["bono_base", "bono_extra"]] = df_ri["pct_ocupacion"].apply(
        lambda p: pd.Series(_calc_bono(p))
    )
    df_ri["bono_total"] = df_ri["bono_base"] + df_ri["bono_extra"]

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"## Reporte · {resp_sel} · {month_name} {year}")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    avg_ri      = df_ri["pct_ocupacion"].mean() if not df_ri.empty else 0
    n_ri        = df_ri["nombre"].nunique()
    n_excelente = int((df_ri["performance"] == "Excelente").sum())
    n_revisar   = int((df_ri["performance"] == "Revisar").sum())
    total_bono       = df_ri["bono_total"].sum()
    bono_base_total  = df_ri["bono_base"].sum()
    bono_extra_total = df_ri["bono_extra"].sum()
    sueldo_base      = n_ri * 14_000
    total_mes        = sueldo_base + total_bono

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, f"{avg_ri*100:.1f}%",   "Ocupación promedio"),
        (c2, str(n_ri),              "Propiedades a cargo"),
        (c3, str(n_excelente),       "Excelente (≥ 70%)"),
        (c4, str(n_revisar),         "Revisar (< 40%)"),
    ]:
        with col:
            st.markdown(f"""
            <div class="bmh-card">
              <div class="bmh-val">{val}</div>
              <div class="bmh-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Resumen de cobro del mes ───────────────────────────────────────────────
    ca, cb, cc = st.columns(3)
    for col, val, label in [
        (ca, f"${sueldo_base:,.0f}", f"Sueldo base ({n_ri} deptos × $14.000)"),
        (cb, f"${total_bono:,.0f}",  "Bono por ocupación"),
        (cc, f"${total_mes:,.0f}",   "Total a cobrar en el mes"),
    ]:
        with col:
            st.markdown(f"""
            <div class="bmh-card">
              <div class="bmh-val">{val}</div>
              <div class="bmh-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    if df_ri.empty:
        st.info("Sin reservas para este responsable en el período seleccionado.")
    else:
        # ── Gráfico ocupación por propiedad ───────────────────────────────────
        st.markdown('<div class="section-title">Ocupación por propiedad</div>', unsafe_allow_html=True)

        df_ri_sorted = df_ri.sort_values("pct_ocupacion", ascending=True).copy()
        df_ri_sorted["color"] = df_ri_sorted["pct_ocupacion"].apply(_occ_color)

        fig_ri = go.Figure(go.Bar(
            x=df_ri_sorted["pct_ocupacion"] * 100,
            y=df_ri_sorted["nombre"],
            orientation="h",
            text=(df_ri_sorted["pct_ocupacion"] * 100).round(1).astype(str) + "%",
            textposition="outside",
            marker_color=df_ri_sorted["color"],
            hovertemplate="<b>%{y}</b><br>Ocupación: %{x:.1f}%<extra></extra>",
        ))
        fig_ri.add_vline(x=70, line_dash="dash", line_color=C_TEXT_SEC,
                         annotation_text="meta 70%", annotation_position="top right",
                         annotation_font_color=C_TEXT_SEC)
        fig_ri.update_layout(
            xaxis=dict(title="% Ocupación", ticksuffix="%", range=[0, 118],
                       gridcolor=C_BORDER, zerolinecolor=C_BORDER,
                       tickfont=dict(color=C_TEXT), title_font=dict(color=C_TEXT)),
            yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT)),
            **_chart_layout(max(320, len(df_ri_sorted) * 40)),
        )
        st.plotly_chart(fig_ri, use_container_width=True)

        # ── Comparativa vs mes anterior ────────────────────────────────────────
        if not df_ri_ant.empty:
            st.markdown(
                f'<div class="section-title">Comparativa {month_name} vs {prev_label}</div>',
                unsafe_allow_html=True,
            )
            df_ri_c = df_ri_ant.sort_values("delta", ascending=True).copy()
            df_ri_c["color"] = df_ri_c["delta"].apply(
                lambda x: C_GREEN if x > 0.01 else (C_RED_SOFT if x < -0.01 else C_BORDER)
            )
            df_ri_c["label"] = df_ri_c["delta"].apply(
                lambda x: f"+{x*100:.1f}pp" if x >= 0 else f"{x*100:.1f}pp"
            )
            fig_rc = go.Figure(go.Bar(
                x=df_ri_c["delta"] * 100,
                y=df_ri_c["nombre"],
                orientation="h",
                text=df_ri_c["label"],
                textposition="outside",
                marker_color=df_ri_c["color"],
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
            ))
            fig_rc.update_layout(
                xaxis=dict(title="Δ puntos porcentuales", ticksuffix="pp",
                           zeroline=True, zerolinecolor=C_TEXT_SEC, gridcolor=C_BORDER,
                           tickfont=dict(color=C_TEXT), title_font=dict(color=C_TEXT)),
                yaxis=dict(title="", tickfont=dict(size=12, color=C_TEXT)),
                **_chart_layout(max(320, len(df_ri_c) * 40)),
            )
            st.plotly_chart(fig_rc, use_container_width=True)

        # ── Bono desglose ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">Detalle por propiedad</div>', unsafe_allow_html=True)

        # Bono summary line
        st.markdown(
            f"**Bono del mes:** "
            f"Base (70%) `${bono_base_total:,.0f}` + "
            f"Extra (pts sobre 70%) `${bono_extra_total:,.0f}` = "
            f"**Total `${total_bono:,.0f}`**"
        )

        PERF_ORDER = {"Excelente": 0, "Ajustar": 1, "Mejorar": 2, "Revisar": 3}
        df_ri_tbl = df_ri[[
            "nombre", "dias_ocupados", "dias_mes", "pct_ocupacion",
            "performance", "bono_base", "bono_extra", "bono_total"
        ]].copy()
        df_ri_tbl["pct_pct"] = (df_ri_tbl["pct_ocupacion"] * 100).round(1)
        df_ri_tbl["_sort"]   = df_ri_tbl["performance"].map(PERF_ORDER)
        df_ri_tbl = df_ri_tbl.sort_values(["_sort", "pct_pct"], ascending=[True, False]).reset_index(drop=True)
        df_ri_tbl = df_ri_tbl.drop(columns=["_sort", "pct_ocupacion"])
        df_ri_tbl.columns = [
            "Propiedad", "Días ocupados", "Días mes",
            "Performance", "Bono base ($)", "Bono extra ($)", "Bono total ($)", "Ocupación (%)"
        ]

        st.dataframe(
            df_ri_tbl,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Propiedad":      st.column_config.TextColumn("Propiedad"),
                "Días ocupados":  st.column_config.NumberColumn("Días ocupados"),
                "Días mes":       st.column_config.NumberColumn("Días mes"),
                "Performance":    st.column_config.TextColumn("Performance"),
                "Bono base ($)":  st.column_config.NumberColumn("Bono base ($)",  format="$%.0f"),
                "Bono extra ($)": st.column_config.NumberColumn("Bono extra ($)", format="$%.0f"),
                "Bono total ($)": st.column_config.NumberColumn("Bono total ($)", format="$%.0f"),
                "Ocupación (%)":  st.column_config.ProgressColumn(
                    "Ocupación (%)", min_value=0, max_value=100, format="%.1f%%"
                ),
            },
        )
