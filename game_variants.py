# 2021-05-15

import enum
import json
import pathlib

import common


class RenumberingRange:
    """
    Represents a "renumber" entry from one of the jsons, like
        "291-*": "+2"
    from NSMBU 1.3.0, for example
    """
    range_start: int
    range_end: int
    offset: int

    def __init__(self, range_start: int, range_end: int, offset: int):
        self.range_start = range_start
        self.range_end = range_end
        self.offset = offset

    @classmethod
    def read_from_json(cls, key, value):
        """
        Create from a json key/value pair
        """
        start_str, end_str = key.split('-')

        range_start = int(start_str)

        if end_str == '*':
            range_end = None
        else:
            range_end = int(end_str)

        offset = int(value)

        return cls(range_start, range_end, offset)


    def apply(self, value: int) -> int:
        """
        Apply this renumbering to the value provided
        """
        offset = 0

        if self.range_end is None:
            if self.range_start <= value:
                offset = self.offset
        else:
            if self.range_start <= value <= self.range_end:
                offset = self.offset

        return value + offset


class NumberedListDiff:
    """
    A class representing the difference between two {id: value} maps --
    some items may have been renumbered, some added, and some deleted
    """
    renumber: list
    add: dict
    delete: set

    def __init__(self, renumber: list, add: dict, delete: set):
        self.renumber = renumber
        self.add = add
        self.delete = delete

    @classmethod
    def read_from_json(cls, json_info: dict):
        """
        Create a NumberedListDiff from a dict read from a json
        """
        renumber = []
        for key, value in json_info.get('renumber', {}).items():
            renumber.append(RenumberingRange.read_from_json(key, value))

        add = common.convert_str_keys_to_int_keys(json_info.get('add', {}))
        delete = common.convert_str_keys_to_int_keys(json_info.get('delete', {}))

        return cls(renumber, add, delete)


class GameVariant:
    """
    A specific version of a game (like "NSMBU 1.3.0")
    """
    id: str
    game: common.Game
    parent: 'GameVariant' = None
    name: str = None
    scripts: NumberedListDiff
    commands: NumberedListDiff

    def __init__(self, id: str, parent: str, name: 'GameVariant', scripts: NumberedListDiff, commands: NumberedListDiff):
        self.id = id
        self.parent = parent
        self.name = name
        self.scripts = scripts
        self.commands = commands

    @classmethod
    def read_from_json(cls, json_info: dict):
        """
        Create a GameVariant from a dict read from a json
        """
        name = json_info.get('name')
        scripts = NumberedListDiff.read_from_json(json_info.get('scripts', {}))
        commands = NumberedListDiff.read_from_json(json_info.get('commands', {}))

        return cls(None, None, name, scripts, commands)


def load_game_json(game: common.Game) -> dict:
    """
    Load {game}.json and return the dict of {variant_name: GameVariant}
    """
    # Load json
    with open(f'data/{game.value}.json', 'r', encoding='utf-8') as f:
        j = json.load(f)

    # Load variants individually
    variants = {}
    for id, variant_dict in j.items():
        variant = GameVariant.read_from_json(variant_dict)
        variant.id = id
        variant.game = game
        variants[id] = variant

    # Assign parents
    for id, variant_dict in j.items():
        variant = variants[id]
        parent_name = variant_dict.get('parent')
        if parent_name:
            variant.parent = variants[parent_name]

    return variants
