from screeninfo import get_monitors

# number of practice and real stimuli the subject will be shown
num_practice = 5
num_real = 10

background_color = (1,1,1) # background color for screen
text_color = (0, 0, 0) # text color

# get screen size for each monitor in the system
def get_screen_info():
    win_info = []
    for m in get_monitors():
        win_info.append((m.width, m.height))
    return win_info

# get info for subject screen
win_info = get_screen_info()
screen_size = win_info[0]
screen_width = win_info[0][0]
screen_height = win_info[0][1]

# getting the valid letters and numbers for user info
def get_valid_chars():
    valid_letters = []
    valid_numbers = []
    
    # valid digits (0 - 9)
    for i in range(48, 58):
        valid_numbers.append(chr(i))
        
    # valid lowercase letters (a - z)
    for i in range(97, 123):
        valid_letters.append(chr(i))
        
    # valid uppercase letters (A - Z)
    for i in range(65, 91):
        valid_letters.append(chr(i))
    
    return valid_letters, valid_numbers

valid_letters, valid_numbers = get_valid_chars()

explanation_text = 'You will be shown a series of images.\n\n'\
                    'In some of these images there is a hidden "+" sign in the middle '\
                    'of the image on the screen.\n\nPlease press "Y" if you believe that '\
                    'you see a cross hidden in the middle of the image.\n\n' \
                    'Please press "N" if you do not believe that you see a cross hidden in the middle '\
                    'of the image.\n\n\n'\
                    'Please let your experimenter know if you encounter any issues or if you would '\
                    'like to terminate your participation in the experiment.\n\n\n\n'\
                    'Press the spacebar to continue.\n\n\n'\

practice_text = 'You will now be given %d practice stimuli.\n\n\n\n'\
                'Remember to press "Y" if you believe that you see a hidden "+" sign.\n\n\n\n'\
                'Remember to press "N" if you do not believe that you see a hidden "+" sign.\n\n\n\n'\
                'Press the spacebar to continue.'%num_practice
                
real_text = 'You will now participate in the real experiment\n\n\n\n'\
            'Remember to press "Y" if you believe that you see a hidden "+" sign.\n\n\n\n'\
            'Remember to press "N" if you do not believe that you see a hidden "+" sign.\n\n\n\n'\
            'Press the spacebar to continue.'


                        
    

 