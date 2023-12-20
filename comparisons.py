import numpy as np
from csv import writer
from create_images import image_width, image_height
import os

sigma = 1

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

# get row and column from flattened index
def row_and_col(i):
    col = i % image_width
    row = np.floor(i / image_width)
    return row, col

# finds the distance of the pixel from the template
def get_distance(i, coords):
    row, col = row_and_col(i)
    min_distance = 1000
    for temp_row, temp_col in coords:
        distance = np.sqrt(((row - temp_row) ** 2) + ((col - temp_col) ** 2))
        if distance < min_distance:
            min_distance = distance
    return min_distance

# calculates the weight of the pixel
def get_weight(distance, metric, i):
# calulates the appropriate weight
    if 'linear' in metric:
        weight = 1 / distance
    elif 'quadratic' in metric:
        weight = 1 / distance ** 2
    elif 'logarithmic' in metric:
        weight = 1 / np.log(distance)
    elif 'gaussian' in metric:
        weight = np.exp(-1 * (distance ** 2) / (2 * (sigma ** 2)))
    elif 'central' in metric:
        row, col = get_coordinates(i)
                    # potential off by one error
        distance_to_center = np.sqrt(((row - image_width / 2) ** 2) + ((col - image_height / 2) ** 2))
        weight = 1 / distance_to_center
    elif 'unweighted' in metric:
        weight = 1
        
    return weight

# get the weighted mean of the flattened image data
def weighted_mean(array, metric, coords):
    numerator = 0
    denominator = 0
    for i, pixel in enumerate(array):
            
        # calculates the pixel's distance from the template
        # and the weight for that pixel
        distance = get_distance(i, coords)
        weight = get_weight(distance, metric, i)
        
        # keep adding to numerator and denominator
        numerator += weight * pixel
        denominator += weight
        
    # calculate mean and return
    mean = numerator / denominator
    return mean

# returns the locations of the black pixels (row, col) in an image
def get_coordinates(path):
    image_old = np.load(path)
    image = image_old.flatten()
    
    black_pixels = []
    for i, pixel in enumerate(image):
        if pixel == 0:
            black_pixels.append(row_and_col(i))
    return black_pixels

# calculates the weighted or unweighted pearsons depending on type
def pearsons(array_name, stim_arrays_path, template_name, temp_arrays_path, metric, coords):
    
    # get locations of template and array
    stim_path = os.path.join(stim_arrays_path, array_name)
    template_path = os.path.join(temp_arrays_path, template_name)
    
    # load the template and the array
    stim_old = np.load(stim_path)
    temp_old = np.load(template_path)
    stimulus = stim_old.flatten() / 255 # reduce back to ones and zeros
    template = temp_old.flatten() / 255
    
    # mean pixel values
    mean_stim = weighted_mean(stimulus, metric, coords)
    mean_temp = weighted_mean(template, metric, coords)
    
    # caclulating the modified pearson coefficient
    numerator = 0
    denom_stim, denom_temp = 0
    for i, stim_pixel in enumerate(stimulus):
            # get distance and weight for pixel
            distance = get_distance(i, coords)
            weight = get_weight(distance, metric, i)
            
            # calculate numerator and denominator
            numerator += weight * (stim_pixel - mean_stim) * (template[i] - mean_temp)
            denom_stim += weight * ((stim_pixel - mean_stim) ** 2)
            denom_temp += weight * ((stim_pixel - mean_temp) ** 2)
    denom_stim = np.sqrt(denom_stim)
    denom_temp = np.sqrt(denom_temp)
    denominator = denom_stim * denom_temp
    
    result = numerator / denominator
    
    return result


if __name__ == '__main__':
        
    # various save and load paths
    stim_arrays_path, temp_arrays_path, metric_list = get_paths()
    
    # list the file names in the array and template folders
    stims = os.listdir(stim_arrays_path)
    templates = os.listdir(temp_arrays_path)
    
    # for each template, get a list of the points that are the stimulus
    template_coords = []
    for template in templates:
        path = os.path.join(temp_arrays_path, template) 
        template_coords.append(get_coordinates(path).copy())
    
    # perform the weighted vs unweighted pearson tests and save results
    # go over each metric (each metric is stored in a unqiue csv file)
    for metric in metric_list:
        
        # open the metric-specific csv file for writing
        with open(metric, 'w', newline = '') as f:
                
            # setup a writer/header and write the header
            write = writer(f)
            header = ['stimulus number'] + map(split, templates)
            write.writerow(header)
            
            # for each array, perform the analysis on all of the templates
            for stim in stims:
                results = [split(stim)]
                for i, template in enumerate(templates):
                        result = pearsons(stim, stim_arrays_path, template, \
                                          temp_arrays_path, metric, template_coords[i])
                        results.append(str(result))
                write.writerow(results)
            f.close()
    
    