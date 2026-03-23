def file_hex_to_bin(filename):

    f = open(filename, "rb")
    myfile = f.read()
    mystring = ""

    for byte in myfile:
        mystring = mystring + "{:08b}".format(byte) #formats as an 8bit binary number with 0 padding to the left 

    return mystring 

def dec_to_bin(num):
    bin_num = "{:08b}".format(num) #formats as an 8bit binary number with 0 padding to the left
    return bin_num 

def bin_to_dec(bstring):
    dec_num = int(bstring, 2)
    return dec_num


def bitstring_to_bytes(s):
    if (len(s)%8) != 0:
        s = s + (8-(len(s)%8))*"0"

    # python to_bytes function takes decimal values of binary string and converts to bytes  
    return int(s, 2).to_bytes(len(s)//8, byteorder='big') 