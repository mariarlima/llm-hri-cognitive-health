import cv2
import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from eye_gaze_data_reader import get_eye_gaze_data
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV
import matplotlib as mpl


def get_normalized_log_likelihood(points, gmm, x_scale=1920, y_scale=1080, show_plot=True):
    points[:, 0] *= x_scale
    points[:, 1] *= y_scale
    log_llh = gmm.score(points)
    # log_llh /= points.shape[0]
    # TODO: Add titles Pxx Sx
    if show_plot:
        plt.scatter(points[:, 0], points[:, 1], marker='x', s=1)
        plt.show()
    return log_llh

# def get_mean_entropy(points, gmm, x_scale=1920, y_scale=1080, show_plot=True):
#     points[:, 0] *= x_scale
#     points[:, 1] *= y_scale
#     # After fitting GMM
#     probs = gmm.predict_proba(X)  # shape: (n_samples, n_components)
#     # Entropy per gaze point
#     entropies = np.array([entropy(p) for p in probs])  # shape: (n_samples,)
#     # Mean entropy across all points
#     mean_entropy = np.mean(entropies)

def plot_gmm_likelihood(gmm, title, width, height, task):
    img = cv2.imread('./images/Cookie_theft_padded.png')
    if task != "Cognitive Picture Description Task":
        img = cv2.imread('./images/Picnic_padded.png')
    width, height = 1920, 1080

    # Create a grid of all pixel coordinates
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)

    # Flatten into a list of (x, y) points → shape: (height*width, 2)
    coords = np.column_stack((xx.ravel(), yy.ravel()))

    log_likelihoods = gmm.score_samples(coords)

    log_likelihood_map = log_likelihoods.reshape((height, width))
    # Normalize to [0, 1] for visualization
    log_likelihood_map_norm = (log_likelihood_map - log_likelihood_map.min()) / (log_likelihood_map.max() - log_likelihood_map.min())

    plt.imshow(img)
    plt.imshow(log_likelihood_map_norm, cmap='bwr', alpha=0.6)
    plt.title("GMM Log-Likelihood")
    plt.show()



def plot_gmm(X, Y_, means, covariances, index, title, width, height, segmented_mask):
    plt.figure(dpi=200)
    splot = plt.subplot(2, 1, 1 + index)
    for i, (mean, covar) in enumerate(zip(means, covariances)):
        v, w = linalg.eigh(covar)
        v = 2.0 * np.sqrt(2.0) * np.sqrt(v)
        u = w[0] / linalg.norm(w[0])
        # as the DP will not use every component it has access to
        # unless it needs it, we shouldn't plot the redundant
        # components.
        # if not (X is None or Y_ is None):
        #     if not np.any(Y_ == i):
        #         continue
        #     plt.scatter(X[Y_ == i, 0], X[Y_ == i, 1], 0.8, color=color)

        # Plot an ellipse to show the Gaussian component
        angle = np.arctan(u[1] / u[0])
        angle = 180.0 * angle / np.pi  # convert to degrees
        ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180.0 + angle, color=plt.cm.tab20(i))
        ell.set_clip_box(splot.bbox)
        ell.set_alpha(0.5)
        splot.add_artist(ell)

    splot.set_aspect('equal', 'box')
    # splot.invert_yaxis()
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.gca().invert_yaxis()
    # plt.xticks(())
    # plt.yticks(())
    plt.title(title)
    plt.imshow(segmented_mask, cmap='Pastel2', alpha=1)
    plt.show()


def get_pixel_coordinates(segmented_mask, label):
    # print(np.column_stack(np.where(segmented_mask == label)))
    image_component_mask = segmented_mask.copy()
    image_component_mask[image_component_mask != label] = -1
    # plt.imshow(image_component_mask, cmap='nipy_spectral')
    # print(np.unique(segmented_mask))
    # print(np.unique(image_component_mask))
    # plt.show()
    return np.column_stack(np.where(segmented_mask == label))


def fit_gmm_to_component(coordinates, n_components):
    gmm = GaussianMixture(n_components=n_components, covariance_type='full')
    gmm.fit(coordinates)
    return gmm


