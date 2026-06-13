import json
import logging
import os
import re
import shutil
import traceback
import unicodedata
from pathlib import Path

from pydantic import BaseModel
from pytubefix import Playlist, YouTube
from pytubefix.exceptions import BotDetection
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MetadataPlaylist(BaseModel):
    type: str
    url: str


class MetadataVideo(BaseModel):
    type: str
    url: str
    id: str


class Settings(BaseModel):
    extensive: bool = False


METADATA_PLAYLIST_FILENAME = "metadata_playlist.json"
METADATA_VIDEO_FILENAME = "metadata_video.json"
TRANSCRIPT_FILENAME = "transcript.txt"


def process_dir(directory: Path, configs: Path) -> None:
    assert os.path.isdir(directory), f"'{directory}' is not a directory"
    assert os.path.isdir(configs), f"'{configs}' is not a directory"

    with open(configs) as f:
        settings = Settings.model_validate_json(f.read())

    to_process = []
    for root, dirs, files in os.walk(directory):
        if METADATA_PLAYLIST_FILENAME not in files:
            continue

        to_process.append((root, dirs, files))

    for i, (root, dirs, _files) in enumerate(to_process):
        logger.info(f"Progress: {i + 1}/{len(to_process)}")
        process_playlist(Path(root), dirs, settings.extensive)


def process_playlist(root: Path, dirs: list[str], extensive: bool) -> None:
    logger.info(f"Processing playlist root: '{root}'")
    current_video_dirs = get_current_video_dirs(root, dirs)

    with open(Path(root) / METADATA_PLAYLIST_FILENAME) as f:
        metadata_playlist = MetadataPlaylist.model_validate_json(f.read())
        playlist = Playlist(metadata_playlist.url)

    logger.info("Playlist title: '%s'", playlist.title)
    for n, video in enumerate(playlist.videos):
        try:
            logger.info(f"Processing video {n + 1}")

            video_dirname_prefix = get_video_dirname_prefix(n)
            if not extensive:
                for video_dirname in current_video_dirs.values():
                    if (
                        video_dirname.name.startswith(video_dirname_prefix)
                        and (Path(video_dirname) / TRANSCRIPT_FILENAME).exists()
                    ):
                        continue

            video_title = get_video_title(video.title)

            video_dirpath_current = current_video_dirs.get(video.video_id)

            video_dirname_new = video_dirname_prefix + video_title
            video_dirpath_new = root / video_dirname_new

            if video_dirpath_current and video_dirpath_current != video_dirpath_new:
                os.rename(video_dirpath_current, video_dirpath_new)
            else:
                os.makedirs(video_dirpath_new, exist_ok=True)

            if not (video_dirpath_new / TRANSCRIPT_FILENAME).exists():
                save_video_transcript(video, video_dirpath_new)

            save_video_metadata(video, video_dirpath_new)
            current_video_dirs.pop(video.video_id, None)

        except BotDetection as e:
            logger.warning(f"Bot detection error processing video with index {n}")
            write_error(root, n, e)
        except Exception as e:
            logger.exception(f"Error processing video with index '{video.title}'")
            write_error(root, video, e)

    for video_dirpath_current in current_video_dirs.values():
        shutil.rmtree(video_dirpath_current)

    logger.info("Finished processing playlist root: '%s'\n", root)


def get_current_video_dirs(root: Path, dirs: list[str]) -> dict[str, Path]:
    current_video_dirs = {}
    for d in dirs:
        video_dirpath_current = root / d
        metadata_video_filepath = video_dirpath_current / METADATA_VIDEO_FILENAME
        if not metadata_video_filepath.exists():
            continue
        with open(metadata_video_filepath) as f:
            metadata_video = MetadataVideo.model_validate_json(f.read())

        current_video_dirs[metadata_video.id] = video_dirpath_current

    return current_video_dirs


def save_video_transcript(video: YouTube, video_dir: Path) -> None:
    transcript = YouTubeTranscriptApi().fetch(video_id=video.video_id)
    transcript_text = " ".join(x["text"] for x in transcript.to_raw_data())

    with open(video_dir / TRANSCRIPT_FILENAME, "w") as f:
        f.write(transcript_text)


def save_video_metadata(video: YouTube, video_dir: Path) -> None:
    with open(video_dir / METADATA_VIDEO_FILENAME, "w") as f:
        json.dump(
            {
                "type": "video",
                "url": video.watch_url,
                "title": video.title,
                "id": video.video_id,
            },
            f,
            indent=4,
        )


def get_video_title(title: str) -> str:
    title = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    title = re.sub(r"[^A-Za-z0-9_ ]", " ", title)
    title = title.strip()
    return re.sub(r" +", "_", title)


def get_video_dirname_prefix(n: int) -> str:
    return f"{n + 1:04d}_"


def write_error(directory: Path, video: YouTube | int, exc: Exception) -> None:
    errors_dir = directory / "errors"
    os.makedirs(errors_dir, exist_ok=True)
    video_title = (
        get_video_title(video.title)
        if isinstance(video, YouTube)
        else f"video_{video + 1:04d}"
    )
    with open(errors_dir / (video_title + ".txt"), "a") as f:
        f.write("------------------------------------------------------\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
