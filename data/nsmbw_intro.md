The information below is specifically for the EU v1 release; specific numbers may vary in other releases.

Thanks to [Ninji](https://github.com/Treeki) and [Skawo](https://github.com/skawo) for helping with research in this game.

The `WM_DIRECTOR` actor (664) (class name `daWmDirector`) is responsible for executing scripts. Scripts and the scripts table are stored as static arrays in the actor `WM_CS_SEQ_MNG` (621) (class name `dCsSeqMng_c`).

The scripts table (`dCsSeqMng_c::smc_demo_table`) is at 0x8031DBCC, and is just an array of 53 pointers to scripts. Script commands are 8 bytes long: `{uint32_t command_id; uint32_t argument}`. The terminator command to end a script is 5.

The script names in the table below are official. They're derived from the Nvidia Shield TV release of NSMBW.
