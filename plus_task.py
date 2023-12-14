from psychopy import visual, core
from random import randint
from create_images import num_images, image_width, image_height
from helper_functions import *

# factor by which to scale each of the stimuli
image_size = image_width * image_height
scale_factor = screen_height / image_height
scaled_image_size = (image_width * scale_factor, image_height * scale_factor)

# The experiment itself
def experiment(gametype, data_save_path, outlet, win, subject_name, subject_number):
    
    # path for images folder and image extension label
    cur_dir = os.path.dirname(__file__)
    images_dir = os.path.join(cur_dir, 'images')
    extension = '.png'

    # various variables for handling the game
    images_shown = 0
    reset = False
    start_time = core.Clock()
    first_write = True # check to make sure that we are not overwriting an existing file

    # initialize a starting image
    while True:
        stimulus_number = randint(1, num_images)
        image_path = os.path.join(images_dir, str(stimulus_number) + extension)
        if not stimulus_number in used_images:
            image = visual.ImageStim(win = win, image = image_path, 
                                     size = scaled_image_size, units = 'pix')
            break
    
    # Loop for handling events
    while True:
        
        # break loop if we have shown the specified number of images
        if (images_shown >= num_real and gametype == 'real') \
        or (images_shown >= num_practice and gametype == 'practice'):
            return
        
        # handling key presses
        for key in event.getKeys():
            if key == 'escape':
                win.close()
                core.quit()
            elif key == 'y':
                reset = True
                if gametype == 'real':
                    response_time = start_time.getTime()
                    push_sample(outlet, 'YEySS')
                    record_response(data_save_path, True, response_time, subject_name, 
                                    subject_number, stimulus_number, first_write)
                    first_write = False
            elif key == 'n':
                reset = True
                if gametype == 'repopoal':
                    response_time = start_time.getTime()
                    push_sample(outlet, 'NOOO')
                    record_response(data_save_path, False, response_time, subject_name,
                                    subject_number, stimulus_number, first_write)
                    first_write = False
            
        # while the trial continues on
        if not reset:
            # define the image and put it on the screen
            image.draw()
            win.n()
            
        # end of a trial
        else:
            
            # increment/reset variables for next trial
            images_shown += 1
            reset = False
            win.flip()
            event.clearEvents()
    
            # add the current stimuli number 
            used_images.append(stimulus_number)
            
            # get a new iymage
            while True:
                if len(used_images) == num_images:
                    break
                stimulus_number = randint(1, num_images)
                image_path = os.path.join(images_dir, str(stimulus_number) + extension)
                if not stimulus_number in used_images:
                    image = visual.ImageStim(win = win, image = image_path,
                                             size = scaled_image_size, units = 'pix')
                    break
            
            # reset the trial timer
            start_time.reset()
            win.callOnFlip(push_sample, outlet = outlet, tag = 'STRT')

if __name__ == '__main__':
    
    # Create LSL outlet
    outlet = initialize_outlet()
    
    # initialize window and mouse object (set mouse to invisible)
    win = visual.Window(size = screen_size, fullscr = True, color = background_color)
    mouse = event.Mouse(win = win)
    mouse.setVisible(False)
    
    # get user info and where to store their results
    subject_name, subject_number, data_save_path = opening_screen(win)
    
    # explain the experiment to the subject
    experiment_explanation(win)
    
    # global variable to keep track of which stimuli we have used
    # so we don't have to keep passing and returning it.
    # Will be referenced in the "experiment" function.
    used_images = [] 
    
    # gives the subject some practice trials
    practice_instructions(win)
    experiment('practice', data_save_path, outlet, win, subject_name, subject_number)
    
    # move onto the real experiment
    real_instructions(win)
    experiment('real', data_save_path, outlet, win, subject_name, subject_number)