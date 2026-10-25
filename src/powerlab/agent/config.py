"""
src/powerlab/agent/config.py
Ajan ayarları: Gemini API anahtarı ve model adı.

Anahtar önce GEMINI_API_KEY ortam değişkeninden, yoksa .env dosyasından okunur. .env .gitignore'dadır
(tests/test_agent.py bunu denetler); anahtar hiçbir zaman loga, çıktıya ya da hata mesajına yazılmaz.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
# Model adları zamanla değişir; güncel liste: https://ai.google.dev/gemini-api/docs/models
DEFAULT_MODEL = "gemini-2.5-flash"


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    model: str


def default_env_files() -> list:
    return [Path.cwd() / ".env", REPO_ROOT / ".env"]


def read_env_file(path: Path) -> dict:
    """KEY=VALUE satırları; # ile başlayan satırlar ve boş satırlar atlanır, tırnaklar soyulur."""
    values = {}
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_settings(env: Optional[Mapping[str, str]] = None,
                  env_files: Optional[Iterable[Path]] = None) -> Settings:
    env = os.environ if env is None else env
    from_file = {}
    for path in (default_env_files() if env_files is None else env_files):
        for key, value in read_env_file(Path(path)).items():
            from_file.setdefault(key, value)

    api_key = env.get("GEMINI_API_KEY") or from_file.get("GEMINI_API_KEY")
    if not api_key:
        raise ConfigError(
            "Gemini API anahtarı bulunamadı. Repo kökündeki .env dosyasına GEMINI_API_KEY=... satırını "
            "yazın (şablon: .env.example) ya da GEMINI_API_KEY ortam değişkenini tanımlayın."
        )
    model = env.get("GEMINI_MODEL") or from_file.get("GEMINI_MODEL") or DEFAULT_MODEL
    return Settings(api_key=api_key, model=model)
