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

import json
import pathlib
import re
import struct

import common
import game_variants


RE_SCRIPT_HEADER_LINE = re.compile(
    r'(?P<name>\w+)'      # name
    r'\s*'                # (optional whitespace)
    r'(?:'                # optional group for priority value
    r'\['                 # | literal "["
    r'\s*'                # | (optional whitespace)
    r'priority'           # | literal "priority"
    r'\s*'                # | (optional whitespace)
    r'='                  # | literal "="
    r'\s*'                # | (optional whitespace)
    r'(?P<priority>\d+)'  # | priority value
    r'\s*'                # | (optional whitespace)
    r'\]'                 # | literal "]"
    r')?'                 # (ending the group)
    r':'                  # literal ":"
)

RE_COMMAND_LINE = re.compile(
    r'(?P<id>\w+)'        # ID
    r'\s*'                # (optional whitespace)
    r'(?:'                # optional group for argument
    r'\s'                 # | (required whitespace)
    r'(?P<arg>\w+)'       # | argument
    r')?'                 # (ending the group)
)

RE_SCRIPT_DEFAULT_NAME = re.compile(
    r'scr_'               # literal "scr_"
    r'(?P<id>\d+)'        # ID
)

RE_COMMAND_DEFAULT_NAME = re.compile(
    r'cmd_'               # literal "cmd_"
    r'(?P<id>\d+)'        # ID
)

class ScriptsFileReader:
    """
    Class for reading scripts files
    """
    def __init__(self, file):
        self.file = file
        self.scripts = {}

        self.current_script_name = None
        self.current_script = None

    def read_all_from_file(self) -> None:
        """
        Read all lines from self.file
        """
        for i, line in enumerate(self.file):
            line = line.rstrip('\n')
            self.read_line(line, i)

        self.flush_current_script()

    def read_line(self, line: str, line_num: int) -> None:
        """
        Read a single line from the script file.
        line_num is only needed for error messages.
        """
        # Do some basic preprocessing
        line = line.split('#')[0]  # comments
        line = line.strip()
        if not line: return

        # Is it a script-header line?
        match = RE_SCRIPT_HEADER_LINE.fullmatch(line)
        if match:
            gd = match.groupdict()

            self.flush_current_script()
            self.current_script_name = gd['name']
            self.current_script = common.HighLevelScript()
            if gd.get('priority') is not None:
                self.current_script.priority = int(gd['priority'])
            return

        # Must be a command, then
        match = RE_COMMAND_LINE.fullmatch(line)
        if match:
            gd = match.groupdict()

            if self.current_script is None:
                raise ValueError(f'Command not within any script (line {line_num+1})')

            cmd = common.HighLevelCommand(gd['id'], gd.get('arg'))
            self.current_script.append(cmd)
            return

        else:
            raise ValueError(f"Couldn't read line {line_num+1}")

    def flush_current_script(self) -> None:
        """
        Flush self.current_script[_name] to self.scripts, and reset them
        to None
        """
        if self.current_script is not None:
            self.scripts[self.current_script_name] = self.current_script
        self.current_script_name = None
        self.current_script = None


def read_scripts_file(file) -> dict:
    """
    Read a file-like object (text mode) and convert to a dict of
    {name: HighLevelScript}
    """
    reader = ScriptsFileReader(file)
    reader.read_all_from_file()
    return reader.scripts


def convert_to_low_level(high_level_scripts: dict, variant: game_variants.GameVariant) -> dict:
    """
    Convert a dict of {name: HighLevelScript} to a dict of
    {id: LowLevelScript} according to the provided GameVariant
    """
    def get_script_info(name: str) -> (int, dict):
        """
        Get the correct ID and info dict for a script name
        """
        this_variant = variant
        while this_variant:
            for other_id, other_dict in this_variant.scripts.add.items():
                if name == other_dict.get('name'):
                    return other_id, other_dict
            for ren in this_variant.scripts.renumber:
                id = ren.apply(id)
            this_variant = this_variant.parent

        match = RE_SCRIPT_DEFAULT_NAME.fullmatch(name)
        if match:
            return int(match.groupdict()['id']), {}

        raise ValueError(f'Unknown script name: "{name}"')

    def get_command_info(name: str) -> (int, dict):
        """
        Get the correct ID and info dict for a command name
        """
        this_variant = variant
        while this_variant:
            for other_id, other_dict in this_variant.commands.add.items():
                if name == other_dict.get('name'):
                    return other_id, other_dict
            for ren in this_variant.commands.renumber:
                id = ren.apply(id)
            this_variant = this_variant.parent

        match = RE_COMMAND_DEFAULT_NAME.fullmatch(name)
        if match:
            return int(match.groupdict()['id']), {}

        raise ValueError(f'Unknown command name: "{name}"')

    low_level_scripts = {}
    for script_name, script_high in high_level_scripts.items():
        script_id, script_info = get_script_info(script_name)

        # Make LowLevelScript and add it to the dict by ID
        script_low = common.LowLevelScript()
        low_level_scripts[script_id] = script_low

        if script_high.priority is not None:
            script_low.priority = script_high.priority

        for command_high in script_high:
            command_id, command_info = get_command_info(command_high.id)

            # Argument
            low_arg = 0
            if command_high.argument is not None:
                try:
                    low_arg = int(command_high.argument, 0)
                except ValueError:
                    low_arg = command_info.get('enum', {}).get(command_high.argument)
                    if low_arg is None:
                        raise ValueError(f'Unable to understand argument: "{command_high.argument}"')

            # Create LowLevelCommand and add it to the script
            command_low = common.LowLevelCommand(command_id, low_arg)
            script_low.append(command_low)

    return low_level_scripts


def encode_wms(scripts: dict, *, endian: str, use_priorities: bool) -> bytes:
    """
    Convert a dict of common.LowLevelScript to .wms file data
    """
    data = bytearray()
    table_entry_len = (8 if use_priorities else 4)

    def u32(val: int) -> bytes:
        return struct.pack(f'{endian}I', val)

    # Number of scripts
    data += u32(len(scripts))

    # IDs table
    for id in sorted(scripts):
        data += u32(id)

    # Scripts table (dummy at first)
    scripts_table_ptr = len(data)
    data += (b'\0' * table_entry_len) * len(scripts)

    # Each script
    for id in sorted(scripts):
        script = scripts[id]

        if use_priorities:
            table_entry = u32(script.priority) + u32(len(data))
        else:
            table_entry = u32(len(data))

        data[scripts_table_ptr : scripts_table_ptr + table_entry_len] = table_entry
        scripts_table_ptr += table_entry_len

        for command in script:
            data += u32(command.id) + u32(command.argument)

    return bytes(data)


def do_encode(scripts_file: pathlib.Path, version_info_file: pathlib.Path, wms_file: pathlib.Path) -> None:
    """
    Handle the "encode" command (with all default parameter values filled in as needed)
    """
    # Load scripts file
    with scripts_file.open('r', encoding='utf-8') as f:
        scripts_high = read_scripts_file(f)

    # Load version-info file
    with version_info_file.open('r', encoding='utf-8') as f:
        version_info = json.load(f)

    # Get a GameVariant instance
    variants = game_variants.load_game_json(common.Game(version_info['game']))
    variant = variants[version_info['game_variant']]

    # Convert high- to low-level scripts
    scripts_low = convert_to_low_level(scripts_high, variant)

    # Encode and save .wms data
    wms_data = encode_wms(scripts_low,
        endian=variant.game.endian(),
        use_priorities=variant.game.uses_script_priorities())

    with wms_file.open('wb') as f:
        f.write(wms_data)
