from PIL import Image
import os
import numpy as np

num_images = 1000
image_width, image_height = 200, 200
image_size = (image_height, image_width)
WHITE = (255, 255, 255)

# creates/returns the path to where we save the images
def create_image_folder():
    
    # create the path
    cur_dir = os.path.dirname(__file__)
    save_folder_path = os.path.join(cur_dir, 'images')
    
    # check if folder exists, create it if necessary
    if not os.path.exists(save_folder_path):
        os.mkdir(save_folder_path)
    
    return save_folder_path

# create the requested number of images
def create_images(save_path):

    # modifies creates the specified number of images
    for i in range(num_images):    
        # image name
        image_name = os.path.join(save_path, '%d.png'%(i + 1))
                 
        # creates a randomly assigned black and white image
        array = np.random.randint(2, size = image_size, dtype = np.uint8)
        image = Image.fromarray(array * 255, 'L')

        # save the new image
        image.save(image_name)
        image.close()

if __name__ == '__main__':
    save_folder_path = create_image_folder()
    create_images(save_folder_path)

