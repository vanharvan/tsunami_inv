import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import nnls

unit_sources = ['A1', 'A2', 'B1', 'B2']

# Load matrices
A = np.loadtxt("matrix_A_GF.csv", delimiter=",")
B = np.loadtxt("matrix_B_OBS.csv", delimiter=",")


#A = A.reshape(-1, 1)
#B = B.reshape(-1, 1)

print('#', "-" * 40, '#' )
print('     ', "Matrix A Dimension:", A.shape)
print('     ', "Matrix B Dimension:", B.shape)
print('#', "-" * 40, '#' )

assert A.shape[0] == B.shape[0], "A and B have incompatible dimensions!"

rank = np.linalg.matrix_rank(A)

print('     ', "Rank(A):", rank)
print('     ', "Number of columns:", A.shape[1])

cond_number = np.linalg.cond(A)
print("Condition Number of A:", cond_number)

# ----- manual inverse calculation ----- #

ATA = A.T @ A
ATB = A.T @ B

# check if inversion is possible
if np.abs(ATA[0,0]) < 1e-12:
    raise ValueError("Cannot invert because A^T A is zero.")

X = np.linalg.inv(ATA) @ ATB

print('#', "-" * 40, '#' )
print('     ', f"X (manual) = {X}")

# --------- least-square method --------- #
X, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

print('#', "-" * 40, '#' )
print('     ', f"X (Least-Square) = {X}")
print('     ', f"Residuals = {residuals}")

# --------- NNLS --------- #


print('#', "-" * 40, '#' )
X, residual = nnls(A, B)
print('     ', f"X (NNLS) = {X}")
print('     ', "Residual =", residual)
print('#', "-" * 40, '#' )

# --------- check fitting --------- #

unit_sources = unit_sources
with open("matrix_X_result.csv", "w") as f:
    f.write("Unit_Source,Slip\n")  # Column headers
    for source, slip in zip(unit_sources, X):
        f.write(f"{source},{slip:.8f}\n")

print('     ', "Successfully saved NNLS results to 'matrix_X_result.csv'")
print('#', "-" * 40, '#' )

# Create a mathematically perfect B directly from your A matrix
B_perfect = A @ np.array([1.0, 2.0, 3.0, 4.0])

# Run your least squares on this perfect data
X_test, _, _, _ = np.linalg.lstsq(A, B_perfect, rcond=None)
print("Sanity Check X:", X_test)
print('#', "-" * 40, '#' )
B_fit = A @ X

rmse = np.sqrt(np.mean((B - B_fit)**2))
print('     ',"RMSE =", rmse)                                       # 0 ~ almost no difference

corr = np.corrcoef(B.flatten(), B_fit.flatten())[0,1]
print('     ', "Correlation =", corr)                                # 1 ~ very similar

# --------- plot graph --------- #

# plot waveform fitting
import matplotlib.pyplot as plt
plt.figure(figsize=(10,4))
plt.plot(B, label="Observation")
plt.plot(B_fit, label="Inversion")
plt.legend()
plt.grid(True)
plt.show()

#
#plt.plot(5*A, label="Green function (1 m) * 5 ")
#plt.plot(B, label="Synthetic observation (5 m)")
#plt.legend()
#plt.show()

#
#plt.plot(B, label='5 m simulation')
#plt.plot(5*A, label='5 x 1 m simulation')
#plt.legend()
#plt.show()