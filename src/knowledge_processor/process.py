from pathlib import Path

from knowledge_processor.knowledge_source.youtube.youtube import (
    extract_data_from_playlists,
    write_notes_from_playlists,
)
from knowledge_processor.models.models import Settings
from knowledge_processor.utils.utils import get_logger, get_settings, get_to_process

logger = get_logger()


def process_dir(directory: Path, settings: Path | Settings) -> None:
    to_process = get_to_process(directory)
    settings = get_settings(settings)

    extract_data_from_playlists(to_process, settings)
    write_notes_from_playlists(to_process, settings)
