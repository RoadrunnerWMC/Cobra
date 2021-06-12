# World Map Scripts in NSMBW

**THIS IS AN AUTO-GENERATED FILE -- DO NOT EDIT DIRECTLY!** Instead, edit the "nsmbw" files in the `data/` folder and run `cobra.py generate_documentation`. (Generated 2021-06-12T00:04:35.960725.)

## Introduction

The information below is specifically for the EU v1 release; specific numbers may vary in other releases.

Thanks to [Ninji](https://github.com/Treeki) and [Skawo](https://github.com/skawo) for helping with research in this game.

The `WM_DIRECTOR` actor (664) is responsible for executing scripts. Scripts and the scripts table are stored as static arrays in the actor `WM_CS_SEQ_MNG` (621) (class name `dCsSeqMng_c`).

The scripts table is at 0x8031DBCC, and is just an array of 53 pointers to scripts. Script commands are 8 bytes long: `{uint32_t command_id; uint32_t argument}`. The terminator command to end a script is 5.

The script names in the table below are official (though there's a common prefix among all of them that hasn't yet been identified), except where noted. They're derived from the Nvidia Shield TV release of NSMBW.

## Scripts

ID | Name | Description
-- | ---- | -----------
**0** | `default_clr` | Script that plays when a normal course is successfully completed.
**1** | `default_fail` | Script that plays when a normal course is failed.
**2** | `enemy_clr` | -
**3** | `enemy_fail` | -
**4** | `toride_in` | Script that plays when a tower is entered.
**5** | `toride_clr` | Script that plays when a tower is successfully completed.
**6** | `toride_fail` | -
**7** | `toride_fail2` | -
**8** | `castle_in` | Script that plays when a castle is entered.
**9** | `castle_clr` | Script that plays when a castle is successfully completed.
**10** | `castle_fail` | -
**11** | `castle_fail2` | -
**12** | `ghost_in` | Script that plays when a ghost house is entered.
**13** | `ghost_clr` | Script that plays when a ghost house is successfully completed.
**14** | `ghost_fail` | -
**15** | `ghost_fail2` | -
**16** | `cannon` | -
**17** | `show_wm_note` | Unofficial name, real name is unknown. Demangled symbol hash is 0x56f66ffc.<br><br>Causes a WM_NOTE actor (if previously spawned) to appear above Mario's head, and then move to a random map node, with the camera following it.
**18** | `dokan` | -
**19** | `dokan_warp` | -
**20** | `dokan_start` | -
**21** | `W_Walking_in` | -
**22** | `W_Walking_in_Normal` | -
**23** | `W_Flying_in` | -
**24** | `W_Cannon_in` | -
**25** | `W_Cannon_in_Normal` | -
**26** | ?? | Unknown name. Demangled symbol hash is 0x649307aa.
**27** | ?? | Unknown name. Demangled symbol hash is 0x2a5ec5a7.
**28** | `wSign_koopaCastle_in` | -
**29** | ?? | Unknown name. Demangled symbol hash is 0xcae3b49f. Might be "fade_test"?
**30** | `view_world` | -
**31** | `course_in` | -
**32** | `kinoko_out` | -
**33** | `airship_course_in` | -
**34** | `airship_course_out` | -
**35** | `start_kinoko_in` | -
**36** | ?? | Unknown name. Demangled symbol hash is 0x281e8a18.
**37** | ?? | Unknown name. Demangled symbol hash is 0xcf0daa08.
**38** | `null` | -
**39** | `antlion` | -
**40** | `killer` | -
**41** | `start_battle` | -
**42** | `Switch` | -
**43** | `KoopaCastleAppear` | -
**44** | `KinopioStart` | -
**45** | ?? | Unknown name. Demangled symbol hash is 0xcfc42869.
**46** | ?? | Unknown name. Demangled symbol hash is 0xaefdd774.
**47** | `Pause_Menu` | -
**48** | `airship_clear` | -
**49** | `Stock_Menu` | -
**50** | `WorldSelect_Menu` | -
**51** | `antlion_star` | -
**52** | `GameStart` | -

## Commands

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
