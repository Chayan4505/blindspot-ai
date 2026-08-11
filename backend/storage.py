"""
Storage abstraction — Supabase Storage (S3-compatible) in production,
local filesystem fallback for development.
"""
import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")          # https://<ref>.supabase.co
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "blindspot")
BASE_API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Use Supabase when the URL is provided
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

# Local data directory (used in dev / fallback)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ── Supabase Storage client (lazy) ────────────────────────────────────────────

def _supabase_client():
    """Return a Supabase client instance (imported lazily to avoid hard dep in dev)."""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ── Public API ────────────────────────────────────────────────────────────────

def upload_file(local_path: str, storage_key: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file from a local path. Returns the storage_key."""
    if USE_SUPABASE:
        try:
            client = _supabase_client()
            with open(local_path, "rb") as f:
                data = f.read()
            client.storage.from_(STORAGE_BUCKET).upload(
                path=storage_key,
                file=data,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            logger.info(f"[storage] Uploaded {storage_key} to Supabase")
            return storage_key
        except Exception as e:
            logger.error(f"[storage] Supabase upload failed: {e}")
            raise

    # ── Local fallback ──
    dest = os.path.join(DATA_DIR, storage_key)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(local_path, dest)
    return storage_key


def upload_bytes(data: bytes, storage_key: str, content_type: str = "application/octet-stream") -> str:
    """Upload raw bytes. Returns the storage_key."""
    if USE_SUPABASE:
        try:
            client = _supabase_client()
            client.storage.from_(STORAGE_BUCKET).upload(
                path=storage_key,
                file=data,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            logger.info(f"[storage] Uploaded bytes -> {storage_key} to Supabase")
            return storage_key
        except Exception as e:
            logger.error(f"[storage] Supabase bytes upload failed: {e}")
            raise

    # ── Local fallback ──
    dest = os.path.join(DATA_DIR, storage_key)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return storage_key


def get_public_url(storage_key: str) -> str:
    """Return a public URL for a stored file."""
    if USE_SUPABASE:
        client = _supabase_client()
        res = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_key)
        return res

    # ── Local fallback: serve via FastAPI /media ──
    return f"{BASE_API_URL}/media/{storage_key}"


def get_presigned_url(storage_key: str, expiry: int = 3600) -> str:
    """Return a signed (time-limited) download URL."""
    if USE_SUPABASE:
        try:
            client = _supabase_client()
            res = client.storage.from_(STORAGE_BUCKET).create_signed_url(storage_key, expiry)
            return res["signedURL"]
        except Exception as e:
            logger.warning(f"[storage] Could not create signed URL, falling back to public: {e}")
            return get_public_url(storage_key)

    return f"{BASE_API_URL}/media/{storage_key}"


def download_file(storage_key: str, local_path: str):
    """Download a file to a local path."""
    if USE_SUPABASE:
        try:
            client = _supabase_client()
            data = client.storage.from_(STORAGE_BUCKET).download(storage_key)
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(data)
            return
        except Exception as e:
            logger.error(f"[storage] Supabase download failed for {storage_key}: {e}")
            raise

    # ── Local fallback ──
    src = os.path.join(DATA_DIR, storage_key)
    shutil.copy(src, local_path)
