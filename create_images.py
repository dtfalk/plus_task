from PIL import Image
import os
import numpy as np

num_images = 20
image_width, image_height = 50, 50
image_size = (image_height, image_width)
WHITE = (255, 255, 255)

# creates/returns the path to where we save the images.
def create_image_folder():
    
    # create the path
    cur_dir = os.path.dirname(__file__)
    stimulus_path = os.path.join(cur_dir, 'stimuli')
    template_path = os.path.join(cur_dir, 'templates')
    stim_image_path = os.path.join(stimulus_path, 'images')
    stim_array_path = os.path.join(stimulus_path, 'arrays')
    temp_image_path = os.path.join(template_path, 'images')
    temp_array_path = os.path.join(template_path, 'arrays')
    
    # check if folder exists, create it if necessary
    if not os.path.exists(stimulus_path):
        os.mkdir(stimulus_path)
    
    # check if folder exists, create it if necessary
    if not os.path.exists(template_path):
        os.mkdir(template_path)
        
    # check if folder exists, create it if necessary
    if not os.path.exists(stim_image_path):
        os.mkdir(stim_image_path)
    
    # check if folder exists, create it if necessary
    if not os.path.exists(stim_array_path):
        os.mkdir(stim_array_path)
    
    # check if folder exists, create it if necessary
    if not os.path.exists(temp_image_path):
        os.mkdir(temp_image_path)
    
    # check if folder exists, create it if necessary
    if not os.path.exists(temp_array_path):
        os.mkdir(temp_array_path)
        
    return stim_image_path, stim_array_path, \
        temp_image_path, temp_array_path

# creates the template images for comparison
def create_templates(temp_image_path, temp_array_path):
    
    # true widths are doubled plus one
    widths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # find screen center
    horiz_center = image_width // 2
    vert_center = image_height // 2

    # make template images for all widths
    for i, width in enumerate(widths):
        
         # create empty array (black)
        array = np.zeros((image_height, image_width))
        
        for j, row in enumerate(array):
            for k, _ in enumerate(row):
                if abs(j - vert_center) < width or \
                    abs(k - horiz_center) < width:
                    array[j][k] = 255
    
        # create image and save
        image_name = os.path.join(temp_image_path, '%d.png'%(width * 2))
        image = Image.fromarray(array.astype(np.uint8), 'L')
        image.save(image_name)
        image.close()
        
        # save array
        array_name = os.path.join(temp_array_path, '%d.npy'%(width * 2))
        np.save(array_name, array)
    
# create the requested number of images
def create_images(stim_image_path, stim_array_path):

    # modifies creates the specified number of images
    for i in range(num_images):    
                 
        # creates a randomly assigned black and white image
        array = np.random.randint(2, size = image_size, dtype = np.uint8)
        image = Image.fromarray(array * 255, 'L')

        # save the new image
        image_name = os.path.join(stim_image_path, '%d.png'%(i + 1))
        image.save(image_name)
        image.close()
        
        # save the array
        array_name = os.path.join(stim_array_path, '%d.npy'%(i + 1))
        np.save(array_name, array)

if __name__ == '__main__':
    stim_image_path, stim_array_path, \
        temp_image_path, temp_array_path = create_image_folder()
    create_templates(temp_image_path, temp_array_path)
    create_images(stim_image_path, stim_array_path)

