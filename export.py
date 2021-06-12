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

import enum
import json
import pathlib
import struct
import typing

import export_base
import export_nsmbw
import export_nsmbu
import export_nsmbudx

import common


class SourceType(enum.Enum):
    """
    Different things we're able to read scripts from
    """
    # Strings here are used in error messages, so they should look nice.

    # Wii
    DOL_FILE = 'DOL file'
    ALF_FILE = 'ALF file'
    DOLPHIN_RAM_DUMP_FOLDER = 'Dolphin RAM dump folder'
    DOLPHIN_RAM_DUMP_FILE = 'Dolphin MEM1 RAM dump file'

    # 3DS
    CITRA_RAM_DUMP_FOLDER = 'Citra RAM dump folder'
    CITRA_RAM_DUMP_FILE = 'Citra RAM dump file'

    # Wii U
    RPX_FILE = 'RPX file'
    CEMU_RAM_DUMP_FOLDER = 'Cemu RAM dump folder'
    CEMU_RAM_DUMP_FILE = 'Cemu RAM dump file'

    # Switch
    NSO_FILE = 'NSO file'

    def game(self) -> common.Game:
        """
        Get the Game which corresponds to this source type
        """
        if self in {self.CITRA_RAM_DUMP_FOLDER, self.CITRA_RAM_DUMP_FILE}:
            return common.Game.NSMB2
        elif self in {self.RPX_FILE, self.CEMU_RAM_DUMP_FOLDER, self.CEMU_RAM_DUMP_FILE}:
            return common.Game.NSMBU
        elif self is NSO_FILE:
            return common.Game.NSMBUDX
        else:
            return common.Game.NSMBW


def detect_source_type(path: pathlib.Path) -> SourceType:
    """
    Auto-detect the type of input data provided by the user
    """
    def detect_dol_from_header(header: bytes) -> bool:
        """
        Given the first 0x100 bytes of a file, check if it looks like
        a NSMBW DOL file
        """
        if len(header) < 0x100:
            return False

        PLACES_TO_CHECK = {
            # 0 = "expected to be 00000000", 1 = "expected to be nonzero"
            0x00: 1,  # executable section offsets array (start)
            0x04: 1,  # ibid
            0x10: 0,  # executable section offsets array (end)
            0x14: 0,  # ibid
            0x18: 0,  # ibid
            0x1C: 1,  # data section offsets array (start)
            0x20: 1,  # ibid
            0x24: 1,  # ibid
            0x44: 0,  # data section offsets array (end)
            0x48: 1,  # executable section addresses array (start)
        }

        for offs, should_be_nonzero in PLACES_TO_CHECK.items():
            value_here, = struct.unpack_from('>I', header, offs)
            if bool(value_here) != bool(should_be_nonzero):
                return False

        return True

    if path.is_dir():
        if (path / 'mem1.raw').is_file():
            return SourceType.DOLPHIN_RAM_DUMP_FOLDER
        # TODO: Citra ram dump folder
        elif (path / '02000000.bin').is_file():
            return SourceType.CEMU_RAM_DUMP_FOLDER

    elif path.is_file():
        size = path.stat().st_size

        if size == 0x01800000:  # 24 MB
            return SourceType.DOLPHIN_RAM_DUMP_FILE
        # TODO: Citra ram dump file
        elif size == 0x4e000000:  # ~ 1.2 GB
            return SourceType.CEMU_RAM_DUMP_FILE

        # Check header
        with path.open('rb') as f:
            first_0x100 = f.read(0x100)

        if first_0x100[:4] == b'\x7fELF':
            return SourceType.RPX_FILE

        if first_0x100[:4] == b'RBOF':
            return SourceType.ALF_FILE

        if detect_dol_from_header(first_0x100):
            return SourceType.DOL_FILE

        if first_0x100[:4] == b'NSO0':
            return SourceType.NSO_FILE


def resolve_folder_source_to_file(path: pathlib.Path, source_type: SourceType) -> (pathlib.Path, SourceType):
    """
    If the source is a folder containing the file we actually want,
    adjust the path and source type appropriately
    """
    if source_type is SourceType.DOLPHIN_RAM_DUMP_FOLDER:
        return (path / 'mem1.raw'), SourceType.DOLPHIN_RAM_DUMP_FILE

    elif source_type is SourceType.CITRA_RAM_DUMP_FOLDER:
        raise NotImplementedError

    elif source_type is SourceType.CEMU_RAM_DUMP_FOLDER:
        return (path / '02000000.bin'), SourceType.CEMU_RAM_DUMP_FILE

    else:
        return path, source_type


def make_source_and_analysis(source_type: SourceType, file) -> (export_base.Source, export_base.Analysis):
    """
    Create instances of the appropriate Source and Analysis subclasses
    for a file-like object representing the specified source_type
    """
    if source_type is SourceType.DOL_FILE:
        source = export_nsmbw.DOLFileSource(file)
        return source, export_nsmbw.NSMBWAnalysis(source)

    elif source_type is SourceType.DOLPHIN_RAM_DUMP_FILE:
        source = export_nsmbw.DolphinRAMDumpSource(file)
        return source, export_nsmbw.NSMBWAnalysis(source)

    elif source_type is SourceType.RPX_FILE:
        source = export_nsmbu.RPXFileSource(file)
        return source, export_nsmbu.NSMBUAnalysis(source)

    elif source_type is SourceType.CEMU_RAM_DUMP_FILE:
        source = export_nsmbu.CemuRAMDumpSource(file)
        return source, export_nsmbu.NSMBUAnalysis(source)

    elif source_type is SourceType.NSO_FILE:
        source = export_nsmbudx.NSOFileSource(file)
        return source, export_nsmbudx.NSMBUDXAnalysis(source)

    raise NotImplementedError(f'Not yet implemented: {source_type.value}')


