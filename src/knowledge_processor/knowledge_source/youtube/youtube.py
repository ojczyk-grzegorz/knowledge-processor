from pathlib import Path

from knowledge_processor.knowledge_source.youtube.utils import (
    extract_data_from_playlist,
    get_playlist_data,
    write_playlist_notes,
)
from knowledge_processor.models.models import Settings, YtPlaylist
from knowledge_processor.utils.utils import get_logger

logger = get_logger()


def extract_data_from_playlists(
    to_process: list[tuple[Path, list[str], list[str]]], settings: Settings
) -> list[YtPlaylist]:
    yt_playlists = []
    logger.info("Extracting data from playlists")
    for i, (root, _, files) in enumerate(to_process):
        if settings.yt_playlist.file_name not in files:
            continue

        logger.info(f"Extracting data from playlist in '{root}' directory")

        playlist_filepath = Path(root) / settings.yt_playlist.file_name
        yt_playlist = get_playlist_data(playlist_filepath)

        if settings.yt_playlist.extract_data:
            yt_playlist = extract_data_from_playlist(yt_playlist, playlist_filepath)

        yt_playlists.append(yt_playlist)

        with open(playlist_filepath, "w") as f:
            f.write(yt_playlist.model_dump_json(indent=4))

        logger.info(
            f"Finished extracting data from playlist. Progress: {i / len(to_process) * 100:.0f}%"
        )
    logger.info("Finished extracting data from playlists")
    return yt_playlists


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
    yt_playlists: list[YtPlaylist], settings: Settings
) -> None:
    if not settings.yt_playlist.write_notes:
        return

    logger.info("Writing notes from playlists")
    for yt_playlist in yt_playlists:
        write_playlist_notes(yt_playlist, Path(yt_playlist.file_path).parent, settings)
    logger.info("Finished writing notes from playlists")