def compute_likelihoods(gmm, coordinates):
    return gmm.score_samples(coordinates)


def gmm_bic_score(estimator, X):
    """Callable to pass to GridSearchCV that will use the BIC score."""
    # Make it negative since GridSearchCV expects a score to maximize
    return -estimator.bic(X)


def get_GMM_baseline_naive(task="Cognitive Picture Description Task", height=1080, width=1920, verbose=False):
    img = cv2.imread('./images/Cookie_theft_segmentation.png')
    image_component_id_lookup = {
        0: "Surrounding",
        1: "Cookie Jar",
        2: "Window",
        3: "Boy",
        4: "Lady",
        5: "Plate, Washing Cloth",
        6: "Girl",
        7: "Sink, Water",
        8: "Stool",
        9: "Dishes",
        10: "Image Components"
    }
    if task != "Cognitive Picture Description Task":
        img = cv2.imread('./images/Picnic_segmentation.png')
        image_component_id_lookup = {
            0: "Surrounding",
            1: "Tree, House, Car",
            2: "Kite",
            3: "Flag",
            4: "Boat",
            5: "Fishing",
            6: "Boy",
            7: "Lady",
            8: "Man",
            9: "Girl, Sand Castle",
            10: "Dog",
            11: "Glass, Beverage",
            12: "Book",
            13: "Basket",
            14: "Blanket",
            15: "Radio",
            16: "Sandals",
            17: "Image Components"
        }

    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape the image to a 2D array of pixels
    pixels = image_rgb.reshape(-1, 3)

    # Use a KD-Tree to find unique colors within a threshold
    threshold = 5
    tree = cKDTree(pixels)
    unique_colors = []
    labels = np.zeros(pixels.shape[0], dtype=int) - 1

    for i, pixel in enumerate(pixels):
        if labels[i] == -1:
            indices = tree.query_ball_point(pixel, threshold)
            unique_colors.append(pixel)
            labels[indices] = len(unique_colors) - 1

    unique_colors = np.array(unique_colors)

    if verbose:
        # Print unique colors
        print(f"Unique colors (within threshold): {unique_colors}")

    # Create a dictionary mapping from color tuples to segment labels
    color_to_label = {tuple(color): label for label, color in enumerate(unique_colors)}

    if verbose:
        # Print the mapping
        print(f"Color to label mapping: {color_to_label}")

    # Initialize the segmented mask with the same height and width as the input image
    segmented_mask = np.zeros((image_rgb.shape[0], image_rgb.shape[1]), dtype=np.int32)

    # Assign labels to each pixel based on the color
    for i, color in enumerate(unique_colors):
        mask = np.all(image_rgb == color, axis=-1)
        # if verbose:
        #     plt.imshow(mask, cmap='tab20b')
        #     plt.show()
        #     print(i)
        segmented_mask[mask] = i

    if verbose:
        # Print the segmented mask
        print(segmented_mask)

    mask_id_list = np.unique(segmented_mask)
    separated_masks = {}

    for mask_id in mask_id_list:
        isolated_mask = segmented_mask.copy()
        isolated_mask[isolated_mask != mask_id] = -1
        if verbose:
            print(f"id: {mask_id}, tag: {image_component_id_lookup[mask_id]}")
            print(np.unique(isolated_mask))
            # plt.imshow(separated_masks[id], cmap='nipy_spectral')
            # plt.colorbar()
            # plt.show()
        separated_masks[mask_id] = isolated_mask

    image_component_mask = segmented_mask.copy()
    image_component_mask[image_component_mask != 0] = len(image_component_id_lookup) - 1
    separated_masks[len(image_component_id_lookup) - 1] = image_component_mask

    if verbose:
        plt.imshow(segmented_mask, cmap='nipy_spectral')
        plt.colorbar()
        plt.show()


