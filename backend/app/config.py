"""Central configuration, loaded from environment / .env.

Locked decisions (requirements §2) and infra knobs live here so the rest of the
codebase never reads os.environ directly.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql+asyncpg://gmaps:gmaps@postgres:5432/gmaps"

    # --- gosom scraping engine (pure engine, never rewritten) ---
    gosom_url: str = "http://gmaps-scraper:8080"
    # gosom writes CSV per job into this shared folder (mounted into backend too).
    gmaps_data_dir: str = "/gmapsdata"
    scrape_email: bool = True  # gosom -email flag is enabled in compose

    # --- LLM (OpenAI-compatible endpoint, e.g. vLLM) ---
    llm_host: str = ""            # e.g. https://orion.devoutsys.com/v1
    llm_model: str = ""           # e.g. vllm/qwen3.5-35b
    llm_api_key: str = "not-needed"
    llm_temperature: float = 0.2
    llm_timeout: float = 120.0

    # --- Google Sheet export (Apps Script web app) ---
    google_sheet_web_app_url: str = ""

    # --- Pipeline tuning (requirements §9, §17) ---
    enrichment_score_threshold: int = 70   # leads >= this get expensive enrichment
    export_default_score: int = 70         # default score filter on export
    poll_interval_seconds: int = 8         # job poller cadence
    scoring_batch_size: int = 25           # leads per LLM scoring call

    # --- Scrape defaults forwarded to gosom ---
    scrape_lang_default: str = "en"
    scrape_zoom: int = 15
    scrape_depth: int = 10
    scrape_max_time: int = 600
    scrape_fast_mode: bool = True
    scrape_radius: int = 10000  # meters, gosom search radius around the map center
    # Fallback map center when a city/country can't be geocoded (0,0 is open
    # ocean, but the location is also embedded in the keyword so results hold).
    scrape_fallback_lat: float = 0.0
    scrape_fallback_lon: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
