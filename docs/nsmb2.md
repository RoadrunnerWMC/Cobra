# World Map Scripts in NSMB2

**THIS IS AN AUTO-GENERATED FILE -- DO NOT EDIT DIRECTLY!** Instead, edit the "nsmb2" files in the `data/` folder and run `cobra.py generate_documentation`. (Generated 2023-02-20T16:55:49.785157.)

The information below is specifically for the US Gold Edition release; specific numbers may vary in other releases. Process names are official, but others are not.

Thanks to [Bent](https://github.com/RicBent) for helping with research in this game.

## Code Structure

Scripts are initially empty, and are initialized in the static init function at 0x004D18F8. Commands are read and executed by the `BsEventMgr` process. The `BsSequenceMgr` process is also involved in some way.

The scripts table is at 0x00570780, and is an array of 39 of the following: `{uint32_t priority; ScriptCommand *script_ptr}` with `ScriptCommand` (unofficial name) having the same format as NSMBW, being `{uint32_t command_id; uint32_t argument}` Scripts are executed using a priority queue, so if multiple scripts are triggered at the same time, they'll execute in order of descending priority.

The arguments in ScriptCommand are always 0 in this game and nothing seems to read them. The terminator command to end a script is 46.

## Scripts

ID | Name | Description
-- | ---- | -----------
**0** | `enter_level` | -
**1** | `exit_level_fail` | -
**2** | `exit_level_success` | -
**3** | ?? | -
**4** | ?? | -
**5** | ?? | -
**6** | ?? | -
**7** | ?? | -
**8** | ?? | -
**9** | ?? | -
**10** | ?? | -
**11** | ?? | -
**12** | ?? | -
**13** | ?? | -
**14** | ?? | -
**15** | ?? | -
**16** | ?? | -
**17** | ?? | -
**18** | ?? | -
**19** | ?? | -
**20** | ?? | -
**21** | ?? | -
**22** | ?? | -
**23** | ?? | -
**24** | ?? | -
**25** | ?? | -
**26** | ?? | -
**27** | ?? | -
**28** | ?? | -
**29** | ?? | -
**30** | ?? | -
**31** | ?? | -
**32** | ?? | -
**33** | ?? | -
**34** | ?? | -
**35** | ?? | -
**36** | ?? | -
**37** | ?? | -
**38** | ?? | -


## Commands

ID | Name | Description | Argument
-- | ---- | ----------- | --------
**46** | `end` | Ends the script. | None

