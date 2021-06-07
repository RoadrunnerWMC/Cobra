# 2021-05-15

import datetime
import pathlib

import common
import game_variants



def generate_md_scripts_table(game: common.Game, scripts: dict) -> list:
    """
    Generate a list of lines (str's) for a Markdown table showing the
    scripts info for the specified game.
    """
    lines = []

    headers = []
    headers.append('ID')
    headers.append('Name')
    headers.append('Description')

    lines.append(' | '.join(headers))
    lines.append(' | '.join([('-' * len(h)) for h in headers]))

    for script_id in sorted(scripts):
        script_info = scripts.get(script_id, {})
        this_line = []

        this_line.append(f'**{script_id}**')

        if 'name' in script_info:
            this_line.append(f'`{script_info["name"]}`')
        else:
            this_line.append('??')

        this_line.append(script_info.get('description', '-').replace('\n', '<br>'))

        lines.append(' | '.join(this_line))

    return lines


def generate_md_commands_table(game: common.Game, commands: dict) -> list:
    """
    Generate a list of lines (str's) for a Markdown table showing the
    commands info for the specified game.
    """
    lines = []

    headers = []
    headers.append('ID')
    headers.append('Name')
    headers.append('Description')
    if game.uses_command_arguments():
        headers.append('Argument')

    lines.append(' | '.join(headers))
    lines.append(' | '.join([('-' * len(h)) for h in headers]))

    for command_id in sorted(commands):
        command_info = commands.get(command_id, {})
        this_line = []

        # ID
        this_line.append(f'**{command_id}**')

        # Name
        if 'name' in command_info:
            this_line.append(f'`{command_info["name"]}`')
        else:
            this_line.append('??')

        # Description
        description = ''

        if command_info.get('unused', False):
            description += 'Unused. '

        description += command_info.get('description', '').replace('\n', '<br>')

        if not description:
            description = '-'

        this_line.append(description.strip())

        # Argument
        argument = ''

        if 'arg' in command_info:
            arg_info = command_info['arg']
            if arg_info is None:
                argument = 'None'
            else:
                argument = arg_info['name']

                if 'unit' in arg_info:
                    argument += f' ({arg_info["unit"]})'

                if 'enum' in arg_info:
                    value_names = []

                    for val_str, name in arg_info['enum'].items():
                        value_names.append(f'<li>`{name}` ({val_str})</li>')

                    argument += f' &mdash; named values:<br><br><ul>{"".join(value_names)}</ul>'

        else:
            argument = '??'

        this_line.append(argument.strip())

        lines.append(' | '.join(this_line))


    return lines


def generate_md_sections_for_variants(game: common.Game, variants: dict, attr_name: str, table_renderer) -> list:
    """
    A helper function to generate sections showing all variants'
    versions of some attribute ("scripts" or "commands")
    """
    lines = []

    for name, variant in variants.items():
        thing = getattr(variant, attr_name)

        if not thing.renumber and not thing.add and not thing.delete:
            continue

        if len(variants) > 1:
            lines.append(f'### {variant.name}')
            lines.append('')

        if thing.renumber:
            lines.append('#### Re-numbered')
            lines.append('')
            for item in thing.renumber:
                if item.range_end:
                    lines.append(f'* **{item.range_start}-{item.range_end}**'
                        f' renumbered to **{item.range_start + self.offset}-{item.range_end + item.offset}**')
                else:
                    lines.append(f'* **{item.range_start}+** renumbered to **{item.range_start + item.offset}+**')
            lines.append('')

        if thing.add:
            if thing.renumber or thing.delete:
                lines.append('#### Added')
                lines.append('')

            lines.extend(table_renderer(game, thing.add))
            lines.append('')

        if thing.delete:
            lines.append('#### Removed')
            lines.append('')
            lines.append(', '.join(f'**{id}**' for id in thing.delete))
            lines.append('')

    return lines


def do_docs() -> None:
    """
    Handle the "docs" command
    """
    for game in common.Game:
        if game.gets_scripts_and_commands_from() is not game:
            # NSMBUDX (it doesn't get its own docs page because it's
            # essentially just NSMBU)
            continue

        print(f'Generating documentation for {game.value.upper()}...')

        variants = game_variants.load_game_json(game)

        output_file = pathlib.Path(f'docs_{game.value}.md')

        file_lines = []

        file_lines.append(f'# World Map Scripts in {game.value.upper()}')
        file_lines.append(f'')
        file_lines.append(f'**THIS IS AN AUTO-GENERATED FILE -- DO NOT EDIT DIRECTLY!** Instead, edit the "{game.value}" files in the `data/` folder and run `cobra.py generate_documentation`. (Generated {datetime.datetime.now().isoformat()}.)')
        file_lines.append(f'')

        file_lines.append('## Introduction')
        file_lines.append('')
        file_lines.extend(
            pathlib.Path(f'data/{game.value}_intro.md')
                .read_text(encoding='utf-8')
                .splitlines())
        file_lines.append('')

        file_lines.append('## Scripts')
        file_lines.append('')
        file_lines.extend(generate_md_sections_for_variants(game, variants, 'scripts', generate_md_scripts_table))

        file_lines.append('## Commands')
        file_lines.append('')
        file_lines.extend(generate_md_sections_for_variants(game, variants, 'commands', generate_md_commands_table))

        output_file.write_text('\n'.join(file_lines), encoding='utf-8')
