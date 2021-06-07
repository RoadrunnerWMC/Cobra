import struct
import zlib

import common
import export_base
import game_variants



class TheWorldsWorstPowerPCInterpreter:
    """
    An extremely minimal PPC interpreter that only implements the bare
    minimum instructions required to reconstruct the command lists
    """
    def __init__(self, source):
        self.source = source
        self.registers = [0] * 32
        self.memory = {}

    def run_function_at(self, addr: int):
        """
        Run the function at addr up to the blr
        """
        for i in range(9999):
            inst = self.source.read_u32_from(addr)

            if inst == 0x4E800020:  # blr
                return

            self.run_inst(inst)

            addr += 4

        else:
            print("WARNING: function didn't end")

    def run_inst(self, inst: int):
        """
        Run one instruction with the value given
        """
        # Decode
        opcode = inst >> 26
        s = (inst >> 21) & 0x1f
        a = (inst >> 16) & 0x1f
        d = inst & 0xffff
        if d & 0x8000:
            d = d - 0x10000

        if opcode == 14:  # addi
            b = 0 if a == 0 else self.registers[a]
            self.registers[s] = b + d

        elif opcode == 15:  # addis
            b = 0 if a == 0 else self.registers[a]
            self.registers[s] = b + (d << 16)

        elif opcode == 31:  # (various, depends on opcode2)
            opcode2 = (inst >> 1) & 0x3ff

            if opcode2 == 444:  # or (used because mr is a pseudoinst of it)
                b = (inst >> 11) & 0x1f
                self.registers[a] = self.registers[s] | self.registers[b]

            else:
                print(f'WARNING: unexpected opcode 31.{opcode2}')

        elif opcode == 32:  # lwz
            b = 0 if a == 0 else self.registers[a]
            self.registers[s] = self.memory.get(b + d)

        elif opcode == 36:  # stw
            self.memory[self.registers[a] + d] = self.registers[s]

        elif opcode == 37:  # stwu
            ea = self.registers[a] + d
            self.memory[ea] = self.registers[s]
            self.registers[a] = ea

        elif opcode == 46:  # lmw
            pass  # Not required

        elif opcode == 47:  # stmw
            pass  # Not required

        elif opcode == 48:  # lfs
            pass  # Not required

        elif opcode == 52:  # stfs
            pass  # Not required

        else:
            print(f'WARNING: unexpected opcode {opcode}')


class RPXSection:
    """
    Abstract base class for a RPX section
    """
    def __init__(self, file, flags: int, addr: int, offset: int, size: int):
        self.file = file
        self.addr = addr


    def has(self, addr: int) -> bool:
        """
        Check if this section contains the specified address
        """
        raise NotImplementedError


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


class RPXSectionUncompressed(RPXSection):
    """
    Uncompressed RPX section. This is just a thin wrapper around the
    file-like object, since we can read from it directly
    """
    def __init__(self, file, flags: int, addr: int, offset: int, size: int):
        super().__init__(file, flags, addr, offset, size)
        self.addr = addr
        self.offset = offset
        self.size = size


    def has(self, addr: int) -> bool:
        """
        Check if this section contains the specified address
        """
        return self.addr <= addr < self.addr + self.size


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


class RPXSectionCompressed(RPXSection):
    """
    Compressed RPX section. This class is lazy, decompressing the
    section data only if .read() is called.
    """
    def __init__(self, file, flags: int, addr: int, offset: int, size: int):
        super().__init__(file, flags, addr, offset, size)
        self.addr = addr

        self._decompressed_yet = False
        self.offset = offset
        self.size = size

        self.file.seek(offset)
        self.decomp_size, = struct.unpack('>I', file.read(4))

        self.cursor = 0


    def has(self, addr: int) -> bool:
        """
        Check if this section contains the specified address
        """
        return self.addr <= addr < self.addr + self.decomp_size


    def _ensure_decompressed(self):
        """
        If the data hasn't been decompressed yet, decompress it.
        Otherwise do nothing.
        """
        if self._decompressed_yet: return

        self.file.seek(self.offset + 4)
        self.decomp_data = zlib.decompress(self.file.read(self.size - 4))

        self._decompressed_yet = True


    def seek(self, addr: int):
        """
        Seek to a specific RAM address
        """
        self.cursor = addr - self.addr


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        self._ensure_decompressed()
        data = self.decomp_data[self.cursor : self.cursor + amount]
        self.cursor += amount
        return data


class RPXFileSource(export_base.Source):
    """
    Source subclass for an RPX file
    """
    endian = '>'
    needs_interpreter = True

    def __init__(self, file):
        super().__init__(file)

        # Check magic
        file.seek(0)
        magic = file.read(4)
        if magic != b'\x7fELF':
            raise ValueError(f'Incorrect RPX magic ({magic})')

        # Read sections table info (offset, entry size, num entries)
        file.seek(0x20)
        shoff, = struct.unpack('>I', file.read(4))
        file.seek(0x2E)
        shentsize, shnum = struct.unpack('>HH', file.read(4))

        # Read sections table
        self.sections = []
        for i in range(shnum):
            shent_base = shoff + shentsize * i
            file.seek(shent_base + 8)
            flags, addr, offset, size = struct.unpack('>4I', file.read(16))

            if flags & 0x08000000:
                self.sections.append(RPXSectionCompressed(file, flags, addr, offset, size))
            else:
                self.sections.append(RPXSectionUncompressed(file, flags, addr, offset, size))

        # So .read() can know which section was most recently .seek()ed in
        self.current_section = None


    def get_section(self, addr: int) -> RPXSection:
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
        self.current_section.seek(addr)


    def read(self, amount: int) -> bytes:
        """
        Like file.read()
        """
        return self.current_section.read(amount)


class CemuRAMDumpSource(export_base.SimpleRAMDumpSource):
    """
    SimpleRAMDumpSource subclass for a Cemu RAM dump
    """
    endian = '>'
    base_address = 0x02000000


class NSMBUAnalysis(export_base.Analysis):
    """
    Analysis subclass for NSMBU
    """
    uses_priorities = True

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

            for idx in common.iter_bytes_matches(block, BLR_BYTES):
                if idx % 4 != 0: continue  # if it's not aligned, it's
                                           # not actually an instruction

                func_start = block_start_addr + idx + 4
                if check_if_static_init_func(func_start):
                    return func_start


    def run_interpreter(self) -> dict:
        """
        Run an interpreter on the static init func to recover relevant
        memory overrides.
        Return a dict mapping memory addresses to u32 values.
        """
        interpreter = TheWorldsWorstPowerPCInterpreter(self.source)
        interpreter.run_function_at(self.static_init_func_addr)
        return interpreter.memory


    def find_table_addr(self) -> int:
        """
        Auto-detect the address of the scripts table in memory (e.g.
        0x10044a98 for NSMBU 1.0.0 US).
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
        # (the first script's priority, and the most-significant byte of its pointer)
        TABLE_START = bytes.fromhex('00 00 00 FF 10')

        for offs in range(0, len(window), 4):
            if window[offs : offs+len(TABLE_START)] == TABLE_START:
                return window_base + offs


    def find_static_init_hook_point(self) -> int:
        """
        Auto-detect the address in the static init function at which we can hook.
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
