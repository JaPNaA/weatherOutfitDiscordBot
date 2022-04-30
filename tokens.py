import os
from typing import Optional


def get_token(token_name: str) -> Optional[str]:
    token_path = "./cache/." + token_name

    try:
        with open(token_path) as file:
            return file.read().strip()
    except IOError:
        new_token = input(f"Enter token '{token_name}': ")

        with open(token_path, 'w') as file:
            file.write(new_token)

        return new_token
