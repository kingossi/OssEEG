
from PIL import Image

# Load the image
image = Image.open('logo.png')

# Create a list to store the frames
frames = []

# Rotate the image and store each frame
for angle in range(0, 360, 10):  # Rotate in steps of 10 degrees
    rotated_image = image.rotate(angle)
    frames.append(rotated_image)

# Save the frames as a GIF
frames[0].save('rotating_logo.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
