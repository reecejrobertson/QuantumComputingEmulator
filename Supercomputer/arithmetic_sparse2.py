import sys
sys.path.append('/fslhome/reecejr/software/QuantumComputingEmulator') # Change this to match your installation location.
sys.path.append('/fslhome/reecejr/software/intel-qs/build/lib') # Change this to match your installation location.
import intelqs_py as simulator
import emulator
import numpy as np
import scipy.sparse as sp
import time
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

# Define the number of times to repeat each following experiment.
M = 10

# Define the number of qubits to simulate for each experiment.
min_qubit = 5
max_qubit = 21

# Define the function that we will use to fit the curves.
def curve(x, a, b):
    return a * (2 ** (b * x))

# ---------------------------------------------------------------------------- #
#                            Arithmetic Sparse                                 #
# ---------------------------------------------------------------------------- #

# Set the number of states for each simulation.
S = 30

# Create a list of various numbers of qubits <= N to simulate.
num_qubits = np.arange(min_qubit, max_qubit+1, 2)

# Define a list to hold the times of each operation.
add_times = []
mult_times = []
exp_times = []

# For each iteration of the experiment:
for m in range(1, M+1):
    
    print('m = ' + str(m) + '...', end='')
    
    # Define arrays to hold the results of this iteration (batch).
    add_batch = []
    mult_batch = []
    exp_batch = []

    # For each number of states:
    for n in num_qubits:

        # Define a random initial state.
        numbers = np.arange(0, 2**n, 1)
        a = sp.dok_matrix((2**n, 1), dtype=complex)
        b = sp.dok_matrix((2**n, 1), dtype=complex)
        a_val = np.random.uniform(0, 1, S).astype(complex)
        b_val = np.random.uniform(0, 1, S).astype(complex)
        a_ind = np.random.choice(numbers, S, False)
        b_ind = np.random.choice(numbers, S, False)
        a[a_ind] = a_val
        b[b_ind] = b_val

        # Perform the addition with the emulator and time how long it takes.
        start_time = time.time()
        emulator.add_sparse(a, b)
        add_batch.append(time.time() - start_time)

        # Perform the multiplication with the emulator and time how long it takes.
        start_time = time.time()
        emulator.multiply_sparse(a, b)
        mult_batch.append(time.time() - start_time)

        # Perform the exponentiation with the emulator and time how long it takes.
        start_time = time.time()
        emulator.exponentiate_sparse(a, b)
        exp_batch.append(time.time() - start_time)

    # Append the batch results to the main array.
    add_times.append(add_batch)
    mult_times.append(mult_batch)
    exp_times.append(exp_batch)
    
    print('Done')

print('----------')

# Average the times over each batch to get the average time for each operation.
add_array = np.array(add_times)
mult_array = np.array(mult_times)
exp_array = np.array(exp_times)
add_array = np.sum(add_times, axis=0)/m
mult_array = np.sum(mult_times, axis=0)/m
exp_array = np.sum(exp_times, axis=0)/m

# Record the raw data.
print("Addition data:", add_array)
print("Multiplication data:", mult_array)
print("Exponentiation data:", exp_array)
print('----------')

# Plot the times for each operation.
fig = plt.figure()
plt.plot(num_qubits, add_array, 'o-b', label='Addition')
plt.plot(num_qubits, mult_array, 'o-g', label='Multiplication')
plt.plot(num_qubits, exp_array, 'o-c', label='Exponentiation')
plt.xticks(np.arange(min_qubit, max_qubit+1, 2))
plt.xlabel('Number of Qubits in State Vector')
plt.ylabel('Time (seconds)')
plt.legend(loc='best')
plt.savefig('Plots/arithmetic_sparse2.png', dpi=600)

# Fit a curve to the data.
add_params = curve_fit(f=curve, xdata=num_qubits, ydata=add_array, p0=[1, 1], bounds=(-np.inf, np.inf))[0]
mult_params = curve_fit(f=curve, xdata=num_qubits, ydata=mult_array, p0=[1, 1], bounds=(-np.inf, np.inf))[0]
exp_params = curve_fit(f=curve, xdata=num_qubits, ydata=exp_array, p0=[1, 1], bounds=(-np.inf, np.inf))[0]

# Record the parameters of the fit curve.
print('Parameters for addition curve:', add_params)
print('Parameters for multiplication curve:', mult_params)
print('Parameters for exponentiation curve:', exp_params)

# Plot the times for each operation on a log plot.
domain = np.linspace(min_qubit, max_qubit, 1000)
fig = plt.figure()
plt.plot(num_qubits, add_array, 'ob', label='Addition Data')
plt.plot(domain, curve(domain, add_params[0], add_params[1]), 'b', label='Addition Fit Curve')
plt.plot(num_qubits, mult_array, 'og', label='Multiplication Data')
plt.plot(domain, curve(domain, mult_params[0], mult_params[1]), 'g', label='Multiplication Fit Curve')
plt.plot(num_qubits, exp_array, 'oc', label='Exponentiation Data')
plt.plot(domain, curve(domain, exp_params[0], exp_params[1]), 'c', label='Exponentiation Fit Curve')
plt.xticks(np.arange(min_qubit, max_qubit+1, 2))
plt.xlabel('Number of Qubits in State Vector')
plt.ylabel('Time (seconds)')
plt.legend(loc='best')
plt.savefig('Plots/arithmetic_sparse_fit2.png', dpi=600)
