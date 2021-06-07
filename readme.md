# Cobra (working title)

A tool for exporting and importing world map scripts in NSMBW, NSMB2, NSMBU, and NSMBUDX.

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

## Script Documentation

The scripts and their commands vary between games. Documentation on them is kept in the `data` folder, mostly in the form of JSON files so that the info can be used programmatically.

The `generate_documentation` command converts it all to Github-flavored Markdown files, which are checked into the repository and kept up-to-date:

* [World Map Scripts in NSMBW](docs_nsmbw.md)
* [World Map Scripts in NSMB2](docs_nsmb2.md)
* [World Map Scripts in NSMBU/NSMBUDX](docs_nsmbu.md)
