import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow
import time
from enum import Enum

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class MicroMouse:
    def __init__(self, maze_size=9):
        self.maze_size = maze_size
        self.position = [0, 0]  # Start at bottom-left corner
        self.direction = Direction.NORTH
        self.goal = [maze_size//2, maze_size//2]  # Center of maze
        
        # Initialize maze walls (unknown initially)
        self.walls = np.zeros((maze_size, maze_size, 4), dtype=bool)  # N,E,S,W walls for each cell
        self.known_walls = np.zeros((maze_size, maze_size, 4), dtype=bool)  # Discovered walls
        
        # Initialize flood fill values
        self.flood_values = np.full((maze_size, maze_size), float('inf'))
        self.flood_values[self.goal[0], self.goal[1]] = 0
        
        # For visualization
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        
    def generate_maze(self):
        # Initialize all walls
        self.walls[:, :, :] = True
        
        # Remove walls to create paths (ensure multiple solutions)
        def remove_wall(x, y, direction):
            self.walls[y, x, direction] = False
            if direction == Direction.NORTH.value and y < self.maze_size-1:
                self.walls[y+1, x, Direction.SOUTH.value] = False
            elif direction == Direction.SOUTH.value and y > 0:
                self.walls[y-1, x, Direction.NORTH.value] = False
            elif direction == Direction.EAST.value and x < self.maze_size-1:
                self.walls[y, x+1, Direction.WEST.value] = False
            elif direction == Direction.WEST.value and x > 0:
                self.walls[y, x-1, Direction.EAST.value] = False
        
        # Create main path to goal
        current = [0, 0]
        visited = set()
        stack = [(0, 0)]
        
        while stack:
            current = stack[-1]
            visited.add((current[0], current[1]))
            
            # Get possible directions
            directions = []
            x, y = current
            if y < self.maze_size-1 and (x, y+1) not in visited:
                directions.append(Direction.NORTH.value)
            if x < self.maze_size-1 and (x+1, y) not in visited:
                directions.append(Direction.EAST.value)
            if y > 0 and (x, y-1) not in visited:
                directions.append(Direction.SOUTH.value)
            if x > 0 and (x-1, y) not in visited:
                directions.append(Direction.WEST.value)
            
            if directions:
                direction = np.random.choice(directions)
                remove_wall(x, y, direction)
                if direction == Direction.NORTH.value:
                    stack.append((x, y+1))
                elif direction == Direction.EAST.value:
                    stack.append((x+1, y))
                elif direction == Direction.SOUTH.value:
                    stack.append((x, y-1))
                else:
                    stack.append((x-1, y))
            else:
                stack.pop()
        
        # Add additional paths (to ensure multiple solutions)
        for _ in range(self.maze_size):
            x = np.random.randint(0, self.maze_size)
            y = np.random.randint(0, self.maze_size)
            direction = np.random.randint(0, 4)
            remove_wall(x, y, direction)
    
    def sense_walls(self):
        x, y = self.position
        # Update known walls based on current position and direction
        self.known_walls[y, x] = self.walls[y, x]
    
    def update_flood_values(self):
        # Update flood fill values based on known walls
        new_values = np.full((self.maze_size, self.maze_size), float('inf'))
        new_values[self.goal[0], self.goal[1]] = 0
        changed = True
        
        while changed:
            changed = False
            for y in range(self.maze_size):
                for x in range(self.maze_size):
                    if (y, x) == tuple(self.goal):
                        continue
                    
                    # Check accessible neighbors
                    min_neighbor = float('inf')
                    if not self.known_walls[y, x, Direction.NORTH.value] and y < self.maze_size-1:
                        min_neighbor = min(min_neighbor, new_values[y+1, x])
                    if not self.known_walls[y, x, Direction.EAST.value] and x < self.maze_size-1:
                        min_neighbor = min(min_neighbor, new_values[y, x+1])
                    if not self.known_walls[y, x, Direction.SOUTH.value] and y > 0:
                        min_neighbor = min(min_neighbor, new_values[y-1, x])
                    if not self.known_walls[y, x, Direction.WEST.value] and x > 0:
                        min_neighbor = min(min_neighbor, new_values[y, x-1])
                    
                    if min_neighbor != float('inf'):
                        new_value = min_neighbor + 1
                        if new_value != new_values[y, x]:
                            new_values[y, x] = new_value
                            changed = True
        
        self.flood_values = new_values
    
    def decide_next_move(self):
        x, y = self.position
        current_value = self.flood_values[y, x]
        
        # Check all possible moves
        possible_moves = []
        values = []
        
        # Check North
        if not self.known_walls[y, x, Direction.NORTH.value] and y < self.maze_size-1:
            possible_moves.append(Direction.NORTH)
            values.append(self.flood_values[y+1, x])
        
        # Check East
        if not self.known_walls[y, x, Direction.EAST.value] and x < self.maze_size-1:
            possible_moves.append(Direction.EAST)
            values.append(self.flood_values[y, x+1])
        
        # Check South
        if not self.known_walls[y, x, Direction.SOUTH.value] and y > 0:
            possible_moves.append(Direction.SOUTH)
            values.append(self.flood_values[y-1, x])
        
        # Check West
        if not self.known_walls[y, x, Direction.WEST.value] and x > 0:
            possible_moves.append(Direction.WEST)
            values.append(self.flood_values[y, x-1])
        
        if possible_moves:
            # Choose the direction with the lowest flood value
            next_direction = possible_moves[np.argmin(values)]
            
            # Calculate number of turns needed
            turns_needed = (next_direction.value - self.direction.value) % 4
            self.direction = next_direction
            
            # Move in the chosen direction
            if next_direction == Direction.NORTH:
                self.position[1] += 1
            elif next_direction == Direction.EAST:
                self.position[0] += 1
            elif next_direction == Direction.SOUTH:
                self.position[1] -= 1
            elif next_direction == Direction.WEST:
                self.position[0] -= 1
    
    def draw(self):
        self.ax.clear()
        
        # Draw cells
        for y in range(self.maze_size):
            for x in range(self.maze_size):
                # Draw actual maze walls (in light gray)
                if self.walls[y, x, Direction.NORTH.value]:
                    self.ax.plot([x, x+1], [y+1, y+1], color='lightgray', linestyle='-', linewidth=2)
                if self.walls[y, x, Direction.EAST.value]:
                    self.ax.plot([x+1, x+1], [y, y+1], color='lightgray', linestyle='-', linewidth=2)
                if self.walls[y, x, Direction.SOUTH.value]:
                    self.ax.plot([x, x+1], [y, y], color='lightgray', linestyle='-', linewidth=2)
                if self.walls[y, x, Direction.WEST.value]:
                    self.ax.plot([x, x], [y, y+1], color='lightgray', linestyle='-', linewidth=2)
                
                # Draw known walls (in blue)
                if self.known_walls[y, x, Direction.NORTH.value]:
                    self.ax.plot([x, x+1], [y+1, y+1], color='blue', linestyle='-', linewidth=2)
                if self.known_walls[y, x, Direction.EAST.value]:
                    self.ax.plot([x+1, x+1], [y, y+1], color='blue', linestyle='-', linewidth=2)
                if self.known_walls[y, x, Direction.SOUTH.value]:
                    self.ax.plot([x, x+1], [y, y], color='blue', linestyle='-', linewidth=2)
                if self.known_walls[y, x, Direction.WEST.value]:
                    self.ax.plot([x, x], [y, y+1], color='blue', linestyle='-', linewidth=2)
                
                # Draw flood values
                if self.flood_values[y, x] != float('inf'):
                    self.ax.text(x+0.5, y+0.5, f'{int(self.flood_values[y, x])}',
                               ha='center', va='center')
        
        # Draw micromouse
        mouse_x = self.position[0] + 0.5
        mouse_y = self.position[1] + 0.5
        direction_dx = {
            Direction.NORTH: 0,
            Direction.EAST: 0.2,
            Direction.SOUTH: 0,
            Direction.WEST: -0.2
        }
        direction_dy = {
            Direction.NORTH: 0.2,
            Direction.EAST: 0,
            Direction.SOUTH: -0.2,
            Direction.WEST: 0
        }
        self.ax.add_patch(Rectangle((mouse_x-0.3, mouse_y-0.3), 0.6, 0.6,
                                  facecolor='red', alpha=0.5))
        self.ax.arrow(mouse_x, mouse_y,
                     direction_dx[self.direction],
                     direction_dy[self.direction],
                     head_width=0.1, head_length=0.1, fc='red', ec='red')
        
        # Draw goal
        goal_x = self.goal[0] + 0.5
        goal_y = self.goal[1] + 0.5
        self.ax.add_patch(Rectangle((goal_x-0.3, goal_y-0.3), 0.6, 0.6,
                                  facecolor='green', alpha=0.3))
        
        # Add legend
        self.ax.plot([], [], color='lightgray', linestyle='-', linewidth=2, label='Actual Maze')
        self.ax.plot([], [], color='blue', linestyle='-', linewidth=2, label='Known Walls')
        self.ax.legend(loc='upper right')
        
        self.ax.set_xlim(-0.5, self.maze_size+0.5)
        self.ax.set_ylim(-0.5, self.maze_size+0.5)
        self.ax.set_aspect('equal')
        plt.pause(0.5)  # Pause to show the frame
    
    def run(self):
        self.generate_maze()
        while tuple(self.position) != tuple(self.goal):
            self.sense_walls()
            self.update_flood_values()
            self.draw()
            self.decide_next_move()
        
        # Final draw
        self.draw()
        plt.show()

# Create and run the simulation
mouse = MicroMouse()
mouse.run()