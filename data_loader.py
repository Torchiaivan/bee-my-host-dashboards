"""
data_loader.py — Carga y merge de Reservas + Departamentos desde Google Sheets.
"""

import gspread
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Columns to pull from Departamentos and how to rename them
DEPTO_COLS = {
    "Departamentos":            "depto_key",
    "Nombre":                   "nombre",
    "Dirección Exacta":         "direccion",
    "Fee Limpieza (airbnb)":    "fee_limpieza",
    "Ubicación Locker":         "ubicacion_locker",
    "Dueño":                    "dueno",
    "Cantidad Max de huespedes":"cant_huespedes",
    "Link al aviso":            "link_aviso",
    "Responsable":              "responsable",
    "Red WiFi":                 "red_wifi",
    "Password WiFi":            "pw_wifi",
    "Barrio":                   "barrio",
}


def _get_spreadsheet():
    """
    Supports two auth modes:
    - Local dev:        reads credentials.json file
    - Streamlit Cloud:  reads from st.secrets["gcp_service_account"]
    """
    try:
        import streamlit as st
        creds = dict(st.secrets["gcp_service_account"])
        # private_key newlines are stored escaped in secrets
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        gc = gspread.service_account_from_dict(creds)
    except Exception:
        gc = gspread.service_account(filename="credentials.json")
    return gc.open_by_key(SPREADSHEET_ID)


def load_reservas(sh) -> pd.DataFrame:
    ws = sh.worksheet("Reservas")
    data = ws.get_all_records(expected_headers=[])
    df = pd.DataFrame(data)

    # Normalize column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Drop fully empty rows
    df = df[df["Anuncio"].astype(str).str.strip() != ""].copy()

    # Type conversions
    date_cols = ["Fecha de inicio", "Fecha de finalización", "Reservada"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    numeric_cols = ["Número de noches", "Número de adultos", "Número de niños",
                    "Número de bebés", "Ganancias", "Valor de limpieza"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace("$", "").str.replace(",", ".").str.strip(),
                errors="coerce"
            )

    return df


def load_departamentos(sh) -> pd.DataFrame:
    ws = sh.worksheet("Departamentos")
    data = ws.get_all_records(expected_headers=[])
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()

    # Departamentos has two "Barrio" columns — keep only the first occurrence
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated(keep="first")]

    # Select and rename only the columns we need
    available = {k: v for k, v in DEPTO_COLS.items() if k in df.columns}
    df = df[list(available.keys())].rename(columns=available)

    df = df[df["depto_key"].astype(str).str.strip() != ""].copy()
    return df


def build_master(min_year: int = 2025) -> pd.DataFrame:
    """
    Returns merged Reservas + Departamentos master table.
    min_year: only load reservations from this year onwards (default 2025
              to cover current year + one year back for comparisons).
    """
    try:
        sh = _get_spreadsheet()
        reservas = load_reservas(sh)
        deptos = load_departamentos(sh)
    except Exception as e:
        raise RuntimeError(f"Error loading data from Google Sheets: {e}") from e

    if min_year:
        reservas = reservas[
            reservas["Fecha de inicio"].dt.year >= min_year
        ].copy()

    master = reservas.merge(
        deptos,
        left_on="Anuncio",
        right_on="depto_key",
        how="left",
        validate="many_to_one",
    ).drop(columns=["depto_key"])

    return master


if __name__ == "__main__":
    print("Cargando datos...")
    df = build_master(min_year=2025)
    matched = df["nombre"].notna().sum()
    print(f"Filas: {len(df)} | Match: {matched} ({matched/len(df)*100:.1f}%)")
    print(f"Rango: {df['Fecha de inicio'].min().date()} → {df['Fecha de inicio'].max().date()}")
