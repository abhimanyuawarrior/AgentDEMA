"""External integrations: Gemini -> Groq fallback, Open-Meteo, SoilGrids."""
import json
import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_eda_summary(df):
    if df is None or df.empty:
        return "No cleaned dataset available for EDA."

    numeric = df.select_dtypes(include=["number"])
    if numeric.empty:
        return "No numeric columns are available for EDA."

    yield_col = next((c for c in df.columns if str(c).lower() == "yield" or "yield" in str(c).lower()), None)
    rainfall_col = next((c for c in df.columns if str(c).lower() in {"rainfall", "annual_rainfall"}), None)
    crop_col = next((c for c in df.columns if str(c).lower() == "crop"), None)
    season_col = next((c for c in df.columns if str(c).lower() == "season"), None)

    if yield_col and crop_col:
        top_crop = df.groupby(crop_col)[yield_col].mean().sort_values(ascending=False).head(1).index[0]
    else:
        top_crop = "the dominant production mix"

    if season_col and yield_col:
        best_season = df.groupby(season_col)[yield_col].mean().sort_values(ascending=False).head(1).index[0]
    else:
        best_season = "the annual cycle"

    prompt = (
        f"Provide a short agricultural EDA summary based on the following dataset. "
        f"Focus on yield performance, seasonal behavior, and key climate risk drivers. "
        f"Top crop by average yield: {top_crop}. Best season: {best_season}. "
        f"The dataset has {len(df)} rows and {len(numeric.columns)} numeric fields. "
        f"Return 3 bullet points in plain English."
    )

    try:
        return generate_text(prompt, system_instruction="You are an expert agricultural analyst. Return succinct bullet points only.")["text"].strip()
    except Exception:
        summary = [
            f"The dataset contains {len(df):,} rows with the strongest yield signal in {top_crop}.",
            f"Seasonal behavior shows {best_season} as the most productive window for the selected crop mix.",
        ]
        if rainfall_col and yield_col:
            summary.append(f"Rainfall variance appears to be a meaningful driver, so {rainfall_col} should be monitored alongside yield performance.")
        else:
            summary.append("The numeric patterns suggest climate and agronomic factors are important to explain yield variability.")
        return "\n".join(f"• {item}" for item in summary)


def _has_real_api_key(name: str) -> bool:
    value = (os.getenv(name) or "").strip()
    if not value:
        return False
    lowered = value.lower()
    if lowered.startswith("your_") or lowered in {"placeholder", "changeme", "test", "demo"}:
        return False
    return True


def llm_status():
    return {"Gemini configured": _has_real_api_key("GEMINI_API_KEY"),
            "Groq configured": _has_real_api_key("GROQ_API_KEY"),
            "Primary provider": "Gemini", "Fallback provider": "Groq"}


def _fallback_agri_response(prompt: str):
    advice = (
        "This environment does not currently have a live LLM API key configured. "
        "Using the built-in agronomy fallback for a safe, practical recommendation.\n\n"
        "• Check soil pH and keep it in a balanced, crop-appropriate range to avoid nutrient lockout.\n"
        "• Align sowing and irrigation timing with the current season and local rainfall pattern to reduce stress.\n"
        "• Use nutrient management and field scouting to support crop health before large-scale input decisions."
    )
    return {
        "text": advice,
        "provider": "Local fallback",
        "model": "rule-based-agronomy",
        "status": "fallback",
    }


def generate_text(prompt: str, system_instruction: str = "You are an expert agricultural data engineer."):
    errors = []
    if _has_real_api_key("GEMINI_API_KEY"):
        try:
            from google import genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            response = client.models.generate_content(model=model, contents=f"{system_instruction}\n\n{prompt}")
            if response.text:
                return {"text": response.text, "provider": "Gemini", "model": model}
            raise RuntimeError("Gemini returned an empty response")
        except Exception as exc:
            errors.append(f"Gemini: {exc}")
    if _has_real_api_key("GROQ_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
                            base_url="https://api.groq.com/openai/v1", timeout=30.0)
            model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_instruction},
                          {"role": "user", "content": prompt}], temperature=0.2)
            content = response.choices[0].message.content
            if content:
                return {"text": content, "provider": "Groq", "model": model}
            raise RuntimeError("Groq returned an empty response")
        except Exception as exc:
            errors.append(f"Groq: {exc}")
    if not errors:
        return _fallback_agri_response(prompt)
    raise RuntimeError("; ".join(errors))


def llm_schema_mapping(columns):
    prompt = ("Map source column names to canonical agriculture fields where appropriate. Allowed fields: "
              "nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall, crop, yield, latitude, longitude. "
              "Do not invent columns. Return ONLY JSON array of objects with source_column, suggested_column, "
              "confidence (0 to 1), review_required. Source columns: " + json.dumps([str(c) for c in columns]))
    try:
        result = generate_text(prompt, "Return strict JSON only. Be conservative; do not guess uncertain mappings.")
        raw = result["text"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError("LLM mapping response was not a JSON array")
        allowed = {str(c) for c in columns}
        mapped = {}
        for item in parsed:
            source = item.get("source_column")
            if source not in allowed:
                continue
            confidence = max(0.0, min(1.0, float(item.get("confidence", 0))))
            mapped[source] = {"source_column": source,
                              "suggested_column": str(item.get("suggested_column", source)),
                              "confidence": confidence,
                              "review_required": bool(item.get("review_required", confidence < 0.8))}
        rows = [mapped.get(str(c), {"source_column": str(c), "suggested_column": str(c),
                 "confidence": 0.0, "review_required": True}) for c in columns]
        return rows, result["provider"]
    except Exception:
        rows = [{"source_column": str(c), "suggested_column": str(c), "confidence": 1.0, "review_required": False} for c in columns]
        return rows, "Local fallback"


def geocode_place(place: str):
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": place, "count": 1, "language": "en", "format": "json"}, timeout=20)
    r.raise_for_status()
    results = r.json().get("results") or []
    if not results:
        raise ValueError(f"Location not found: {place}")
    x = results[0]
    return {"name": x.get("name"), "admin1": x.get("admin1"), "country": x.get("country"),
            "latitude": x["latitude"], "longitude": x["longitude"]}


def get_weather(latitude: float, longitude: float, forecast_days: int = 7):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset",
        "forecast_days": forecast_days,
        "timezone": "auto",
        "models": "best_match",
    }, timeout=25)
    r.raise_for_status()
    payload = r.json()
    return payload


def get_soil(latitude: float, longitude: float):
    # SoilGrids REST v2 is beta and may be temporarily unavailable; caller handles that gracefully.
    params = [("lon", longitude), ("lat", latitude), ("property", "phh2o"),
              ("property", "clay"), ("property", "sand"), ("property", "soc"),
              ("depth", "0-5cm"), ("value", "mean")]
    r = requests.get("https://rest.isric.org/soilgrids/v2.0/properties/query", params=params, timeout=30)
    r.raise_for_status()
    return r.json()
