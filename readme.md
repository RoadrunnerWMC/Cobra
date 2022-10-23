# Cobra

A tool for exporting and importing world map scripts in all versions\* of
NSMBW, NSMB2, NSMBU, NSLU, and NSMBU Deluxe.

(\*Except for demo builds that don't have world maps at all.)

## Status

Still in early development and constantly changing. **Instructions below are
likely to be outdated**, as I'm not bothering to rewrite all of them every time
I change something. I will rewrite it all before the first official release,
though.

Also, keep in mind that this is very unfinished -- for example, as I write
this, NSMBW only partially works, I haven't started on NSMB2 at all yet, and
there's no way to load your .wms files into any of the three games. ...So don't
expect very much to work just yet.

## World map scripts?

todo: explain what that even means

## Overview

Editing world map scripts with Cobra is essentially a four-step process:

* Use `cobra export` to perform auto-analysis of the game's code (or a RAM dump) and export its results:
    * A text file containing scripts
    * A JSON file containing important address values required for patching
* Edit the text-file scripts to your heart's content
* Use `cobra encode` to convert the text file to a binary file (.wms, a simple custom format)
* Compile a patch for the game's code using the auto-detected addresses from step 1

## Setup

todo

## Usage

todo

## Script documentation

The scripts and their commands vary between games. Documentation on them is
kept in the `data` folder, mostly in the form of JSON files so that the info
can be used programmatically.

The `generate_documentation` command converts it all to Github-flavored
Markdown files, which are checked into the repository and kept up-to-date:

* [World Map Scripts in NSMBW](docs/nsmbw.md)
* [World Map Scripts in NSMB2](docs/nsmb2.md)
* [World Map Scripts in NSMBU/NSLU/NSMBUDX](docs/nsmbu.md)

## .wms format specification

.wms (unimaginatively, "world map scripts") is the custom output file type
produced by Cobra. It's similar to the simple script tables it's replacing, but
with a header added. Thus this spec.

The games themselves always use an *array* of scripts, i.e. script IDs are
implicitly from 0 to num_scripts - 1. For modding purposes, though, it's
convenient to be able to replace a *subset* of script IDs rather than replacing
the entire table. Thus, .wms defines a *sparse* array of scripts, via an array
of script IDs parallel to the custom scripts array. For example, if the script
IDs array is [10, 12, 23, 35], then the four scripts in the .wms's scripts
table are intended to replace the retail scripts at those indices.

Script IDs are allowed to go beyond the number of scripts in the original
game's table, so that you can define brand-new scripts if you want to.

Pseudo-C description of the format:

```c
// (Same struct as native script commands)
struct ScriptCommand {
    uint32_t id;
    uint32_t argument;
}

// (Same struct as native scripts-table entries)
struct ScriptsTableEntry {
#ifdef NSMBW
    // (Assume priority = 0)
#else
    uint32_t priority;
#endif
    ScriptCommand *start;  // offset relative to start of .wms file
}

struct WMSFile {
    char magic[3];  // "WMS"
    char version;  // Current version: '0' (as a character, not byte value
                   // zero). If version is unrecognized, consider everything
                   // beyond this point unparseable.
    char game;  // - 'W' = NSMBW
                // - '2' = NSMB2
                // - 'U' = NSMBU or NSLU (on Wii U)
                // - 'X' = NSMBUDX
                // From this, you can infer endianness, and whether the
                // scriptsTableEntry struct (above) includes priorities or not.
                // If you load a .wms into the wrong game, the loader can
                // panic instead of trying to read it.
    char gameVariant[3];  // Game variant identifier, so that loading a .wms
                          // file into the wrong version of a game can be
                          // detected. The list of game variants is defined
                          // elsewhere.
                          // If you load a .wms into the wrong game variant,
                          // the loader can panic instead of trying to read it.
    uint32_t numScripts;
    uint32_t scriptIDs[numScripts];  // Guaranteed to be in sorted order so
                                     // that binary searching is valid
    ScriptsTableEntry scriptsTable[numScripts];
    ScriptCommand scriptsData[];  // all of the commands data goes here
}
```

### Game variants in .wms version 0

NSMBU:

- `100`: NSMBU version 1.0.0
- `110`: NSMBU versions 1.1.0 and 1.2.0
- `130`: NSMBU version 1.3.0 (including the early EU version "64"), NSLU standalone, the NSMBU+NSLU bundle, and the JP eShop demo

NSMBUDX:

- `all`: all versions (international 1.0.0, and CN versions 1.0.0 and 1.0.1)

Other games: (todo)
