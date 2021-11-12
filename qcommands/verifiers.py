import re


def is_tag(x):
    if '=' in x:
        return True
    else:
        return False


def is_valid_num_qubits(n):
    try:
        n = int(n)
        if n > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def is_valid_preset_state(p):
    if p == 'zero' or p == 'one':
        return True
    else:
        return False


def is_valid_new_name(s):
    illegal_chars = re.search("[^0-9a-zA-Z]", s)
    if illegal_chars:
        return False
    else:
        return True


def is_existing_state(s, env):
    if s in env['states_dict'].keys():
        return True
    else:
        return False


def is_existing_gate(g, env):
    if g in env['gates_dict'].keys():
        return True
    else:
        return False


def is_valid_qubit_of_state(q, s):
    try:
        q = int(q)
        if (1 <= q <= s.num_qubits):
            return True
        else:
            return False
    except ValueError:
        return False


def is_valid_qubit_list_of_state(q_list, s):
    for q in q_list:
        if not is_valid_qubit_of_state(q, s):
            return False
    for i in range(len(q_list)):
        for j in range(i+1, len(q_list)):
            if q_list[i] == q_list[j]:
                return False
    return True


def construct_int_list(q_list):
    if q_list[0] != '[' or q_list[-1] != ']':
        return None
    else:
        q_list = q_list[1:-1]
    items = q_list.split(',')
    try:
        for i in range(len(items)):
            items[i] = int(items[i])    
        return items  
    except ValueError:
        return None
  

def remove_braces(code_block):
    if code_block[0] != '{' or code_block[-1] != '}':
        return None
    else:
        return code_block[1:-1]