import cv2
import numpy as np
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt

# Load the manually drawn mask
mask = cv2.imread('./images/Cookie_theft_segmentation.png', cv2.IMREAD_GRAYSCALE)

# Convert the mask to binary (assuming the mask is white on black background)
_, binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

# Label the connected components
labeled_mask = label(binary_mask)

# Extract the coordinates of each component
components = regionprops(labeled_mask)

# Plot the labeled mask for visualization
plt.imshow(labeled_mask, cmap='nipy_spectral')
plt.colorbar()
plt.show()

# # Extract and print coordinates of each component
# for component in components:
#     coords = component.coords  # Coordinates of the current component
#     print(f'Component {component.label}:')
#     print(coords)
