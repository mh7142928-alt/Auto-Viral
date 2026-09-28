import json
import random
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "series_state.json"

DEFAULT_STATE = {
    "fruits": {
        "series_id": "fruits_season_1",
        "series_title": "مغامرة بيري: الفراولة الصغيرة والمدينة السحرية",
        "universe_type": "fruits",
        "current_episode": 1,
        "total_episodes": 32,
        "protagonist": "Berry the tiny sweet strawberry with big emotional eyes, woolen gloves and a backpack",
        "character_prompt": "Adorable cute 3D Pixar animated anthropomorphic little strawberry named Berry, big expressive emotional teary brown eyes, wearing tiny brown boots, tiny wool mittens, small backpack, highly detailed 3D Disney Pixar render, 9:16 vertical ratio",
        "overall_plot": "بيري فراولة صغيرة تعيش في مدينة الفواكه الخيالية، تبحث عن بذور شجرة الحياة لإنقاذ متجر الفواكه القديم من الإغلاق. تواجه ألغازاً ومخاطر وأشراراً من الخضار الجافة، وتتعلم معنى الشجاعة.",
        "previous_summary": "تبدأ القصة في ليلة ممطرة وباردة حين يقف بيري وحيداً في شارع مدينة الفواكه، محاولاً حماية المتجر المتداعي."
    },
    "animals": {
        "series_id": "animals_season_1",
        "series_title": "رحلة ميلو: القط الصغير والمخبز السري",
        "universe_type": "animals",
        "current_episode": 1,
        "total_episodes": 30,
        "protagonist": "Milo the tiny cute fluffy ginger kitten wearing an apron and baker hat",
        "character_prompt": "Adorable cute 3D Pixar animated anthropomorphic fluffy baby ginger kitten named Milo, big cute glistening green eyes, wearing a tiny flour-dusted chef apron and little baker hat, standing in a cozy old bakery, warm cinematic lighting, ultra-detailed 8k, Disney Pixar style, 9:16 vertical ratio",
        "overall_plot": "ميلو قط صغير مشرد وجد ملجأه في مخبز مهجور لجد عجوز، ويحاول إحياء وصفة الخبز الذهبي السحرية ليجمع حيوانات القرية ويمنع هدم الحي القديم.",
        "previous_summary": "تبدأ القصة عندما يهرب ميلو الصغير من الرياح العاصفة ليلجأ إلى نافذة مخبز قديم دافئ مغلق منذ سنين."
    }
}

def load_state() -> dict:
    """Loads current series state from json or initializes with defaults."""
    if not STATE_FILE.exists():
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()

def save_state(state: dict):
    """Saves series state atomically to disk."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def advance_episode(series_key: str, episode_summary: str):
    """Increments the episode number and updates memory recap. Rolls over if series completed."""
    state = load_state()
    series = state.get(series_key)
    if not series:
        return

    series["current_episode"] += 1
    # Keep rolling recap of last events
    series["previous_summary"] = (series.get("previous_summary", "") + " " + episode_summary)[-400:]

    # Check for season finale rollover
    if series["current_episode"] > series["total_episodes"]:
        print(f"🎉 Series '{series['series_title']}' has reached its grand finale! Rolling over to a new saga...")
        rollover_new_series(series_key, state)
    else:
        save_state(state)

def rollover_new_series(series_key: str, state: dict):
    """Initializes a brand new story series when the current 30-35 episode arc concludes."""
    new_season_num = random.randint(2, 999)
    total_eps = random.randint(30, 35)

    if series_key == "fruits":
        characters = [
            ("Lemo", "cute little round lemon wearing glasses and a scarf", "ليمو.. الليمونة الفيلسوفة التي تبحث عن ينبوع العصير النقي"),
            ("Avy", "cute baby avocado with big eyes and a tiny compass", "آفي.. الأفوكادو الصغير الباحث عن عائلته عبر غابة الفواكه"),
            ("Melon", "adorable baby watermelon holding a wooden sword", "ميلون.. البطيخ الشجاع حارس قصر التوت الملكي")
        ]
        chosen = random.choice(characters)
        state["fruits"] = {
            "series_id": f"fruits_season_{new_season_num}",
            "series_title": f"حكاية {chosen[0]}: {chosen[2]}",
            "universe_type": "fruits",
            "current_episode": 1,
            "total_episodes": total_eps,
            "protagonist": chosen[0],
            "character_prompt": f"Adorable cute 3D Pixar animated anthropomorphic {chosen[1]}, emotional expressive eyes, cinematic lighting, Disney Pixar 3d, 9:16 vertical ratio",
            "overall_plot": chosen[2],
            "previous_summary": f"بداية الرحلة والمغامرة الجديدة لشخصية {chosen[0]}."
        }
    else: # animals
        characters = [
            ("Barny", "cute little fluffy bunny wearing tiny boots and a backpack", "بارني.. الأرنب الساعي وسر الرسالة الملكية المفقودة"),
            ("Rusty", "cute tiny red panda wearing an explorer vest", "راستي.. الباندا الأحمر ومغامرة البحث عن شجرة الخيزران الذهبية"),
            ("Pip", "cute little puppy wearing a tiny raincoat", "بيب.. الجرو الصغير الذي يجمع النجوم المتساقطة في الغابة")
        ]
        chosen = random.choice(characters)
        state["animals"] = {
            "series_id": f"animals_season_{new_season_num}",
            "series_title": f"مغامرة {chosen[0]}: {chosen[2]}",
            "universe_type": "animals",
            "current_episode": 1,
            "total_episodes": total_eps,
            "protagonist": chosen[0],
            "character_prompt": f"Adorable cute 3D Pixar animated anthropomorphic {chosen[1]}, emotional expressive eyes, cinematic lighting, Disney Pixar 3d, 9:16 vertical ratio",
            "overall_plot": chosen[2],
            "previous_summary": f"بداية المغامرة الشيقة لشخصية {chosen[0]}."
        }

    save_state(state)
    print(f"✨ New Series Created: {state[series_key]['series_title']} (Target: {total_eps} episodes)")

if __name__ == "__main__":
    s = load_state()
    print("Series State loaded successfully:")
    for k, v in s.items():
        print(f" - [{k.upper()}]: {v['series_title']} | Ep {v['current_episode']}/{v['total_episodes']}")
