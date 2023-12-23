import numpy as np
from csv import writer
from create_images import image_width, image_height
import os
from pylsl import local_clock

sigma = 1
image_center = image_width // 2 # assumes a square image

# true widths are doubled plus one
widths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# template names for csv file
template_names = ['temp2', 'temp4', 'temp6', 'temp8', 'temp10', \
                'temp12', 'temp14', 'temp16', 'temp18', 'temp20']
header = ['stimulus number'] + template_names

# array, templates and results save paths
def get_paths():
    cur_dir = os.path.dirname(__file__)
    
    # where to find stimulus arrays
    stim_arrays_path = os.path.join(cur_dir, 'stimuli')
    stim_arrays_path = os.path.join(stim_arrays_path, 'arrays')
    
    # where to find template arrays
    temp_arrays_path = os.path.join(cur_dir, 'templates')
    temp_arrays_path = os.path.join(temp_arrays_path, 'arrays')
    
    # paths for storing results
    results_path = os.path.join(cur_dir, 'results')
    linear_path = os.path.join(results_path, 'linear.csv')
    quadratic_path = os.path.join(results_path, 'quadratic.csv')
    central_path = os.path.join(results_path, 'central.csv')
    log_path = os.path.join(results_path, 'logarithmic.csv')
    gaussian_path = os.path.join(results_path, 'gaussian.csv')
    unweighted_path = os.path.join(results_path, 'unweighted.csv')
    
    # store csv names as a list
    result_files_list = [linear_path, quadratic_path, central_path, \
            log_path, unweighted_path, gaussian_path]
    
    # create save folder if necessary
    if not os.path.exists(results_path):
        os.mkdir(results_path)
        
    return stim_arrays_path, temp_arrays_path, result_files_list


def split(string):
    return string.split('.')[0]

# get the weighted mean of the image data
def weighted_mean(array, weight_matrix):
    weighted_sum = np.sum(weight_matrix * array)
    total_weight = np.sum(weight_matrix)
    
    if total_weight > 0:
        return weighted_sum / total_weight
    
    return 0

# calculates the weighted or unweighted pearsons depending on type
def pearsons(stimulus, template, stimulus_mean, template_mean, weight_matrix):

    base_stim = stimulus - stimulus_mean
    base_temp = template - template_mean
    
    numerator = np.sum(weight_matrix * base_stim * base_temp)
    denom_stim = np.sqrt(np.sum(weight_matrix * np.square(base_stim)))
    denom_temp = np.sqrt(np.sum(weight_matrix * np.square(base_temp)))
    
    return numerator / (denom_stim * denom_temp)

# Define a key function to extract the numerical part of the filename
def extract_number(filename):
    # Extract the number from the filename and convert it to an integer
    return int(filename.split('.')[0].replace('temp_', ''))
    
# calculates a distance matrix
def distances(filename, folder, width):
    # Load the file
    filepath = os.path.join(folder, filename)
    file = np.load(filepath)

    # Create a grid of row and column indices
    row_indices, col_indices = np.indices(file.shape)

    # Calculate vertical and horizontal distances from the image center
    vert_distances = np.abs(row_indices - image_height)
    horiz_distances = np.abs(col_indices - image_width)

    # Calculate the minimum distance from the center for each pixel
    # and set it to 0 if within the width of the cross
    distance_matrix = np.minimum(vert_distances, horiz_distances)
    distance_matrix = np.where((vert_distances <= width) | (horiz_distances <= width), 0, distance_matrix)

    return distance_matrix.flatten()

