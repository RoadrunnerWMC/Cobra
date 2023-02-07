# World Map Scripts in NSMBW

{{DISCLAIMER}}

The information below is specifically for the EU v1 release; specific numbers may vary in other releases. All names are official (derived from the Chinese Nvidia Shield TV release of NSMBW) except where noted.

Thanks to [Ninji](https://github.com/Treeki) and [Skawo](https://github.com/skawo) for helping with research in this game.

## Code Structure

### dCsSeqMng_c (singleton)

`dCsSeqMng_c` (actor 621, `WM_CS_SEQ_MNG`) is a singleton (`dCsSeqMng_c::ms_instance` at 0x8042A48C) which contains script data as static arrays, and is responsible for managing script execution state. It communicates with subclasses of `dWmDemoActor_c` as described in the next section.

The scripts table itself (`dCsSeqMng_c::smc_demo_table`) is at 0x8031DBCC, and is just an array of 53 pointers to scripts. Script commands are 8 bytes long: `{uint32_t command_id; uint32_t argument}` (field names unofficial). The terminator command to end a script is 5.

Actors can launch scripts by calling `dCsSeqMng_c`'s method at 0x801017C0 (unofficially, `dCsSeqMng_c::addScriptToQueue()`), which adds an entry to its internal priority queue. Actors can check the current command ID and argument with `dCsSeqMng_c::GetCutName()` and `dCsSeqMng_c::GetCutArg0()`, respectively.

### dWmDemoActor_c (actors that respond to cutscenes)

`dWmDemoActor_c` -- a superclass for world-map actors involved in cutscenes -- defines the following attribute (among many others) and virtual methods:

```cpp
class dWmDemoActor_c : dWmActor_c {
    /* 0x139 */ bool m_cut_end;  // (unofficial name)
    /* 0x164 */ bool unknown_flag;  // (unofficial name, unknown purpose)

    // ("vf60", "CutDataName", and parameters: unofficial names)
    /* vtable + 0x60 */ virtual void dWmDemoActor_c::vf60(CutDataName cmd, bool unknown_flag) {
        if (cmd != -1)
            m_cut_end = true;
    }

    /* vtable + 0x64 */ virtual bool checkCutEnd(void) {
        return m_cut_end;
    }

    /* vtable + 0x68 */ virtual void setCutEnd(void) {
        m_cut_end = true;
    }

    /* vtable + 0x6c */ virtual void clearCutEnd(void) {
        m_cut_end = false;
    }
}
```

Subclasses all have the following call in their `execute()` methods:

```cpp
vf60(dCsSeqMng_c::m_instance->GetCutName(), unknown_flag);
```

That virtual function is overridden by each subclass. Its purpose is to check if the current command type is one the actor recognizes, and perform any necessary actions if so.

When a `dWmDemoActor_c` is satisfied that it has nothing more to do to handle the current command (because it's finished handling it or the command isn't relevant to it), it either calls `setCutEnd()` on itself or sets the attribute to `true` directly. Every frame when a script is running, `dCsSeqMng_c` calls `checkCutEnd()` on each `dWmDemoActor_c` instance to see if any of them *don't* have the flag set. If it finds any, it remains on the current command to give those actors more time to complete their tasks. Once all actors have the flag set, it advances to the next command, and calls `clearCutEnd()` on all `dWmDemoActor_c` instances to reset them.

It's a slightly convoluted system, for sure.

#### daWmDirector

One notable `dWmDemoActor_c` subclass is `daWmDirector` (actor 664, `WM_DIRECTOR`), which is responsible for various tasks that don't belong under any other actor. (TODO: provide examples of things it does)

## Scripts

As with the documentation above, the script names below are official. They're static arrays in `dCsSeqMng_c`.

### By usage

Here are some tables to illustrate some of the more confusing script-selection scenarios:

#### World entrances

|                      | First time (airship present) | First time (airship not present) | Not the first time
| -------------------- | ---------------------------- | -------------------------------- | ------------------------------
| **Walking**          | `smc_demo_W_Walking_in`      | `smc_demo_WorldIn_NoShip`        | `smc_demo_W_Walking_in_Normal`
| **Cannon**           | `smc_demo_W_Cannon_in`       | `smc_demo_WorldIn_Jump_NoShip`   | `smc_demo_W_Cannon_in_Normal`
| **Riding airship**\* | `smc_demo_W_Flying_in`       |                                  |
| **Menu**             |                              | `null`**                         | `null`

*\*Unused entrance method.*

*\*\*World 9 is entered this way.*

#### Clearing a tower

|                 | First time               | Not the first time
| --------------- | ------------------------ | ---------------------
| **(Any world)** | `smc_demo_W1_toride_clr` | `smc_demo_toride_clr`

#### Clearing a castle

|             | First time (airship present) | First time (airship not present) | Not the first time
| ----------- | ---------------------------- | -------------------------------- | ---------------------
| **World 1** | `smc_demo_W1_castle_clr`     | `smc_demo_W1_castle_clr`         | `smc_demo_castle_clr`
| **World 2** | `smc_demo_W1_castle_clr`     | `smc_demo_W1_castle_clr`         | `smc_demo_castle_clr`
| **World 3** | `smc_demo_W1_castle_clr`     | `smc_demo_W1_castle_clr`         | `smc_demo_castle_clr`
| **World 4** | `smc_demo_W3_castle_clr`     | `smc_demo_castle_clr`            | `smc_demo_castle_clr`
| **World 5** | `smc_demo_W1_castle_clr`     | `smc_demo_W1_castle_clr`         | `smc_demo_castle_clr`
| **World 6** | `smc_demo_W3_castle_clr`     | `smc_demo_castle_clr`            | `smc_demo_castle_clr`
| **World 7** | `smc_demo_W1_castle_clr`     | `smc_demo_W1_castle_clr`         | `smc_demo_castle_clr`
| **World 8** |                              |                                  | `smc_demo_castle_clr`

#### Failing an airship

|                 | Airship present               | Airship not present ("anchor course")
| --------------- | ----------------------------- | -------------------------------------
| **(Any world)** | `smc_demo_airship_course_out` | `smc_demo_default_fail`

#### Clearing an airship

|             | First time (airship present) | First time (airship not present) | Not the first time
| ----------- | ---------------------------- | -------------------------------- | ------------------------
| **World 4** | `smc_demo_airship_gonext`    | `smc_demo_W36_Clear_Normal`      | `smc_demo_default_clr`
| **World 6** | `smc_demo_airship_gonext`    | `smc_demo_W36_Clear_Normal`      | `smc_demo_default_clr`
| **World 8** | `smc_demo_KoopaCastleAppear` |                                  | `smc_demo_airship_clear`

### By number

{{SCRIPTS}}

## Commands

These names are *not* official.

{{COMMANDS}}
