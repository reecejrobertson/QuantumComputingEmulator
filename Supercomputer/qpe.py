import sys
sys.path.append('/fslhome/reecejr/software/QuantumComputingEmulator') # Change this to match your installation location.
sys.path.append('/fslhome/reecejr/software/intel-qs/build/lib') # Change this to match your installation location.
import intelqs_py as simulator
import emulator
import numpy as np
import time
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

# Define the number of times to repeat each following experiment.
M = 10

# Define the number of qubits to simulate for each experiment.
min_qubit = 2
max_qubit = 20

# Define the function that we will use to fit the curves.
def curve(x, a, b):
    return a * (2 ** (b * x))

# ---------------------------------------------------------------------------- #
#                                      QPE                                     #
# ---------------------------------------------------------------------------- #

# Define a matrix (U) and an eigenvector.
z = np.random.uniform(0, 1)
U = np.array([[1, 0], [0, np.exp(1j*z)]])
phi = np.array([0, 1])

# Define the z-rotations needed for the simulation method.
Z = []
for n in range(1, max_qubit):
   Z.append(np.array([[1, 0], [0, np.exp(-1j*np.pi/2**n)]], dtype=complex))

# Create a list of various numbers of qubits <= max_qubit to simulate.
num_qubits = np.arange(min_qubit, max_qubit+1, 2)

# Define a list to hold the emulator and simulator times respectively.
em_times = []
sim_times = []

# For each iteration of the experiment:
for m in range(1, M+1):
    
    print('m = ' + str(m) + '...', end='')

    # Define arrays to hold the results of this iteration (batch).
    em_batch = []
    sim_batch = []

    # For each number of qubits:
    for n in num_qubits:
        
        # Initialize the simulator to the 0 state.
        psi = simulator.QubitRegister(n+1, 'base', 0, 0)
        
        # Extract the simulator state to pass it into the emulator.
        state = []
        for i in range(2**n):
            state.append(psi[i])
        state = np.array(state, dtype=complex)
        
        # Perform the QPE with the emulator and time how long it takes.
        start_time = time.time()
        em_state = emulator.qpe(U, phi, n)
        em_batch.append(time.time() - start_time)

        # Perform the QPE with the simulator and time how long it takes.
        start_time = time.time()
        for i in range(n):
            psi.ApplyHadamard(i)
        psi.ApplyPauliX(n)
        for i in range(0, n):
            for j in range(2**i):
                psi.ApplyControlled1QubitGate(i, n, U)
        for i in range(n//2):
            psi.ApplySwap(i, n-i-1)
        for j in range(n):
            for m in range(j):
                psi.ApplyControlled1QubitGate(m, j, Z[j-m-1])
            psi.ApplyHadamard(j)
        for i in range(n):
            prob = psi.GetProbability(i)
            if prob < 0.5:
                psi.CollapseQubit(i, False)
            else:
                psi.CollapseQubit(i, True)
        sim_batch.append(time.time() - start_time)
        
        # Extract the resultant state from the simulator.
        sim_state = []
        for i in range(2**n, 2**(n+1)):
            sim_state.append(psi[i])
        sim_state = np.array(sim_state, dtype=complex)
        
        # Ensure that the final states of the emulator and simulator agree.
        if not np.allclose(np.nonzero(sim_state), np.nonzero(em_state)):
            print('Output differed for ' + str(n) + ' qubits.')
            print(sim_state)
            print(em_state)
            print()
        
    # Append the batch results to the main array.     
    em_times.append(em_batch)
    sim_times.append(sim_batch)
    
    print('Done')

print('----------')

# Average the times over each batch.
em_array = np.array(em_times)
sim_array = np.array(sim_times)
em_array = np.sum(em_times, axis=0)/m
sim_array = np.sum(sim_times, axis=0)/m

# Record the raw data.
print("Emulator data:", em_array)
print("Simulator data:", sim_array)
print('----------')

# Plot the times for each QPE operation.
ticks = np.arange(2, max_qubit + 1, 2)
fig = plt.figure()
plt.plot(num_qubits, em_array, 'o-k', label='Emulator')   
plt.plot(num_qubits, sim_array, 'o-r', label='Simulator')
plt.xticks(ticks)
plt.xlabel('Number of Qubits')
plt.ylabel('Time (seconds)')
plt.legend(loc='best')
plt.savefig('Plots/qpe.png', dpi=600)

# Fit a curve to the data.
em_params = curve_fit(f=curve, xdata=num_qubits, ydata=em_array, p0=[1, 1], bounds=(-np.inf, np.inf))[0]
sim_params = curve_fit(f=curve, xdata=num_qubits, ydata=sim_array, p0=[1, 1], bounds=(-np.inf, np.inf))[0]

# Record the parameters of the fit curve.
print('Parameters for emulator curve:', em_params)
print('Parameters for simulator curve:', sim_params)

# Plot the raw data points and the fit curve.
domain = np.linspace(min_qubit, max_qubit, 1000)
fig = plt.figure()
plt.plot(num_qubits, em_array, 'ok', label='Emulator Data')
plt.plot(domain, curve(domain, em_params[0], em_params[1]), 'k', label='Emulator Fit Curve')
plt.plot(num_qubits, sim_array, 'or', label='Simulator Data')
plt.plot(domain, curve(domain, sim_params[0], sim_params[1]), 'r', label='Simulator Fit Curve')
plt.xticks(ticks)
plt.xlabel('Number of Qubits')
plt.ylabel('Time (seconds)')
plt.legend(loc='best')
plt.savefig('Plots/qpe_fit.png', dpi=600)