from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def config_path() -> None:
    cfg_path = Path(__file__).parent / "data/config.json"
    if not cfg_path.exists() and not cfg_path.is_file():
        raise FileNotFoundError(f"File not found: {cfg_path}")
    return cfg_path
