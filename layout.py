import os
import pickle
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.animation import FuncAnimation

# Define the path to your parking file
parking_file = 'CarParkPos'  # Adjust this path if necessary

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
    ax.clear()

    if not pos_list:
        print("No positions to draw.")
        return

    # Set plot limits dynamically based on slot positions
    x_min = min(px for px, _, _, _, _, _ in pos_list) - 20
    x_max = max(px + size[0] for px, _, _, _, _, size in pos_list) + 20
    y_min = min(py for _, py, _, _, _, _ in pos_list) - 20
    y_max = max(py + size[1] for _, py, _, _, _, size in pos_list) + 20

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.invert_yaxis()
    ax.set_facecolor('#D3D3D3')

    for idx, pos in enumerate(pos_list):
        px, py, reserved, shape, points, size = pos

        color = 'lightgreen' if not reserved else 'lightcoral'
        edgecolor = 'blue'

        if shape == 'rect':
            rect = FancyBboxPatch(
                (px, py), size[0], size[1], boxstyle="round,pad=0.1", 
                linewidth=2, edgecolor=edgecolor, facecolor=color)
            ax.add_patch(rect)
            # Centered text for rectangles
            text_x, text_y = px + size[0] / 2, py + size[1] / 2

        elif shape == 'trapezoid':
            if points and len(points) == 4:  # Valid trapezoid
                trapezoid = Polygon(points, closed=True, linewidth=2, 
                                    edgecolor=edgecolor, facecolor=color)
                ax.add_patch(trapezoid)
                # Calculate text position as the centroid of the trapezoid
                text_x = sum(x for x, _ in points) / 4
                text_y = sum(y for _, y in points) / 4
            else:
                print(f"Invalid points for trapezoid at Slot {idx + 1}")
                continue  # Skip invalid trapezoids

        ax.text(text_x, text_y, 
                f'Slot {idx + 1}\n{"Reserved" if reserved else "Available"}',
                ha='center', va='center', fontsize=10, color='black',
                fontweight='bold', fontname='Arial', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.5'))

    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

def update(frame):
    pos_list = load_pos_list()
    draw_parking_slots(ax, pos_list)

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=3000, cache_frame_data=False)

plt.get_current_fig_manager().toolbar.pack_forget()
plt.tight_layout()
plt.show()
