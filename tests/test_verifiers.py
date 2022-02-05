from scripts import utils
from scripts import main
# python3 -m pytest -v


def test_is_tag():
    assert utils.is_tag("tag=value") == True
    assert utils.is_tag("==value") == True

    assert utils.is_tag("tag") == False
    assert utils.is_tag("...") == False


def test_is_valid_num_qubits():
    assert utils.is_valid_num_qubits("1.0") == True
    assert utils.is_valid_num_qubits("6.0") == True
    assert utils.is_valid_num_qubits("8") == True
    assert utils.is_valid_num_qubits("1") == True

    assert utils.is_valid_num_qubits("^*£^^*()()^") == False
    assert utils.is_valid_num_qubits("1/0") == False
    assert utils.is_valid_num_qubits("1!") == False
    assert utils.is_valid_num_qubits("0") == False
    assert utils.is_valid_num_qubits("-2") == False
    assert utils.is_valid_num_qubits("3.490") == False
    assert utils.is_valid_num_qubits("-3.0") == False    
    assert utils.is_valid_num_qubits("1.0000000000000000000001") == False


def test_is_valid_preset_state():
    assert utils.is_valid_preset_state("zero") == True
    assert utils.is_valid_preset_state("one") == True

    assert utils.is_valid_preset_state("oneee") == False
    assert utils.is_valid_preset_state("zzero") == False


def test_is_valid_new_name():
    assert utils.is_valid_new_name("q1") == True
    assert utils.is_valid_new_name("Qwe9wesd") == True

    assert utils.is_valid_new_name(".q1") == False
    assert utils.is_valid_new_name(" ") == False


def test_is_existing_state():
    env = {}
    env['states_dict'] = {}
    env['states_dict']['q'] = 1
    env['states_dict']['r'] = None
    assert utils.is_existing_state("q", env) == True
    assert utils.is_existing_state("r", env) == True
    
    assert utils.is_existing_state(1, env) == False
    assert utils.is_existing_state("s", env) == False


def test_is_existing_gate():
    env = {}
    env['gates_dict'] = {}
    env['gates_dict']['X'] = 1
    env['gates_dict']['H'] = None
    assert utils.is_existing_gate("X", env) == True
    assert utils.is_existing_gate("H", env) == True
    
    assert utils.is_existing_gate(1, env) == False
    assert utils.is_existing_gate("s", env) == False


def test_is_valid_qubit_of_state():
    pass


def test_is_valid_qubit_list_of_state():
    pass


def test_is_code_block():
    assert utils.is_code_block("{code}") == True
    assert utils.is_code_block(" {code} ") == True
    assert utils.is_code_block(" {code   } ") == True
    assert utils.is_code_block(" {  code    } ") == True

    assert utils.is_code_block("hello") == False
    assert utils.is_code_block("{code") == False
    assert utils.is_code_block(" {cod}e ") == False
    assert utils.is_code_block(" }{") == False


def test_is_letters():
    assert utils.is_letters("abcdefGJSuahSU") == True
    assert utils.is_letters("A") == True

    assert utils.is_letters("ahdshjdsj_sjahj") == False
    assert utils.is_letters("1") == False


def test_construct_int_list():
    assert utils.construct_int_list("[1, 2, 3]") == [1, 2, 3]
    assert utils.construct_int_list("[1,2,3]") == [1, 2, 3]
    
    assert utils.construct_int_list("[1, 2, 3.0]") == None # TODO: Does this need changing?
    assert utils.construct_int_list("[]") == None
    assert utils.construct_int_list("(1, 2, 3)") == None
    assert utils.construct_int_list("] [") == None


def test_construct_list():
    assert utils.construct_list("[1, 2, 3]") == [1, 2, 3]
    assert utils.construct_list("[1,2,3]") == [1, 2, 3]
    assert utils.construct_list("[1.0, 2, 3.0]") == [1, 2, 3]
    assert utils.construct_list("[1.5, 2, 3]") == [1.5, 2, 3]

    assert utils.construct_list("[s]") == None
    assert utils.construct_list("] [") == None


def test_construct_range_list():
    assert utils.construct_range_list("(1, 2, -1)") == [1, 2, -1]
    assert utils.construct_range_list("(-1, 2, -1)") == [-1, 2, -1]

    assert utils.construct_range_list("(1.5, 2, -1)") == None
    assert utils.construct_range_list("([1], 2, [-1])") == None