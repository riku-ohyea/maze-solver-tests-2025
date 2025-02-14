import numpy as np
import matplotlib.pyplot as plt
import time

# Maze size
MAZE_SIZE = 9

# Directions: 0=North, 1=East, 2=South, 3=West
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# Initialize maze with walls (1 = wall, 0 = open)
maze = np.zeros((MAZE_SIZE, MAZE_SIZE), dtype=int)

# Goal is the center of the maze
goal = (MAZE_SIZE // 2, MAZE_SIZE // 2)

# Robot's initial position and direction
robot_pos = (0, 0)
robot_dir = 1  # Facing East

# Flood fill distances
distances = np.zeros((MAZE_SIZE, MAZE_SIZE), dtype=int)

# Function to check if a cell is valid
def is_valid(x, y):
    return 0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE

# Function to detect walls around the robot
def detect_walls(x, y):
    walls = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if not is_valid(nx, ny) or maze[ny][nx] == 1:
            walls.append(True)
        else:
            walls.append(False)
    return walls

# Function to update the flood fill distances
def update_flood_fill():
    global distances
    queue = [goal]
    distances = np.full((MAZE_SIZE, MAZE_SIZE), -1, dtype=int)
    distances[goal[1]][goal[0]] = 0

    while queue:
        x, y = queue.pop(0)
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and distances[ny][nx] == -1 and maze[ny][nx] == 0:
                distances[ny][nx] = distances[y][x] + 1
                queue.append((nx, ny))

# Function to move the robot
def move_robot():
    global robot_pos, robot_dir

    x, y = robot_pos
    walls = detect_walls(x, y)

    # Update flood fill distances
    update_flood_fill()

    # Find the direction with the smallest distance
    min_dist = float('inf')
    best_dir = robot_dir
    for i in range(4):
        dx, dy = DIRECTIONS[i]
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny) and not walls[i] and distances[ny][nx] < min_dist:
            min_dist = distances[ny][nx]
            best_dir = i

    # Turn the robot to the best direction
    if best_dir != robot_dir:
        print(f"Turning from {robot_dir} to {best_dir}")
        robot_dir = best_dir

    # Move the robot
    dx, dy = DIRECTIONS[robot_dir]
    nx, ny = x + dx, y + dy
    if is_valid(nx, ny) and not walls[robot_dir]:
        robot_pos = (nx, ny)
        print(f"Moving to {robot_pos}")

# Function to visualize the maze and robot
def visualize_maze():
    plt.clf()
    plt.imshow(maze, cmap='binary', origin='lower')
    plt.plot(robot_pos[0], robot_pos[1], 'ro', markersize=10)  # Robot position
    plt.plot(goal[0], goal[1], 'go', markersize=10)  # Goal position
    plt.title("Micromouse Simulation")
    plt.pause(0.5)

# Main simulation loop
def simulate():
    while robot_pos != goal:
        visualize_maze()
        move_robot()
        time.sleep(1)  # Pause to see the frame-by-frame movement
    visualize_maze()
    print("Goal reached!")

# Example maze (1 = wall, 0 = open)
maze = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
])

# Start simulation
simulate()