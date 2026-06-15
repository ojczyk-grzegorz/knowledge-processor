import os
import re
import unicodedata
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from knowledge_processor.models.models import Settings, SourceTypes, YtPlaylist, YtVideo
from knowledge_processor.utils.utils import get_logger

logger = get_logger()

_YTDLP_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": "in_playlist",
}


def get_playlist_data(playlist_filepath) -> YtPlaylist:
    with open(playlist_filepath) as f:
        yt_playlist = YtPlaylist.model_validate_json(f.read())

    return yt_playlist


def extract_data_from_playlist(yt_playlist: YtPlaylist, path: Path) -> YtPlaylist:
    yt_playlist.file_path = path

    with yt_dlp.YoutubeDL(_YTDLP_OPTS) as ydl:
        info = ydl.extract_info(yt_playlist.url, download=False)

    yt_playlist.id = info.get("id")
    yt_playlist.title = info.get("title")

    if not info or not info.get("entries"):
        logger.warning(
            "No videos returned for playlist '%s', skipping to avoid data loss",
            yt_playlist.url,
        )
        return yt_playlist

    videos_current = {}
    for video in [*yt_playlist.videos, *yt_playlist.videos_missing]:
        videos_current[video.id] = video
    videos_new = []

    entries = list(info["entries"])
    logger.info("Playlist videos count: %d", len(entries))

    for entry in entries:
        video_id = entry.get("id")
        if not video_id:
            logger.warning("Skipping entry with no id: %s", entry)
            continue

        yt_video = videos_current.get(video_id)
        try:
            yt_video = get_video_data(yt_video, video_id, entry)
        except Exception as e:
            logger.error("Error processing video %s: %s", video_id, e)

        if yt_video:
            videos_new.append(yt_video)
            videos_current.pop(video_id, None)

    yt_playlist.videos = videos_new
    yt_playlist.videos_missing = list(videos_current.values())

    return yt_playlist


def get_video_data(yt_video: YtVideo | None, video_id: str, entry: dict) -> YtVideo:
    if not yt_video:
        yt_video = YtVideo(
            id=video_id,
            type=SourceTypes.yt_video,
            url=f"https://www.youtube.com/watch?v={video_id}",
        )

    if not yt_video.title:
        yt_video.title = entry.get("title")
    # if not yt_video.title_simplified and yt_video.title:
    yt_video.title_simplified = get_video_title(yt_video.title)
    if not yt_video.transcript:
        transcript = YouTubeTranscriptApi().fetch(video_id=video_id)
        yt_video.transcript = " ".join(x["text"] for x in transcript.to_raw_data())

    return yt_video


def write_playlist_notes(
    yt_playlist: YtPlaylist, root: Path, settings: Settings
) -> None:
    notes_dir = get_notes_dir(root, settings.yt_playlist.notes_dir_name)

    for i, video in enumerate(yt_playlist.videos):
        if not video.notes:
            continue

        prefix = get_video_dirname_prefix(i + 1)
        notes_filename = "_".join([prefix, video.title_simplified])
        notes_filepath = notes_dir / f"{notes_filename}.md"
        with open(notes_filepath, "w") as f:
            f.write(video.notes)

    notes_dir = get_notes_dir(root, settings.yt_playlist.notes_missing_dirname)
    if not yt_playlist.videos_missing:
        return

    for video in yt_playlist.videos_missing:
        if not video.notes:
            continue

        notes_filepath = notes_dir / f"{video.title_simplified}.md"
        with open(notes_filepath, "w") as f:
            f.write(video.notes)


def get_notes_dir(root: Path, notes_dir_name: str) -> Path:
    notes_dir = Path(root) / notes_dir_name
    notes_dir.mkdir(exist_ok=True)
    for rt, _, files in os.walk(notes_dir):
        for file in files:
            (Path(rt) / file).unlink()
    for rt, dirs, _ in os.walk(notes_dir):
        for dr in dirs:
            (Path(rt) / dr).rmdir()
    return notes_dir


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
    return f"{n:04d}"
