import random
from typing import List


class Outfit:
    # hats = beanie, knitted had
    outfits = [
        [
            ["knit cap (beanie)", "ushanka (trapper)", "winter headband", "fedora", "santa hat"],
            ["knit cap (beanie)", "hood", "fedora"],
            ["knit cap (beanie)", "hood", "fedora", None],
            ["cap", None],
            ["cap", None]
        ],
        [
            ["layers of jacket"],
            ["jacket"],
            ["jacket"],
            ["long sleeve shirt", "polo neck (turtle neck)"],
            ["t-shirt", "tanktop"]
        ],
        [
            ["snow pants"],
            ["jeans"],
            ["jeans", "baggy pants"],
            ["jeans", "baggy pants", "shorts", "sweatpants"],
            ["jeans", "baggy pants", "shorts", "sweatpants"]
        ],
        [
            ["snow boots"],
            ["winter boots"],
            ["winter boots", "sneakers", "white shoes"],
            ["white shoes", "flip flops", "running shoes", "dress shoe"],
            ["white shoes", "flip flops", "running shoes", "dress shoe"]
        ],
        [
            ["winter gloves"],
            ["gloves", "mittens"],
            ["gloves", "mittens", None],
            ["bike gloves", None],
            [None]
        ]
    ]

    rainoutfits = [
        [
            ["knit cap (beanie)", "ushanka (trapper)", "winter headband"],
            ["knit cap (beanie)", "hood"],
            ["knit cap (beanie)", "hood"],
            ["cap"],
            ["cap"]
        ],
        [
            ["layers of jacket"],
            ["jacket"],
            ["jacket"],
            ["raincoat"],
            ["raincoat"]
        ],
        [
            ["snow pants"],
            ["jeans"],
            ["jeans", "baggy pants"],
            ["jeans", "baggy pants", "shorts", "sweatpants"],
            ["jeans", "baggy pants", "shorts", "sweatpants"]
        ],
        [
            ["snow boots"],
            ["winter boots"],
            ["winter boots", "sneakers", "white shoes"],
            ["rainboots"],
            ["flip flops"]
        ],
        [
            ["winter gloves"],
            ["gloves", "mittens", "umbrella"],
            ["gloves", "mittens", "umbrella"],
            ["bike gloves", "umbrella"],
            ["umbrella"]
        ]
    ]

    garmet_type_info = [{
        'type': "hat",
        'goes_on': "head"
    }, {
        'type': "shirt",
        'goes_on': "torso"
    }, {
        'type': "pants",
        'goes_on': "legs"
    }, {
        'type': "shoes",
        'goes_on': "feet"
    }, {
        'type': "gloves",
        'goes_on': "hands"
    }]

    set_type_names = ["freezing", "cold", "cool", "warm", "hot"]

    def pick_outfit(self, set: int, rain: bool) -> List[str]:
        """ Returns a list of outfits you can wear given if it's raining or not"""
        retval = []
        for i in range(5):
            if not rain:
                retval.append(random.choice(self.outfits[i][set]))
            else:
                retval.append(random.choice(self.rainoutfits[i][set]))
        return retval
