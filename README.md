# **Project Report: Elevator MDP Control System**

## **1. Problem Overview**
This project implements a **Markov Decision Process (MDP)** to optimize the control logic of a single elevator operating in a 3-floor building. The primary objective is to develop an **Optimal Policy ($\pi^*$)** that effectively balances two competing goals:
1.  **Minimizing Passenger Wait Time:** Penalizing the system for every timestep a request remains unfulfilled.
2.  **Operational Efficiency:** Minimizing energy consumption associated with vertical movement.

## **2. MDP Formulation**
The environment is modeled as a discrete-time, stochastic system with the following components:

### **States ($S$)**
A factored state representation is used: `(e_floor, request_mask)`.
* **Elevator Position ($e\_floor$):** $\in \{1, 2, 3\}$.
* **Request Mask:** A 3-bit binary tuple where each bit represents a pending request at a specific floor (e.g., `(1, 0, 1)` indicates requests at Floors 1 and 3).
* **Total State Space:** 24 unique configurations ($3 \text{ floors} \times 2^3 \text{ request permutations}$).

### **Actions ($A$)**
The agent chooses from four possible actions at each step:
* `UP` / `DOWN`: Move one floor (subject to boundary constraints).
* `STAY`: Remain at the current floor.
* `PICK`: Attempt to clear a request at the current floor.

### **Transition Model ($P$ or $T$)**
* **Deterministic Movement:** The elevator’s vertical transitions follow standard physics (e.g., `UP` from Floor 1 always results in Floor 2).
* **Stochastic Arrivals:** New passenger requests appear independently at each floor with a probability of **$0.1$ per step**.

### **Reward Function ($R$)**
The agent is trained using a multi-objective reward structure:
* **Service Reward:** $+5.0$ for a successful `PICK` action.
* **Energy Cost:** $-0.5$ for any `UP` or `DOWN` movement.
* **Invalid Action:** $-0.5$ for attempting to `PICK` at a floor without a request.
* **Wait Penalty:** $-1.0$ for **each** pending request currently in the system.

---

## **3. Methodology: Value Iteration**


The system employs the **Value Iteration** algorithm to compute the optimal policy. The algorithm solves the **Bellman Optimality Equation**:

$$V^*(s) = \max_a \sum_{s'} P(s'|s,a) [ R(s,a,s') + \gamma V^*(s') ]$$

### **Hyperparameters:**
* **Discount Factor ($\gamma = 0.9$):** This value ensures the agent prioritizes long-term efficiency while remaining responsive to immediate demands.
* **Convergence Threshold ($\theta = 0.001$):** The iteration continues until the maximum change in the value function across all states is negligible.

---

## **4. Implementation Highlights**
The implementation features a high-fidelity visual interface built with **Pygame**:
* **Real-time HUD:** Displays current actions (e.g., "Moving UP ↑"), the immediate **Step Reward**, and the total **Cumulative Reward**.
* **Net Reward Display:** The interface correctly displays the "Net Step Reward." For example, a pickup might display as **$+4.0$** (representing the $+5.0$ pickup reward minus a $-1.0$ penalty for another pending request).
* **Visual Feedback:** Floors are clearly labeled, passengers appear as red icons, and the elevator's vertical position is updated dynamically.
* **Manual Reset:** Includes a "RESET" button to re-initialize the environment for testing different scenarios.

---

## **5. Analysis of Results**
The simulation demonstrates that the MDP agent consistently identifies the most efficient path to maximize global rewards.
1.  **Strategic Anticipation:** Because wait penalties accumulate for *every* pending request, the agent learns to clear clusters of requests to stop the rapid depletion of points.
2.  **Balancing Costs:** When only one distant request exists, the agent calculates if the movement cost of $-1.0$ (two floors) is justified by the eventual $+5.0$ reward, consistently choosing movement over idleness due to the ongoing wait penalties.
3.  **Correctness:** Behavioral tests confirm the agent avoids "illegal" moves (like going UP from Floor 3) and only executes `PICK` when the state mask confirms a passenger presence.

---

## **6. Conclusion**
The implemented system fulfills all requirements of the project. By utilizing a model-based RL approach, the elevator demonstrates intelligence in a stochastic environment, proving that exact mathematical optimization (Value Iteration) is superior to basic rule-based heuristics for resource management.


## 🚀 How to Install and Run

### **Prerequisites**
Ensure you have Python 3.x installed. You will also need the following libraries:
- `numpy` (for matrix and state management)
- `pygame` (for the graphical simulation)

### **Installation**
1. Clone this repository or download the files.
2. Open your terminal in the project folder.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
