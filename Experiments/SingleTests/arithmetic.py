import sys
sys.path.append('/fslhome/reecejr/software/QuantumComputingEmulator') # Change this to match your installation location.
sys.path.append('/fslhome/reecejr/software/intel-qs/build/lib') # Change this to match your installation location.
import intelqs_py as simulator
import emulator
import numpy as np
import time
from matplotlib import pyplot as plt

# Define the number of times to repeat each following experiment.
M = 10

# Define the number of qubits to simulate for each experiment.
N_ARITHMETIC = 3

# ---------------------------------------------------------------------------- #
#                                  Arithmetic                                  #
# ---------------------------------------------------------------------------- #

# Set the maximum number of qubits to simulate.
N = N_ARITHMETIC

# Create a list of various numbers of qubits <= N to simulate.
num_qubits = np.arange(1, N+1, 1)

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

    # For each number of qubits:
    for n in num_qubits:

        # Define a random initial state.
        a = np.random.uniform(0, 1, 2**n).astype(complex)
        b = np.random.uniform(0, 1, 2**n).astype(complex)

        # Perform the addition with the emulator and time how long it takes.
        start_time = time.time()
        emulator.add(a, b)
        add_batch.append(time.time() - start_time)

        # Perform the multiplication with the emulator and time how long it takes.
        start_time = time.time()
        emulator.multiply(a, b)
        mult_batch.append(time.time() - start_time)

        # Perform the exponentiation with the emulator and time how long it takes.
        start_time = time.time()
        emulator.exponentiate(a, b)
        exp_batch.append(time.time() - start_time)

    # Append the batch results to the main array.
    add_times.append(add_batch)
    mult_times.append(mult_batch)
    exp_times.append(exp_batch)
    
    print('Done')

    # Average the times over each batch to get the average time for each operation.
    add_array = np.array(add_times)
    mult_array = np.array(mult_times)
    exp_array = np.array(exp_times)
    add_array = np.sum(add_times, axis=0)/m
    mult_array = np.sum(mult_times, axis=0)/m
    exp_array = np.sum(exp_times, axis=0)/m

    # Plot the times for each operation.
    fig = plt.figure()
    plt.plot(num_qubits, add_array, 'o-b', label='Addition')
    plt.plot(num_qubits, mult_array, 'o-g', label='Multiplication')
    plt.plot(num_qubits, exp_array, 'o-c', label='Exponentiation')
    plt.xticks(np.arange(1, N+1, 1))
    plt.xlabel('Number of Qubits')
    plt.ylabel('Time (seconds)')
    plt.legend(loc='best')
    plt.savefig('Plots/arithmetic.png', dpi=600)

    # Plot the times for each operation on a log plot.
    fig = plt.figure()
    plt.semilogy(num_qubits, add_array, 'o-b', label='Addition')
    plt.semilogy(num_qubits, mult_array, 'o-g', label='Multiplication')
    plt.semilogy(num_qubits, exp_array, 'o-c', label='Exponentiation')
    plt.xticks(np.arange(1, N+1, 1))
    plt.xlabel('Number of Qubits')
    plt.ylabel('Time (seconds)')
    plt.legend(loc='best')
    plt.savefig('Plots/arithmetic_log.png', dpi=600)
