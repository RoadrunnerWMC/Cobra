import struct

try:
    import lz4.block  # pip install lz4
    HaveLZ4 = True
except ImportError:
    HaveLZ4 = False

import common
import export_base
import game_variants


class NSOSectionUncompressed(export_base.LazilyDecompressedSection_Uncompressed):
    """
    Uncompressed NSO section
    """
    pass


class NSOSectionCompressed(export_base.LazilyDecompressedSection_Compressed):
    """
    Compressed NSO section
    """
    def decompress(self, data: bytes) -> bytes:
        if not HaveLZ4:
            raise ValueError(
                "Can't read NSO data because python-lz4 is not installed!"
                ' Install with pip: `pip install lz4`')

        return lz4.block.decompress(data, self.decomp_size)


class NSOFileSource(export_base.FileSourceWithLazilyDecompressedSections):
    """
    Source subclass for a NSO file ("main")
    """
    endian = '<'

    def __init__(self, file):
        super().__init__(file)

        # Check magic
        file.seek(0)
        magic = file.read(4)
        if magic != b'NSO0':
            raise ValueError(f'Incorrect NSO magic ({magic})')

        # Read flags
        file.seek(0xC)
        flags, = struct.unpack_from('<I', file.read(4))

        # Iterate over sections
        sections_info = [
            # (section header offs, section len offs, is compressed)
            (0x10, 0x60, flags & 1),  # .text
            (0x20, 0x64, flags & 2),  # .rodata
            (0x30, 0x68, flags & 4),  # .data
        ]

        for section_header_offs, section_len_offs, is_compressed in sections_info:
            file.seek(section_header_offs)
            offset, addr, decomp_size = struct.unpack_from('<3I', file.read(12))

            file.seek(section_len_offs)
            comp_size, = struct.unpack_from('<I', file.read(4))

            if is_compressed:
                self.sections.append(NSOSectionCompressed(file, addr, offset, comp_size, decomp_size))
            else:
                self.sections.append(NSOSectionUncompressed(file, addr, offset, comp_size))


class NSMBUDXAnalysis(export_base.Analysis):
    """
    Analysis subclass for NSMBUDX
    """
    uses_priorities = True
    uses_static_init_func = False

    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory (e.g.
        0x00bd5514 for NSMBUDX US).
        Return None if not found.
        """
        # Unlike in the Wii U version, there are no strings near the
        # table which we can search for.
        # Instead, we pattern-match over a wide area on the first four
        # script priority values: 255, 128, 170, 170.

        SEARCH_START = 0x00bc0000
        SEARCH_END = 0x00c00000
        FIRST_4_PRIORITIES = [255, 128, 170, 170]
        ROLLING_WINDOW_SIZE = 7  # enough to match [A, _, B, _, C, _, D]

        rolling_window = []

        self.source.seek(SEARCH_START)
        for addr in range(SEARCH_START, SEARCH_END, 4):
            rolling_window.append(self.source.read_u32())

            if len(rolling_window) > ROLLING_WINDOW_SIZE:
                rolling_window.pop(0)

                every_other_u32 = [rolling_window[i] for i in [0, 2, 4, 6]]

                if every_other_u32 == FIRST_4_PRIORITIES:
                    return addr - (ROLLING_WINDOW_SIZE - 1) * 4


    def detect_game_variant(self) -> game_variants.GameVariant:
        """
        Return the appropriate GameVariant instance for the source
        """
        # Only one variant defined for NSMBUDX
        variants = game_variants.load_game_json(common.Game.NSMBU)
        return variants['DX']