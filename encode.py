import struct

import common

def create_wms(scripts: dict, *, endian: str, use_priorities: bool) -> bytes:
    """
    Convert a list of common.LowLevelScript to .wms file data
    """
    data = bytearray()
    table_entry_len = (8 if use_priorities else 4)

    def u32(val: int) -> bytes:
        return struct.pack(f'{endian}I', val)

    # Number of scripts
    data += u32(len(scripts))

    # IDs table
    for id in sorted(scripts):
        data += u32(id)

    # Scripts table (dummy at first)
    scripts_table_ptr = len(data)
    data += (b'\0' * table_entry_len) * len(scripts)

    # Each script
    for id in sorted(scripts):
        script = scripts[id]

        if use_priorities:
            table_entry = u32(script.priority) + u32(len(data))
        else:
            table_entry = u32(len(data))

        data[scripts_table_ptr : scripts_table_ptr + table_entry_len] = table_entry
        scripts_table_ptr += table_entry_len

        for command in script:
            data += u32(command.id) + u32(command.argument)

    return bytes(data)
