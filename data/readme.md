This folder contains the data files specifying the scripts and commands across every version (when they differ) of each supported game.

## JSON Schema

The schema for the json files is something like this. Note that basically everything is optional.
````json
{
    "version_key": {  // the base version must be called "root"
        "name": "Human-Readable Name",
        "parent": "other_version_key",  // the version this one is based on. Omit for the "root" version

        // Scripts, relative to the parent version
        "scripts": {
            // "renumber" lets you change the IDs of scripts defined in the parent
            "renumber": {
                "123-129": "+2",  // means "script IDs 123 through 129 from the parent version are now numbered 125-131"
                "231-*": "+5"     // means "script IDs 231 onward are now numbered starting at 236"
            },
            // "add" lets you add new scripts not found in the parent
            "add": {
                "0": {  // script ID
                    "name": "Human-Readable Name",
                    "description": "This script does whatever."
                },
                ...  // more scripts here
            },
            // "delete" lets you remove scripts that were in the parent
            "delete": [
                0, 2, 17  // script IDs to remove
            ]
        },

        // Command types, relative to the parent version
        "commands": {
            // "renumber" and "delete" are also supported, and work the same as for "scripts" above
            "add": {
                "0": {  // command ID
                    "name": "frobnicate",
                    "description": "Frobnicates the foobar.",
                    "arg": null  // means the command ignores its argument value (i.e. no argument)
                },
                "1": {
                    "name": "write_null_to_memory",
                    "description": "Writes a null pointer to a memory address.",
                    "arg": {
                        "name":
                    }
                }
            }
        }
    },
    ...
}
```