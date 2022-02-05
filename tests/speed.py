from scripts import quantum_state
from scripts import gates
import timeit


def measurement_speed(num_qubits=1):
    q = quantum_state.QuantumState(state_name='q', num_qubits=num_qubits)
    for x in range(1, q.num_qubits+1):
        q.measurement(qubit=2)


print(1, 8, timeit.timeit(lambda: measurement_speed(num_qubits=8), number=1))
print(1, 9, timeit.timeit(lambda: measurement_speed(num_qubits=9), number=1))
print(1, 10, timeit.timeit(lambda: measurement_speed(num_qubits=10), number=1))
print(1, 11, timeit.timeit(lambda: measurement_speed(num_qubits=11), number=1))

# import cProfile, pstats, io
# pr = cProfile.Profile()
# pr.enable()
# ...
# pr.disable()
# s = io.StringIO()
# ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
# ps.print_stats()
# print(s.getvalue())



# def right_kron_zero_matrix(self, in_matrix):
#     def yield_rows(in_matrix):
#         zero_row = [0 for x in in_matrix[0]]
#         for in_row in in_matrix:
#             yield in_row
#             yield zero_row
#     def yield_row_items(in_row):
#         for val in in_row:
#             yield val
#             yield 0
    
#     out_matrix = [[val for val in yield_row_items(in_row)] for in_row in yield_rows(in_matrix)]
#     return np.array(out_matrix, dtype=complex)


# def right_kron_one_matrix(self, in_matrix):
#     def yield_rows(in_matrix):
#         zero_row = [0 for x in in_matrix[0]]
#         for in_row in in_matrix:
#             yield zero_row
#             yield in_row
#     def yield_row_items(in_row):
#         for val in in_row:
#             yield 0
#             yield val
    
#     out_matrix = [[val for val in yield_row_items(in_row)] for in_row in yield_rows(in_matrix)]
#     return np.array(out_matrix, dtype=complex)


# def right_kron_identity_matrix(self, in_matrix):
#     def yield_rows(in_matrix):
#         for in_row in in_matrix:
#             yield in_row
#             yield in_row
#     def yield_row_items_1(in_row):
#         for val in in_row:
#             yield val
#             yield 0
#     def yield_row_items_2(in_row):
#         for val in in_row:
#             yield 0
#             yield val

#     out_matrix = [[val for val in yield_row_items_1(in_row)] if i % 2 == 0 else [val for val in yield_row_items_2(in_row)] for i, in_row in enumerate(yield_rows(in_matrix))]
#     return np.array(out_matrix, dtype=complex)