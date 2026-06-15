from pathlib import Path

import duckdb

from knowledge_processor.db.db import create_index, create_table, insert_playlists
from knowledge_processor.knowledge_source.youtube.youtube import (
    extract_data_from_playlists,
    write_notes_from_playlists,
)
from knowledge_processor.models.models import Settings
from knowledge_processor.utils.utils import (
    get_directory,
    get_logger,
    get_settings,
    get_to_process,
)

logger = get_logger()


def process_dir(settings: Path | Settings, directory: Path | None = None) -> None:
    settings = get_settings(settings)
    directory = get_directory(settings, directory)
    to_process = get_to_process(directory)

    yt_playlists = extract_data_from_playlists(to_process, settings)
    write_notes_from_playlists(yt_playlists, settings)
    with duckdb.connect(str(settings.db_path)) as conn:
        create_table(conn)
        insert_playlists(yt_playlists, conn)
        create_index(conn)
