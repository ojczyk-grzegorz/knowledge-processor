import logging
import os
from functools import lru_cache
from pathlib import Path

from knowledge_processor.models.models import Settings


@lru_cache(maxsize=1)
def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logger


def get_to_process(directory: Path) -> list[tuple[Path, list[str], list[str]]]:
    assert os.path.isdir(directory), f"'{directory}' is not a directory"
    return [(Path(root), dirs, files) for root, dirs, files in os.walk(directory)]


def get_directory(settings: Settings, directory: Path | None = None) -> Path:
    if isinstance(directory, Path):
        assert directory.is_dir(), f"'{directory}' is not a directory"
        return directory
    assert settings.directory.is_dir(), f"'{settings.directory}' is not a directory"
    return settings.directory


def get_settings(settings: Path | Settings) -> Settings:
    if isinstance(settings, Path):
        assert os.path.isfile(settings), f"'{settings}' is not a file"
        with open(settings) as f:
            settings = Settings.model_validate_json(f.read())
    else:
        assert isinstance(settings, Settings), (
            f"'{settings}' is not a '{Settings.__name__}' instance"
        )
    return settings
