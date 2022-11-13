# Copyright 2021 RoadrunnerWMC
#
# This file is part of Cobra.
#
# Cobra is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cobra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cobra.  If not, see <https://www.gnu.org/licenses/>.

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

    def handle_analyze(pArgs):
        """
        Handle the "analyze" command.
        """
        input_file = pArgs.input_file

        export.do_analyze(input_file)

    parser_analyze = subparsers.add_parser('analyze', aliases=['a'],
        help='analyze a code file or memory dump, and print findings')
    parser_analyze.add_argument('input_file', type=pathlib.Path,
        help='file to inspect')
    parser_analyze.set_defaults(func=handle_analyze)

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

    parser_export = subparsers.add_parser('export', aliases=['ex'],
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

        wmsc_file = pArgs.wmsc_file
        if wmsc_file is None: wmsc_file = scripts_file.with_suffix('.wmsc')

        encode.do_encode(scripts_file, version_info_file, wmsc_file)

    parser_encode = subparsers.add_parser('encode', aliases=['en'],
        help='convert a scripts file to a .wmsc binary file')
    parser_encode.add_argument('scripts_file', type=pathlib.Path,
        help='input file containing one or more scripts')
    parser_encode.add_argument('version_info_file', type=pathlib.Path,
        help="a version-info file (.json) characterizing the particular version of the game you're going to be using this with")
    parser_encode.add_argument('wmsc_file', nargs='?', type=pathlib.Path,
        help='output .wmsc file to save to')
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
