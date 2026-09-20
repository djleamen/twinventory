import { apiFetch } from "./client"

/** POST /models/convert — turns an image into a 3D model and returns the GLB link. Takes a minute or more. */
export function convertToModel(imageUrl: string): Promise<{ model_url: string }> {
  return apiFetch<{ model_url: string }>("/models/convert", {
    method: "POST",
    body: JSON.stringify({ image_url: imageUrl }),
  })
}
