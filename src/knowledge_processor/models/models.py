from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class YtTypes(StrEnum):
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
    yt_playlist: SettingsYtPlaylist = SettingsYtPlaylist()


class YtVideo(BaseModel):
    id: str
    type: Literal["yt_video"]
    url: str | None = None
    title: str | None = None
    title_simplified: str | None = None
    transcript: str | None = None
    notes: str | None = None


class YtPlaylist(BaseModel):
    url: str
    type: Literal["yt_playlist"]
    title: str | None = None
    videos: list[YtVideo] = []
    videos_missing: list[YtVideo] = []
