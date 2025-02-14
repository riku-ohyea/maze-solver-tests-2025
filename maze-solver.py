import time

# Constants
MAZE_SIZE = 9
WALL = 1
OPEN = 0
VISITED = 2
ROBOT = 3

# Directions
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# Robot movements
MOVES = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # North, East, South, West

# Initialize maze (9x9 grid with walls)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Robot state
robot_pos = (1, 1)  # Starting position
robot_dir = EAST  # Starting direction

# Flood fill distance grid
distance = [[0 for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]


def print_maze():
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            if (x, y) == robot_pos:
                print("R", end=" ")  # Robot position
            elif maze[y][x] == WALL:
                print("#", end=" ")  # Wall
            elif maze[y][x] == VISITED:
                print(".", end=" ")  # Visited
            else:
                print(" ", end=" ")  # Open space
        print()
    print()


def detect_walls(x, y, direction):
    walls = [False, False, False]  # Front, Left, Right

    # Check front wall
    nx, ny = x + MOVES[direction][0], y + MOVES[direction][1]
    if nx < 0 or nx >= MAZE_SIZE or ny < 0 or ny >= MAZE_SIZE or maze[ny][nx] == WALL:
        walls[0] = True

    # Check left wall
    left_dir = (direction - 1) % 4
    nx, ny = x + MOVES[left_dir][0], y + MOVES[left_dir][1]
    if nx < 0 or nx >= MAZE_SIZE or ny < 0 or ny >= MAZE_SIZE or maze[ny][nx] == WALL:
        walls[1] = True

    # Check right wall
    right_dir = (direction + 1) % 4
    nx, ny = x + MOVES[right_dir][0], y + MOVES[right_dir][1]
    if nx < 0 or nx >= MAZE_SIZE or ny < 0 or ny >= MAZE_SIZE or maze[ny][nx] == WALL:
        walls[2] = True

    return walls


def update_flood_fill():
    # Reset distance grid
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            if maze[y][x] == WALL:
                distance[y][x] = -1  # Walls are unreachable
            else:
                distance[y][x] = float('inf')  # Initialize to infinity

    # Start from the goal (center of the maze)
    goal = (MAZE_SIZE // 2, MAZE_SIZE // 2)
    queue = [goal]
    distance[goal[1]][goal[0]] = 0

    # Perform BFS to calculate distances
    while queue:
        x, y = queue.pop(0)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
                if distance[ny][nx] == float('inf'):
                    distance[ny][nx] = distance[y][x] + 1
                    queue.append((nx, ny))


def choose_next_move(x, y):
    min_dist = float('inf')
    best_move = None

    for i, (dx, dy) in enumerate(MOVES):
        nx, ny = x + dx, y + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            if distance[ny][nx] < min_dist and maze[ny][nx] != WALL:
                min_dist = distance[ny][nx]
                best_move = i

    return best_move


def move_robot():
    global robot_pos, robot_dir

    x, y = robot_pos
    walls = detect_walls(x, y, robot_dir)

    # Update maze with detected walls
    if walls[0]:  # Front wall
        nx, ny = x + MOVES[robot_dir][0], y + MOVES[robot_dir][1]
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            maze[ny][nx] = WALL
    if walls[1]:  # Left wall
        left_dir = (robot_dir - 1) % 4
        nx, ny = x + MOVES[left_dir][0], y + MOVES[left_dir][1]
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            maze[ny][nx] = WALL
    if walls[2]:  # Right wall
        right_dir = (robot_dir + 1) % 4
        nx, ny = x + MOVES[right_dir][0], y + MOVES[right_dir][1]
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            maze[ny][nx] = WALL

    # Update flood fill distances
    update_flood_fill()

    # Choose next move
    next_move = choose_next_move(x, y)
    if next_move is not None:
        # Turn robot if necessary
        if next_move != robot_dir:
            turn_direction = (next_move - robot_dir) % 4
            if turn_direction == 1:
                print("Turning right")
            elif turn_direction == 3:
                print("Turning left")
            robot_dir = next_move

        # Move forward
        dx, dy = MOVES[robot_dir]
        nx, ny = x + dx, y + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE and maze[ny][nx] != WALL:
            robot_pos = (nx, ny)
            maze[ny][nx] = VISITED
            print(f"Moving to ({nx}, {ny})")
        else:
            print("Cannot move forward")
    else:
        print("No valid moves")


# Main simulation loop
while True:
    print_maze()
    move_robot()
    time.sleep(1)  # Pause for 1 second between frames