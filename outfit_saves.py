import json
import os
from typing import Dict, List, Union


class OutfitItem:
    garmet_type: int
    garmet_name: Union[str, None]
    image_url: str

    def __init__(self, garmet_type: int, garmet_name: Union[str, None], image_url: str) -> None:
        self.garmet_type = garmet_type
        self.garmet_name = garmet_name
        self.image_url = image_url

    def _to_obj(self):
        return {
            'garmet_type': self.garmet_type,
            'garmet_name': self.garmet_name,
            'image_url': self.image_url
        }


class OutfitSet:
    items: List[OutfitItem]

    def __init__(self):
        self.items = []

    def add_item(self, item: OutfitItem):
        self.items.append(item)

    def _to_obj(self):
        return [x._to_obj() for x in self.items]


class SavedOutfits:
    outfits_per_channel: Dict[int, List[OutfitSet]]

    def __init__(self):
        self.outfits_per_channel = {}
        self._load_saved_outfits()

    def save_outfit(self, channel_id: int, outfit: OutfitSet):
        self.outfits_per_channel.setdefault(channel_id, []).append(outfit)
    
    def forget_outfit(self, channel_id: int, outfit_index: int):
        if channel_id not in self.outfits_per_channel:
            return
        outfits = self.outfits_per_channel[channel_id]
        outfits.remove(outfits[outfit_index])

    def get_saved_outfit(self, channel_id: int):
        if channel_id not in self.outfits_per_channel:
            return []
        return self.outfits_per_channel[channel_id]

    def save(self):
        with open("cache/.saved_outfits", 'w') as file:
            file.write(json.dumps(self._to_obj()))

    def _to_obj(self):
        return {key: [x._to_obj() for x in value] for key, value in self.outfits_per_channel.items()}

    def _load_saved_outfits(self):
        if not os.path.exists("cache/.saved_outfits"):
            return

        with open("cache/.saved_outfits") as file:
            try:
                saved_data = json.load(file)
            except json.JSONDecodeError:
                return

        for channel_id, saved_outfits in saved_data.items():
            parsed_saved_outfits = []

            for outfit_set in saved_outfits:
                parsed_outfit_set = OutfitSet()

                for item in outfit_set:
                    parsed_outfit_item = OutfitItem(
                        garmet_type=item['garmet_type'],
                        garmet_name=item['garmet_name'],
                        image_url=item['image_url']
                    )
                    parsed_outfit_set.add_item(parsed_outfit_item)

                parsed_saved_outfits.append(parsed_outfit_set)

            self.outfits_per_channel[int(channel_id)] = parsed_saved_outfits
