from pathlib import Path

from knowledge_processor.knowledge_source.youtube.utils import (
    extract_data_from_playlist,
    get_playlist_data,
    write_playlist_notes,
)
from knowledge_processor.models.models import Settings
from knowledge_processor.utils.utils import get_logger

logger = get_logger()


def extract_data_from_playlists(
    to_process: list[tuple[Path, list[str], list[str]]], settings: Settings
) -> None:
    if not settings.yt_playlist.extract_data:
        return

    logger.info("Extracting data from playlists")
    for i, (root, _, files) in enumerate(to_process):
        if settings.yt_playlist.file_name not in files:
            continue

        logger.info(f"Extracting data from playlist in '{root}' directory")

        playlist_filepath = Path(root) / settings.yt_playlist.file_name
        yt_playlist = get_playlist_data(playlist_filepath)
        yt_playlist = extract_data_from_playlist(yt_playlist)

        with open(playlist_filepath, "w") as f:
            f.write(yt_playlist.model_dump_json(indent=4))

        logger.info(
            f"Finished extracting data from playlist. Progress: {i / len(to_process) * 100:.0f}%"
        )
    logger.info("Finished extracting data from playlists")


def generate_notes_from_playlists(
    to_process: list[tuple[Path, list[str], list[str]]], settings: Settings
) -> None:
    logger.info("Generating notes from playlists")

    for i, (root, _, files) in enumerate(to_process):
        if settings.yt_playlist.file_name not in files:
            continue

        logger.info(f"Writing notes for playlist in '{root}' directory")

        logger.info(
            f"Finished writing notes for playlist. Progress: {i / len(to_process) * 100:.0f}%"
        )

    logger.info("Finished generating notes from playlists")


def write_notes_from_playlists(
    to_process: list[tuple[Path, list[str], list[str]]], settings: Settings
) -> None:
    if not settings.yt_playlist.write_notes:
        return

    logger.info("Writing notes from playlists")
    for i, (root, _, files) in enumerate(to_process):
        if settings.yt_playlist.file_name not in files:
            continue

        logger.info(f"Writing notes for playlist in '{root}' directory")

        yt_playlist = get_playlist_data(Path(root) / settings.yt_playlist.file_name)
        write_playlist_notes(yt_playlist, Path(root), settings)

        logger.info(
            f"Finished writing notes for playlist. Progress: {i / len(to_process) * 100:.0f}%"
        )
    logger.info("Finished writing notes from playlists")
