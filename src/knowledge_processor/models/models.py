from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class SourceTypes(StrEnum):
    yt_video = "yt_video"
    yt_playlist = "yt_playlist"


class SettingsYtPlaylist(BaseModel):
    extract_data: bool = False
    file_name: str = "_obj_yt_playlist.json"

    generate_notes: bool = False

    write_notes: bool = False
    notes_dir_name: str = "notes"
    notes_missing_dirname: str = "notes_missing_videos"


class Settings(BaseModel):
    directory: Path | None = None
    db_path: Path | None = None
    yt_playlist: SettingsYtPlaylist = SettingsYtPlaylist()


class Source(BaseModel):
    id: str | None = None
    type: SourceTypes
    title: str | None = None


class YtVideo(Source):
    type: Literal[SourceTypes.yt_video]
    title_simplified: str | None = None
    url: str
    transcript: str | None = None
    notes: str | None = None


class YtPlaylist(Source):
    type: Literal[SourceTypes.yt_playlist]
    title: str | None = None
    url: str
    file_path: Path | None = None
    videos: list[YtVideo] = []
    videos_missing: list[YtVideo] = []
