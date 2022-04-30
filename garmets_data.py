from curses import has_extended_color_support
from email.charset import SHORTEST
import random


class Outfit:
    # hats = beanie, knitted had
    outfits = [
        [["beanie", "trapper", "winter headband"], ["beanie", "hood"], ["beanie", "hood", "nothing"], ["cap", "nothing"], ["cap", "nothing"]],
        [["layers of jacket"], ["jacket"], ["jacket"], ["long sleeve shirt", "turtle neck"], ["t-shirt", "tanktop"]],
        [["snow pants"], ["jeans"], ["jeans", "baggy pants"], ["jeans","baggy pants", "shorts", "joggers"], ["jeans", "baggy pants", "shorts", "joggers"]],
        [["snow boots"], ["winter boots"], ["winter boots", "sneakers", "white shoes"], ["white shoes", "flip flops", "running shoes", "dress shoe"], ["white shoes", "flip flops", "running shoes", "dress shoe"]],
        [["winter gloves"], ["gloves", "mittens"], ["gloves", "mittens", "none"], ["bike gloves", "none"], ["none"]]
    ]

    rainoutfits = [
        [["beanie", "trapper", "winter headband"], ["beanie", "hood"], ["beanie", "hood"], ["cap"], ["cap"]],
        [["layers of jacket"], ["jacket"], ["jacket"], ["raincoat"], ["raincoat"]],
        [["snow pants"], ["jeans"], ["jeans", "baggy pants"], ["jeans","baggy pants", "shorts", "joggers"], ["jeans", "baggy pants", "shorts", "joggers"]],
        [["snow boots"], ["winter boots"], ["winter boots", "sneakers", "white shoes"], ["running shoes"], ["flip flops", "running shoes"]],
        [["winter gloves"], ["gloves", "mittens"], ["gloves", "mittens", "none"], ["bike gloves", "none"], ["none"]]
    ]

    def pick_outfit(self, set: int, rain: bool):
        """ Returns a list of outfits you can wear given if it's raining or not"""
        retval = []
        for i in range(5):
            if not rain:
                retval.append(random.choice(outfits[i][set]))
            else:
                retval.append(random.choice(winteroutfits[i][set]))
        return retval