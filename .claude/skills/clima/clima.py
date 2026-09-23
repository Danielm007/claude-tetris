#!/usr/bin/env python3
"""Clima actual y pronóstico para la ubicación local (por IP) o una ciudad dada.

Uso: python3 clima.py [ciudad]
Salida: JSON en stdout. Solo usa la biblioteca estándar.
"""
import json
import sys
import urllib.parse
import urllib.request

TIMEOUT = 10
UA = {"User-Agent": "claude-clima-skill/1.0"}

WMO = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna intensa",
    56: "Llovizna helada ligera", 57: "Llovizna helada intensa",
    61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
    66: "Lluvia helada ligera", 67: "Lluvia helada intensa",
    71: "Nieve ligera", 73: "Nieve moderada", 75: "Nieve intensa", 77: "Granos de nieve",
    80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos violentos",
    85: "Chubascos de nieve ligeros", 86: "Chubascos de nieve intensos",
    95: "Tormenta", 96: "Tormenta con granizo ligero", 99: "Tormenta con granizo intenso",
}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def ubicacion_por_ip():
    try:
        d = get_json("https://ipapi.co/json/")
        if "latitude" in d:
            return {"ciudad": d.get("city"), "region": d.get("region"), "pais": d.get("country_name"),
                    "lat": d["latitude"], "lon": d["longitude"], "fuente": "ip"}
    except Exception:
        pass
    d = get_json("http://ip-api.com/json/")
    if d.get("status") != "success":
        raise RuntimeError("No se pudo detectar la ubicación por IP")
    return {"ciudad": d.get("city"), "region": d.get("regionName"), "pais": d.get("country"),
            "lat": d["lat"], "lon": d["lon"], "fuente": "ip"}


def ubicacion_por_nombre(nombre):
    q = urllib.parse.urlencode({"name": nombre, "count": 1, "language": "es", "format": "json"})
    d = get_json(f"https://geocoding-api.open-meteo.com/v1/search?{q}")
    res = d.get("results") or []
    if not res:
        raise RuntimeError(f"No se encontró la ciudad '{nombre}'")
    r = res[0]
    return {"ciudad": r.get("name"), "region": r.get("admin1"), "pais": r.get("country"),
            "lat": r["latitude"], "lon": r["longitude"], "fuente": "busqueda"}


def clima(lat, lon):
    q = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 3,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "precipitation,weather_code,wind_speed_10m,is_day",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_probability_max,precipitation_sum",
    })
    d = get_json(f"https://api.open-meteo.com/v1/forecast?{q}")
    c = d["current"]
    actual = {
        "hora": c["time"],
        "condicion": WMO.get(c["weather_code"], f"Código {c['weather_code']}"),
        "temperatura_c": c["temperature_2m"],
        "sensacion_c": c["apparent_temperature"],
        "humedad_pct": c["relative_humidity_2m"],
        "precipitacion_mm": c["precipitation"],
        "viento_kmh": c["wind_speed_10m"],
        "es_de_dia": bool(c["is_day"]),
    }
    dd = d["daily"]
    pronostico = [{
        "fecha": dd["time"][i],
        "condicion": WMO.get(dd["weather_code"][i], f"Código {dd['weather_code'][i]}"),
        "max_c": dd["temperature_2m_max"][i],
        "min_c": dd["temperature_2m_min"][i],
        "prob_lluvia_pct": dd["precipitation_probability_max"][i],
        "lluvia_mm": dd["precipitation_sum"][i],
    } for i in range(len(dd["time"]))]
    return d.get("timezone"), actual, pronostico


def main():
    nombre = " ".join(sys.argv[1:]).strip()
    try:
        ub = ubicacion_por_nombre(nombre) if nombre else ubicacion_por_ip()
        tz, actual, pronostico = clima(ub["lat"], ub["lon"])
        ub["zona_horaria"] = tz
        out = {"ubicacion": ub, "actual": actual, "pronostico": pronostico}
    except Exception as e:
        out = {"error": str(e)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 1 if "error" in out else 0


if __name__ == "__main__":
    sys.exit(main())
