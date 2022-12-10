# I used the following website: https://medium.com/@vedanshvijay/steganography-5d9d8a557587
# cryptosteganography: https://onthegoalways.com/blog/steganography/

import cv2
import os
import shutil
from subprocess import call,STDOUT
from cryptosteganography import CryptoSteganography



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
def encode_string(input_string,crypto_steganography):
    crypto_steganography.hide('./temp/0.png', './temp/0.png', input_string)
    print("The message is stored in the output_video.mp4 file")



# This function would decode the hidden message by extracting frames from the video
def decode_string(video, password):
    frame_extraction(video)        # Extracting each frame from the video
    crypto_steganography = CryptoSteganography(password)
    # Extract the message from stego image.
    secret = crypto_steganography.retrieve('./temp/0.png')
    print("***********************************************************************************\n"
          "The hidden message: " + secret+ "\n"+
          "***********************************************************************************\n")
    clean_temp()

# This function would delete the temp directory
def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")


# This function would extraxt audio from the video so as to stitch them back later.
def input_main(f_name,password):
    input_string = input("Enter the message :")   # To collect the message
    frame_extraction(f_name)
    crypto_steganography = CryptoSteganography(password)
    # The call function would be used to extract the audio and then stitch it again properly with the frames extracted.
    call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    encode_string(input_string,crypto_steganography)

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
        print("1.Hide a message in video with key\n2.Reveal the secret from the video with key\n")
        print("Any other value to exit\n")
        choice = input("Enter your choice :")
        if choice == '1':
            f_name=input("Enter the name of video file with extension:")
            password = input("Enter password key:")
            input_main(f_name,password)
        elif choice == '2':
            password = input("Enter password key:")
            decode_string(input("Enter the name of video with extension :"),password)
        else:
            break



