import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import json

from utils import point_in_polygon

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

# Initialize global variables
shapes = {}
current_shape = []
selection_key = None
selection_index = 0
image = None
original_image = None
x_global = 0
y_global = 0
window_height = 720
window_width = 1280
is_in_selection_mode = False


def show_popup(message):
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Show the message box
    messagebox.showinfo("Information", message)

    # Destroy the root window
    root.destroy()


def get_user_input(prompt):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring(title="Input", prompt=prompt)
    root.destroy()  # Destroy the main window
    return user_input


def validate_select_shape():
    global selection_key, selection_index
    try:
        i = list(shapes.keys())[selection_index]
        selection_key = i
    except IndexError:
        selection_index = 0
        selection_key = None


def select_next_shape():
    global selection_key, selection_index
    selection_index = selection_index + 1
    if selection_index > len(shapes) - 1:
        selection_index = 0
    validate_select_shape()


def select_previous_shape():
    global selection_key, selection_index
    selection_index = selection_index - 1
    if selection_index < 0:
        selection_index = len(shapes) - 1
    validate_select_shape()


def update_key(dictionary, old_key, new_key):
    new_dict = {}
    for key, value in dictionary.items():
        if old_key == key:
            new_dict[new_key] = value
        else:
            new_dict[key] = value
    return new_dict


def mouse_callback(event, x, y, flags, param):
    global x_global, y_global
    if event == cv2.EVENT_MOUSEMOVE:
        x_global, y_global = x, y
        # detect_shape = point_in_polygon.detect(x, y, shapes)
        # if detect_shape is not None:
        #     print(f"Mouse moved to x:{x}, y:{y} in shape: {detect_shape}")
        print("Mouse moved to x:", x, "y:", y)


def load_annotation_file(file_path):
    global shapes, selection_index, current_shape
    with open(file_path, 'r') as f:
        shapes = json.load(f)
    # Restore the shapes from normalized coordinates
    for key in shapes.keys():
        shape = shapes[key]
        for i in range(len(shape)):
            shape[i] = [int(shape[i][0] * window_width), int(shape[i][1] * window_height)]
    print(f"Shapes Loaded:{json.dumps(shapes, indent=4)}")
    current_shape = []
    selection_index = 0


def save_annotation_file(file_path):
    with open(file_path, 'w') as f:
        json.dump(shapes, f, indent=4)


def is_convex(shape):
    hull = cv2.convexHull(np.array(shape))
    if len(shape) == len(hull):
        return True
    else:
        return False


def redrawn_image():
    global image, original_image, current_shape, shapes
    image = original_image.copy()
    edit_mode_color = (255, 0, 0)
    selected_color = (0, 0, 255)
    selection_mode_color = (255, 0, 255)
    circle_color = (0, 255, 0)

    normal_color = edit_mode_color
    focused_color = edit_mode_color
    if is_in_selection_mode:
        normal_color = selection_mode_color
        focused_color = selected_color

    for key in shapes.keys():
        shape = shapes[key]
        if key == selection_key:
            cv2.polylines(image, [np.array(shape)], isClosed=True, color=focused_color, thickness=2)
        else:
            cv2.polylines(image, [np.array(shape)], isClosed=True, color=normal_color, thickness=2)
    for point in current_shape:
        cv2.circle(image, point, 3, circle_color, -1)


def main():
    global image, original_image, current_shape, shapes, selection_key, selection_index, is_in_selection_mode
    image_path = "./images/Cookie_theft_padded.png"
    window_title = "Image Annotation Tool - Press 'h' for help."
    image = cv2.imread(image_path)
    original_image = image.copy()

    image = cv2.resize(image, (window_width, window_height))
    original_image = cv2.resize(original_image, (window_width, window_height))

    cv2.namedWindow(window_title)
    cv2.setMouseCallback(window_title, mouse_callback)

    current_shape = []

    while True:
        cv2.imshow(window_title, image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Press 'q' to quit
            break
        if key == ord('x'):
            cv2.destroyAllWindows()
            exit()
        elif key == ord('a'):
            if is_in_selection_mode:
                show_popup("Please exit selection mode to add a new point.")
                continue
            current_shape.append((x_global, y_global))
            cv2.circle(image, (x_global, y_global), 3, (0, 255, 0), -1)
        elif key == ord('f'):
            if is_in_selection_mode:
                show_popup("Please exit selection mode to finalize the shape.")
                continue
            if len(current_shape) > 2:  # Minimum three points to form a shape
                shapes.update({len(shapes): current_shape})
                cv2.polylines(image, [np.array(current_shape)], isClosed=True, color=(0, 0, 255), thickness=2)
            else:
                show_popup("Shape must have at least 3 points")
            current_shape = []

        elif key == ord('z'):
            if is_in_selection_mode:
                show_popup("Please exit selection mode to undo a point or shape.")
                continue
            if current_shape:
                current_shape.pop()
            else:
                if shapes:
                    last_key = list(shapes.keys())[-1]
                    shapes.pop(last_key)
                    validate_select_shape()
            redrawn_image()

        elif key == ord('s'):
            is_in_selection_mode = not is_in_selection_mode
            print(f"Selection mode: {is_in_selection_mode}")
            if is_in_selection_mode:
                # selection_index = 0
                if not shapes:
                    show_popup("No valid shape annotation.")
                    continue
                validate_select_shape()
                if selection_key is not None:
                    print(f"Selected shape: {selection_key}")
            redrawn_image()

        elif key == ord(']'):
            if is_in_selection_mode:
                select_next_shape()
                redrawn_image()

        elif key == ord('['):
            if is_in_selection_mode:
                select_previous_shape()
                redrawn_image()

        elif key == ord('t'):
            if not is_in_selection_mode:
                show_popup("Please enter selection mode to rename a shape.")
            if selection_key is not None:
                new_key = get_user_input("Name the selected shape:")
                if new_key:
                    shapes = update_key(shapes, selection_key, new_key)
            else:
                show_popup("Please select a shape first.")

        elif key == ord('l'):
            annotation_file_path = (os.path.splitext(image_path)[0] + '.annotation')
            try:
                load_annotation_file(annotation_file_path)
                show_popup("Annotation file loaded successfully.")
                redrawn_image()
            except FileNotFoundError:
                show_popup("No annotation file found.")

        elif key == ord('d'):
            if not is_in_selection_mode:
                show_popup("Please enter selection mode to delete a shape.")
            if selection_key is not None:
                shapes.pop(selection_key)
                validate_select_shape()
                redrawn_image()

        elif key == ord('h'):
            show_popup(
                "Press 'a' to add a point.\nPress 'f' to finalize a shape.\nPress 'z' to undo a point or "
                "shape.\nPress 's' to enter selection mode.\nPress '[' to select previous shape.\nPress ']' "
                "to select next shape. \nPress 't' to name/rename a shape. \nPress 'd' to delete selected shape."
                "\nPress 'q' to save & quit. \nPress 'x' to exit without saving.")

    cv2.destroyAllWindows()

    # Normalize the shapes
    for key in shapes.keys():
        shape = shapes[key]
        for i in range(len(shape)):
            shape[i] = [shape[i][0] / window_width, shape[i][1] / window_height]

    print(f"Shapes:{json.dumps(shapes, indent=4)}")

    # Save shapes to a file
    # with open((os.path.splitext(image_path)[0] + '.annotation'), 'w') as f:
    #     json.dump(shapes, f, indent=4)
    annotation_filename = (os.path.splitext(image_path)[0] + '.annotation')
    save_annotation_file(annotation_filename)
    print("Shapes saved for later eye gaze data analysis.")


if __name__ == "__main__":
    main()
