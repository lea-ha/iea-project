# Shapeshifter - Multi-Agent Pathfinding Visualization

## Overview
Shapeshifter is a visualization tool for multi-agent pathfinding algorithms. It demonstrates how multiple agents can navigate from their starting positions to designated destinations while being fast and avoiding collisions.

## Architecture
The project uses a client-server architecture:
- **Frontend**: Python with Pygame for visualization
- **Backend**: Java for pathfinding algorithms

## Backend (Java)
The Java backend implements several key algorithms:
- **CBS (Conflict-Based Search)**: A multi-agent pathfinding algorithm that prioritizes and resolves conflicts between agents
- **A* Algorithm**: Used for single-agent path planning
- **Hungarian Algorithm**: Optimally assigns agents to destinations

## Frontend (Python)
The Python frontend visualizes the paths calculated by the backend:
- Interactive grid-based display
- Animated movement of agents
- Statistics tracking
- Pause/resume functionality
- Destination selection interface

## Running the Application

### Step 1: Start the Backend
Navigate to the Java project directory and run:
```
cd src/main/java/api
java -jar main.jar
```
This will start the backend server that calculates optimal paths.

### Step 2: Start the Frontend
In a separate terminal, navigate to the Python project directory and run:
```
python main.py
```

### Step 3: Using the Application
1. The destination selector will appear first
2. Click on grid cells to select destinations for your agents
3. Click the "Start Simulation" button when ready
4. Watch the agents navigate to their destinations
5. Use the pause button to pause/resume the simulation

## Requirements
- Python with Pygame
- Java 
- Network connection between frontend and backend (localhost)