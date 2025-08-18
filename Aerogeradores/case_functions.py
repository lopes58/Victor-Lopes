import requests
from pathlib import Path
import json
import time
from urllib.parse import urlencode

import geopandas as gpd
from shapely.geometry import Point
import math
import datetime
import unicodedata
import re
import statistics

# Configurações
SERVICE_URL = "https://sigel.aneel.gov.br/arcgis/rest/services/PORTAL/WFS/MapServer/0/query"
OUTPUT_DIR = "outputs"
CSV_PATH = Path(OUTPUT_DIR) / "aerogeradores.csv"
RAW_PATH = Path(OUTPUT_DIR) / "raw_response.json"
VALIDATION_REPORT_PATH = Path(OUTPUT_DIR) / "validation_report.json"
GEOJSON_PATH = Path(OUTPUT_DIR) / "aerogeradores.geojson"


def fetch_wind_turbines():
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "outSR": "4326",
        "resultRecordCount": 2000
    }

    all_features = []
    offset = 0
    retry_count = 0
    max_retries = 3

    while True:
        try:
            params["resultOffset"] = offset
            url = f"{SERVICE_URL}?{urlencode(params)}"

            print("Requisitando dados...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", "Erro desconhecido na API")
                raise ValueError(f"API Error: {error_msg}")

            features = data.get("features", [])
            if not features:
                break

            all_features.extend(features)
            print(f"Recebidos {len(features)} registros")

            if len(features) < params["resultRecordCount"]:
                break

            offset += len(features)
            retry_count = 0

        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count > max_retries:
                raise ConnectionError(f"Falha após {max_retries} tentativas: {str(e)}")
            wait_time = 2 ** retry_count
            print(f"Erro na requisição. Tentando novamente em {wait_time}s... (Tentativa {retry_count}/{max_retries})")
            time.sleep(wait_time)

    return all_features


def _safe_float_convert(v):
    if v is None:
        return None
    try:
        s = str(v).strip().replace(",", ".")
        if s == "" or s.lower() in {"nan", "none"}:
            return None
        return float(s)
    except Exception:
        return None


def _safe_datetime_convert(v):
    """Retorna datetime timezone-aware quando possível. Aceita ms/segundos ints ou strings ISO."""
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=datetime.timezone.utc)
        return v
    try:
        iv = int(float(v))
        if iv > 1_000_000_000_000:  # ms com 13+ dígitos
            return datetime.datetime.fromtimestamp(iv / 1000.0, datetime.timezone.utc)
        if iv > 1_000_000_000:  # possivelmente ms
            return datetime.datetime.fromtimestamp(iv / 1000.0, datetime.timezone.utc)
        return datetime.datetime.fromtimestamp(iv, datetime.timezone.utc)
    except Exception:
        try:
            dt = datetime.datetime.fromisoformat(str(v))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            return None


def _normalize_column(name: str) -> str:
    """Converte para snake_case, remove acentos e caracteres inválidos."""
    if name is None:
        return name
    nfkd = unicodedata.normalize("NFKD", name)
    no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    s = re.sub(r"[^0-9a-zA-Z]+", "_", no_accents)
    s = s.strip("_").lower()
    return s or name