def get_GMM_baseline(task="Cognitive Picture Description Task", height=1080, width=1920, verbose=False):
    img = cv2.imread('./images/Cookie_theft_segmentation.png')
    image_component_id_lookup = {
        0: "Surrounding",
        1: "Cookie Jar",
        2: "Window",
        3: "Boy",
        4: "Lady",
        5: "Plate, Washing Cloth",
        6: "Girl",
        7: "Sink, Water",
        8: "Stool",
        9: "Dishes",
        10: "Image Components"
    }
    if task != "Cognitive Picture Description Task":
        img = cv2.imread('./images/Picnic_segmentation.png')
        image_component_id_lookup = {
            0: "Surrounding",
            1: "Tree, House, Car",
            2: "Kite",
            3: "Flag",
            4: "Boat",
            5: "Fishing",
            6: "Boy",
            7: "Lady",
            8: "Man",
            9: "Girl, Sand Castle",
            10: "Dog",
            11: "Glass, Beverage",
            12: "Book",
            13: "Basket",
            14: "Blanket",
            15: "Radio",
            16: "Sandals",
            17: "Image Components"
        }

    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape the image to a 2D array of pixels
    pixels = image_rgb.reshape(-1, 3)

    # Use a KD-Tree to find unique colors within a threshold
    threshold = 5
    tree = cKDTree(pixels)
    unique_colors = []
    labels = np.zeros(pixels.shape[0], dtype=int) - 1

    for i, pixel in enumerate(pixels):
        if labels[i] == -1:
            indices = tree.query_ball_point(pixel, threshold)
            unique_colors.append(pixel)
            labels[indices] = len(unique_colors) - 1

    unique_colors = np.array(unique_colors)

    if verbose:
        # Print unique colors
        print(f"Unique colors (within threshold): {unique_colors}")

    # Create a dictionary mapping from color tuples to segment labels
    color_to_label = {tuple(color): label for label, color in enumerate(unique_colors)}

    if verbose:
        # Print the mapping
        print(f"Color to label mapping: {color_to_label}")

    # Initialize the segmented mask with the same height and width as the input image
    segmented_mask = np.zeros((image_rgb.shape[0], image_rgb.shape[1]), dtype=np.int32)

    # Assign labels to each pixel based on the color
    for i, color in enumerate(unique_colors):
        mask = np.all(image_rgb == color, axis=-1)
        # if verbose:
        #     plt.imshow(mask, cmap='tab20b')
        #     plt.show()
        #     print(i)
        segmented_mask[mask] = i

    if verbose:
        # Print the segmented mask
        print(segmented_mask)

    mask_id_list = np.unique(segmented_mask)
    separated_masks = {}

    for mask_id in mask_id_list:
        isolated_mask = segmented_mask.copy()
        isolated_mask[isolated_mask != mask_id] = -1
        if verbose:
            print(f"id: {mask_id}, tag: {image_component_id_lookup[mask_id]}")
            print(np.unique(isolated_mask))
            # plt.imshow(separated_masks[id], cmap='nipy_spectral')
            # plt.colorbar()
            # plt.show()
        separated_masks[mask_id] = isolated_mask

    image_component_mask = segmented_mask.copy()
    image_component_mask[image_component_mask != 0] = len(image_component_id_lookup) - 1
    separated_masks[len(image_component_id_lookup) - 1] = image_component_mask

    if verbose:
        plt.imshow(segmented_mask, cmap='nipy_spectral')
        plt.colorbar()
        plt.show()

    param_grid = {
        'n_components': range(1, 4),
        'covariance_type': ['full'],
        # 'reg_covar': [1e-6, 1e-4, 1e-2, 1e-1]
    }

    # Search for best parameters for each component
    hyperparameters = {}
    for key in list(image_component_id_lookup.keys()):
        if key == 0 or key == list(image_component_id_lookup.keys())[-1]:
            continue
        if verbose:
            print(f"Searching: {key} - {image_component_id_lookup[key]}")
        # Define the GMM model
        gmm = GaussianMixture(random_state=0)
        grid_search = GridSearchCV(
            gmm, param_grid=param_grid, scoring=gmm_bic_score
        )
        # Perform GridSearchCV
        component_coords = get_pixel_coordinates(separated_masks[key], key)
        component_coords[:, [0, 1]] = component_coords[:, [1, 0]]
        grid_search.fit(component_coords)

        # Best parameters
        best_params = grid_search.best_params_
        hyperparameters[key] = best_params

        if verbose:
            print(f'Best parameters: {best_params}')

    component_gmms = {}
    gmm_means = []
    gmm_covariances = []
    gmm_weights = []
    for key in list(image_component_id_lookup.keys()):
        if key == 0 or key == len(image_component_id_lookup) - 1:
            continue
        if verbose:
            print(f"Fitting: {key} - {image_component_id_lookup[key]}")
        component_coords = get_pixel_coordinates(separated_masks[key], key)
        component_coords[:, [0, 1]] = component_coords[:, [1, 0]]
        gmm = fit_gmm_to_component(component_coords, hyperparameters[key]["n_components"])
        gmm_means.append(gmm.means_)
        gmm_covariances.append(gmm.covariances_)
        gmm_weights.append(gmm.weights_)
        component_gmms[image_component_id_lookup[key]] = gmm

    combined_means = np.vstack(gmm_means)
    combined_covariances = np.vstack(gmm_covariances)
    combined_weights = np.hstack(gmm_weights)
    combined_weights /= np.sum(combined_weights)

    combined_gmm = GaussianMixture(n_components=len(combined_means), covariance_type='full')
    combined_gmm.means_ = combined_means
    combined_gmm.covariances_ = combined_covariances
    combined_gmm.weights_ = combined_weights
    combined_gmm.precisions_cholesky_ = np.linalg.cholesky(np.linalg.inv(combined_covariances)).transpose((0, 2, 1))

    component_gmms[len(image_component_id_lookup) - 1] = combined_gmm

    if verbose:
        plot_gmm(None, None, combined_gmm.means_, combined_gmm.covariances_, 0, 'GMM Components over Image Components',
                 width, height, segmented_mask)

    return combined_gmm

