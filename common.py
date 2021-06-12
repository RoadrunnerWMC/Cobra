# Copyright 2021 RoadrunnerWMC
#
# This file is part of Cobra.
#
# Cobra is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cobra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cobra.  If not, see <https://www.gnu.org/licenses/>.

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


def convert_str_keys_to_int_keys(map: dict) -> dict:
    """
    JSON doesn't allow object keys to be ints, so the closest you can do
    is strings containing ints.
    This function takes such a dict and converts it to one with actual
    int keys. (Any base is allowed, i.e. you can do "0x1234ABCD".)
    """
    return {int(key, 0): value for key, value in map.items()}


@enum.unique
class Game(enum.Enum):
    """
    Supported games
    """
    NSMBW = 'nsmbw'
    NSMB2 = 'nsmb2'
    NSMBU = 'nsmbu'
    NSMBUDX = 'nsmbudx'

    def uses_script_priorities(self) -> bool:
        """
        Only the games after NSMBW use a priority queue for scripts
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

    def endian(self) -> str:
        """
        Return '>' or '<' for this game's endianness
        """
        if self in {Game.NSMBW, Game.NSMBU}:
            return '>'
        else:
            return '<'


@dataclasses.dataclass
class LowLevelCommand:
    """
    Represents a "low-level" command -- an (ID, argument) pair, both ints.
    """
    id: int
    argument: int = 0

    def __init__(self, id: int, argument: int):
        self.id = id
        self.argument = argument


class LowLevelScript(list):
    """
    `list` subclass representing a "low-level" script -- a list of LowLevelCommand
    """
    priority: int = 0



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
    priority: int = None

