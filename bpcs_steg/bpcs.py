import os
from PIL import Image 
import numpy as np

from bpcs_steg.get_bin import * 
from bpcs_steg.fileType import *

### constants 
THRESHOLD = 0.3 #threshold to determine a block as complex 

### small functions ###

# segment data into 8x8 blocks
def get_8x8_secret(secret_bin): #turns secret into 8x8 array 
    temp = "0" # flag 0 = not conjugated, 1 = conjugated 

    #get 63 bits of secret data - first bit is saved as conjugation flag 
    if len(secret_bin)>63:
        temp = temp + secret_bin[:63]
        secret_bin = secret_bin[63:]
    else:
        temp = temp + secret_bin
        secret_bin = ""
        while len(temp)<64:
            temp = temp + "0" # padding, will likely make complexity low but conjugating will fix this 

    secret_8x8 = np.zeros((8,8), dtype='uint8') #create an 8x8 array 
    for i in range(8): #copy secret data into array 
        for j in range(8):
            secret_8x8[i,j]=temp[0]
            temp = temp[1:]

    return secret_8x8, secret_bin


def get_8x8_image(arr, startY, startX, bit): #gets 8x8 block from image array 
    image_8x8 = np.zeros((8,8), dtype='uint8') #create an 8x8 array
    for i in range(startY, startY+8): #copies 8x8 section of bitplane into array
        for j in range(startX, startX+8):
            image_8x8[i%8,j%8] = arr[bit,i,j]

    return image_8x8


# convert PBC to CGC
def pbc_to_cgc(arr, height, width):

    cgc_arr = np.zeros((8,height, width), dtype='uint8')
    for i in range(8): #for each of the bitplanes 
        for j in range(height): #each row of bitplane i
            if j==0:
                cgc_arr[i][0] = arr[i][0] #first row stays the same 
            else:
                cgc_arr[i][j] = np.logical_xor(arr[i][j], arr[i][j-1]) #XOR each row with the previous row

    # print("converted to cgc")

    return cgc_arr


# convert CGC to PBC 
def cgc_to_pbc(arr, height, width):

    pbc_arr = np.zeros((8, height, width), dtype='uint8')
    for i in range(8): #for each of the bitplanes
        for j in range(height): #each row of bitplane i 
            if j==0:
                pbc_arr[i][0] = arr[i][0] #first row stays the same 
            else: 
                pbc_arr[i][j] = np.logical_xor(arr[i][j], pbc_arr[i][j-1]) #XOR each row of the cgc array with the previous row of the PBC array

    # print("converted to pbc")

    return pbc_arr


# determine complexity of 2d block 
def complexity(arr, height, width):

    # max complexity = (rows-1)*cols + (cols-1)*rows
    max_complexity = float((height-1)*width + (width-1)*height)

    changes = 0.0 

    # number of colour changes horizontally 
    curr_bit_val = arr[0,0]
    for i in range(height):
        for j in range(width):
            if curr_bit_val != arr[i,j]:
                changes +=1
                curr_bit_val= arr[i,j]

    # number of colour changes vertically
    curr_bit_val = arr[0,0]
    for i in range(width):
        for j in range(height):
            if curr_bit_val != arr[j,i]:
                changes +=1
                curr_bit_val = arr[j,i]  

    return round(changes/max_complexity, 6)


# conjugate block 
def conjugate(block):
    # wc = checkerboard with 0 in upper left - has maximum complexity for 8x8 block
    wc = np.array([[0,1,0,1,0,1,0,1],
                  [1,0,1,0,1,0,1,0],
                  [0,1,0,1,0,1,0,1],
                  [1,0,1,0,1,0,1,0],
                  [0,1,0,1,0,1,0,1],
                  [1,0,1,0,1,0,1,0],
                  [0,1,0,1,0,1,0,1],
                  [1,0,1,0,1,0,1,0]])

    # xor block with wc to get conjugate 
    conj_block = np.zeros((8,8), dtype='uint8')

    for i in range(8):
        conj_block[i] = np.logical_xor(block[i], wc[i]) 

    conj_block[0,0]=1 #flag conjugated 

    return conj_block


