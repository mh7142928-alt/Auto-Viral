import time
import urllib.parse
import requests
from pathlib import Path
from config import TEMP_DIR

def generate_scene_image(prompt: str, output_path: str, seed: int = None) -> str:
    """
    Generates a stylized 3D character image via fast Pollinations API.
    Returns the path to the saved image.
    """
    clean_prompt = prompt.replace("\n", " ").strip()
    encoded = urllib.parse.quote(clean_prompt)
    seed_param = f"&seed={seed}" if seed else ""
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true{seed_param}"

    for attempt in range(3):
        try:
            res = requests.get(url, timeout=35)
            if res.status_code == 200 and len(res.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(res.content)
                return output_path
        except Exception as e:
            print(f"Warning: Image generation attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise RuntimeError(f"Failed to generate image after 3 attempts for prompt: {prompt[:60]}...")

def generate_scenes_images(scenes: list, session_prefix: str, fixed_seed: int = 42) -> list:
    """Generates images for all scenes in an episode, keeping a consistent seed for character similarity."""
    image_paths = []
    for idx, scene in enumerate(scenes):
        prompt = scene.get("visual_prompt", "cute 3d animated character, cinematic lighting")
        out_file = str(TEMP_DIR / f"{session_prefix}_scene_{idx + 1}.jpg")
        print(f"🎨 Generating visual for scene {idx + 1}/{len(scenes)}...")
        # Use consistent seed + slight offset for scene variation
        seed = (fixed_seed + idx * 7) % 10000
        path = generate_scene_image(prompt, out_file, seed=seed)
        image_paths.append(path)
    return image_paths

if __name__ == "__main__":
    print("Testing image generator...")
    p = generate_scene_image("cute 3d baby ginger kitten baker holding bread", "D:/Auto/temp/test_milo.jpg")
    print("Saved to:", p)
