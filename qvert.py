import numpy as np
import random

# Class for creating, displaying and measuring quantum states
class QuantumState:
    # Create a new QuantumState object
    def __init__(self, num_qubits=1, preset_state=None, preset_state_vector=None, state_name=None):
        # Set number of qubits and the number of classical states
        # The number of classical states equals the number of complex numbers necessary to fully describe the state
        self.num_qubits = num_qubits
        self.num_classical_states = 2**self.num_qubits
        # Set the name of the state, if provided
        self.state_name = ""
        if state_name != None:
            self.state_name = state_name
        else:
            self.state_name = "(no name)"
        # Set the initial state vector
        # The initial state vector will be generated randomly if neither a string description or ndarray are provided     
        if preset_state == "zero_state":
            # The zero state is the state |00...00>, i.e. the first element in the state vector has amplitude one
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[0] = 1
        elif preset_state == "one_state":
            # The one state is the state |11...11>, i.e. the last element in the state vector has amplitude one
            self.state_vector = np.zeros(self.num_classical_states) + np.zeros(self.num_classical_states) * 1j
            self.state_vector[self.num_classical_states-1] = 1
        elif type(preset_state_vector) is np.ndarray:
            self.state_vector = preset_state_vector
        else:
            # A state vector is created with random values from the unit circle around the origin
            self.state_vector = (2*np.random.random(self.num_classical_states)-1) + (2*np.random.random(self.num_classical_states)-1) * 1j
            # The vector is normalised to have length 1
            # Below seems to get norm closer to 1 than above
            self.state_vector = self.state_vector/np.linalg.norm(self.state_vector)
        # Create the initial circuit string for the state
        self.actions = 0
        self.action_string = "[x]  "
        self.circuit_string = " "*len(self.action_string)
        self.w = 5
        for i in range(0, self.num_qubits):
            self.circuit_string += str((i+1)%10)+" "*self.w
        self.circuit_string += "\n"+"["+str(self.actions)+"]  "
        for i in range(0, self.num_qubits):
            self.circuit_string += "|"+" "*self.w

    # Print the QuantumState object's state vector in Dirac notation
    def print_state(self, dp=16):
        state_string = str(self.state_name) + " = "
        for i in range(0, self.num_classical_states):
            current_amplitude = self.state_vector[i]
            if current_amplitude != 0:
                current_amplitude_string = str(round(current_amplitude.real, dp) + round(current_amplitude.imag, dp) * 1j)
                state_string += current_amplitude_string + " |" + bin(i)[2:].zfill(self.num_qubits) + ">\n"
        newline_count = state_string.count("\n")
        state_string = state_string.replace("\n", "\n" + " " * len(self.state_name) + " + ", newline_count-1)
        print("["+str(self.actions)+"] "+"State vector for "+self.state_name+":\n"+state_string)
    
    def update_circuit(self, new_wire):
        self.actions += 1
        self.circuit_string += "\n"+" "*len(self.action_string)+new_wire+"\n"+"["+str(self.actions)+"]  "
        for i in range(0, self.num_qubits):
            self.circuit_string += "|"+" "*self.w
        
    def print_circuit(self):
        print("Circuit diagram for "+self.state_name+":\n"+self.circuit_string+"\n")

    def measurement(self, qubit=1):
        I_matrix = np.array([[1+0j, 0+0j],
                             [0+0j, 1+0j]])
        zero_matrix = np.array([[1+0j, 0+0j],
                                [0+0j, 0+0j]])
        one_matrix = np.array([[0+0j, 0+0j],
                               [0+0j, 1+0j]])
        if (qubit == 1):
            measurement_matrix_zero = zero_matrix
            measurement_matrix_one = one_matrix
        else:
            measurement_matrix_zero = I_matrix
            measurement_matrix_one = I_matrix
        for i in range(2, self.num_qubits+1):
            if (i == qubit):
                measurement_matrix_zero = np.kron(measurement_matrix_zero, zero_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, one_matrix)
            else:
                measurement_matrix_zero = np.kron(measurement_matrix_zero, I_matrix)
                measurement_matrix_one = np.kron(measurement_matrix_one, I_matrix)
        collapsed_zero = np.matmul(measurement_matrix_zero, self.state_vector)
        zero_probability = np.matmul(measurement_matrix_zero.conjugate().transpose(), collapsed_zero)   
        zero_probability = np.matmul(self.state_vector.conjugate().transpose(), zero_probability)
        collapsed_one = np.matmul(measurement_matrix_one, self.state_vector)
        one_probability = np.matmul(measurement_matrix_one.conjugate().transpose(), collapsed_one)
        one_probability = np.matmul(self.state_vector.conjugate().transpose(), one_probability)
        # Dividing each probability by their sum gets the sum of both resulting probabilities (closer) to 1    
        sum_of_probabilities = zero_probability + one_probability
        zero_probability = zero_probability/sum_of_probabilities
        one_probability = one_probability/sum_of_probabilities
        dice = random.random()
        if dice < zero_probability:
            self.state_vector = collapsed_zero
            bit = 0
        else:
            self.state_vector = collapsed_one
            bit = 1
        # self.state_vector = self.state_vector/np.sqrt(np.sum(self.state_vector**2))
        self.state_vector = self.state_vector/np.linalg.norm(self.state_vector)
        new_wire = ""
        gap = " "
        for i in range(0, self.num_qubits):
            if (i+1) == qubit: 
                gap = "="
                new_wire += "M"+gap*self.w
            else:
                new_wire += "|"+gap*self.w
        new_wire += str(bit)
        self.update_circuit(new_wire)
        return bit

