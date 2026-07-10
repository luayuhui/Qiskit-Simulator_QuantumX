import os
import sys
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import matplotlib
matplotlib.use('TkAgg')  # Forces Matplotlib to use a safer interface wrapper for macOS

# Import Qiskit components
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector

# Import Matplotlib backend for Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class QuantumSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Single-Qubit Quantum Gate Simulator - Yuhui (UTM)")
        self.root.geometry("1200x750") # Slightly wider layout for high-res rendering
        
        # --- Professional Rigid Color Palette ---
        self.bg_dark = "#0B0F19"       
        self.bg_card = "#161F30"       
        self.border_gray = "#2E3C54"   
        self.fg_white = "#F0F4F8"      
        self.fg_muted = "#A2B2C8"      
        self.accent_blue = "#60A5FA"   
        
        self.root.configure(bg=self.bg_dark)

        # Style configurations for dropdowns
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TCombobox", fieldbackground=self.bg_dark, background=self.border_gray, foreground="black")

        # Keep track of active components
        self.canvas = None
        self.current_fig = None
        self.latest_results_text = ""

        # --- Top Header Bar (Now displaying explicit credit to Yuhui) ---
        header_frame = tk.Frame(root, bg=self.bg_card, bd=1, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="QUANTUM SIMULATOR INTERFACE // DEVELOPED BY: YUHUI (MSc Physics, UTM)", 
                               font=("Helvetica", 12, "bold"), bg=self.bg_card, fg=self.fg_white)
        title_label.pack(side=tk.LEFT, padx=20, pady=14)

        # --- Main Workspace Splitter ---
        workspace = tk.Frame(root, bg=self.bg_dark)
        workspace.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Left Control Deck ---
        control_deck = tk.Frame(workspace, bg=self.bg_card, bd=1, relief=tk.SOLID, padx=18, pady=18)
        control_deck.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        tk.Label(control_deck, text="OPERATIONAL SETUP", font=("Helvetica", 10, "bold"), 
                 bg=self.bg_card, fg=self.accent_blue).pack(anchor=tk.W, pady=(0, 12))

        # Gate Selection Area
        tk.Label(control_deck, text="Select Target Quantum Gate:", font=("Helvetica", 10), 
                 bg=self.bg_card, fg=self.fg_white).pack(anchor=tk.W, pady=2)
        
        self.gate_var = tk.StringVar(value="X Gate")
        gates = ["X Gate", "Y Gate", "Z Gate", "Hadamard (H) Gate", "RY Gate (Rotation)"]
        self.gate_menu = ttk.Combobox(control_deck, textvariable=self.gate_var, values=gates, state="readonly", width=24)
        self.gate_menu.pack(anchor=tk.W, pady=(0, 12))
        self.gate_menu.bind("<<ComboboxSelected>>", self.on_gate_change)

        # RY Angle Input Frame
        self.angle_frame = tk.Frame(control_deck, bg=self.bg_card)
        tk.Label(self.angle_frame, text="Theta Angle (Radians):", font=("Helvetica", 10), bg=self.bg_card, fg=self.fg_white).pack(anchor=tk.W, pady=2)
        self.angle_entry = tk.Entry(self.angle_frame, width=26, bg=self.bg_dark, fg=self.fg_white, 
                                    insertbackground="white", bd=1, relief=tk.SOLID, font=("Helvetica", 10))
        self.angle_entry.insert(0, "1.5708")
        self.angle_entry.pack(fill=tk.X, pady=(0, 12))

        # Rigid Command Buttons Group
        tk.Label(control_deck, text="EXECUTION CONTROLS", font=("Helvetica", 10, "bold"), 
                 bg=self.bg_card, fg=self.accent_blue).pack(anchor=tk.W, pady=(5, 5))

        # 1. Run Button
        self.simulate_btn = tk.Button(control_deck, text="EXECUTE SIMULATION", bg=self.accent_blue, fg="black", 
                                      activebackground=self.fg_white, activeforeground=self.bg_dark,
                                      font=("Helvetica", 10, "bold"), command=self.run_simulation, 
                                      relief=tk.SOLID, bd=1, height=1, cursor="hand2")
        self.simulate_btn.pack(fill=tk.X, pady=4)

        # 2. Save Image Button
        self.save_btn = tk.Label(control_deck, text="EXPORT VECTOR PLOT (.PNG)", bg=self.bg_dark, fg=self.fg_white,
                                 font=("Helvetica", 9, "bold"), relief=tk.SOLID, bd=1, anchor=tk.CENTER, height=2, cursor="hand2")
        self.save_btn.pack(fill=tk.X, pady=4)
        self.save_btn.bind("<Button-1>", lambda e: self.save_bloch_sphere())

        # 3. Print Logs Button
        self.print_btn = tk.Label(control_deck, text="PRINT QUANTUM RAW DATA", bg=self.bg_dark, fg=self.fg_white,
                                  font=("Helvetica", 9, "bold"), relief=tk.SOLID, bd=1, anchor=tk.CENTER, height=2, cursor="hand2")
        self.print_btn.pack(fill=tk.X, pady=4)
        self.print_btn.bind("<Button-1>", lambda e: self.print_summary())

        # Output Results Log Box
        tk.Label(control_deck, text="PROBABILITY ANALYSIS MATRIX", font=("Helvetica", 10, "bold"), 
                 bg=self.bg_card, fg=self.accent_blue).pack(anchor=tk.W, pady=(15, 5))
        self.result_text = tk.Text(control_deck, width=32, height=9, font=("Courier New", 10), 
                                   bg=self.bg_dark, fg=self.fg_white, insertbackground="white", bd=1, relief=tk.SOLID)
        self.result_text.pack(anchor=tk.W, pady=(0, 12))

        # Mathematical Operator Properties Panel
        tk.Label(control_deck, text="OPERATOR TRANSFORM DETAILS", font=("Helvetica", 10, "bold"), 
                 bg=self.bg_card, fg=self.accent_blue).pack(anchor=tk.W, pady=(5, 5))
        self.info_text = tk.Text(control_deck, width=32, height=9, font=("Courier New", 10), 
                                 bg=self.bg_dark, fg=self.fg_muted, wrap=tk.WORD, bd=1, relief=tk.SOLID)
        self.info_text.pack(anchor=tk.W)

        # --- Right Technical Visualization Viewport ---
        self.visual_frame = ttk.LabelFrame(workspace, text=" VECTOR VISUALIZATION VIEWPORT (BLOCH SPHERE MODEL) ", padding=15)
        self.visual_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- Bottom Academic Footer ---
        footer_frame = tk.Frame(root, bg=self.bg_card, bd=1, relief=tk.SOLID)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        credits_label = tk.Label(footer_frame, text="RESEARCH METRICS CONSOLE // AUTHOR: YUHUI // MSC PHYSICS // UNIVERSITI TEKNOLOGI MALAYSIA (UTM)", 
                                 font=("Courier New", 9, "bold"), bg=self.bg_card, fg=self.fg_muted)
        credits_label.pack(pady=8)
        
        self.on_gate_change()

    def on_gate_change(self, event=None):
        self.toggle_angle_input()
        self.update_physics_info()
        self.run_simulation()

    def toggle_angle_input(self, event=None):
        if self.gate_var.get().startswith("RY"):
            self.angle_frame.pack(anchor=tk.W, fill=tk.X)
        else:
            self.angle_frame.pack_forget()

    def update_physics_info(self):
        gate = self.gate_var.get()
        self.info_text.delete("1.0", tk.END)
        
        if gate == "X Gate":
            info = (
                "Operator: Pauli-X\n"
                "Matrix Form:\n  [ 0  1 ]\n  [ 1  0 ]\n\n"
                "Geometric Dynamics:\n"
                "Forces a Pi rad (180 deg)\n rotation around X-axis.\n"
                "Maps |0> -> |1> & |1> -> |0>."
            )
        elif gate == "Y Gate":
            info = (
                "Operator: Pauli-Y\n"
                "Matrix Form:\n  [ 0 -i ]\n  [ i  0 ]\n\n"
                "Geometric Dynamics:\n"
                "Forces a Pi rad (180 deg)\n rotation around Y-axis."
            )
        elif gate == "Z Gate":
            info = (
                "Operator: Pauli-Z\n"
                "Matrix Form:\n  [ 1  0 ]\n  [ 0 -1 ]\n\n"
                "Geometric Dynamics:\n"
                "Forces a Pi rad (180 deg)\n rotation around Z-axis.\n"
                "Flips the relative phase sign."
            )
        elif gate == "Hadamard (H) Gate":
            info = (
                "Operator: Hadamard (H)\n"
                "Matrix Form:\n  1/sqrt(2) * [ 1  1 ]\n              [ 1 -1 ]\n\n"
                "Geometric Dynamics:\n"
                "Rotates state space along\n X+Z diagonal vector.\n"
                "Generates coherent equal\n superposition states."
            )
        elif gate == "RY Gate (Rotation)":
            info = (
                "Operator: Ry(theta)\n"
                "Matrix Form:\n  [ cos(t/2) -sin(t/2) ]\n  [ sin(t/2)  cos(t/2) ]\n\n"
                "Geometric Dynamics:\n"
                "Continuous state shifts\n around the Y-axis path via\n custom variable input."
            )
        self.info_text.insert(tk.END, info)

    def run_simulation(self):
        qc = QuantumCircuit(1)
        gate = self.gate_var.get()

        if gate == "X Gate":
            qc.x(0)
        elif gate == "Y Gate":
            qc.y(0)
        elif gate == "Z Gate":
            qc.z(0)
        elif gate == "Hadamard (H) Gate":
            qc.h(0)
        elif gate == "RY Gate (Rotation)":
            try:
                theta = float(self.angle_entry.get())
                qc.ry(theta, 0)
            except ValueError:
                return 

        state = Statevector.from_instruction(qc)
        probs = state.probabilities_dict()
        prob_0 = probs.get('0', 0.0) * 100
        prob_1 = probs.get('1', 0.0) * 100

        self.result_text.delete("1.0", tk.END)
        summary = (
            f"Active Operator: {gate.upper()}\n"
            f"{'='*28}\n"
            f"SCHEMATIC MATRIX ARRAY:\n{qc.draw(output='text')}\n"
            f"{'='*28}\n"
            f"State Density |0>: {prob_0:.2f}%\n"
            f"State Density |1>: {prob_1:.2f}%\n"
        )
        self.latest_results_text = summary
        self.result_text.insert(tk.END, summary)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Temporarily shift global matplotlib text rendering properties to force white color
        plt.rcParams['text.color'] = '#F0F4F8'
        plt.rcParams['axes.labelcolor'] = '#F0F4F8'

        # Generate the figure from Qiskit
        self.current_fig = plot_bloch_multivector(state)
        
        # --- RETINA DISPLAY CORRECTION ---
        self.current_fig.set_dpi(160)
        
        self.current_fig.patch.set_facecolor(self.bg_card)
        for ax in self.current_fig.axes:
            ax.set_facecolor(self.bg_card)
            ax.set_title("") 
            ax.xaxis.label.set_color('#F0F4F8')
            ax.yaxis.label.set_color('#F0F4F8')
            
        # Restore default matplotlib settings for environmental stability
        plt.rcParams.update(plt.rcParamsDefault)
        
        self.canvas = FigureCanvasTkAgg(self.current_fig, master=self.visual_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(self.current_fig)

    def save_bloch_sphere(self):
        if self.current_fig is not None:
            file_path = filedialog.asksaveasfilename(
                initialdir=os.path.expanduser("~"),
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")],
                title="Save Vector Plot Data As..."
            )
            if file_path:
                try:
                    self.current_fig.savefig(file_path, dpi=300, facecolor=self.current_fig.get_facecolor(), edgecolor='none')
                    messagebox.showinfo("Success", f"Plot data exported cleanly to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Export Exception", f"Failed to complete save array structure.\nDetails: {str(e)}")
        else:
            messagebox.showwarning("Execution Warning", "Cannot export blank dashboard layers.")

    def print_summary(self):
        if self.latest_results_text:
            print("\n" + "="*50)
            print("       QUANTUM MEASUREMENT CONSOLE EXPORT      ")
            print("="*50)
            print(f"METADATA LOG RECORD // AUTHOR: YUHUI // UTM PHYSICS")
            print(f"{self.latest_results_text}")
            print("="*50 + "\n")
            messagebox.showinfo("Hardware Data Matrix Sent", "Quantum data report has been successfully outputted to the console log terminal.")
        else:
            messagebox.showwarning("Buffer Underflow", "No computational parameters currently logged to database storage.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumSimulatorGUI(root)
    root.mainloop()