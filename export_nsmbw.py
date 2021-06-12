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

import os
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
    endian = '>'

    def __init__(self, file):
        super().__init__(file)

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
    endian = '>'
    base_address = 0x80000000


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
