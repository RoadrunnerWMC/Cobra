# 2021-05-15

import argparse
import pathlib
import typing

import common
import docs
import encode
import export


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

    def handle_encode(pArgs):
        """
        Handle the "encode" command.
        """
        scripts_file = pArgs.scripts_file
        version_info_file = pArgs.version_info_file

        wms_file = pArgs.wms_file
        if wms_file is None: wms_file = scripts_file.with_suffix('.wms')

        encode.do_encode(scripts_file, version_info_file, wms_file)

    parser_encode = subparsers.add_parser('encode', aliases=['i'],
        help='convert a scripts file to a .wms binary file')
    parser_encode.add_argument('scripts_file', type=pathlib.Path,
        help='input file containing one or more scripts')
    parser_encode.add_argument('version_info_file', type=pathlib.Path,
        help="a version-info file (.json) characterizing the particular version of the game you're going to be using this with")
    parser_encode.add_argument('wms_file', nargs='?', type=pathlib.Path,
        help='output .wms file to save to')
    parser_encode.set_defaults(func=handle_encode)

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