# replace block data 
def block_replace(arr, startY, startX, bit, secret_block):
    for i in range(startY, startY+8):
        for j in range(startX, startX+8):
            arr[bit,i,j] = secret_block[i%8][j%8] 
    return arr 


def embed_data(arr, secret_bin, i, j, k):
    # create 8x8 array from secret bin 
    secret_block, secret_bin = get_8x8_secret(secret_bin)

    # if a block's complexity < alpha(0), conjugate and add flag
    if complexity(secret_block,8,8) < THRESHOLD:
        conj_secret_block = conjugate(secret_block)
        arr = block_replace(arr, i, j, k, conj_secret_block)  
    else:
        arr = block_replace(arr, i, j, k, secret_block)

    return arr, secret_bin


def extract_data(image_8x8,):
    extracted_bin = ""

    if image_8x8[0,0]==1: #look for flag 
        block = conjugate(image_8x8,)
    else:
        block = image_8x8

    for i in range(8):
        for j in range(8):
            extracted_bin = extracted_bin + str(block[i,j])

    return extracted_bin[1:] #removes flag bit 




def en_bpcs(cover_filename, secret_filename, output_file):
    # open cover image file 
    print("encoding bpcs...")
    Error = False 
    ErrorMessage = ""

    #open file
    try:
        temp_img = Image.open(cover_filename)
        img = temp_img.convert('RGB')
    except:
        ErrorMessage = "Error with file, make sure an image file is selected"   
        Error = True  
        return Error, ErrorMessage

    #save any image to png
    if temp_img.format != "PNG":
        temp_img = temp_img.convert('RGB')
        temp_img.save(cover_filename+".png", format = "png")
        img = Image.open(cover_filename+".png") 

    width, height = img.size

    # split image into colour channels - decimal values
    arr_red = np.array(img.getchannel(0))
    arr_green = np.array(img.getchannel(1))
    arr_blue = np.array(img.getchannel(2))

    #change dec to bin 
    print('slicing image...')
    print("height",height, "width",width)
    binArr_red  = np.zeros( (8, height, width), dtype = 'uint8' ) #create 3d array filled with 0s in size of img
    binArr_green  = np.zeros( (8, height, width), dtype = 'uint8' )
    binArr_blue  = np.zeros( (8, height, width), dtype = 'uint8' )

    for i in range(height):
        for j in range(width):

            #temp storing bin values
            # returns 8 bit binary values of decimal colour values in little endian - arranging the bit planes from LSB to MSB
            red_bin = np.unpackbits(np.uint8(arr_red[i,j]),bitorder='little') 
            green_bin = np.unpackbits(np.uint8(arr_green[i,j]),bitorder='little')
            blue_bin = np.unpackbits(np.uint8(arr_blue[i,j]),bitorder='little')
            
            for k in range(8): # splits bin numbers into 8 bits in 3d array, with k=0 being the least significant layer 
                binArr_red[k,i,j] =  red_bin[k]
                binArr_green[k,i,j] =  green_bin[k]
                binArr_blue[k,i,j] =  blue_bin[k]
    
    del arr_red, arr_green, arr_blue
   
    print('sliced image.')

    # transform planes PBC to CGC
    cgc_red = pbc_to_cgc(binArr_red, height, width)
    cgc_green = pbc_to_cgc(binArr_green, height, width)
    cgc_blue = pbc_to_cgc(binArr_blue, height, width)

    # open secret file
    secret_bin = file_hex_to_bin(secret_filename) 

    print("opened secret file, length", len(secret_bin))

    ## embedding 
    block_counter = 0 
    end = False
    block1_coords=[]
    info_colour="" #which colour array the info block is in 

    # iterate through 3d arrays starting from bit 1
    for k in range(8): #going from least to most sig bit 
        for i in range(0, height-(8+height%8), 8):
            for j in range(0, width-(8+width%8), 8):

                ##RED
                # check if image block is complex 
                block = get_8x8_image(cgc_red, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD) and (len(secret_bin)>0): #threshold for complexity 
                    block_counter += 1

                    if block_counter != 1: # first noisy region: leave blank and flag area to return to later and embed details
                        cgc_red, secret_bin = embed_data(cgc_red, secret_bin, i, j, k)
                    else: 
                        block1_coords=[i,j,k]
                        info_colour="red"

                    if len(secret_bin)==0:
                        # print("finished embedding at",i,j,"bit layer",k,info_colour)
                        end = True 

                ##GREEN
                # check if image block is complex 
                block = get_8x8_image(cgc_green, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD) and (len(secret_bin)>0): #threshold for complexity 
                    block_counter += 1
                    if block_counter != 1: # first noisy region: leave blank and flag area to return to later and embed details
                        cgc_green, secret_bin = embed_data(cgc_green, secret_bin, i, j, k)
                    else: 
                        block1_coords=[i,j,k]
                        info_colour="green"

                    if len(secret_bin)==0:
                        # print("finished embedding at",i,j,"bit layer",k,info_colour)
                        end = True 

                ##BLUE
                # check if image block is complex 
                block = get_8x8_image(cgc_blue, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD) and (len(secret_bin)>0): #threshold for complexity 
                    block_counter += 1
                    if block_counter != 1: # first noisy region: leave blank and flag area to return to later and embed details
                        cgc_blue, secret_bin = embed_data(cgc_blue, secret_bin, i, j, k)
                    else: 
                        block1_coords=[i,j,k]
                        info_colour="blue"

                    if len(secret_bin)==0:
                        # print("finished embedding at",i,j,"bit layer",k,info_colour)
                        end = True 

                if end == True: 
                    break        
            if end == True: 
                break          
        if end == True: 
            break    

    #embed info 
    info_string = dec_to_bin(block_counter)
    info_string = "0"*(63-len(info_string)) + info_string
    # print("info block at",block1_coords, info_colour)
    # print(info_string)

    if info_colour=="red":
        cgc_red, info_string = embed_data(cgc_red, info_string, block1_coords[0],block1_coords[1],block1_coords[2])
    elif info_colour=="green":
        cgc_green, info_string = embed_data(cgc_green, info_string, block1_coords[0],block1_coords[1],block1_coords[2])
    elif info_colour=="blue":
        cgc_blue, info_string = embed_data(cgc_blue, info_string, block1_coords[0],block1_coords[1],block1_coords[2])


    # convert arrays back to PBC 
    pbc_red = cgc_to_pbc(cgc_red, height, width)
    pbc_green = cgc_to_pbc(cgc_green, height, width)
    pbc_blue = cgc_to_pbc(cgc_blue, height, width)

    img_array = np.zeros((height,width,3), dtype= 'uint8')

    for i in range(height):
        for j in range(width):
            red_bin=""
            green_bin=""
            blue_bin=""

            for k in range(8): # collect bits from each layer of array
                red_bin = red_bin + str(pbc_red[7-k,i,j]) # make sure binary is in big endian format
                green_bin = green_bin + str(pbc_green[7-k,i,j])
                blue_bin = blue_bin + str(pbc_blue[7-k,i,j])

            img_array[i,j,0] = bin_to_dec(red_bin)
            img_array[i,j,1] = bin_to_dec(green_bin)
            img_array[i,j,2] = bin_to_dec(blue_bin)
    
    img_output = Image.fromarray(img_array, "RGB")

    img_output.save(output_file+".png")

    print("output image saved")




