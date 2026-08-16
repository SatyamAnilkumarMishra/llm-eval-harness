"""
Factory: turns a CLI string ("gemini", "openai") into a concrete Target
instance, using settings as defaults but allowing per-call overrides.

WHY A FACTORY (rather than just importing the class you want directly):
`main.py` and `experiments/compare.py` both need to build targets from
*string* provider names that come from argparse or a config dict — not
from Python code where you could just write `GeminiTarget(...)`
directly. This is the seam that makes `--compare` (running many model
configs from a list of dicts) possible without a big if/elif chain
scattered across the codebase.
"""

from target.base import BaseTarget
from target.providers import GeminiTarget, OpenAICompatibleTarget
from config.settings import settings


def get_model_target(provider: str, model_name: str, **overrides) -> BaseTarget:
    provider = provider.lower().strip()

    if provider == "gemini":
        return GeminiTarget(
            model_name=model_name,
            api_key=overrides.get("api_key", settings.gemini_api_key),
            **{k: v for k, v in overrides.items() if k != "api_key"},
        )

    if provider in ("openai", "openai-compatible"):
        return OpenAICompatibleTarget(
            model_name=model_name,
            api_key=overrides.get("api_key", settings.openai_api_key),
            base_url=overrides.get("base_url", settings.openai_base_url),
            **{k: v for k, v in overrides.items() if k not in ("api_key", "base_url")},
        )

    raise ValueError(f"Unknown provider: {provider}")
