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
import os
import pathlib
import struct

import common
import export_base
import game_variants



class DOLSection(export_base.SectionedFileSource_UncompressedSection):
    """
    DOL section
    """
    pass


class DOLFileSource(export_base.SectionedFileSource):
    """
    Source subclass for a DOL file ("main.dol")
    """
    name = 'DOL file'
    game = common.Game.NSMBW
    endian = '>'

    def __init__(self, file):
        super().__init__(file)

        file.seek(0)
        section_offsets = struct.unpack('>18I', file.read(0x48))
        section_addresses = struct.unpack('>18I', file.read(0x48))
        section_sizes = struct.unpack('>18I', file.read(0x48))

        for offset, addr, size in zip(section_offsets, section_addresses, section_sizes):
            self.sections.append(DOLSection(file, addr, offset, size))


class ALFSection(export_base.SectionedFileSource_UncompressedSection):
    """
    ALF section
    """
    pass


class ALFFileSource(export_base.SectionedFileSource):
    """
    Source subclass for an ALF file ("WIIMJ2DNP.alf")
    """
    name = 'ALF file'
    game = common.Game.NSMBW
    # ALF headers are little-endian, but the data *within each section*
    # is big-endian, which is what this attribute is really about
    endian = '>'

    def __init__(self, file):
        super().__init__(file)

        file.seek(0xC)
        num_sections, = struct.unpack('<I', file.read(4))

        for _ in range(num_sections):
            addr, stored_size, virtual_size = struct.unpack('<3I', file.read(0xC))
            if stored_size:
                self.sections.append(ALFSection(file, addr, file.tell(), stored_size))

            # Skip past the section data
            file.seek(stored_size, os.SEEK_CUR)


class DolphinRAMDumpSource(export_base.SimpleRAMDumpSource):
    """
    SimpleRAMDumpSource subclass for a Dolphin MEM1 RAM dump
    """
    name = 'Dolphin RAM dump'
    game = common.Game.NSMBW
    endian = '>'
    base_address = 0x80000000


def _detect_dol_from_header(file) -> bool:
    """
    Given a file-like object, try to check if it looks more-or-less like
    a regular DOL file.
    (Helper function for try_open_source().)
    """
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
        file.seek(offs)
        data_here = file.read(4)
        if len(data_here) < 4:
            return False
        value_here, = struct.unpack('>I', data_here)
        if bool(value_here) != bool(should_be_nonzero):
            return False

    return True


@contextlib.contextmanager
def try_open_source(path: pathlib.Path):
    """
    Context manager.
    If the given Path can be recognized as a Source for this game, yield
    that as the `with` target. Otherwise the `with` target will be None.
    """
    if path.is_dir():
        # Dolphin RAM dump
        mem1_fp = (path / 'mem1.raw')
        if mem1_fp.is_file():
            with mem1_fp.open('rb') as f:
                yield DolphinRAMDumpSource(f)
                return

    elif path.is_file():
        size = path.stat().st_size

        with path.open('rb') as f:

            # Dolphin RAM dump
            if size == 0x01800000:  # 24 MB
                yield DolphinRAMDumpSource(f)
                return

            # ALF
            f.seek(0)
            if f.read(4) == b'RBOF':
                yield ALFFileSource(f)
                return

            # DOL
            if _detect_dol_from_header(f):
                yield DOLFileSource(f)
                return

    yield None


class NSMBWAnalysis(export_base.Analysis):
    """
    Analysis subclass for NSMBW
    """

    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory (e.g.
        0x8031dbcc for NSMBW PAL v1).
        Return None if not found.
        """
        # Find "AUTO_SELECT\0WORLD_MAP", which is an easily identified
        # string right at the end of the table
        window_base = self.source.search(
            b'AUTO_SELECT\0WORLD_MAP', 0x80300000, 0x80400000)

        if window_base is None:
            # :(
            return None

        # Read a "window" of the preceding 0x1000 bytes
        # (this is more than enough to contain the whole table)
        window_base -= 0x1000
        self.source.seek(window_base)
        window = self.source.read(0x1000)

        # Starting at the end of the window, look for the first word
        # that doesn't start with "80" (i.e. that doesn't look like a
        # pointer)
        for offs in range(len(window) - 4, 0, -4):
            if window[offs] != 0x80:
                return window_base + offs + 4


    def detect_game_variant(self) -> game_variants.GameVariant:
        """
        Return the appropriate GameVariant instance for the source
        """
        # Only one variant defined for NSMBW
        variants = game_variants.load_game_json(common.Game.NSMBW)
        return variants['all']