def de_bpcs(image_file, output_file):
    # open cover image file 
    print("decoding bpcs...")
    Error = False 
    ErrorMessage = ""

    #open file
    try:
        temp_img = Image.open(image_file)
        img = temp_img.convert('RGB')
    except:
        ErrorMessage = "Error with file, make sure an image file is selected"   
        Error = True  
        return Error, ErrorMessage

    #save any image to png
    if temp_img.format != "PNG":
        temp_img = temp_img.convert('RGB')
        temp_img.save(image_file+".png", format = "png")
        img = Image.open(image_file+".png") 

    width, height = img.size

    # split image into colour channels - decimal values
    arr_red = np.array(img.getchannel(0))
    arr_green = np.array(img.getchannel(1))
    arr_blue = np.array(img.getchannel(2))

    #change dec to bin 
    print('slicing image...')
    print("height",height, "width",width)
    binArr_red  = np.zeros( (8, height, width), dtype = 'uint8' ) #create 3d array filled with 0s in size of img
    binArr_green  = np.zeros( (8, height, width), dtype = 'uint8' )
    binArr_blue  = np.zeros( (8, height, width), dtype = 'uint8' )
        
    for i in range(height):
        for j in range(width):

            #temp storing bin values 
            # returns 8 bit binary values of decimal colour values in little endian - arranging the bit planes from LSB to MSB
            red_bin = np.unpackbits(np.uint8(arr_red[i,j]),bitorder='little') 
            green_bin = np.unpackbits(np.uint8(arr_green[i,j]),bitorder='little')
            blue_bin = np.unpackbits(np.uint8(arr_blue[i,j]),bitorder='little')
            
            for k in range(8): # splits bin numbers into 8 bits in 3d array
                binArr_red[k,i,j] =  red_bin[k]
                binArr_green[k,i,j] =  green_bin[k]
                binArr_blue[k,i,j] =  blue_bin[k]

    del arr_red, arr_green, arr_blue

    print('sliced image.')

    # transform planes PBC to CGC
    cgc_red = pbc_to_cgc(binArr_red, height, width)
    cgc_green = pbc_to_cgc(binArr_green, height, width)
    cgc_blue = pbc_to_cgc(binArr_blue, height, width)

    ## extracting
    block_counter = 0
    total_blocks = 0 
    end = False
    secret=""

     # iterate through 3d arrays starting from bit 1
    for k in range(8): #going from least to most sig bit 
        for i in range(0, height-(8+height%8), 8):
            for j in range(0, width-(8+width%8), 8):

                # red
                # check if image block is complex 
                block = get_8x8_image(cgc_red, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD):
                    block_counter+=1
                    bit_string = extract_data(block) #data in block as string of data
                    if block_counter != 1:
                        secret = secret + bit_string
                    else:
                        while bit_string[0] == "0":
                            bit_string = bit_string[1:]
                        total_blocks = bin_to_dec(bit_string)
                        # print("red",i,j,k,"total blocks",total_blocks)   

                    if block_counter == total_blocks:
                        # print("finished extracting at",i,j,"bit layer",k)
                        end = True 

                # green
                # check if image block is complex 
                block = get_8x8_image(cgc_green, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD):
                    block_counter+=1
                    bit_string = extract_data(block) #data in block as string of data
                    if block_counter != 1:
                        secret = secret + bit_string
                    else:
                        while bit_string[0] == "0":
                            bit_string = bit_string[1:]
                        total_blocks = bin_to_dec(bit_string)
                        # print("green",i,j,k,"total blocks",total_blocks)
                    
                    if block_counter == total_blocks:
                        # print("finished extracting at",i,j,"bit layer",k)
                        end = True 

                # blue
                # check if image block is complex 
                block = get_8x8_image(cgc_blue, i, j, k)
                alpha = complexity(block, 8, 8)

                if (alpha>=THRESHOLD):
                    block_counter+=1
                    bit_string = extract_data(block) #data in block as string of data
                    if block_counter != 1:
                        secret = secret + bit_string
                    else:
                        while bit_string[0] == "0":
                            bit_string = bit_string[1:]
                        total_blocks = bin_to_dec(bit_string)
                        # print("blue",i,j,k,"total blocks",total_blocks)

                    if block_counter == total_blocks:
                        # print("finished extracting at",i,j,"bit layer",k)
                        end = True 

                if end == True: 
                    break        
            if end == True: 
                break          
        if end == True: 
            break  

    secret_bin = bitstring_to_bytes(secret)

    temp_path = os.path.join(os.path.dirname(output_file) or ".", "bpcs_file")
    
    f = open(temp_path, "wb")
    f.write(secret_bin)
    f.close()

    file_info = get_file_type(temp_path) 
    filetype = file_info[1]
    if file_info[1] == "":
        filetype = file_info[4]
    else: 
        filetype = file_info[1]

    #save to file and return 
    output_file = open(output_file+filetype, "wb")
    output_file.write(secret_bin)
    output_file.close()
    print("extraction complete")

    return "de_bpcs_output"+filetype


 

if __name__ == "__main__":
    
    print("BPCS steganography")
    