def get_Overall_Mask_GMM_baseline(task="Cognitive Picture Description Task", height=1080, width=1920, num_components=0,
                                              verbose=False):
    img = cv2.imread('./images/Cookie_theft_segmentation.png')
    image_component_id_lookup = {
        0: "Surrounding",
        1: "Cookie Jar",
        2: "Window",
        3: "Boy",
        4: "Lady",
        5: "Plate, Washing Cloth",
        6: "Girl",
        7: "Sink, Water",
        8: "Stool",
        9: "Dishes",
        10: "Image Components"
    }
    if task != "Cognitive Picture Description Task":
        img = cv2.imread('./images/Picnic_segmentation.png')
        image_component_id_lookup = {
            0: "Surrounding",
            1: "Tree, House, Car",
            2: "Kite",
            3: "Flag",
            4: "Boat",
            5: "Fishing",
            6: "Boy",
            7: "Lady",
            8: "Man",
            9: "Girl, Sand Castle",
            10: "Dog",
            11: "Glass, Beverage",
            12: "Book",
            13: "Basket",
            14: "Blanket",
            15: "Radio",
            16: "Sandals",
            17: "Image Components"
        }

    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape the image to a 2D array of pixels
    pixels = image_rgb.reshape(-1, 3)

    # Use a KD-Tree to find unique colors within a threshold
    threshold = 5
    tree = cKDTree(pixels)
    unique_colors = []
    labels = np.zeros(pixels.shape[0], dtype=int) - 1

    for i, pixel in enumerate(pixels):
        if labels[i] == -1:
            indices = tree.query_ball_point(pixel, threshold)
            unique_colors.append(pixel)
            labels[indices] = len(unique_colors) - 1

    unique_colors = np.array(unique_colors)

    if verbose:
        # Print unique colors
        print(f"Unique colors (within threshold): {unique_colors}")

    # Create a dictionary mapping from color tuples to segment labels
    color_to_label = {tuple(color): label for label, color in enumerate(unique_colors)}

    if verbose:
        # Print the mapping
        print(f"Color to label mapping: {color_to_label}")

    # Initialize the segmented mask with the same height and width as the input image
    segmented_mask = np.zeros((image_rgb.shape[0], image_rgb.shape[1]), dtype=np.int32)

    # Assign labels to each pixel based on the color
    for i, color in enumerate(unique_colors):
        mask = np.all(image_rgb == color, axis=-1)
        # if verbose:
        #     plt.imshow(mask, cmap='tab20b')
        #     plt.show()
        #     print(i)
        segmented_mask[mask] = i

    if verbose:
        # Print the segmented mask
        print(segmented_mask)

    mask_id_list = np.unique(segmented_mask)
    separated_masks = {}

    for mask_id in mask_id_list:
        isolated_mask = segmented_mask.copy()
        isolated_mask[isolated_mask != mask_id] = -1
        if verbose:
            print(f"id: {mask_id}, tag: {image_component_id_lookup[mask_id]}")
            print(np.unique(isolated_mask))
            # plt.imshow(separated_masks[id], cmap='nipy_spectral')
            # plt.colorbar()
            # plt.show()
        separated_masks[mask_id] = isolated_mask

    image_component_mask = segmented_mask.copy()
    image_component_mask[image_component_mask != 0] = len(image_component_id_lookup) - 1
    separated_masks[len(image_component_id_lookup) - 1] = image_component_mask

    if verbose:
        plt.imshow(segmented_mask, cmap='nipy_spectral')
        plt.colorbar()
        plt.show()

    if task == "Cognitive Picture Description Task":
        num_components_baseline = 9
    else:
        num_components_baseline = 16

    if num_components != 0:
        num_components_baseline = num_components

    overall_gmm = GaussianMixture(random_state=0)
    
    points = get_pixel_coordinates(separated_masks[len(image_component_id_lookup) - 1], len(image_component_id_lookup) - 1)
    # points[:, 0] *= 1
    # points[:, 1] *= 1
    points[:, [0, 1]] = points[:, [1, 0]]
    overall_gmm = fit_gmm_to_component(points, num_components_baseline)


    if verbose:
        plot_gmm(None, None, overall_gmm.means_, overall_gmm.covariances_, 0, 'Overall GMM Baseline',
                 width, height, segmented_mask)

    return overall_gmm

