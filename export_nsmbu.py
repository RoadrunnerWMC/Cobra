import struct

import common
import export_base
import game_variants


class NSMBUAnalysis(export_base.Analysis):
    """
    Analysis subclass for NSMBU
    """
    uses_categories = True
    endianness = '>'

    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory.
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

        # :(
        return None


    def find_table_length(self) -> int:
        """
        Auto-detect the number of entries in the scripts table (i.e. 119 for NSMBU 1.0.0)
        """
        self.source.seek(self.table_addr)
        table = self.source.read(0x1000)

        # Look for null entry, i.e. 8 null bytes
        for i in range(len(table) // 8):
            if table[i*8 : (i+1)*8] == b'\0' * 8:
                return i


    def find_terminator_command_id(self) -> int:
        """
        Auto-detect the terminator command ID (i.e. 341 for NSMBU 1.0.0)
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


    def find_static_init_hook_point(self) -> int:
        """
        Auto-detect the address in the static init function at which we can hook.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
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
            return variants['root']
        elif self.terminator_command == 342:
            return variants['110']
        elif self.terminator_command == 344:
            return variants['130']

        raise ValueError(f'Unrecognized version of NSMBU, using terminator command {self.terminator_command}')
