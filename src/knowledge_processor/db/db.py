import duckdb

from knowledge_processor.db.utils.utils import insert_playlist
from knowledge_processor.models.models import YtPlaylist
from knowledge_processor.utils.utils import get_logger

logger = get_logger()


def create_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE OR REPLACE TABLE knowledge (
            id VARCHAR,
            type VARCHAR,
            title VARCHAR,
            notes VARCHAR,
            parent_id VARCHAR,
            parent_type VARCHAR,
            parent_title VARCHAR,
            parent_filepath VARCHAR,
            other JSON
        );
    """)


def insert_playlists(
    playlists: list[YtPlaylist], conn: duckdb.DuckDBPyConnection
) -> None:
    logger.info(f"Processing {len(playlists)} playlists into database")
    for i, playlist in enumerate(playlists):
        logger.info(f"Processing playlist: {playlist.title}")
        insert_playlist(conn, playlist)
        logger.info(
            f"Finished processing playlist: {playlist.title}. Progress: {(i + 1) / len(playlists) * 100:.0f}%"
        )
    logger.info(f"Finished processing {len(playlists)} playlists into database")


def create_index(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("INSTALL fts; LOAD fts;")

    conn.execute("""
        PRAGMA create_fts_index(
            'knowledge',    -- table
            'id',           -- id column
            'notes',        -- columns to index
            overwrite=1
        );
    """)
