import tomllib
from pydantic import BaseModel


class Bungie(BaseModel):
    token: str


class Destiny(BaseModel):
    member_id: int
    character_id: int


class Config(BaseModel):
    bungie: Bungie
    destiny: Destiny


def load_config(config_file: str) -> Config:
    with open(config_file, "rb") as f:
        return Config.parse_obj(tomllib.load(f))
