import re
from quantum_state import QuantumState

class NewCommandError(Exception):
    pass

def command(env, command_args):
    tags = {'num_qubits' : {'rep' : ['nq=', 'qubits='], 'type' : int, 'choices' : 'integers'}, 
            'preset_state' : {'rep' : ['s=', 'state='], 'type' : str, 'choices' : ['zero', 'one']}}
    keyword_args = {'num_qubits' : 1, 'preset_state' : None}
    new_states = []
    for i in range(len(command_args)):
        s = command_args[i]
        # If s is already a state, delete it
        if s in env['states_dict']:
            del env['states_dict'][s]
            measurements_to_delete = []
            # Delete all measurements made from s 
            for v in env['vars_dict']:
                if v.startswith(f'{s}.'):
                    measurements_to_delete.append(v)
            for v in measurements_to_delete:
                del env['vars_dict'][v]
        # Variable to store whether current command arg s is a tag or not
        is_tag = False
        # If a command argument starts with a tag, we record its value (provided it is an integer)
        for tag_name in tags.keys():
            for tag_rep in tags[tag_name]['rep']:
                if s.startswith(tag_rep):
                    try:
                        tag_value = s[len(tag_rep):]
                        # If no value was assigned to the tag, take the next argument to be the tag's assigned value
                        if len(tag_value) == 0:
                            tag_value = command_args[i+1]
                        # Assign the designated type to the value
                        typed_tag_value = tags[tag_name]['type'](tag_value) 
                        # If the value can be only one of a select few choices (indicated by choices being a list), then check it matches and if not raise an error.
                        if isinstance(tags[tag_name]['choices'], list):
                            if typed_tag_value in tags[tag_name]['choices']:
                                keyword_args[tag_name] = typed_tag_value
                            else:
                                raise NewCommandError(f"'{tag_value}' cannot be assigned to the {tag_rep[:-1]} tag. Accepted values are: {', '.join(tags[tag_name]['choices'])}")
                        # Otherwise, assign the value to the corresponding keyword_arg
                        else:
                            keyword_args[tag_name] = typed_tag_value
                        is_tag = True
                        break
                    except ValueError:
                        raise NewCommandError(f"'{tag_value}' cannot be assigned to the {tag_rep[:-1]} tag. Accepted values are: {tags[tag_name]['choices']}")
        # If we have encountered a potential new state name
        if not is_tag:
            if '=' in s:
                # We assume a faulty tag assignment and raise appropriate error
                raise NewCommandError(f"'{s.split('=')[0]}' is not a recognised tag.")
            else:
                illegal_chars = re.search("[^0-9a-zA-Z]", s)
                # If the name contains an illegal character, declare an error. Otherwise, append to list of states to be created
                if illegal_chars:
                    raise NewCommandError(f"Invalid character(s) in state name: {s[illegal_chars.span()[0]]}")
                else:
                    new_states.append(s)
    # Create the new states, and return the modified environment
    for s in new_states:
        env['states_dict'][s] = QuantumState(num_qubits=keyword_args['num_qubits'], state_name=s, preset_state=keyword_args['preset_state'])
    return env