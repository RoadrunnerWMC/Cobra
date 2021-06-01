# 2020-02-07 RoadrunnerWMC
# Based on Cuyler36's Ghidra GameCube Loader

import struct

import code_file_base


class DOLSection(code_file_base.CodeFileSection):
    """
    Represents a single section in a .dol file
    """
    def __init__(self, address: int, size: int, data: bytes, is_executable: bool):
        self.address = address
        self.size = size
        self.is_executable = is_executable
        self.data = data


class DOL(code_file_base.CodeFile):
    """
    Represents a .dol executable file
    """
    def __init__(self, data: bytes):
        self.data = data
        self.read_header_and_sections()

    def read_header_and_sections(self):
        offs = 0

        section_offsets = struct.unpack_from('>18I', self.data, offs)
        offs += 18 * 4

        section_addresses = struct.unpack_from('>18I', self.data, offs)
        offs += 18 * 4

        section_sizes = struct.unpack_from('>18I', self.data, offs)
        offs += 18 * 4

        bss_address, bss_size, self.entry_point = struct.unpack_from('>3I', self.data, offs)
        offs += 3 * 4

        assert offs == 0xE4

        # Load initialized sections
        self.sections = []
        for i, (offset, address, size) in enumerate(zip(section_offsets, section_addresses, section_sizes)):

            section = DOLSection(address, size, self.data[offset : offset + size], i < 7)
            if not section.is_null():
                self.sections.append(section)

        # Load BSS sections.
        # The DOL header specifies one giant chunk of memory to zero out,
        # which covers all of the logical BSS sections and also overlaps
        # with some regular sections
        made_bss = True
        bss_end_address = bss_address + bss_size
        while made_bss and bss_address < bss_end_address:
            made_bss = False

            for section in self.sections:
                if section.is_executable: continue

                if bss_address <= section.address < bss_end_address:
                    this_section_size = section.address - bss_address
                    if this_section_size > 0:
                        new_section = DOLSection(bss_address, this_section_size, None, False)
                        self.sections.append(new_section)

                        bss_address = new_section.address + new_section.size

                        made_bss = True
                        break

        if bss_address < bss_end_address:
            new_section = DOLSection(bss_address, bss_end_address - bss_address, None, False)
            self.sections.append(new_section)

        # And finally, sort by address
        self.sections.sort(key=lambda section: section.address)


extension = '.dol'
file_type = DOL
section_type = DOLSection
