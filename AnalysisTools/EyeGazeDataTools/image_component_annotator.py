import cv2
import matplotlib.pyplot as plt
import numpy as np

# Initialize global variables
shapes = []
current_shape = []
image = None

def is_convex(shape):
    hull = cv2.convexHull(np.array(shape))
    if len(shape) == len(hull):
        return True
    else:
        return False

def draw_shape(event, x, y, flags, param):
    global current_shape, image

    if event == cv2.EVENT_KEYDOWN:
        if event.key == ord('a'):
            current_shape.append((x, y))
            cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
        elif event.key == ord('f'):
            if len(current_shape) > 2 and is_convex(current_shape):  # Minimum three points to form a convex shape
                shapes.append(current_shape)
                cv2.polylines(image, [np.array(current_shape)], isClosed=True, color=(0, 0, 255), thickness=2)
            current_shape = []
            
        elif event.key == ord('z'):
            pass
    # if event == cv2.EVENT_RBUTTONDOWN:
    #     if len(current_shape) > 2:  # Minimum three points to form a convex shape
    #         shapes.append(current_shape)
    #         cv2.polylines(image, [np.array(current_shape)], isClosed=True, color=(0, 0, 255), thickness=2)
    #     current_shape = []

def main():
    global image
    image_path = "image.jpg"
    image = cv2.imread(image_path)

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", draw_shape)

    while True:
        cv2.imshow("Image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            break

    cv2.destroyAllWindows()

    # Save shapes to a file
    with open((os.path.splitext(image_path)[0] + '.annotation'), 'w') as f:
        for shape in shapes:
            f.write(f"{shape}\n")

    print("Shapes saved for later collision detection.")

if __name__ == "__main__":
    main()
