# **Elevator MDP Control System**

## **1. Project Overview**

This project implements a **Markov Decision Process (MDP)** to optimize the control logic of a single elevator in a 3-floor building. The objective is to find an **Optimal Policy ($\pi^*$)** that minimizes passenger wait time and energy consumption. The agent is trained using **Value Iteration** to navigate a stochastic environment where passenger requests appear randomly.

-----

## **2. MDP Formulation**

### **States ($S$)**

The state is represented as a compact tuple: `(e_floor, request_mask)`.

  * **e\_floor**: The current floor of the elevator $\in \{1, 2, 3\}$.
  * **request\_mask**: A 3-bit mask for pending requests on floors 1–3 (e.g., `(1, 0, 1)` means requests at floors 1 and 3).
  * **Total States**: 24 unique configurations.

### **Actions ($A$)**

The agent can choose from four actions: `{UP, DOWN, STAY, PICK}`.

  * **UP/DOWN**: Move one floor (subject to boundaries).
  * **STAY**: Remain at the current floor.
  * **PICK**: Serve a request at the current floor (clears the request).

### **Transition Model ($T$)**

  * **Movement**: Deterministic for the elevator position.
  * **Arrivals**: New requests appear independently at each floor with a probability of **0.1 per step**.

### **Reward Function ($R$)**

  * **Wait Penalty**: $-1.0$ per timestep for each pending request.
  * **Energy Cost**: $-0.5$ for every movement (`UP` or `DOWN`).
  * **Service Reward**: $+5.0$ for a successful pickup.

-----

## **3. Methodology: Value Iteration**

The system employs the **Value Iteration** algorithm to compute the optimal policy. The algorithm solves the **Bellman Optimality Equation**:

$$V^*(s) = \max_a \sum_{s'} P(s'|s,a) \left[ R(s,a,s') + \gamma V^*(s') \right]$$

### **Hyperparameters**

  * **Discount Factor ($\gamma = 0.9$)**: This ensures the agent prioritizes long-term efficiency while remaining responsive to immediate demands.
  * **Convergence Threshold ($\theta = 0.001$)**: The iteration continues until the maximum change in the value function across all states is negligible.

-----

## **4. Results and Analysis**

### **Visual Simulation**

The implementation features a high-fidelity **Pygame** interface. The simulation tracks:

  * **Step Rewards**: Net reward per action (e.g., **$+4.0$** represents a $+5.0$ pickup reward minus a $-1.0$ penalty for another pending request).
  * **Moving Tags**: Displays real-time status such as "Moving UP ↑" or "PICKING Passenger".
  * **Cumulative Reward**: The total sum of rewards over the episode.

### **Heuristic Comparison**

Testing confirmed that the **MDP Optimal Policy** consistently outperforms a standard "Nearest Request" heuristic.

  * **Average MDP Score**: \~176.1.
  * **Average Heuristic Score**: \~168.7.

-----

## **5. Installation and Execution**

### **Prerequisites**

  * Python 3.x
  * `numpy`, `pygame`

### **Setup**

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the simulation:
    ```bash
    python elevator_mdp.py
    ```

### **Controls**

  * **RESET**: Click the on-screen button to re-initialize the environment state.
  * **Simulation**: The AI runs automatically based on the pre-calculated policy.
