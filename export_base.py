
import dataclasses
import struct

import common
import game_variants


class Source:
    """
    Source base class. Essentially a wrapper around a file object, which
    is capable of "seeking" to particular memory addresses.
    """
    endian = '>'

    def __init__(self, file):
        self.file = file


    def search(self, target: bytes, start_addr: int, end_addr: int) -> int:
        """
        Search for a piece of data in memory, efficiently.
        Return None if not found.
        No guarantees about where the file will be seeked to afterward.
        """

        # Larger block sizes are faster but also use more RAM.
        # Also needs to be much greater than len(target).
        block_size = max(0x8000, len(target) * 3)
        inc_size = block_size // 2  # this is so we don't miss the target if
                                    # it's between two blocks

        for addr in range(start_addr, end_addr, inc_size):
            self.seek(addr)

            idx = self.read(block_size).find(target)
            if idx != -1:
                return addr + idx

        # :(
        return None


    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        raise NotImplementedError


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        return self.file.read(amount)


class SimpleRamDumpSource(Source):
    """
    Basic source that just interprets the file as a RAM dump from some base address
    """
    def __init__(self, file, base_address: int, endianness: str):
        super().__init__(file)
        self.base_address = base_address
        self.endian = endianness

    def seek(self, addr: int):
        self.file.seek(addr - self.base_address)


class Analysis:
    """
    Base class for an analyzer that finds important addresses and constants.
    Can be serialized to/from json.
    """
    # Override this group statically in subclasses
    uses_categories = False
    endianness: str

    game_variant: game_variants.GameVariant

    table_addr: int
    table_length: int
    terminator_command: int

    @dataclasses.dataclass
    class HookPoint:
        address: int
        original_instruction: int

    static_init_hook_point: HookPoint
    table_read_hook_point: HookPoint

    def __init__(self, source, table_addr:int=None):
        self.source = source
        self.table_addr = table_addr


    def analyze(self):
        """
        Call all the analysis functions
        """
        if self.table_addr is None:
            self.table_addr = self.find_table_addr()

        self.table_length = self.find_table_length()
        self.terminator_command = self.find_terminator_command_id()

        self.static_init_hook_point = self.find_static_init_hook_point()
        self.table_read_hook_point = self.find_table_read_hook_point()

        self.game_variant = self.detect_game_variant()


    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory.
        Return None if not found.
        """
        raise NotImplementedError


    def find_table_length(self) -> int:
        """
        Auto-detect the number of entries in the scripts table (i.e. 119 for NSMBU 1.0.0).
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError


    def find_terminator_command_id(self) -> int:
        """
        Auto-detect the terminator command ID (i.e. 341 for NSMBU 1.0.0).
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError


    def find_static_init_hook_point(self) -> int:
        """
        Auto-detect the address in the static init function at which we can hook.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError


    def find_table_read_hook_point(self) -> int:
        """
        Auto-detect the address in the table-read function at which we can hook.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError


    def detect_game_variant(self) -> game_variants.GameVariant:
        """
        Return the appropriate GameVariant instance for the source.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError
