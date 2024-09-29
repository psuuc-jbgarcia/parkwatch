import cv2
import numpy as np

# Function to create a textured background
def create_parking_background(width, height):
    # Create a gray canvas for the pavement
    pavement = np.ones((height, width, 3), dtype=np.uint8) * 200

    # Create random noise to simulate texture
    noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    textured_background = cv2.add(pavement, noise)

    return textured_background

# Function to draw realistic parking slots
def draw_realistic_parking_layout(image, parking_slots, occupied_slots=None):
    for idx, (x, y, w, h) in enumerate(parking_slots):
        # Determine if the slot is occupied or available
        if occupied_slots and idx in occupied_slots:
            color = (0, 0, 255)  # Red for occupied
        else:
            color = (0, 255, 0)  # Green for available
        
        # Draw the parking slot as a filled rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness=-1)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), thickness=2)  # Border
        
        # Draw a lighter shade for a 3D effect
        cv2.rectangle(image, (x + 5, y + 5), (x + w - 5, y + h - 5), (255, 255, 255), thickness=-1)

        # Draw the slot ID inside the rectangle
        slot_label = f'Slot {idx + 1}'
        cv2.putText(image, slot_label, (x + 10, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Add lane markings
    for i in range(0, image.shape[1], 50):  # Vertical lane markings
        cv2.line(image, (i, 0), (i, image.shape[0]), (255, 255, 255), 2)

    return image

# Define the size of the parking lot canvas (2D layout)
canvas_width = 800
canvas_height = 600

# Create the parking lot background
canvas = create_parking_background(canvas_width, canvas_height)

# Define the parking slots as rectangles [(x, y, width, height)]
# Example parking slots
parking_slots = [
    (50, 50, 100, 200),
    (200, 50, 100, 200),
    (350, 50, 100, 200),
    (500, 50, 100, 200),
    (650, 50, 100, 200),
]

# Define occupied slots by their index (optional)
occupied_slots = [1, 3]  # For example, slots 2 and 4 are occupied

# Draw the realistic parking layout on the canvas
layout_image = draw_realistic_parking_layout(canvas, parking_slots, occupied_slots)

# Display the parking layout
cv2.imshow('Parking Layout', layout_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
