import os
import json
import glob

if os.path.exists("pack/assets/minecraft/models/item/shield.json"):
    with open("pack/assets/minecraft/models/item/shield.json") as f:
        data = json.load(f)
        predicate = [d["predicate"] for d in data["overrides"]]
        model = [d["model"] for d in data["overrides"]]

    for m, p in zip(model, predicate):
        if m == "item/shield" or ("custom_model_data" not in p):
            continue
        try:
            fpath = f"cache/shield/{p['custom_model_data']}.json"
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            if not os.path.exists(fpath):
                with open(fpath, "w") as f:
                    f.write("{}")
            with open(fpath, "r") as f:
                data = json.load(f)

            if "blocking" in m:
                data["blocking"] = m
            else:
                data["default"] = m

            data["check"] = data.get("check", 0) + 1
            with open(fpath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(e)

for file in glob.glob("cache/shield/*.json"):
    with open(file, "r") as f:
        data = json.load(f)
    if data.get("check") == 2:
        animation = {}
        for i in ["default", "blocking"]:
            namespace, path = data[i].split(":")
            files = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            fa = None
            for candidate in files:
                if f"{path.split('/')[-1]}." in candidate:
                    fa = candidate
                    break
            if not fa:
                print(f"[WARN] Không tìm thấy attachable cho {data[i]}")
                continue

            with open(fa, "r") as f:
                dataA = json.load(f)
                anims = dataA["minecraft:attachable"]["description"]["animations"]
                gmdl = dataA["minecraft:attachable"]["description"]["identifier"]

            if i == "default":
                saf = fa
                adata = dataA
                animation.update({
                    "mainhand.first_person": anims["firstperson_main_hand"],
                    "mainhand.third_person": anims["thirdperson_main_hand"],
                    "offhand.first_person": anims["firstperson_off_hand"],
                    "offhand.third_person": anims["thirdperson_off_hand"],
                })
                animate = [
                    {"mainhand.third_person.block": f"!c.is_first_person && c.item_slot == 'main_hand' && q.is_item_name_any('slot.weapon.mainhand', '{gmdl}') && query.is_sneaking"},
                    {"mainhand.first_person.block": f"c.is_first_person && c.item_slot == 'main_hand' && q.is_item_name_any('slot.weapon.mainhand', '{gmdl}') && query.is_sneaking"},
                    {"mainhand.first_person": f"c.is_first_person && c.item_slot == 'main_hand' && q.is_item_name_any('slot.weapon.mainhand', '{gmdl}') && !query.is_sneaking"},
                    {"mainhand.third_person": f"!c.is_first_person && c.item_slot == 'main_hand' && q.is_item_name_any('slot.weapon.mainhand', '{gmdl}') && !query.is_sneaking"},
                    {"offhand.third_person.block": f"!c.is_first_person && c.item_slot == 'off_hand' && q.is_item_name_any('slot.weapon.offhand', '{gmdl}') && query.is_sneaking"},
                    {"offhand.first_person.block": f"c.is_first_person && c.item_slot == 'off_hand' && q.is_item_name_any('slot.weapon.offhand', '{gmdl}') && query.is_sneaking"},
                    {"offhand.first_person": f"c.is_first_person && c.item_slot == 'off_hand' && q.is_item_name_any('slot.weapon.offhand', '{gmdl}') && !query.is_sneaking"},
                    {"offhand.third_person": f"!c.is_first_person && c.item_slot == 'off_hand' && q.is_item_name_any('slot.weapon.offhand', '{gmdl}') && !query.is_sneaking"}
                ]
            else:
                animation.update({
                    "mainhand.first_person.block": anims["firstperson_main_hand"],
                    "mainhand.third_person.block": anims["thirdperson_main_hand"],
                    "offhand.first_person.block": anims["firstperson_off_hand"],
                    "offhand.third_person.block": anims["thirdperson_off_hand"],
                })
                if "_blocking" in fa:
                    os.remove(fa)

        with open(saf, "w") as f:
            adata["minecraft:attachable"]["description"]["animations"] = animation
            adata["minecraft:attachable"]["description"]["scripts"]["animate"] = animate
            json.dump(adata, f, indent=2)
