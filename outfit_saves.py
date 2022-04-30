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
        return json.dumps({
            'garmet_type': self.garmet_type,
            'garmet_name': self.garmet_name,
            'image_url': self.image_url
        })


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

        if os.path.exists("cache/.saved_outfits"):
            with open("cache/.saved_outfits") as file:
                try:
                    self.outfits_per_channel = json.load(file)
                except json.JSONDecodeError:
                    pass

    def save_outfit(self, channel_id: int, outfit: OutfitSet):
        self.outfits_per_channel.setdefault(channel_id, []).append(outfit)

    def get_saved_outfit(self, channel_id: int):
        if channel_id not in self.outfits_per_channel:
            return []
        return self.outfits_per_channel[channel_id]

    def save(self):
        with open("cache/.saved_outfits", 'w') as file:
            file.write(json.dumps(self._to_obj()))

    def _to_obj(self):
        print(self.outfits_per_channel)
        return {key: [x._to_obj() for x in value] for key, value in self.outfits_per_channel.items()}
