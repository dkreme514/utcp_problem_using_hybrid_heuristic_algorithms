# University Course Timetabling (NP-Hard Optimization)

This project implements a hybrid algorithmic approach to solving the University Course Timetabling Problem (UCTP), a classical NP-hard combinatorial optimization problem.

## 🔍 Overview
The goal is to assign courses to time slots and rooms while satisfying hard constraints (e.g., no instructor conflicts, room capacity) and minimizing soft constraint violations (e.g., schedule compactness).

The problem is modeled as a combination of:
- Graph Coloring (conflict resolution)
- Bin Packing (room assignment)

## ⚙️ Approach
This project explores multiple algorithms:
- **DSATUR (baseline graph coloring heuristic)**
- **Simulated Annealing (probabilistic local search)**
- **Genetic Algorithm (population-based optimization)**

### ⭐ Key Contribution: Hybrid Algorithm
A custom hybrid method that combines:
- DSATUR initialization
- Local search refinement
- Adaptive penalty functions for constraint handling
- Priority-based scheduling of high-conflict courses

## 📐 Mathematical Modeling
- Integer Linear Programming (ILP) formulation
- Linear Programming relaxation used to compute an **a-posteriori lower bound**

## 📊 Results
The hybrid algorithm:
- Eliminates hard constraint violations
- Reduces scheduling cost by up to **65% vs baseline**
- Achieves solutions within ~26% of the LP lower bound

## 🧪 Tech Stack
- Python
- NumPy / Pandas
- OR-Tools / PuLP (LP solver)

## 📁 Repository Structure
