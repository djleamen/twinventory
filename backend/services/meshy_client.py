from functools import lru_cache
import time

import requests

from services.mongo_client import get_model_task, save_model_task
from utils import _get_required_env, resolve_image_url

BASE_URL = "https://api.meshy.ai/openapi/v1/image-to-3d"


@lru_cache(maxsize=1)
def get_meshy_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {"Authorization": f"Bearer {_get_required_env('MESHY_API_KEY')}"}
    )
    return session


def get_3d_model(image_url: str, cache_key: str | None = None) -> str:
    """Converts a 2D image to a 3D model, reusing the cached Meshy task per image.

    Try-on results are keyed by their outfit cache_key; other images by URL.
    Ephemeral data-URI inputs without a cache_key are never cached.
    """
    if cache_key:
        lookup_key = f"tryon:{cache_key}"
    elif image_url.startswith("data:"):
        lookup_key = None
    else:
        lookup_key = image_url

    if lookup_key:
        task_id = get_model_task(lookup_key)
        if task_id:
            try:
                task = get_task(task_id)
                # Fetching a finished task returns a freshly signed GLB URL.
                if task.get("status") == "SUCCEEDED":
                    return task["model_urls"]["glb"]
            except requests.HTTPError:
                pass  # task gone upstream — regenerate below

    task_id = create_task(image_url)
    task = wait_for_task(task_id)
    if lookup_key:
        save_model_task(lookup_key, task_id)
    return task["model_urls"]["glb"]


def create_task(image_url: str) -> str:
    """Starts an image-to-3D task."""
    response = get_meshy_session().post(
        BASE_URL,
        json={
            "image_url": resolve_image_url(image_url),
            "model_type": "standard",
            "should_texture": True,
            "target_formats": ["glb"],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["result"]


def get_task(task_id: str) -> dict:
    """Fetch a Meshy task by ID."""
    response = get_meshy_session().get(f"{BASE_URL}/{task_id}", timeout=30)
    response.raise_for_status()
    return response.json()


def wait_for_task(task_id: str, interval: float = 5, timeout: float = 600) -> dict:
    """Polls until the task finishes and returns the full task data."""
    start = time.time()
    while True:
        task = get_task(task_id)

        status = task.get("status")
        if status == "SUCCEEDED":
            return task
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(
                f"Meshy task {task_id} {status}: {task.get('task_error')}"
            )
        if time.time() - start > timeout:
            raise TimeoutError(
                f"Meshy task {task_id} did not finish within {timeout} seconds"
            )

        time.sleep(interval)
