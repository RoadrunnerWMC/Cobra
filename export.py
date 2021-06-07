# 2021-05-15

import enum
import pathlib
import struct
import typing

import code_file_dol  # TODO: use code_file_all instead, for alf (also maybe redesign those classes now that I actually understand the formatss)

import export_base
import export_nsmbu

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
    DOLPHIN_RAM_DUMP_FILE = 'Dolphin RAM dump file'

    # 3DS
    CITRA_RAM_DUMP_FOLDER = 'Citra RAM dump folder'
    CITRA_RAM_DUMP_FILE = 'Citra RAM dump file'

    # Wii U
    RPX_FILE = 'RPX file'
    CEMU_RAM_DUMP_FOLDER = 'Cemu RAM dump folder'
    CEMU_RAM_DUMP_FILE = 'Cemu RAM dump file'

    # Switch
    ...

    def game(self) -> common.Game:
        """
        Get the Game which corresponds to this source type
        """
        if self in {self.CITRA_RAM_DUMP_FOLDER, self.CITRA_RAM_DUMP_FILE}:
            return common.Game.NSMB2
        elif self in {self.RPX_FILE, self.CEMU_RAM_DUMP_FOLDER, self.CEMU_RAM_DUMP_FILE}:
            return common.Game.NSMBU
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
        if (path / 'mem2.raw').is_file():
            return SourceType.DOLPHIN_RAM_DUMP_FOLDER
        # TODO: Citra ram dump folder
        elif (path / '02000000.bin').is_file():
            return SourceType.CEMU_RAM_DUMP_FOLDER

    elif path.is_file():
        size = path.stat().st_size

        if size == 0x04000000:  # 64 MB
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


def resolve_folder_source_to_file(path: pathlib.Path, source_type: SourceType) -> (pathlib.Path, SourceType):
    """
    If the source is a folder containing the file we actually want,
    adjust the path and source type appropriately
    """
    if source_type is SourceType.DOLPHIN_RAM_DUMP_FOLDER:
        return (path / 'mem2.raw'), SourceType.DOLPHIN_RAM_DUMP_FILE

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
    if source_type is SourceType.RPX_FILE:
        source = export_nsmbu.RPXFileSource(file)
        return source, export_nsmbu.NSMBUAnalysis(source)

    elif source_type is SourceType.CEMU_RAM_DUMP_FILE:
        source = export_nsmbu.CemuRAMDumpSource(file)
        return source, export_nsmbu.NSMBUAnalysis(source)

    raise NotImplementedError(f'Not yet implemented: {source_type.value}')


def read_scripts(source: export_base.Source, analysis: export_base.Analysis) -> list:
    """
    Return a list of LowLevelScripts
    """
    scripts = []
    for i in range(analysis.table_length):
        script = common.LowLevelScript()

        # Read the entry from scripts table
        if analysis.uses_categories:
            source.seek(analysis.table_addr + i * 8)
            script.category_id = source.read_u32()
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


def do_export(input_file: pathlib.Path, scripts_file: pathlib.Path, addrs_file: pathlib.Path) -> None:
    """
    Handle the "export" command (with all default parameter values filled in as needed)
    """
    source_type = detect_source_type(input_file)

    # If the user specified a folder (like a Dolphin or Cemu RAM dump
    # folder), get the actual file instead
    input_file, source_type = \
        resolve_folder_source_to_file(input_file, source_type)

    with input_file.open('rb') as f:
        # Create the appropriate source and analysis classes
        source, analysis = make_source_and_analysis(source_type, f)

        # Analyze
        analysis.analyze()

        # Read scripts
        scripts = read_scripts(source, analysis)

        for i, s in enumerate(scripts):
            print(f'ScriptCommand script_{i:03d}[] = {{')
            for cmd in s:
                print(f'    {{{cmd.id}, {cmd.argument}}},')
            print('};')
            print('')

        print('')
        print('ScriptsTableEntry custom_world_map_scripts_table[] = {')
        for i, s in enumerate(scripts):
            print(f'    {{{s.category_id}, script_{i:03d}}},')
        print('};')

        variant = analysis.detect_game_variant()
        print(variant.name)
