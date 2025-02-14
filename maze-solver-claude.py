import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import time

class MazeCell:
    def __init__(self):
        self.walls = {'N': True, 'E': True, 'S': True, 'W': True}
        self.visited = False
        self.distance = float('inf')

class Micromouse:
    def __init__(self, x=0, y=0, direction='N'):
        self.x = x
        self.y = y
        self.direction = direction
        self.visited_cells = set()
        
    def turn_left(self):
        directions = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.direction = directions[self.direction]
        
    def turn_right(self):
        directions = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.direction = directions[self.direction]

class MazeSimulator:
    def __init__(self, size=9):
        self.size = size
        self.maze = [[MazeCell() for _ in range(size)] for _ in range(size)]
        self.mouse = Micromouse()
        self.goal = (size//2, size//2)
        self.frames = []
        
    def generate_maze(self):
        def recursive_backtracker(x, y):
            self.maze[y][x].visited = True
            directions = [(0, -1, 'N', 'S'), (1, 0, 'E', 'W'),
                         (0, 1, 'S', 'N'), (-1, 0, 'W', 'E')]
            random.shuffle(directions)
            
            for dx, dy, wall1, wall2 in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.size and 0 <= new_y < self.size and 
                    not self.maze[new_y][new_x].visited):
                    self.maze[y][x].walls[wall1] = False
                    self.maze[new_y][new_x].walls[wall2] = False
                    recursive_backtracker(new_x, new_y)
        
        recursive_backtracker(0, 0)
        # Reset visited flags
        for row in self.maze:
            for cell in row:
                cell.visited = False
    
    def flood_fill(self):
        # Reset distances
        for row in self.maze:
            for cell in row:
                cell.distance = float('inf')
        
        # Set goal distance to 0
        self.maze[self.goal[1]][self.goal[0]].distance = 0
        queue = [(self.goal[0], self.goal[1])]
        
        while queue:
            x, y = queue.pop(0)
            current_dist = self.maze[y][x].distance
            
            # Check all adjacent cells
            directions = [(0, -1, 'N'), (1, 0, 'E'), (0, 1, 'S'), (-1, 0, 'W')]
            for dx, dy, direction in directions:
                new_x, new_y = x + dx, y + dy
                
                if (0 <= new_x < self.size and 0 <= new_y < self.size and
                    not self.maze[y][x].walls[direction]):
                    if self.maze[new_y][new_x].distance > current_dist + 1:
                        self.maze[new_y][new_x].distance = current_dist + 1
                        queue.append((new_x, new_y))
    
    def get_next_move(self):
        x, y = self.mouse.x, self.mouse.y
        current_dist = self.maze[y][x].distance
        
        # Check all possible moves
        directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        best_direction = None
        min_distance = float('inf')
        
        for direction, (dx, dy) in directions.items():
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.size and 0 <= new_y < self.size and
                not self.maze[y][x].walls[direction]):
                if self.maze[new_y][new_x].distance < min_distance:
                    min_distance = self.maze[new_y][new_x].distance
                    best_direction = direction
        
        return best_direction
    
    def move_mouse(self):
        next_direction = self.get_next_move()
        
        # Turn mouse to face the correct direction
        while self.mouse.direction != next_direction:
            self.mouse.turn_right()
        
        # Move forward
        dx, dy = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[next_direction]
        self.mouse.x += dx
        self.mouse.y += dy
        self.mouse.visited_cells.add((self.mouse.x, self.mouse.y))
    
    def draw_frame(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(-0.5, self.size - 0.5)
        ax.set_ylim(self.size - 0.5, -0.5)
        
        # Draw walls
        for y in range(self.size):
            for x in range(self.size):
                if self.maze[y][x].walls['N']:
                    ax.plot([x-0.5, x+0.5], [y-0.5, y-0.5], 'k-', linewidth=2)
                if self.maze[y][x].walls['E']:
                    ax.plot([x+0.5, x+0.5], [y-0.5, y+0.5], 'k-', linewidth=2)
                if self.maze[y][x].walls['S']:
                    ax.plot([x-0.5, x+0.5], [y+0.5, y+0.5], 'k-', linewidth=2)
                if self.maze[y][x].walls['W']:
                    ax.plot([x-0.5, x-0.5], [y-0.5, y+0.5], 'k-', linewidth=2)
                
                # Draw distance values
                ax.text(x, y, str(self.maze[y][x].distance), 
                       ha='center', va='center')
        
        # Draw visited cells
        for x, y in self.mouse.visited_cells:
            ax.add_patch(plt.Rectangle((x-0.5, y-0.5), 1, 1, 
                                     color='lightgreen', alpha=0.3))
        
        # Draw goal
        ax.add_patch(plt.Rectangle((self.goal[0]-0.5, self.goal[1]-0.5), 1, 1, 
                                 color='green', alpha=0.3))
        
        # Draw mouse
        ax.add_patch(plt.Circle((self.mouse.x, self.mouse.y), 0.3, 
                               color='red'))
        # Draw mouse direction
        direction_vectors = {
            'N': (0, -0.3), 'E': (0.3, 0), 'S': (0, 0.3), 'W': (-0.3, 0)
        }
        dx, dy = direction_vectors[self.mouse.direction]
        ax.arrow(self.mouse.x, self.mouse.y, dx, dy, 
                head_width=0.1, head_length=0.1, fc='red', ec='red')
        
        ax.grid(True)
        return fig
    
    def solve(self):
        self.generate_maze()
        self.flood_fill()
        
        while (self.mouse.x, self.mouse.y) != self.goal:
            fig = self.draw_frame()
            self.frames.append(fig)
            self.move_mouse()
            self.flood_fill()
        
        # Add final frame
        fig = self.draw_frame()
        self.frames.append(fig)
        
        return self.frames

# Run the simulation
simulator = MazeSimulator()
frames = simulator.solve()

# Display frames
for i, frame in enumerate(frames):
    plt.figure(i)
    frame.show()
    plt.pause(1)  # Pause for 1 second between frames
    if i < len(frames) - 1:  # Don't close the last frame
        plt.close()

plt.show()  # Keep the last frame open