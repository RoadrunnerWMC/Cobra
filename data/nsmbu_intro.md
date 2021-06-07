The information below is specifically for the US 1.0.0 release on Wii U, except where noted. Specific numbers may vary in other releases.

Thanks to [Kinnay](https://github.com/kinnay), [Luminyx](https://github.com/Luminyx1), [Skawo](https://github.com/skawo), [Bent](https://github.com/RicBent), and [STUPID Modder](https://github.com/stupidestmodder) for helping with research in this game.

Scripts are initially empty, and are initialized in the static init function at 0x021DAB60. Commands are read by the class with constructor at 0x021DC720 (unofficially, "CsEventMgr"). The `イベントアシスタント` ("Event Assistant") actor is also involved in some way, and might be responsible for executing the events.

The scripts table is at 0x10044A60, and is an array of 119 of the following: `{uint32_t priority; void *script_ptr}`. Scripts are executed using a priority queue, so if multiple scripts are triggered at the same time, they'll execute in order of descending priority.

Script commands are the same format as NSMBW: `{uint32_t command_id; uint32_t argument}`. The terminator command to end a script is 341.

The script names in the "Scripts" tables below are unofficial.

### Version Differences Summary

Version | Scripts table address (US) | Number of scripts | Terminator command
------- | -------------------------- | ----------------- | ------------------
1.0.0   | 0x10044A60                 | 119               | 341
1.1.0   | 0x10044A98                 | 119               | 342
1.2.0   | 0x10044A98                 | 119               | 342
1.3.0   | 0x100458B8                 | 121               | 344

* **1.1.0**: added a new command, 341 &mdash; not used in any script. Also added command 89 to the beginning of script 114.
* **1.2.0**: no changes.
* **1.3.0**: added two new scripts (119, 120), which use two new commands (291, 292). No changes to existing scripts, except that all command IDs higher than 290 were increased by 2 due to the new commands added there.

### NSMBUDX

TODO: add some info about NSMBUDX
