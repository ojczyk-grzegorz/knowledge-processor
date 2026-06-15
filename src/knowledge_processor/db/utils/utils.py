import json

import duckdb

from knowledge_processor.models.models import YtPlaylist


def insert_playlist(conn: duckdb.DuckDBPyConnection, playlist: YtPlaylist) -> None:
    for video in [*playlist.videos, *playlist.videos_missing]:
        conn.execute(
            "INSERT INTO knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                video.id,
                str(video.type),
                video.title,
                video.notes,
                playlist.id,
                str(playlist.type),
                playlist.title,
                str(playlist.file_path),
                json.dumps(
                    {
                        "url": video.url,
                        "title_simplified": video.title_simplified,
                        "transcript": video.transcript,
                        "parent_url": playlist.url,
                    }
                ),
            ),
        )