def read_scripts(source: export_base.Source, analysis: export_base.Analysis) -> list:
    """
    Return a list of LowLevelScripts
    """
    scripts = []
    for i in range(analysis.table_length):
        script = common.LowLevelScript()

        # Read the entry from scripts table
        if analysis.uses_priorities:
            source.seek(analysis.table_addr + i * 8)
            script.priority = source.read_u32()
            script_addr = source.read_u32()
        else:
            script_addr = source.read_u32_from(analysis.table_addr + i * 4)

        # Read the script itself
        source.seek(script_addr)
        for j in range(999):
            command_id = analysis.read_commands_u32_from(script_addr + j * 8 + 0)
            arg = analysis.read_commands_u32_from(script_addr + j * 8 + 4)

            script.append(common.LowLevelCommand(command_id, arg))

            if command_id == analysis.terminator_command:
                break

        else:
            print(f'WARNING: Terminator not found (script {i})')

        scripts.append(script)

    return scripts


def convert_to_high_level(low_level_scripts: list, analysis: export_base.Analysis) -> dict:
    """
    Convert a list of LowLevelScript to a dict of {name: HighLevelScript}
    """
    def get_script_info(id: int) -> dict:
        """
        Get the correct info dict for a script ID
        """
        variant = analysis.game_variant
        while variant:
            if id in variant.scripts.add:
                return variant.scripts.add[id]
            for ren in variant.scripts.renumber:
                id = ren.apply(id)
            variant = variant.parent
        return {}

    def get_command_info(id: int) -> dict:
        """
        Get the correct info dict for a command ID
        """
        variant = analysis.game_variant
        while variant:
            if id in variant.commands.add:
                return variant.commands.add[id]
            for ren in variant.commands.renumber:
                id = ren.apply(id)
            variant = variant.parent
        return {}

    high_level_scripts = {}
    for i, script_low in enumerate(low_level_scripts):
        script_info = get_script_info(i)

        # Make HighLevelScript and add it to the dict by name
        script_high = common.HighLevelScript()
        high_level_scripts[script_info.get('name', f'scr_{i:03d}')] = script_high

        script_high.priority = script_low.priority

        for command_low in script_low:
            command_info = get_command_info(command_low.id)

            # Command ID (simple)
            high_id = command_info.get('name', f'cmd_{command_low.id:03d}')

            # Command arg (a little more complicated)
            high_arg = None

            # If the command is documented to have an argument...
            if command_info.get('arg') is not None:
                # Use a string from an enum if applicable
                for name, value in command_info.get('enum', {}).items():
                    if command_low.argument == value:
                        high_arg = name
                        break
                else:
                    # No enum matches, but the command *is* still
                    # documented to have an argument, so add it here
                    # whether it's zero or not
                    high_arg = str(command_low.argument)

            # Otherwise, only add the arg if it's nonzero
            if high_arg is None and command_low.argument != 0:
                high_arg = str(command_low.argument)

            # Create HighLevelCommand and add it to the script
            command_high = common.HighLevelCommand(high_id, high_arg)
            script_high.append(command_high)

    return high_level_scripts


def convert_to_text(scripts: dict) -> str:
    """
    Convert a dict of scripts to a text-file string
    """
    ARG_COLUMN = 16

    lines = []

    for script_name, script in scripts.items():

        if script.priority:
            lines.append(f'{script_name} [priority={script.priority}]:')
        else:
            lines.append(f'{script_name}:')

        for cmd in script:
            line = f'    {cmd.id}'

            if cmd.argument:
                if len(line) < ARG_COLUMN:
                    line += ' ' * (ARG_COLUMN - len(line))
                else:
                    line += ' '
                line += cmd.argument

            lines.append(line)

        lines.append('')

    return '\n'.join(lines)


def do_analyze(input_file: pathlib.Path) -> None:
    """
    Handle the "analyze" command
    """
    print(f'Analyzing "{input_file.name}"...')

    source_type = detect_source_type(input_file)
    if source_type is None:
        raise ValueError('Unable to determine source type')
    print(f'Source type: {source_type.value}')

    # If the user specified a folder (like a Dolphin or Cemu RAM dump
    # folder), get the actual file instead
    input_file, source_type = \
        resolve_folder_source_to_file(input_file, source_type)

    with input_file.open('rb') as f:
        # Create the appropriate source and analysis classes
        source, analysis = make_source_and_analysis(source_type, f)

        # Analyze
        analysis.analyze(verbose=True)


def do_export(input_file: pathlib.Path, scripts_file: pathlib.Path, version_info_file: pathlib.Path) -> None:
    """
    Handle the "export" command (with all default parameter values filled in as needed)
    """
    source_type = detect_source_type(input_file)
    if source_type is None:
        raise ValueError('Unable to determine source type')

    # If the user specified a folder (like a Dolphin or Cemu RAM dump
    # folder), get the actual file instead
    input_file, source_type = \
        resolve_folder_source_to_file(input_file, source_type)

    with input_file.open('rb') as f:
        # Create the appropriate source and analysis classes
        source, analysis = make_source_and_analysis(source_type, f)

        # Analyze
        analysis.analyze()

        # Save analysis results
        analysis_json = analysis.to_json()
        with version_info_file.open('w', encoding='utf-8') as f:
            json.dump(analysis_json, f, indent=4)

        # Read low-level (int-based) scripts
        scripts_low = read_scripts(source, analysis)

    # Convert to high-level (str-based) scripts
    scripts_high = convert_to_high_level(scripts_low, analysis)

    # Save output
    txt = convert_to_text(scripts_high)
    with scripts_file.open('w', encoding='utf-8') as f:
        f.write(txt)
