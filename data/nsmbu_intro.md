(and NSLU, and NSMBUDX)

The information below is specifically for the US 1.0.0 release on Wii U, except where noted. Specific numbers may vary in other releases.

Thanks to [Kinnay](https://github.com/kinnay), [Luminyx](https://github.com/Luminyx1), [Skawo](https://github.com/skawo), [Bent](https://github.com/RicBent), and [STUPID Modder](https://github.com/stupidestmodder) for helping with research in this game.

Command IDs (but not arguments, strangely) are empty in the static RPX data, and are filled in at runtime by the static init function at 0x021DAB60. Commands are read by the class with constructor at 0x021DC720 (unofficially, "CsEventMgr"). The `イベントアシスタント` ("Event Assistant") actor is also involved in some way, and might be responsible for executing the events.

The scripts table is at 0x10044A60, and is an array of 119 of the following: `{uint32_t priority; ScriptCommand *script_ptr}` with `ScriptCommand` (unofficial name) having the same format as NSMBW, being `{uint32_t command_id; uint32_t argument}`. Scripts are executed using a priority queue, so if multiple scripts are triggered at the same time, they'll execute in order of descending priority.

The terminator command to end a script is 341.

The script names in the "Scripts" tables below are unofficial.

### Version Differences Summary

Version | Scripts table address (US) | Number of scripts | Terminator command
------- | -------------------------- | ----------------- | ------------------
1.0.0   | 0x10044A60                 | 119               | 341
1.1.0   | 0x10044A98                 | 119               | 342
1.2.0   | 0x10044A98                 | 119               | 342
1.3.0   | 0x100458B8                 | 121               | 344
Deluxe  | 0x00bd5514                 | 120               | 343

* **1.1.0**: added a new command, 341 &mdash; not used in any script. Also added a command 89 to the beginning of script 114.
* **1.2.0**: no changes.
* **1.3.0**: added two new scripts (119, 120), which use two new commands (291, 292). No changes to existing scripts, except that all command IDs higher than 290 were increased by 2 due to the new commands added there.
* **Deluxe**: removed script 114 and command 311 (which was only used in script 114), shifting all higher numbers down by one in both cases. No changes to existing scripts, except that all command IDs higher than 311 were decreased by 1.

### NSMBUDX

The scripts table in NSMBUDX (international version) is at `base`+0x00bd5514 (`base` being the ASLR base address for the .text section). Unlike on Wii U, this release has no static init function; the scripts data is fully populated at compile time.
