import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

# Define the path to your parking file
parking_file = 'CarParkPos2'  # Adjust this path if necessary

def load_pos_list():
    if not os.path.exists(parking_file):
        print(f"Error: File not found: {parking_file}")
        return []
    try:
        with open(parking_file, 'rb') as f:
            pos_list = pickle.load(f)
            return pos_list
    except (pickle.PickleError, EOFError, IOError) as e:
        print(f"Error loading pickle file: {e}")
        return []

def draw_parking_slots(ax, pos_list):
    ax.clear()  # Clear the current axes

    if not pos_list:  # Check if the list is empty
        print("No positions to draw.")
        return

    # Dynamically set limits based on parking slot positions
    x_min = min(px for px, _, _, _, _, _ in pos_list) - 20
    x_max = max(px + size[0] for px, _, _, _, _, size in pos_list) + 20
    y_min = min(py for _, py, _, _, _, _ in pos_list) - 20
    y_max = max(py + size[1] for _, py, _, _, _, size in pos_list) + 20

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Invert the y-axis
    ax.invert_yaxis()  # Invert y-axis to display bottom at the top

    # Set a textured background to simulate a parking lot surface
    ax.set_facecolor('#D3D3D3')  # Light gray background simulating asphalt

    # Draw parking slots
    for idx, pos in enumerate(pos_list):
        px, py, reserved, shape, points, size = pos

        # Set colors based on reservation status
        color = 'lightgreen' if not reserved else 'lightcoral'
        edgecolor = 'blue'
        
        # Create the rectangle with a shadow effect
        shadow_offset = 3
        shadow = patches.Rectangle((px + shadow_offset, py - shadow_offset), 
                                   size[0], size[1],
                                   linewidth=0, edgecolor='none', 
                                   facecolor='gray', alpha=0.3)  # Shadow
        ax.add_patch(shadow)

        # Draw the actual parking slot with rounded corners
        rect = patches.FancyBboxPatch((px, py), size[0], size[1], 
                                       boxstyle="round,pad=0.1", 
                                       linewidth=2, edgecolor=edgecolor, 
                                       facecolor=color)
        ax.add_patch(rect)

        # Improved text styling with slot numbers
        ax.text(px + size[0] / 2, py + size[1] / 2, 
                f'Slot {idx + 1}\n{"Reserved" if reserved else "Available"}', 
                ha='center', va='center', fontsize=10, color='black',
                fontweight='bold', fontname='Arial', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.5'))

    # Add separators between slots
    for pos in pos_list:
        px, py, reserved, shape, points, size = pos
        separator = patches.Rectangle((px + size[0], py), 2, size[1], linewidth=0, edgecolor='none', facecolor='black')
        ax.add_patch(separator)

    # Draw lines for parking spots
    for pos in pos_list:
        px, py, reserved, shape, points, size = pos
        ax.plot([px + size[0], px + size[0]], [py, py + size[1]], color='black', linewidth=2)

    # Remove ticks for a cleaner look
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

def update(frame):
    posList = load_pos_list()  # Reload the parking positions
    draw_parking_slots(ax, posList)  # Redraw the parking slots

# Initialize plot with a larger figure size
fig, ax = plt.subplots(figsize=(12, 8))  # Adjust the figure size as needed
ani = FuncAnimation(fig, update, interval=3000, cache_frame_data=False)  # Disable caching

# Hide the toolbar
plt.get_current_fig_manager().toolbar.pack_forget()

# Use tight layout to minimize margins
plt.tight_layout()

plt.show()