#Functions for manipulating quantum states
def gate(s, qubit, chosen_matrix, gate_char):
    I_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, 1+0j]])
    if (qubit == 1):
        gate_matrix = chosen_matrix
    else:
        gate_matrix = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == qubit):
            gate_matrix = np.kron(gate_matrix, chosen_matrix)
        else:
            gate_matrix = np.kron(gate_matrix, I_matrix)
    s.state_vector = np.matmul(gate_matrix, s.state_vector)
    new_wire = ""
    for i in range(0, s.num_qubits):
        if (i+1) == qubit: 
            new_wire += gate_char+" "*s.w
        else:
            new_wire += "|"+" "*s.w
    s.update_circuit(new_wire)

def X(s, qubit=1):
    X_matrix = np.array([[0+0j, 1+0j],
                         [1+0j, 0+0j]])
    gate(s, qubit, X_matrix, "X")

def Y(s, qubit=1):
    Y_matrix = np.array([[0+0j, 0-1j],
                         [0+1j, 0+0j]])
    gate(s, qubit, Y_matrix, "Y")

def Z(s, qubit=1):
    Z_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, -1+0j]])
    gate(s, qubit, Z_matrix, "Z")

def H(s, qubit=1):
    H_matrix = np.array([[1+0j, 1+0j],
                         [1+0j, -1+0j]])/np.sqrt(2)
    gate(s, qubit, H_matrix, "H")

def P(s, qubit=1):
    P_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, 0+1j]])
    gate(s, qubit, P_matrix, "P")

def T(s, qubit=1):
    T_matrix = np.array([[1+0j, 0+0j],
                         [0+0j, (sqrt(2)/2)+(sqrt(2)/2)*1j]])
    gate(s, qubit, T_matrix, "T")

def Cgate(s, control, target, chosen_matrix, gate_char):
    I_matrix = np.array([[1+0j, 0+0j],
                        [0+0j, 1+0j]])    
    zero_matrix = np.array([[1+0j, 0+0j],
                            [0+0j, 0+0j]])
    one_matrix = np.array([[0+0j, 0+0j],
                        [0+0j, 1+0j]])
    if (control == 1):
        gate_matrix_a = zero_matrix
        gate_matrix_b = one_matrix
    elif (target == 1):
        gate_matrix_a = I_matrix
        gate_matrix_b = chosen_matrix
    else:
        gate_matrix_a = I_matrix
        gate_matrix_b = I_matrix
    for i in range(2, s.num_qubits+1):
        if (i == control):
            gate_matrix_a = np.kron(gate_matrix_a, zero_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, one_matrix)
        elif (i == target):
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, chosen_matrix)         
        else:
            gate_matrix_a = np.kron(gate_matrix_a, I_matrix)
            gate_matrix_b = np.kron(gate_matrix_b, I_matrix)
    gate_matrix = np.add(gate_matrix_a, gate_matrix_b)
    s.state_vector = np.matmul(gate_matrix, s.state_vector)
    new_wire = ""
    gap = " "
    if control < target:
        for i in range(0, s.num_qubits):
            if (i+1) == control: 
                gap = "-"
                new_wire += "O"+gap*s.w
            elif (i+1) == target:
                gap = " "                    
                new_wire += gate_char+gap*s.w
            else:
                new_wire += "|"+gap*s.w
    elif target < control:
        for i in range(0, s.num_qubits):
            if (i+1) == control: 
                gap = " "
                new_wire += "O"+gap*s.w
            elif (i+1) == target:
                gap = "-"                    
                new_wire += gate_char+gap*s.w
            else:
                new_wire += "|"+gap*s.w
    s.update_circuit(new_wire)

def CNOT(s, control=1, target=2):
    X_matrix = np.array([[0+0j, 1+0j],
                         [1+0j, 0+0j]])
    Cgate(s, control, target, X_matrix, "X")

def CH(s, control=1, target=2):
    H_matrix = np.array([[1+0j, 1+0j],
                         [1+0j, -1+0j]])/np.sqrt(2)
    Cgate(s, control, target, H_matrix, "H")   

def Uf2(s, f_choice=random.randint(1, 4)):
    if f_choice == 1:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j]]) 
    elif f_choice == 2:
        U_f_matrix = np.array([[0+0j, 1+0j, 0+0j, 0+0j],
                               [1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])         
    elif f_choice == 3:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])  
    elif f_choice == 4:
        U_f_matrix = np.array([[1+0j, 0+0j, 0+0j, 0+0j],
                               [0+0j, 1+0j, 0+0j, 0+0j],
                               [0+0j, 0+0j, 0+0j, 1+0j],
                               [0+0j, 0+0j, 1+0j, 0+0j]])
    s.state_vector = np.matmul(U_f_matrix, s.state_vector)
    new_wire = "<|Uf2|>"
    s.update_circuit(new_wire)

def swap(s, qubit1, qubit2):
    if s.num_qubits > 1:
        CNOT(s, control=qubit1, target=qubit2)
        CNOT(s, control=qubit2, target=qubit1)
        CNOT(s, control=qubit1, target=qubit2)

def join_states(s_list, state_name=""):
    s_list_len = len(s_list)
    if s_list_len > 0:
        s_joint_num_qubits = s_list[0].num_qubits
        s_joint_state_vector = s_list[0].state_vector
        for i in range(1, s_list_len):
            s_joint_num_qubits = s_joint_num_qubits + s_list[i].num_qubits
            s_joint_state_vector = np.kron(s_joint_state_vector, s_list[i].state_vector)
        s_joint = QuantumState(num_qubits=s_joint_num_qubits, preset_state_vector=s_joint_state_vector, state_name=state_name)
    else:
        s_joint = None
    return s_joint