"""
ocupacion_calc.py — Occupation metrics calculation.

Replicates the logic from 'Pivot' and 'Reporte de ocupacion' Excel sheets:
  - dias_ocupados = days of each reservation that fall within the target month
  - pct_ocupacion = dias_ocupados / days_in_month
  - Comparison between current and previous month
"""

import calendar
import pandas as pd


ESTADOS_CANCELADOS = {"cancelación del huésped", "cancelación del anfitrión", "cancelada"}


def _days_overlap(fecha_inicio: pd.Timestamp, fecha_fin: pd.Timestamp,
                  month_start: pd.Timestamp, month_end: pd.Timestamp) -> int:
    """
    Days of [fecha_inicio, fecha_fin) that fall within [month_start, month_end).
    fecha_fin is checkout date — that day is NOT counted as occupied.
    """
    overlap_start = max(fecha_inicio, month_start)
    overlap_end   = min(fecha_fin, month_end)
    days = (overlap_end - overlap_start).days
    return max(days, 0)


def _month_bounds(year: int, month: int) -> tuple[pd.Timestamp, pd.Timestamp, int]:
    """Returns (month_start, month_end_exclusive, days_in_month)."""
    days_in_month = calendar.monthrange(year, month)[1]
    month_start = pd.Timestamp(year=year, month=month, day=1)
    month_end   = month_start + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1)
    return month_start, month_end, days_in_month


def calc_ocupacion(df_master: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """
    Returns occupation table for the given month.

    Input:  build_master() output
    Output: DataFrame with columns:
        nombre, responsable, barrio, dias_ocupados, dias_mes, pct_ocupacion
    Only includes properties with at least one matched reservation (nombre notna).
    """
    month_start, month_end, days_in_month = _month_bounds(year, month)

    # Filter: exclude cancelled, keep only matched (nombre known)
    df = df_master[
        df_master["nombre"].notna() &
        ~df_master["Estado"].str.strip().str.lower().isin(ESTADOS_CANCELADOS)
    ].copy()

    # Filter: only reservations that could overlap with this month
    df = df[
        (df["Fecha de inicio"] < month_end) &
        (df["Fecha de finalización"] > month_start)
    ].copy()

    if df.empty:
        return pd.DataFrame(columns=["nombre", "responsable", "barrio",
                                     "dias_ocupados", "dias_mes", "pct_ocupacion"])

    df["dias_en_mes"] = df.apply(
        lambda r: _days_overlap(r["Fecha de inicio"], r["Fecha de finalización"],
                                month_start, month_end),
        axis=1,
    )

    result = (
        df.groupby(["nombre", "responsable", "barrio"], dropna=False)
        .agg(dias_ocupados=("dias_en_mes", "sum"))
        .reset_index()
    )

    result["dias_mes"]       = days_in_month
    result["pct_ocupacion"]  = (result["dias_ocupados"] / days_in_month).clip(0, 1)

    return result.sort_values("pct_ocupacion", ascending=False).reset_index(drop=True)


def calc_comparativa(df_master: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """
    Returns occupation for current and previous month side by side.

    Output columns:
        nombre, responsable, barrio,
        pct_actual, dias_actual,
        pct_anterior, dias_anterior,
        delta  (pct_actual - pct_anterior)
    """
    # Previous month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    actual   = calc_ocupacion(df_master, year, month)
    anterior = calc_ocupacion(df_master, prev_year, prev_month)

    merged = actual.merge(
        anterior[["nombre", "pct_ocupacion", "dias_ocupados"]],
        on="nombre",
        how="outer",
        suffixes=("_actual", "_anterior"),
    ).fillna({"pct_ocupacion_actual": 0, "dias_ocupados_actual": 0,
              "pct_ocupacion_anterior": 0, "dias_ocupados_anterior": 0})

    merged["delta"] = merged["pct_ocupacion_actual"] - merged["pct_ocupacion_anterior"]

    return merged.rename(columns={
        "pct_ocupacion_actual":   "pct_actual",
        "dias_ocupados_actual":   "dias_actual",
        "pct_ocupacion_anterior": "pct_anterior",
        "dias_ocupados_anterior": "dias_anterior",
    }).sort_values("pct_actual", ascending=False).reset_index(drop=True)


def resumen_por_responsable(df_ocupacion: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates occupation table by responsable.
    Returns: responsable, n_deptos, avg_ocupacion, deptos_sobre_70
    """
    return (
        df_ocupacion.groupby("responsable", dropna=False)
        .agg(
            n_deptos        =("nombre", "count"),
            avg_ocupacion   =("pct_ocupacion", "mean"),
            deptos_sobre_70 =("pct_ocupacion", lambda x: (x >= 0.70).sum()),
        )
        .reset_index()
        .sort_values("avg_ocupacion", ascending=False)
    )
