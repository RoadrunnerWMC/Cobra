
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


class AbstractLazilyDecompressedSection:
    """
    Abstract base class for a section for
    FileSourceWithLazilyDecompressedSections
    """
    def __init__(self, file, addr: int, offset: int, decomp_size: int):
        self.file = file
        self.addr = addr
        self.offset = offset
        self.decomp_size = decomp_size


    def has(self, addr: int) -> bool:
        """
        Check if this section contains the specified address
        """
        return self.addr <= addr < self.addr + self.decomp_size


    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        raise NotImplementedError


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        raise NotImplementedError


class LazilyDecompressedSection_Uncompressed(AbstractLazilyDecompressedSection):
    """
    Abstract base class for an uncompressed section for
    FileSourceWithLazilyDecompressedSections
    """
    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        self.file.seek(self.offset + addr - self.addr)


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        return self.file.read(amount)


class LazilyDecompressedSection_Compressed(AbstractLazilyDecompressedSection):
    """
    Abstract base class for a compressed section for
    FileSourceWithLazilyDecompressedSections
    """
    def __init__(self, file, addr: int, offset: int, comp_size: int, decomp_size: int):
        super().__init__(file, addr, offset, decomp_size)
        self.comp_size = comp_size
        self.decomp_data = None
        self.cursor = 0


    def decompress(self, data: bytes) -> bytes:
        """
        Override in subclasses to provide the appropriate decompression
        algorithm
        """
        raise NotImplementedError


    def ensure_decompressed(self):
        """
        If the data hasn't been decompressed yet, decompress it.
        Otherwise do nothing.
        """
        if self.decomp_data is not None: return
        self.file.seek(self.offset)
        self.decomp_data = self.decompress(self.file.read(self.comp_size))


    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        self.cursor = addr - self.addr


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        self.ensure_decompressed()
        data = self.decomp_data[self.cursor : self.cursor + amount]
        self.cursor += amount
        return data


class FileSourceWithLazilyDecompressedSections(Source):
    """
    Source subclass for a file with lazily decompressed sections (such
    as RPX or NSO)
    """
    sections: list  # of AbstractLazilyDecompressedSection

    def __init__(self, file):
        super().__init__(file)

        self.sections = []

        # So .read() can know which section was most recently .seek()ed in
        self.current_section = None


    def get_section(self, addr: int) -> AbstractLazilyDecompressedSection:
        """
        Get the section containing the specified address (or None if none)
        """
        for section in self.sections:
            if section.has(addr):
                return section


    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        self.current_section = self.get_section(addr)
        if self.current_section is None:
            raise ValueError(f'{addr:08x} is not in any section')

        self.current_section.seek(addr)


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        return self.current_section.read(amount)


class Analysis:
    """
    Base class for an analyzer that finds important addresses and constants.
    """
    # Override this statically in subclasses
    uses_priorities: bool = False
    uses_static_init_func: bool = False

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


    def analyze(self, *, verbose=True):
        """
        Call all the analysis functions
        """
        def vprint(*args, **kwargs):
            if verbose:
                return print(*args, **kwargs)

        if self.uses_static_init_func:
            # Find the static init func
            self.static_init_func_addr = self.find_static_init_func()
            if self.static_init_func_addr is None:
                raise ValueError("Couldn't find static init function")
            vprint(f'Static init function: {self.static_init_func_addr:08x}')

            # Interpret it if needed, to populate self.memory_overrides
            if self.source.needs_interpreter:
                self.memory_overrides = self.run_interpreter()
                vprint(f'Interpreter created {len(self.memory_overrides)} memory overrides')

        # Find basic info about the main table
        self.table_addr = self.find_table_addr()
        if self.table_addr is None:
            raise ValueError("Couldn't find scripts table")
        vprint(f'Scripts table: {self.table_addr:08x}')

        self.table_length = self.find_table_length()
        if self.table_length is None:
            raise ValueError("Couldn't determine scripts table length")
        vprint(f'Scripts table length: {self.table_length}')

        self.terminator_command = self.find_terminator_command_id()
        if self.terminator_command is None:
            raise ValueError("Couldn't determine script terminator command")
        vprint(f'Terminator command: {self.terminator_command}')

        # Find hook points
        ...

        # Finally, classify the game variant we're looking at
        self.game_variant = self.detect_game_variant()
        if self.game_variant is None:
            raise ValueError("Couldn't determine game variant")
        vprint(f'Game variant: {self.game_variant.name}')


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
        info = {
            'game': self.game_variant.game.value,
            'game_variant': self.game_variant.id,

            'table_addr': self.table_addr,
            'table_length': self.table_length,
            'terminator_command': self.terminator_command,
        }

        if self.uses_static_init_func:
            info['static_init_func_addr'] = self.static_init_func_addr

        return info