def process_features(features):
    if not features:
        return gpd.GeoDataFrame()

    rows = []
    for feat in features:
        attrs = feat.get("attributes", {}).copy()
        geom = feat.get("geometry", {}) or {}
        x = geom.get("x")
        y = geom.get("y")
        attrs["x"] = x if x is not None else None
        attrs["y"] = y if y is not None else None
        attrs["longitude"] = x if x is not None else None
        attrs["latitude"] = y if y is not None else None
        rows.append(attrs)

    if not rows:
        return gpd.GeoDataFrame()

    geometries = []
    for r in rows:
        lon = r.get("longitude")
        lat = r.get("latitude")
        if lon is None or lat is None:
            geometries.append(None)
            continue
        try:
            geometries.append(Point(float(lon), float(lat)))
        except Exception:
            geometries.append(None)

    geos = gpd.GeoSeries(geometries, crs="EPSG:4326")
    gdf = gpd.GeoDataFrame(rows, geometry=geos)

    col_map = {c: _normalize_column(c) for c in gdf.columns}
    gdf.rename(columns=col_map, inplace=True)

    numeric_cols = ["pot_mw", "alt_total", "alt_torre", "diam_rotor"]
    for col in numeric_cols:
        if col in gdf.columns:
            gdf[col] = [_safe_float_convert(v) for v in gdf[col]]

    # Conversões de datas
    for col in list(gdf.columns):
        if "data" in col.lower() or "date" in col.lower():
            gdf[col] = [_safe_datetime_convert(v) for v in gdf[col]]
            # Formatar para string ISO compatível com Tableau
            gdf[col] = [v.strftime("%Y-%m-%d %H:%M:%S") if v is not None else None for v in gdf[col]]

    missing_geom_mask = gdf.geometry.isna()
    if missing_geom_mask.any():
        n_missing = int(missing_geom_mask.sum())
        print(f"AVISO: {n_missing} registros sem coordenadas válidas serão removidos.")
        gdf = gdf[~missing_geom_mask].copy()

    if "latitude" in gdf.columns and "longitude" in gdf.columns:
        try:
            gdf["latitude"] = [None if v is None else float(v) for v in gdf["latitude"]]
            gdf["longitude"] = [None if v is None else float(v) for v in gdf["longitude"]]
            valid_mask = [
                (lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180)
                for lat, lon in zip(gdf["latitude"], gdf["longitude"])
            ]
            invalid_count = sum(1 for ok in valid_mask if not ok)
            if invalid_count > 0:
                print(f"AVISO: {invalid_count} registros com coordenadas fora de faixa serão removidos.")
            gdf = gdf[[ok for ok in valid_mask]].copy()
        except Exception:
            pass

    gdf.reset_index(drop=True, inplace=True)

    # Relatório simples
    total = len(gdf)
    null_counts = {col: int(sum(1 for v in gdf[col] if v is None)) for col in gdf.columns}
    numeric_stats = {}
    for col in numeric_cols:
        if col in gdf.columns:
            vals = [v for v in gdf[col] if v is not None]
            if vals:
                numeric_stats[col] = {
                    "count": len(vals),
                    "min": min(vals),
                    "max": max(vals),
                    "mean": statistics.mean(vals)
                }
            else:
                numeric_stats[col] = {"count": 0}

    validation = {
        "total_records": int(total),
        "null_counts": null_counts,
        "numeric_stats": numeric_stats
    }

    try:
        with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(validation, f, indent=2, ensure_ascii=False, default=str)
        print(f"Relatório de validação salvo em: {VALIDATION_REPORT_PATH}")
    except Exception as e:
        print("AVISO: falha ao salvar validation_report.json:", str(e))

    preview_cols = list(gdf.columns)[:10]
    for c in preview_cols:
        print(f"  - {c}: {null_counts.get(c,0)} ausentes")

    # Remover colunas totalmente nulas
    gdf = gdf.dropna(axis=1, how='all')

    return gdf


def save_data_from_gdf(gdf, output_dir=OUTPUT_DIR):
    Path(output_dir).mkdir(exist_ok=True)
    gdf.to_csv(CSV_PATH, index=False, encoding="utf-8")
    # gdf.to_file(GEOJSON_PATH, driver="GeoJSON")
    return str(CSV_PATH)


def main():
    try:
        print("=" * 50)
        print("Iniciando extração de dados de aerogeradores")
        print("=" * 50)

        print("\n[ETAPA 1] Extraindo dados da API...")
        features = fetch_wind_turbines()

        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        with open(RAW_PATH, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=2, ensure_ascii=False)
        print(f"Resposta bruta salva em: {RAW_PATH}")

        print("\n[ETAPA 2] Processando dados com geopandas...")
        gdf = process_features(features)

        if gdf.empty:
            print("AVISO: GeoDataFrame vazio após processamento. Verifique raw_response.json para diagnosticar.")
            return

        print(f"GeoDataFrame criado com {len(gdf)} registros e {len(gdf.columns)} colunas.")

        print("\n[ETAPA 3] Salvando dados em CSV...")
        csv_path = save_data_from_gdf(gdf)
        print(f"Dados salvos em: {csv_path}")

        print("\n" + "=" * 50)
        print("PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print("ERRO NO PROCESSO:", str(e))
        print("=" * 50)
        print("Soluções sugeridas:")
        print("1. Verifique o acesso à URL da API no navegador")
        print("2. Inspecione o arquivo raw_response.json para entender a estrutura dos dados")


if __name__ == "__main__":
    main()