def get_GMM_baseline_with_component_label_map(task="Cognitive Picture Description Task", height=1080, width=1920,
                                              verbose=False):
    component_labels = {}
    img = cv2.imread('./images/Cookie_theft_segmentation.png')
    image_component_id_lookup = {
        0: "Surrounding",
        1: "Cookie Jar",
        2: "Window",
        3: "Boy",
        4: "Lady",
        5: "Plate, Washing Cloth",
        6: "Girl",
        7: "Sink, Water",
        8: "Stool",
        9: "Dishes",
        10: "Image Components"
    }
    if task != "Cognitive Picture Description Task":
        img = cv2.imread('./images/Picnic_segmentation.png')
        image_component_id_lookup = {
            0: "Surrounding",
            1: "Tree, House, Car",
            2: "Kite",
            3: "Flag",
            4: "Boat",
            5: "Fishing",
            6: "Boy",
            7: "Lady",
            8: "Man",
            9: "Girl, Sand Castle",
            10: "Dog",
            11: "Glass, Beverage",
            12: "Book",
            13: "Basket",
            14: "Blanket",
            15: "Radio",
            16: "Sandals",
            17: "Image Components"
        }

    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape the image to a 2D array of pixels
    pixels = image_rgb.reshape(-1, 3)

    # Use a KD-Tree to find unique colors within a threshold
    threshold = 5
    tree = cKDTree(pixels)
    unique_colors = []
    labels = np.zeros(pixels.shape[0], dtype=int) - 1

    for i, pixel in enumerate(pixels):
        if labels[i] == -1:
            indices = tree.query_ball_point(pixel, threshold)
            unique_colors.append(pixel)
            labels[indices] = len(unique_colors) - 1

    unique_colors = np.array(unique_colors)

    if verbose:
        # Print unique colors
        print(f"Unique colors (within threshold): {unique_colors}")

    # Create a dictionary mapping from color tuples to segment labels
    color_to_label = {tuple(color): label for label, color in enumerate(unique_colors)}

    if verbose:
        # Print the mapping
        print(f"Color to label mapping: {color_to_label}")

    # Initialize the segmented mask with the same height and width as the input image
    segmented_mask = np.zeros((image_rgb.shape[0], image_rgb.shape[1]), dtype=np.int32)

    # Assign labels to each pixel based on the color
    for i, color in enumerate(unique_colors):
        mask = np.all(image_rgb == color, axis=-1)
        # if verbose:
        #     plt.imshow(mask, cmap='tab20b')
        #     plt.show()
        #     print(i)
        segmented_mask[mask] = i

    if verbose:
        # Print the segmented mask
        print(segmented_mask)

    mask_id_list = np.unique(segmented_mask)
    separated_masks = {}

    for mask_id in mask_id_list:
        isolated_mask = segmented_mask.copy()
        isolated_mask[isolated_mask != mask_id] = -1
        if verbose:
            print(f"id: {mask_id}, tag: {image_component_id_lookup[mask_id]}")
            print(np.unique(isolated_mask))
            # plt.imshow(separated_masks[id], cmap='nipy_spectral')
            # plt.colorbar()
            # plt.show()
        separated_masks[mask_id] = isolated_mask

    image_component_mask = segmented_mask.copy()
    image_component_mask[image_component_mask != 0] = len(image_component_id_lookup) - 1
    separated_masks[len(image_component_id_lookup) - 1] = image_component_mask

    if verbose:
        plt.imshow(segmented_mask, cmap='nipy_spectral')
        plt.colorbar()
        plt.show()

    param_grid = {
        'n_components': range(1, 4),
        'covariance_type': ['full'],
        # 'reg_covar': [1e-6, 1e-4, 1e-2, 1e-1]
    }

    # Search for best parameters for each component
    hyperparameters = {}
    for key in list(image_component_id_lookup.keys()):
        if key == 0 or key == list(image_component_id_lookup.keys())[-1]:
            continue
        if verbose:
            print(f"Searching: {key} - {image_component_id_lookup[key]}")
        # Define the GMM model
        gmm = GaussianMixture(random_state=0)
        grid_search = GridSearchCV(
            gmm, param_grid=param_grid, scoring=gmm_bic_score
        )
        # Perform GridSearchCV
        component_coords = get_pixel_coordinates(separated_masks[key], key)
        grid_search.fit(component_coords)

        # Best parameters
        best_params = grid_search.best_params_
        hyperparameters[key] = best_params

        if verbose:
            print(f'Best parameters: {best_params}')

    current_component_index = 0
    component_gmms = {}
    gmm_means = []
    gmm_covariances = []
    gmm_weights = []
    for key in list(image_component_id_lookup.keys()):
        # TODO: should I use image component mask?
        if key == 0 or key == len(image_component_id_lookup) - 1:
            continue
        if verbose:
            print(f"Fitting: {key} - {image_component_id_lookup[key]}")
        component_coords = get_pixel_coordinates(separated_masks[key], key)
        component_coords[:, [0, 1]] = component_coords[:, [1, 0]]
        gmm = fit_gmm_to_component(component_coords, hyperparameters[key]["n_components"])
        gmm_means.append(gmm.means_)
        gmm_covariances.append(gmm.covariances_)
        gmm_weights.append(gmm.weights_)
        component_gmms[image_component_id_lookup[key]] = gmm
        for component_count in range(gmm.weights_.shape[0]):
            component_labels[current_component_index] = image_component_id_lookup[key]
            current_component_index += 1
        component_labels[current_component_index] = 'Surroundings'

    if verbose:
        print(f'Combined GMM component labels: \n{component_labels}')

    combined_means = np.vstack(gmm_means)
    combined_covariances = np.vstack(gmm_covariances)
    combined_weights = np.hstack(gmm_weights)
    combined_weights /= np.sum(combined_weights)

    combined_gmm = GaussianMixture(n_components=len(combined_means), covariance_type='full')
    combined_gmm.means_ = combined_means
    combined_gmm.covariances_ = combined_covariances
    combined_gmm.weights_ = combined_weights
    combined_gmm.precisions_cholesky_ = np.linalg.cholesky(np.linalg.inv(combined_covariances)).transpose((0, 2, 1))

    component_gmms[len(image_component_id_lookup) - 1] = combined_gmm

    if verbose:
        plot_gmm(None, None, combined_gmm.means_, combined_gmm.covariances_, 0, 'GMM Components over Image Components',
                 width, height, segmented_mask)

    return combined_gmm, component_labels
