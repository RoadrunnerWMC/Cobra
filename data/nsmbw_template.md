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

As with the documentation above, the script names in the table below are official. They're static arrays in `dCsSeqMng_c`.

{{SCRIPTS}}

## Commands

These names are *not* official.

{{COMMANDS}}
