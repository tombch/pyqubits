help_message = """---BEGIN COMMAND LIST---

  -n state1, state2, ..., --new state1, state2, ...
        create quantum states

  -j state1 state2 ..., --join state1 state2 ...
        join quantum states

  -r state1 state2, --rename state1 state2
        rename a quantum state

  -d dtype object1 object2..., --delete dtype object1 object2...
        delete states and/or measurements

  -k ktype object1 object2..., --keep ktype object1 object2...
        keep states and/or measurements

  -a gate state qubit(s), --apply gate state qubit(s)
        apply a gate to qubit(s) in a given state

  -l, --list
        list currently available states and measurements

  -h, --help
        show help message

  -q, --quit
        quit the program

---END COMMAND LIST---"""


class HelpCommandError(Exception):
    pass


def command(env, command_args):
    if len(command_args) != 0:
        raise HelpCommandError(f"Expected no arguments.")
    else:
        print(help_message)
    return env