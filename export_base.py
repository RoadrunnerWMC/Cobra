
import dataclasses
import struct

import common
import game_variants


class Source:
    """
    Source base class. Essentially a wrapper around a file object, which
    is capable of "seeking" to particular memory addresses.
    """
    endian: str
    needs_interpreter: bool = False

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


    def read_u32(self) -> int:
        """
        Convenience function to read a u32.
        """
        return struct.unpack(f'{self.endian}I', self.read(4))[0]


    def read_u32_from(self, addr: int) -> int:
        """
        Convenience function to read a u32 from a given address.
        """
        self.seek(addr)
        return self.read_u32()


class SimpleRAMDumpSource(Source):
    """
    Basic source that just interprets the file as a RAM dump from some base address
    """
    base_address: int

    def seek(self, addr: int):
        self.file.seek(addr - self.base_address)


class Analysis:
    """
    Base class for an analyzer that finds important addresses and constants.
    """
    # Override this statically in subclasses
    uses_priorities: bool = False

    source: Source

    static_init_func_addr: int
    memory_overrides: dict
    table_addr: int
    table_length: int
    terminator_command: int
    game_variant: game_variants.GameVariant


    def __init__(self, source):
        self.source = source
        self.memory_overrides = {}


    def read_commands_u32_from(self, addr: int) -> int:
        """
        Use this instead of self.source.seek()/.read() when reading the
        commands lists data. This lets subclasses fill in extra data
        derived from the static init functions (NSMB2, NSMBU).
        """
        if addr in self.memory_overrides:
            return self.memory_overrides[addr]
        else:
            return self.source.read_u32_from(addr)


    def analyze(self):
        """
        Call all the analysis functions
        """
        # Find the static init func
        self.static_init_func_addr = self.find_static_init_func()

        # Interpret it if needed, to populate self.memory_overrides
        if self.source.needs_interpreter:
            self.memory_overrides = self.run_interpreter()

        # Find basic info about the main table
        self.table_addr = self.find_table_addr()
        self.table_length = self.find_table_length()
        self.terminator_command = self.find_terminator_command_id()

        # Find hook points
        ...

        # Finally, classify the game variant we're looking at
        self.game_variant = self.detect_game_variant()


    def find_static_init_func(self) -> int:
        """
        Auto-detect the static init function address.
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        raise NotImplementedError


    def run_interpreter(self) -> dict:
        """
        Run an interpreter on the static init func to recover relevant
        memory overrides.
        Return a dict mapping memory addresses to u32 values.
        """
        raise NotImplementedError


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
        # We detect the end of the scripts table as when the addresses
        # suddenly change by more than a maximum threshold.
        # This strategy works for all of the games.
        CHANGE_THRESHOLD = 0x10000
        DEFAULT_IF_UNDETECTABLE = 10  # arbitrary safe small number

        prev_ptr_in_table = None
        self.source.seek(self.table_addr)

        for i in range(999):
            # Read table entry
            if self.uses_priorities:
                self.source.read_u32()  # skip past this
            this_ptr_in_table = self.source.read_u32()

            # If it's more than CHANGE_THRESHOLD away from the previous,
            # we're done
            if prev_ptr_in_table is not None:
                if abs(this_ptr_in_table - prev_ptr_in_table) > CHANGE_THRESHOLD:
                    return i

            # Prepare for next iteration
            prev_ptr_in_table = this_ptr_in_table

        else:
            print(f"WARNING: Couldn't determine scripts table length -- defaulting to {DEFAULT_IF_UNDETECTABLE}")
            return DEFAULT_IF_UNDETECTABLE


    def find_terminator_command_id(self) -> int:
        """
        Auto-detect the terminator command ID (i.e. 341 for NSMBU 1.0.0).
        Some self-fields are guaranteed to have been previously filled
        in; see analyze() for the exact order.
        """
        # Get the address of the second script in the table
        second_script_addr = self.source.read_u32_from(self.table_addr + (12 if self.uses_priorities else 4))

        # Read the command ID preceding it -- i.e. the last command in the
        # *first* script
        first_script_last_cmd = self.read_commands_u32_from(second_script_addr - 8)

        # That must be the terminator command
        return first_script_last_cmd


    def find_static_init_hook_point(self) -> int:
        """
        Auto-detect the address in the static init function at which we can hook.
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


    def to_json(self) -> dict:
        """
        Return a dict representing the analysis results required for
        patching, which can be saved to a json file and later reused
        as a stand-in for the source we just analyzed
        """
        return {
            'game_variant': self.game_variant.id,

            'static_init_func_addr': self.static_init_func_addr,
            'table_addr': self.table_addr,
            'table_length': self.table_length,
            'terminator_command': self.terminator_command,
        }
