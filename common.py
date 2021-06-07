# 2021-05-15

import dataclasses
import enum


def iter_bytes_matches(haystack: bytes, needle: bytes):
    """
    Given a big bytes object and a small one, iterate over indices at
    which the small one is a substring of the big one
    """
    idx = haystack.find(needle)
    while idx != -1:
        yield idx
        idx = haystack.find(needle, idx + 1)


@enum.unique
class Game(enum.Enum):
    """
    Supported games
    """
    NSMBW = 'nsmbw'
    NSMB2 = 'nsmb2'
    NSMBU = 'nsmbu'
    NSMBUDX = 'nsmbudx'

    def uses_script_categories(self) -> bool:
        """
        Only the games after NSMBW use the "categories" system
        """
        return self is not Game.NSMBW

    def uses_command_arguments(self) -> bool:
        """
        NSMB2 doesn't use command arguments
        """
        return True
        # return self is not Game.NSMB2

    def gets_scripts_and_commands_from(self) -> 'Game':
        """
        NSMBUDX leeches most of its info off of NSMBU
        """
        if self is Game.NSMBUDX:
            return Game.NSMBU
        else:
            return self


@dataclasses.dataclass
class LowLevelCommand:
    """
    Represents a "low-level" command -- an (ID, argument) pair, both ints.
    """
    id: int
    argument: int

    def __init__(self, id: int, argument: int):
        self.id = id
        self.argument = argument


class LowLevelScript(list):
    """
    `list` subclass representing a "low-level" script -- a list of LowLevelCommand
    """
    category_id: int = None



@dataclasses.dataclass
class HighLevelCommand:
    """
    Represents a "high-level" command -- an (ID, argument) pair, both strings.
    argument is optional at this level. (The value is implied to be 0 in that case.)
    """
    id: str
    argument: str = None

    def __init__(self, id: str, argument: str):
        self.id = id
        self.argument = argument


class HighLevelScript(list):
    """
    `list` subclass representing a "high-level" script -- a list of HighLevelCommand
    """
    category_id: int = None

