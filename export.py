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

import contextlib
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


EXPORT_MODULES = [
    export_nsmbw,
    export_nsmbu,
    export_nsmbudx,
]
ANALYSIS_FOR_SOURCE = {
    common.Game.NSMBW: export_nsmbw.NSMBWAnalysis,
    common.Game.NSMBU: export_nsmbu.NSMBUAnalysis,
    common.Game.NSMBUDX: export_nsmbudx.NSMBUDXAnalysis,
}


@contextlib.contextmanager
def open_source(path: pathlib.Path):
    """
    Context manager.
    If the given Path can be recognized as a Source for this game, yield
    that as the `with` target. Otherwise the `with` target will be None.
    """
    if not (path.is_file() or path.is_dir()):
        raise ValueError(f'File or folder not found: {path}')

    for export_module in EXPORT_MODULES:
        with export_module.try_open_source(path) as source:
            if source is not None:
                yield source
                return

    raise ValueError(f'Unable to determine source type for {path.name}')


def get_analysis_for_source(source: export_base.Source) -> export_base.Analysis:
    """
    Return the appropriate Analysis subclass for the given Source.
    """
    if source.game in ANALYSIS_FOR_SOURCE:
        return ANALYSIS_FOR_SOURCE[source.game](source)
    else:
        raise NotImplementedError(f'Unknown analysis class for {source}')


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

    with open_source(input_file) as source:
        print(f'Source type: {source.name}')

        analysis = get_analysis_for_source(source)
        analysis.analyze(verbose=True)


def do_export(input_file: pathlib.Path, scripts_file: pathlib.Path, version_info_file: pathlib.Path) -> None:
    """
    Handle the "export" command (with all default parameter values filled in as needed)
    """
    with open_source(input_file) as source:

        # Analyze
        analysis = get_analysis_for_source(source)
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
