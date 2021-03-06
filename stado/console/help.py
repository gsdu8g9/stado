"""Command: help"""

from . import Command
from .. import version


class Help(Command):
    """Shows help messages."""

    name = 'help'

    usage = 'help [command_name]'
    summary = 'Show general help or show help for the given command.'
    description = ''
    options = []



    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('command', default=None, nargs='?')
        parser.set_defaults(function=self.run)


    def run(self, command=None):
        """Command-line interface will execute this method if user type 'help'
        command."""

        if command is None:
            print(self.global_help())
        else:
            print(self.help(command))


    def help(self, command_name):

        command = self.console.commands.get(command_name)
        if command:

            options = ''
            for option, description in command.options:
                options = '{}\n    {}\n       {}'.format(options, option,
                                                         description)

            msg = (
                "  Usage:"
                "\n"
                "\n    " + command.usage +
                "\n"
                "\n  Summary:"
                "\n  "
                "\n    " + command.summary
            )

            if options:
                msg += "\n\n  Options: \n" + options

            return msg

        # Help for given command not found.
        return "Help for the given command not found: {}".format(command_name)

    def global_help(self):

        commands = ''
        for i in sorted(self.console.commands.values(),
                        key=lambda x: x.name):

            commands = '{}\n    {:8}{}'.format(commands, i.name,
                                                          i.summary)

        return (
            "Stado is a simple static site generator with python script support."
            "\n"
            "\n  Commands:"
            "\n  " + commands +
            "\n  "
            "\n  Version: " + str(version)
        )