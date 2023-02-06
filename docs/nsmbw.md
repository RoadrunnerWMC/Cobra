# World Map Scripts in NSMBW

**THIS IS AN AUTO-GENERATED FILE -- DO NOT EDIT DIRECTLY!** Instead, edit the "nsmbw" files in the `data/` folder and run `cobra.py generate_documentation`. (Generated 2023-02-06T06:36:05.808359.)

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
vf60(dCsSeqMng_c::m_instance.GetCutName(), unknown_flag);
```

That virtual function is overridden by each subclass. Its purpose is to check if the current command type is one the actor recognizes, and perform any necessary actions if so.

When a `dWmDemoActor_c` has finished handling a command that it's responsible for, it calls `setCutEnd()` on itself. Every frame when a script is running, `dCsSeqMng_c` calls `checkCutEnd()` on each `dWmDemoActor_c` instance to see if any of them have set the flag. If so, it advances to the next command, and calls `clearCutEnd()` on all `dWmDemoActor_c` instances to reset them.

It's a slightly convoluted system, for sure.

#### daWmDirector

One notable `dWmDemoActor_c` subclass is `daWmDirector` (actor 664, `WM_DIRECTOR`), which is responsible for various tasks that don't belong under any other actor. (TODO: provide examples of things it does)

## Scripts

As with the documentation above, the script names in the table below are official. They're static arrays in `dCsSeqMng_c`.

ID | Name | Description
-- | ---- | -----------
**0** | `smc_demo_default_clr` | Plays when any course (other than ambushes) is cleared.
**1** | `smc_demo_default_fail` | Plays when any course (other than ambushes) is failed.
**2** | `smc_demo_enemy_clr` | Plays when the player defeats an ambush enemy.
**3** | `smc_demo_enemy_fail` | Plays when the player is defeated by an ambush enemy.
**4** | `smc_demo_toride_in` | Plays when entering a tower.
**5** | `smc_demo_toride_clr` | Plays when a tower is re-cleared.
**6** | `smc_demo_toride_fail` | Plays when an uncompleted tower is failed.
**7** | `smc_demo_toride_fail2` | Plays when a completed tower is failed.
**8** | `smc_demo_castle_in` | Plays when entering a castle, except for the secret entrance into the World 7 castle. Peach's Castle also counts.
**9** | `smc_demo_castle_clr` | Plays when a castle is re-cleared, the World 4 or World 6 castle is cleared while the airship isn't present, or Peach's Castle is exited.
**10** | `smc_demo_castle_fail` | Plays when an uncompleted castle is failed.
**11** | `smc_demo_castle_fail2` | Plays when a completed castle is failed.
**12** | `smc_demo_ghost_in` | Plays when entering a ghost house.
**13** | `smc_demo_ghost_clr` | Plays when a ghost house is cleared.
**14** | `smc_demo_ghost_fail` | Plays when an uncompleted ghost house is failed.
**15** | `smc_demo_ghost_fail2` | Plays when a completed ghost house is failed.
**16** | `smc_demo_cannon` | Unused. Plays a very unfinished cannon animation and warps you to another world.
**17** | `smc_demo_trship_appear` | Unused. Causes a WM_NOTE actor (if previously spawned) to appear above Mario's head, and then move to a random map node, with the camera following it.
**18** | `smc_demo_dokan` | Plays when using a pipe shortcut in World 2 or World 6.
**19** | `smc_demo_dokan_warp` | Unused. Intended to be used when entering a pipe to another world or sub-world.
**20** | `smc_demo_dokan_start` | Unused. Intended to be used when exiting a pipe from another world or sub-world.
**21** | `smc_demo_W_Walking_in` | Plays when entering a world for the first time (with an airship cutscene) by walking in from the previous world's castle.
**22** | `smc_demo_W_Walking_in_Normal` | Plays when entering a world for the first time (without an airship cutscene) by walking in from the previous world's castle.
**23** | `smc_demo_W_Flying_in` | Unused. Unused, slightly buggy world-entrance cutscene in which the airship drops Mario off at the start node before continuing to the tower like usual.
**24** | `smc_demo_W_Cannon_in` | Plays when entering a world for the first time (with an airship cutscene) via a cannon.
**25** | `smc_demo_W_Cannon_in_Normal` | Plays when entering a previously-visited world via a cannon.
**26** | `smc_demo_W1_toride_clr` | Plays when a tower is cleared for the first time.
**27** | `smc_demo_W1_castle_clr` | Plays when a castle is cleared for the first time, except in World 4.
**28** | `smc_demo_W3_castle_clr` | Plays when the World 4 or World 6 castle is cleared for the first time, if the airship is present.
**29** | `smc_demo_fade_test` | Unused. Fades the screen out and back in, twice.
**30** | `smc_demo_view_world` | Plays when the player uses the "View Map" feature.
**31** | `smc_demo_course_in` | Plays when entering a normal course.
**32** | `smc_demo_kinoko_out` | Unused.
**33** | `smc_demo_airship_course_in` | Plays when entering an airship or anchor course.
**34** | `smc_demo_airship_course_out` | Plays when an airship (not an anchor course) is failed.
**35** | `smc_demo_start_kinoko_in` | Unused.
**36** | `smc_demo_airship_gonext` | Plays when the World 4 or World 6 airship (not an anchor course) is cleared for the first time.
**37** | `smc_demo_W36_Clear_Normal` | Plays when the World 4 or World 6 anchor course (not an airship) is cleared for the first time.
**38** | `smc_demo_null` | Plays when the world map appears with no particular cutscene, such as when loading a save file or exiting a course from the pause menu.
**39** | `smc_demo_antlion` | Plays when sand traps appear when walking on the northern part of the World 2 map, if Mario isn't invincible.
**40** | `smc_demo_killer` | Plays when the player bumps into a Bullet Bill or Podoboo, if Mario isn't invincible.
**41** | `smc_demo_start_battle` | Plays when the player bumps into an ambush enemy (except for a sand trap, Bullet Bill, or Podoboo).
**42** | `smc_demo_Switch` | Plays when hitting one of the red switches in World 3.
**43** | `smc_demo_KoopaCastleAppear` | Plays when the World 8 airship is cleared for the first time.
**44** | `smc_demo_KinopioStart` | -
**45** | `smc_demo_WorldIn_NoShip` | Plays when entering a world for the first time (without an airship cutscene) by walking in from the previous world's castle.
**46** | `smc_demo_WorldIn_Jump_NoShip` | Plays when entering a world for the first time (without an airship cutscene) via a cannon.
**47** | `smc_demo_Pause_Menu` | Plays when the player opens the pause menu.
**48** | `smc_demo_airship_clear` | Plays when the World 8 airship is re-cleared.
**49** | `smc_demo_Stock_Menu` | Plays when the player opens the powerups menu.
**50** | `smc_demo_WorldSelect_Menu` | Plays when the player opens the world-selection menu.
**51** | `smc_demo_antlion_star` | Plays when sand traps appear when walking on the northern part of the World 2 map, if Mario is invincible.
**52** | `smc_demo_GameStart` | Plays when showing the World 1 map for the first time, after the opening cutscene.


## Commands

These names are *not* official.

ID | Name | Description | Argument
-- | ---- | ----------- | --------
**0** | `wait` | Causes the script to delay before continuing. Note: NSMBW runs at 60 FPS. | Duration (frames)
**1** | ?? | - | ??
**2** | ?? | - | ??
**3** | ?? | - | ??
**4** | ?? | - | ??
**5** | `end` | Ends the script. | None
**6** | ?? | - | ??
**7** | ?? | - | ??
**8** | ?? | - | ??
**9** | ?? | - | ??
**10** | ?? | - | ??
**11** | ?? | - | ??
**12** | ?? | - | ??
**13** | ?? | - | ??
**14** | ?? | - | ??
**15** | ?? | - | ??
**16** | ?? | - | ??
**17** | ?? | - | ??
**18** | ?? | - | ??
**19** | ?? | - | ??
**20** | ?? | - | ??
**21** | ?? | - | ??
**22** | ?? | - | ??
**23** | ?? | - | ??
**24** | ?? | - | ??
**25** | ?? | - | ??
**26** | ?? | - | ??
**27** | ?? | - | ??
**28** | ?? | - | ??
**29** | ?? | - | ??
**30** | ?? | - | ??
**31** | `show_wm_note_over_player` | Causes a WM_NOTE actor (if previously spawned) to appear above Mario's head. | None
**32** | `move_wm_note` | Causes a WM_NOTE actor (if previously spawned) to move to a random map node, with the camera following it. | None
**33** | ?? | - | ??
**34** | ?? | - | ??
**35** | ?? | Unused. | ??
**36** | ?? | - | ??
**37** | ?? | - | ??
**38** | ?? | - | ??
**39** | ?? | Unused. | ??
**40** | ?? | - | ??
**41** | ?? | - | ??
**42** | ?? | - | ??
**43** | ?? | - | ??
**44** | ?? | - | ??
**45** | ?? | - | ??
**46** | ?? | - | ??
**47** | ?? | - | ??
**48** | ?? | - | ??
**49** | ?? | - | ??
**50** | ?? | - | ??
**51** | ?? | - | ??
**52** | ?? | - | ??
**53** | ?? | - | ??
**54** | ?? | - | ??
**55** | ?? | - | ??
**56** | ?? | - | ??
**57** | ?? | - | ??
**58** | ?? | - | ??
**59** | ?? | - | ??
**60** | ?? | - | ??
**61** | ?? | - | ??
**62** | ?? | - | ??
**63** | ?? | - | ??
**64** | ?? | - | ??
**65** | ?? | - | ??
**66** | ?? | - | ??
**67** | ?? | - | ??
**68** | ?? | - | ??
**69** | ?? | - | ??
**70** | ?? | - | ??
**71** | ?? | - | ??
**72** | ?? | - | ??
**73** | ?? | - | ??
**74** | ?? | - | ??
**75** | ?? | - | ??
**76** | ?? | - | ??
**77** | ?? | - | ??
**78** | ?? | - | ??
**79** | ?? | - | ??
**80** | ?? | - | ??
**81** | ?? | - | ??
**82** | ?? | - | ??
**83** | ?? | - | ??
**84** | ?? | - | ??
**85** | ?? | Unused. | ??
**86** | ?? | - | ??
**87** | ?? | - | ??
**88** | ?? | Unused. | ??
**89** | ?? | - | ??
**90** | ?? | - | ??
**91** | ?? | - | ??
**92** | ?? | - | ??
**93** | ?? | Unused. | ??
**94** | ?? | - | ??
**95** | ?? | - | ??
**96** | ?? | - | ??
**97** | ?? | - | ??
**98** | ?? | - | ??
**99** | ?? | - | ??
**100** | ?? | - | ??
**101** | ?? | - | ??
**102** | ?? | - | ??
**103** | ?? | - | ??
**104** | ?? | - | ??
**105** | ?? | - | ??
**106** | ?? | - | ??
**107** | ?? | - | ??
**108** | ?? | - | ??
**109** | ?? | - | ??
**110** | ?? | - | ??
**111** | ?? | - | ??
**112** | ?? | - | ??
**113** | ?? | - | ??
**114** | ?? | - | ??
**115** | ?? | - | ??
**116** | ?? | - | ??
**117** | ?? | Unused. | ??
**118** | ?? | - | ??
**119** | ?? | - | ??
**120** | ?? | - | ??
**121** | ?? | - | ??
**122** | ?? | - | ??
**123** | ?? | - | ??
**124** | ?? | - | ??
**125** | ?? | Unused. | ??
**126** | ?? | - | ??
**127** | ?? | - | ??
**128** | ?? | - | ??
**129** | ?? | - | ??
**130** | ?? | - | ??
**131** | ?? | - | ??
**132** | ?? | - | ??
**133** | ?? | - | ??
**134** | ?? | - | ??
**135** | ?? | - | ??
**136** | ?? | - | ??
**137** | ?? | - | ??
**138** | ?? | Unused. | ??
**139** | ?? | - | ??
**140** | ?? | - | ??
**141** | ?? | - | ??
**142** | ?? | - | ??
**143** | ?? | - | ??
**144** | ?? | - | ??
**145** | ?? | - | ??
**146** | ?? | - | ??
**147** | ?? | - | ??
**148** | ?? | - | ??
**149** | ?? | - | ??
**150** | ?? | - | ??
**151** | ?? | - | ??
**152** | ?? | - | ??
**153** | ?? | - | ??
**154** | ?? | - | ??
**155** | ?? | - | ??
**156** | ?? | - | ??
**157** | ?? | - | ??
**158** | ?? | - | ??
**159** | ?? | - | ??
**160** | ?? | - | ??
**161** | ?? | - | ??
**162** | ?? | - | ??
**163** | ?? | - | ??
**164** | ?? | - | ??
**165** | ?? | - | ??
**166** | ?? | - | ??
**167** | ?? | - | ??
**168** | ?? | - | ??

