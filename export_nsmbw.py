import common
import export_base
import game_variants


# TODO: write DOLFileSource class


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
