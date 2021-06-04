import struct

import common
import export_base
import game_variants


def iter_bytes_matches(haystack: bytes, needle: bytes):
    idx = haystack.find(needle)
    while idx != -1:
        yield idx
        idx = haystack.find(needle, idx + 1)


class NSMBUAnalysis(export_base.Analysis):
    """
    Analysis subclass for NSMBU
    """
    uses_categories = True
    endianness = '>'

    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory (e.g. 0x10044a98 for NSMBU 1.0.0 US).
        Return None if not found.
        """
        # Find "TalkWindow_Sign_00", which is an easily identified string
        # a few hundred bytes before the start of the table
        window_base = self.source.search(
            b'TalkWindow_Sign_00', 0x10000000, 0x11000000)

        if window_base is None:
            # :(
            return None

        # Read a "window" of 0x1000 bytes starting at that point
        # (this is more than enough to contain the whole table)
        self.source.seek(window_base)
        window = self.source.read(0x1000)

        # Look for a specific byte pattern that indicates the start of the table
        # (the first script's category, and the most-significant byte of its pointer)
        TABLE_START = bytes.fromhex('00 00 00 FF 10')

        for offs in range(0, len(window), 4):
            if window[offs : offs+len(TABLE_START)] == TABLE_START:
                return window_base + offs


    def find_table_length(self) -> int:
        """
        Auto-detect the number of entries in the scripts table (e.g. 119 for NSMBU 1.0.0 US).
        Return None if not found.
        """
        self.source.seek(self.table_addr)
        table = self.source.read(0x1000)

        # Look for null entry, i.e. 8 null bytes
        for i in range(len(table) // 8):
            if table[i*8 : (i+1)*8] == b'\0' * 8:
                return i


    def find_terminator_command_id(self) -> int:
        """
        Auto-detect the terminator command ID (e.g. 341 for NSMBU 1.0.0 US).
        Return None if not found.
        """
        # Get the address of the second script in the table
        self.source.seek(self.table_addr + 12)
        second_script_addr, = struct.unpack_from('>I', self.source.read(4))

        # Read the command ID preceding it -- i.e. the last command in the
        # *first* script
        self.source.seek(second_script_addr - 8)
        first_script_last_cmd, = struct.unpack_from('>I', self.source.read(4))

        # That must be the terminator command
        return first_script_last_cmd


    def find_static_init_func(self) -> int:
        """
        Auto-detect the static init function's address (e.g. 0x021DAB60 for NSMBU 1.0.0 US).
        Return None if not found.
        """
        OPCODE_ADDI = 14
        OPCODE_LI = (14, 0)   # addi with rA=0
        OPCODE_LIS = (15, 0)  # addis with rA=0
        OPCODE_STW = 36
        OPCODE_STWU = 37
        OPCODE_STMW = 47
        OPCODE_LFS = 48
        OPCODE_STFS = 52

        BLR_BYTES = bytes.fromhex('4E 80 00 20')

        STATIC_INIT_FUNC_START = [
            OPCODE_STWU,  # 00
            OPCODE_STMW,  # 04
            OPCODE_LIS,   # 08
            OPCODE_LIS,   # 0C
            OPCODE_LI,    # 10
            OPCODE_ADDI,  # 14
            OPCODE_LI,    # 18
            OPCODE_LIS,   # 1C
            OPCODE_LFS,   # 20
            OPCODE_LIS,   # 24
            OPCODE_LI,    # 28
            OPCODE_LIS,   # 2C
            OPCODE_STFS,  # 30
            OPCODE_ADDI,  # 34
            OPCODE_STW,   # 38
            OPCODE_ADDI,  # 3C
        ]

        def check_if_static_init_func(addr: int) -> bool:
            """
            Check if the function at addr matches the instruction
            pattern of STATIC_INIT_FUNC_START
            """
            self.source.seek(addr)
            instructions = struct.unpack_from('>16I', self.source.read(0x40))

            for instruction, expected_opcode in zip(instructions, STATIC_INIT_FUNC_START):
                expected_ra = None
                if isinstance(expected_opcode, tuple):
                    expected_opcode, expected_ra = expected_opcode

                # Opcode: x >> 26
                if instruction >> 26 != expected_opcode:
                    return False

                # rA: (x >> 16) & 0x1f
                if expected_ra is not None and (instruction >> 16) & 0x1f != expected_ra:
                    return False

            return True

        SEARCH_START = 0x021C0000
        SEARCH_END = 0x02200000
        BLOCK_SIZE = 0x8000

        # We search for BLR_BYTES (marking the ends of functions) and
        # check if what immediately follows them (the start of the next
        # function) is the static init function
        for block_start_addr in range(SEARCH_START, SEARCH_END, BLOCK_SIZE):
            self.source.seek(block_start_addr)
            block = self.source.read(BLOCK_SIZE)

            for idx in iter_bytes_matches(block, BLR_BYTES):
                if idx % 4 != 0: continue  # if it's not aligned, it's
                                           # not actually an instruction

                func_start = block_start_addr + idx + 4
                if check_if_static_init_func(func_start):
                    return func_start


    def find_static_init_hook_point(self) -> int:
        """
        Auto-detect the address in the static init function at which we can hook.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        static_init_addr = self.find_static_init_func()
        # TODO: write this function
        return 0


    def find_table_read_hook_point(self) -> int:
        """
        Auto-detect the address in the table-read function at which we can hook.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        # TODO: write this function
        return 0


    def detect_game_variant(self) -> game_variants.GameVariant:
        """
        Return the appropriate GameVariant instance for the source
        """
        variants = game_variants.load_game_json(common.Game.NSMBU)

        if self.terminator_command == 341:
            return variants['1.0.0']
        elif self.terminator_command == 342:
            return variants['1.1.0_1.2.0']
        elif self.terminator_command == 344:
            return variants['1.3.0']

        raise ValueError(f'Unrecognized version of NSMBU, using terminator command {self.terminator_command}')
