The information below is specifically for the US Gold Edition release; specific numbers may vary in other releases.

Thanks to [Bent](https://github.com/RicBent) for helping with research in this game.

Scripts are initially empty, and are initialized in the static init function at 0x004D18F8. Commands are read and executed by the `BsEventMgr` process. The `BsSequenceMgr` process is also involved in some way.

The scripts table is at 0x00570780, and is an array of 39 of the following: `{uint32_t priority; ScriptCommand *script_ptr}` with `ScriptCommand` (unofficial name) having the same format as NSMBW, being `{uint32_t command_id; uint32_t argument}` Scripts are executed using a priority queue, so if multiple scripts are triggered at the same time, they'll execute in order of descending priority.

The arguments in ScriptCommand are always 0 in this game and nothing seems to read them. The terminator command to end a script is 46.

The script names in the table below are unofficial.
