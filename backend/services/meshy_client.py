from functools import lru_cache
import time

import requests

from utils import _get_required_env

BASE_URL = "https://api.meshy.ai/openapi/v1/image-to-3d"


@lru_cache(maxsize=1)
def get_meshy_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {"Authorization": f"Bearer {_get_required_env('MESHY_API_KEY')}"}
    )
    return session


def get_3d_model(image_url: str) -> str:
    """Converts a 2D image to a 3D model."""
    return "https://assets.meshy.ai/e991c18b-f59c-402b-804f-be313fbd1692/tasks/01a0bc86-5c45-73d1-a80c-6019e431a31a/output/model.glb?Expires=1790128609&Signature=mjVDheBXR5unp3ipuSfoRWt0LalpM3VnCmeKYYUJsAlpFrBtWSvMLJjr~OtJ~zkaEIsQAwCC1tiQYim87j7wI7iDSdmyv~puhNNPICzfAtJy3p8~Mngvd0HNiTaZ~eQUWtImE993ltkYlNZ15DpdlZaB2ldBk6zIVF9fpzyDOQCdA702Ae0H2RS9S0vvLzPEblm171TYoc4MDHiKIcyv68rKdmF7QTmCtYeI6wlScr1QOBy3gfZSmzrn~rdOVVlZQVVIvI6QCEN6NP4kYeKD4TU9hxDSvP0GhK2Myd~A4UgAGohEMt-Se3w5ev7rBO0iL0J-RJzw4sKPUBn~cFC-zw__&Key-Pair-Id=K1VGYTHIYLM9UM"
    # NOTE: For the demo, I'll pregenerate some of these. They take 90 seconds to generate from scratch.
    # task = wait_for_task(create_task(image_url))
    # return task["model_urls"]["glb"]


def create_task(image_url: str) -> str:
    """Starts an image-to-3D task."""
    response = get_meshy_session().post(
        BASE_URL,
        json={
            "image_url": image_url,
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
