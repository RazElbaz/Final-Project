# I used the following website: https://medium.com/@vedanshvijay/steganography-5d9d8a557587
# Installing and Importing required modules:
from stegano import lsb
import cv2
import math
import os
import shutil
from subprocess import call,STDOUT


# Defining the String Split function🪓
# Now that we have all the extracted frames, we can divide the strings into small chunks and hide each chunk of the message inside a frame.
def split_string(split_str,count=10):
    per_c=math.ceil(len(split_str)/count)
    c_cout=0
    out_str=''
    split_list=[]
    for s in split_str:
        out_str+=s
        c_cout+=1
        if c_cout == per_c:
            split_list.append(out_str) # The message is divided into substrings
            out_str=''
            c_cout=0
    if c_cout!=0:
        split_list.append(out_str)
    return split_list


# Defining frame extraction function🎞
# Now that we have the video, our first step should be defining a frame extraction function to extract frames in the form of images from the video.
def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    temp_folder="./temp"            # Temporary folder created to store the frames and audio from the video.
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1


# This function would embed the splitted string into the frames extracted from the video.
def encode_string(input_string,root="./temp/"):
    split_string_list=split_string(input_string)   # Acquire the splitted string from the message.
    for i in range(0,len(split_string_list)):
        f_name="{}{}.png".format(root,i)                   
        secret_enc=lsb.hide(f_name,split_string_list[i])   # Embedded the splitted string into each frame.
        secret_enc.save(f_name)                            # Saved the frames after hidding the strings.
        print("[INFO] frame {} holds {}".format(f_name,lsb.reveal(f_name)))
    print("The message is stored in the output_video.mp4 file")



# This function would decode the hidden message by extracting frames from the video
def decode_string(video):
    frame_extraction(video)        # Extracting each frame from the video
    secret=[]
    root="./temp/"
    for i in range(len(os.listdir(root))):
        try:
            # Find a message in an image (with the LSB technique).
            secret_dec=lsb.reveal("./temp/{}.png".format(i))
            secret.append(secret_dec)
        except:
            break

    print(''.join([i for i in secret]))
    clean_temp()

# This function would delete the temp directory 
def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")


# This function would extraxt audio from the video so as to stitch them back later.
def input_main(f_name):
    input_string = input("Enter the message :")   # To collect the message
    frame_extraction(f_name)
    # The call function would be used to extract the audio and then stitch it again properly with the frames extracted.
    call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    encode_string(input_string)
    # Stitching together the frames🖼 and the audio🔊
    # using ffmpeg to stitch together all our frames with a hidden message to form a video and then lay out the audio:
    call(["ffmpeg", "-i", "temp/%d.png" , "-vcodec", "png", "temp/output_video.mp4", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    # this code above creates the video with our secret message hidden in it.
    call(["ffmpeg", "-i", "temp/output_video.mp4", "-i", "temp/audio.mp3", "-codec", "copy", "output_video.mp4", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    clean_temp()

#Inputting the video📹
# First we would decide the inputs. That is first the user needs to specify whether they want to encode or decode a video. Then they would input the video file with extension which we would read using OpenCV.
if __name__ == "__main__":    
    while True:
        print("1.Hide a message in video\n2.Reveal the secret from the video\n")
        print("Any other value to exit\n")
        choice = input("Enter your choice :")
        if choice == '1':
            f_name=input("Enter the name of video file with extension:")
            input_main(f_name)
        elif choice == '2':
            decode_string(input("Enter the name of video with extension :"))
        else:
            break