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

def create_template_means(templates, temp_arrays_path):
    mean_dict = {}
    for i, template_filename in enumerate(templates):
        temp_path = os.path.join(temp_arrays_path, template_filename)
        template = np.load(temp_path)
        for metric in metric_list:
            mean_dict[template_filename + '_' + str(metric)] = weighted_mean(template, metric, widths[i])
    return mean_dict

def split(string):
    return string.split('.')[0]

# finds the distance of the pixel from the template
def get_distance(row, col, width):
    # find vertical and horizontal distance from template cross
    vert_distance = abs(row - image_center)
    horiz_distance = abs(col - image_center)
    
    # if either is within the cross itself, return distance = 0
    if vert_distance <= width or horiz_distance <= width:
        return 0

    # otherwise return the minimum of the two
    min(vert_distance, horiz_distance)
    return min(vert_distance, horiz_distance)


# calculates the weight of the pixel
def get_weight(distance, metric, row, col):
# calulates the appropriate weight
    if distance == 0:
        weight = 1
    elif 'linear' in metric:
        weight = 1 / distance
    elif 'quadratic' in metric:
        weight = 1 / distance ** 2
    elif 'logarithmic' in metric:
        weight = 1 / np.log(distance)
    elif 'gaussian' in metric:
        weight = np.exp(-1 * (distance ** 2) / (2 * (sigma ** 2)))
    elif 'central' in metric:
        distance_to_center = np.sqrt(((row - image_width / 2) ** 2) + ((col - image_height / 2) ** 2))
        weight = 1 / distance_to_center
    elif 'unweighted' in metric:
        weight = 1
        
    return weight

# get the weighted mean of the flattened image data
def weighted_mean(array, metric, width):
    numerator = 0
    denominator = 0
    for row, row_list in enumerate(array):
        for col, pixel in enumerate(row_list):
            
            # calculates the pixel's distance from the template
            # and the weight for that pixel 
            distance = get_distance(row, col, width)
            weight = get_weight(distance, metric, row, col)

            numerator += weight * int(pixel)
            denominator += weight

    # calculate mean and return
    mean = numerator / denominator
    return mean

# calculates the weighted or unweighted pearsons depending on type
def pearsons(stimulus, template, stimulus_mean, template_mean, metric, width):

    # caclulating the modified pearson coefficient
    numerator = 0
    denom_stim = 0 
    denom_temp = 0
    for row, row_list in enumerate(stimulus):
        for col, stim_pixel in enumerate(row_list):
           
            # get distance and weight for pixel
            distance = get_distance(row, col, width)
            weight = get_weight(distance, metric, row, col)

            
            # update numerator and denominator
            base_stim = stim_pixel - stimulus_mean
            base_temp = template[row][col] - template_mean
            numerator += weight * base_stim * base_temp
            denom_stim += weight * (base_stim ** 2)
            denom_temp += weight * (base_temp ** 2)
            
    # calculate final denominator
    denom_stim = np.sqrt(denom_stim)
    denom_temp = np.sqrt(denom_temp)
    denominator = denom_stim * denom_temp
    
    # calculate final result
    result = numerator / denominator
    
    return result

# Define a key function to extract the numerical part of the filename
def extract_number(filename):
    # Extract the number from the filename and convert it to an integer
    return int(filename.split('.')[0])

if __name__ == '__main__':
    start_time = local_clock()
    # various save and load paths
    stim_arrays_path, temp_arrays_path, metric_list = get_paths()
    
    # list the file names in the array and template folders
    stims = sorted(os.listdir(stim_arrays_path), key = extract_number)
    templates = sorted(os.listdir(temp_arrays_path), key = extract_number)

    # weighted means of templates as a dictionary
    mean_dict = create_template_means(templates, temp_arrays_path)
    print('mean calc time: %f'%(local_clock() - start_time))
    
    # perform the weighted vs unweighted pearson tests and save results
    # go over each metric (each metric is stored in a unqiue csv file)
    for metric in metric_list:
        
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
                        stimulus_mean = mean_dict[stimulus_filename + '_' + metric]
                    except KeyError:
                        stimulus_mean = weighted_mean(stimulus, metric, widths[i])
                        mean_dict[stimulus_filename + '_' + metric] = stimulus_mean
                    
                    result = pearsons(stimulus, template, stimulus_mean, template_mean, metric, widths[i])
                    results.append(str(result))
                write.writerow(results)
            f.close()
    print('runtime: %f'%(local_clock() - start_time))
    
    