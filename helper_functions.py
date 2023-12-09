import os
from pylsl import StreamOutlet, StreamInfo
from psychopy import visual, core, event
import csv
from constants import *

# Initializes lab streaming layer outlet
def initialize_outlet():
    info_events = StreamInfo('event_stream', 'events', 1, 0, 'string')
    outlet = StreamOutlet(info_events)
    return outlet

# pushes a sample to the outlet
def push_sample(outlet, tag):
    outlet.push_sample([tag])
    
# gets the subject's name
# need to check if letter or alpha
def get_subject_name(win):
    name_prompt = 'Subject Name: '
    subject_name = ''
    
    while True:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
                return
            elif key == 'return':
                return subject_name
            elif key == 'backspace':
                if subject_name != '':
                    subject_name = subject_name[:-1]
            elif key == 'space':
                subject_name = subject_name + ' '
            elif key in valid_letters:
                subject_name = subject_name + key
        prompt = visual.TextStim(win = win, text = name_prompt + subject_name, height = 0.2, color = text_color)
        prompt.draw()
        win.flip()

def get_subject_num(win):
    num_prompt = 'Subject Number: '
    subject_num = ''
    
    while True:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
                return
            elif key == 'return':
                return subject_num
            elif key == 'backspace':
                if subject_num != '':
                    subject_num = subject_num[:-1]
            elif key in valid_numbers:
                subject_num = subject_num + key
        prompt = visual.TextStim(win = win, text = num_prompt + subject_num, height = 0.2, color = text_color)
        prompt.draw()
        win.flip()
                
# gets the subject's name and subject number
def get_subject_info(win):
    
    # get subject name and subject number
    subject_name = get_subject_name(win)
    subject_num = get_subject_num(win)
    
    return subject_name, subject_num, win

# Returns user name, subject number, and path to where
# we will store their data.
def opening_screen(win):
    
    # file extenstion where we save data to
    extension = '.csv'
    
    # current directory
    cur_dir = os.path.dirname(__file__)
    
    # get user's name and user's subject number
    subject_name, subject_number, win = get_subject_info(win)
    
    # create save folder if necessary and get the save path
    subject_data_folder = os.path.join(cur_dir, 'subject_data')
    if not os.path.isdir(subject_data_folder):
        os.mkdir(subject_data_folder)
    
    # File to where we save the user's data
    data_save_path = os.path.join(subject_data_folder, subject_number + extension)
    
    return subject_name, subject_number, data_save_path

# explains the experiment to the subject
def experiment_explanation(win):
    
    # text height and preparing the explanation text
    height = 0.07
    prompt = visual.TextStim(win = win, text = explanation_text, height = height,
                            color = text_color, wrapWidth = 1.9, alignText = 'left')
    
    # wait for the user to press spacebar before the experiment continues
    while True:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
            if key == 'space':
                return
        prompt.draw()
        win.flip()

def practice_instructions(win):
    
    # text height and preparing the explanation text
    height = 0.07
    prompt = visual.TextStim(win = win, text = practice_text, height = height,
                            color = text_color, wrapWidth = 1.9, alignText = 'left')
    
    # wait for the user to press spacebar before the experiment continues
    while True:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
                return
            if key == 'space':
                return
        prompt.draw()
        win.flip()

def real_instructions(win):
    
    # text height and preparing the explanation text
    height = 0.07
    prompt = visual.TextStim(win = win, text = real_text, height = height,
                            color = text_color, wrapWidth = 1.9, alignText = 'left')
    
    # wait for the user to press spacebar before the experiment continues
    while True:
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                win.close()
                core.quit()
                return
            if key == 'space':
                return
        prompt.draw()
        win.flip()

def record_response(data_save_path, response, response_time, subject_name, subject_number, stimulus_number):
    data = [str(subject_name), str(subject_number), str(stimulus_number), str(response), str(response_time)]
    
    # if csv file does not exist, then write the header and the data
    if not os.path.exists(data_save_path):
        header = ['subject_name', 'subject_number', 'stimulus_number', 'response', 'response_time']
        with open(data_save_path, 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerow(data)
            file.close()
    # otherwise just write the data
    else:
        with open(data_save_path, 'a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            file.close()
    return