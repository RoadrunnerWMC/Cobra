# 2021-05-15

import argparse
import pathlib
import typing

import common
import docs
import export


def do_import(scripts_file: pathlib.Path, cpp_file: pathlib.Path, add_ok:bool=False) -> None:
    """
    Handle the "import" command (with all default parameter values filled in as needed)
    """
    print(f'do_import({scripts_file}, {cpp_file}, {add_ok})')


def main(argv:list=None) -> None:
    parser = argparse.ArgumentParser(
        description='Cobra: a tool for world map scripts in the NSMB series')
    subparsers = parser.add_subparsers(title='commands',
        description='(run a command with -h for additional help)')

    def handle_export(pArgs):
        """
        Handle the "export" command.
        """
        input_file = pArgs.input_file

        scripts_file = pArgs.scripts_file
        if scripts_file is None: scripts_file = input_file.with_suffix('.txt')

        version_info_file = pArgs.version_info_file
        if version_info_file is None: version_info_file = input_file.with_suffix('.json')

        export.do_export(input_file, scripts_file, version_info_file)

    parser_export = subparsers.add_parser('export', aliases=['e'],
        help='export all scripts from a code file or memory dump')
    parser_export.add_argument('input_file', type=pathlib.Path,
        help='file to read scripts from')
    parser_export.add_argument('scripts_file', nargs='?', type=pathlib.Path,
        help='output file to save scripts to (.txt)')
    parser_export.add_argument('version_info_file', nargs='?', type=pathlib.Path,
        help='output file to save important autodetected info to (.json)')
    parser_export.set_defaults(func=handle_export)

    # def handle_import(pArgs):
    #     """
    #     Handle the "import" command.
    #     """
    #     scripts_file = pArgs.scripts_file

    #     cpp_file = pArgs.cpp_file
    #     if cpp_file is None: cpp_file = scripts_file.with_suffix('.cpp')

    #     do_import(scripts_file, cpp_file, pArgs.add_ok)

    # parser_import = subparsers.add_parser('import', aliases=['i'],
    #     help='convert a scripts file into a Kamek patch that can be used to import it')
    # parser_import.add_argument('scripts_file', type=pathlib.Path,
    #     help='input file containing one or more scripts')
    # parser_import.add_argument('cpp_file', nargs='?', type=pathlib.Path,
    #     help='output .cpp file to save the Kamek patch to')
    # parser_import.add_argument('--add_ok', action='store_true',
    #     help=f'if scripts with IDs higher than {NUM_RETAIL_SCRIPTS-1} are specified, handle it by creating a new, larger table instead of printing an error')
    # parser_import.set_defaults(func=handle_import)

    def handle_docs(pArgs):
        """
        Handle the "generate_documentation" command.
        """
        docs.do_docs()

    parser_docs = subparsers.add_parser('generate_documentation',
        help='convert json files to Markdown documentation')
    parser_docs.set_defaults(func=handle_docs)

    # Parse args and run appropriate function
    pArgs = parser.parse_args(argv)
    if hasattr(pArgs, 'func'):
        pArgs.func(pArgs)
    else:  # this happens if no arguments were specified at all
        parser.print_usage()


if __name__ == '__main__':
    main()