# calculates a weight matrix
def weights(filename, folder, metric, distance_matrix):
    # creates a matrix of all ones (helps handles divsion by zero)
    weights_matrix = np.ones_like(distance_matrix)
    
    non_zero_distances = distance_matrix != 0
    if 'linear' in metric:
        weights_matrix[non_zero_distances] = 1 / distance_matrix[non_zero_distances]
    elif 'quadratic' in metric:
        weights_matrix[non_zero_distances] = 1 / np.square(distance_matrix[non_zero_distances])
    elif 'logarithmic' in metric:
        weights_matrix[non_zero_distances] = 1 / np.log(distance_matrix[non_zero_distances])
    elif 'gaussian' in metric:
        weights_matrix[non_zero_distances] = np.exp(-1 * np.square(distance_matrix[non_zero_distances]) / (2 * np.square(sigma)))
    elif 'central' in metric:
        filepath = os.path.join(folder, filename)
        file = np.load(filepath)
        for row, row_list in enumerate(file):
            for col, _ in enumerate(row_list):
                distance_to_center = np.sqrt(np.square(row - image_height) + np.square(col - image_width))
                
                index = (image_height * row) + col
                if distance_to_center != 0:
                    weights_matrix[index] = 1 / distance_to_center
                    
                else:
                    weights_matrix[index] = 1
    return weights_matrix.reshape((50, 50)).copy()
    
if __name__ == '__main__':
    start_time = local_clock()
    # various save and load paths
    stim_arrays_path, temp_arrays_path, metric_list = get_paths()
    
    # list the file names in the array and template folders
    stims = sorted(os.listdir(stim_arrays_path), key = extract_number)
    templates = sorted(os.listdir(temp_arrays_path), key = extract_number)

    # calculate a set of weight and distance matrices
    distance_matrices = {}
    weights_matrices = {}
    for i, template in enumerate(templates):
        distance_matrices[template] = distances(template, temp_arrays_path, widths[i])
    for matrix_name, distance_matrix in distance_matrices.items():
        for metric in metric_list:
            metric_name = os.path.basename(split(metric))
            weights_matrices[matrix_name + '_' + metric_name] = weights(template, temp_arrays_path, metric, distance_matrix)
    i = 0
    for matrix_name, matrix in weights_matrices.items():
        for comp_name, comp_matrix in weights_matrices.items():
            if np.array_equal(matrix, comp_matrix):
                i += 1
                print(matrix_name + ' and ' + comp_name)
    print(i / 2)

    # weighted means of templates as a dictionary
    mean_dict = {}
    for template in templates:
        for metric in metric_list:
            filepath = os.path.join(temp_arrays_path, template)
            file = np.load(filepath)
            metric_name = os.path.basename(split(metric))
            weight_matrix = weights_matrices[template + '_' + metric_name]
            mean_dict[template + '_' + metric] = weighted_mean(file, weight_matrix)
    print('mean calc time: %f'%(local_clock() - start_time))
    
    # perform the weighted vs unweighted pearson tests and save results
    # go over each metric (each metric is stored in a unqiue csv file)
    for metric in metric_list:
        metric_name = os.path.basename(split(metric))
        
        # open the metric-specific csv file for writing
        with open(metric, 'w', newline = '') as f:
                
            # setup a writer/header and write the header
            write = writer(f)
            write.writerow(header)
            
            # for each array, perform the analysis on all of the templates
            for stimulus_filename in stims:
                
                # load the stimulus
                stimulus_path = os.path.join(stim_arrays_path, stimulus_filename)
                stimulus = np.load(stimulus_path)
                
                # prep the results list
                results = [split(stimulus_filename)]
                
                for i, template_filename in enumerate(templates):
                    
                    # load the template and its mean
                    template_path = os.path.join(temp_arrays_path, template_filename)
                    template = np.load(template_path) 
                    template_mean = mean_dict[template_filename + '_' + str(metric)]
                    
                    # load stimulus mean if already calculated, otherwise calculate it
                    try:
                        stimulus_mean = mean_dict[stimulus_filename + '_' + metric + '_' + str(widths[i])]
                    except KeyError:
                        stimulus_mean = weighted_mean(stimulus, weights_matrices[template_filename + '_' + metric_name])
                        mean_dict[stimulus_filename + '_' + metric + '_' + str(widths[i])] = stimulus_mean
                    
                    result = pearsons(stimulus, template, stimulus_mean, template_mean, weights_matrices[template_filename + '_' + metric_name])
                    results.append(str(result))
                write.writerow(results)
            f.close()
    print('runtime: %f'%(local_clock() - start_time))