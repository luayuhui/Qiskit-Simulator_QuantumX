# Single-Qubit Quantum Gate Simulator

A rigid, professional dark-themed desktop application interface built using **Python**, **Tkinter**, and **Qiskit** to simulate single-qubit quantum mechanics states on a high-DPI Bloch Sphere projection model.

## Interface Preview
![Simulator Dashboard](assets/user_interface.png)

## Core Features
* **Dynamic Matrix Calculation:** Calculates exact state probabilities for $|0\rangle$ and $|1\rangle$ based on statevector instructions.
* **High-DPI Vector Plot Viewport:** Implements Retina-display scaling configurations ($160\text{ DPI}$) for crisp coordinate geometries.
* **Physics Operator Analysis Panel:** Displays text-based raw quantum matrix shapes alongside rotation mechanics notes.
* **Export Matrices:** Features discrete, hardware-sterile options to export plots (`.png`) or output parameter reports to terminal logs.

## Quantum Physics & Operator Foundations
This simulator processes pure state spaces on the surface coordinates of a Bloch Sphere using the structural framework:

$$\left|\psi\right\rangle = \cos\left(\frac{\theta}{2}\right)\left|0\right\rangle + e^{i\phi}\sin\left(\frac{\theta}{2}\right)\left|1\right\rangle$$

### Supported Operational Transformations
* **Pauli-X (NOT):** Rotates the target vector $\pi$ radians ($180^\circ$) around the $X$-axis.
* **Pauli-Y:** Rotates the target vector $\pi$ radians around the $Y$-axis.
* **Pauli-Z (Phase Flip):** Inverts the relative phase sign via a $\pi$ radian rotation around the $Z$-axis.
* **Hadamard (H):** Rotates the space along the $X+Z$ diagonal axis to generate an equal coherent superposition state.
* **$R_Y(\theta)$:** Enables continuous geometric coordinate shifts via customizable radian float inputs.

## Setup & Running Environment
Ensure you are running Python 3.10+ on your workspace environment.

1. Install the required dependencies:
   ```bash
   pip install qiskit matplotlib numpy
