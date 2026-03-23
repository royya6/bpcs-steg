from bpcs_steg.get_bin import * 

def sub_bits(
        r: str, 
        g: str, 
        b: str, 
        secret_bin: str, 
        bits: int
    ) -> tuple[int, int, int, str, bool]:

    end = False 

    if len(secret_bin)>=bits: 
        # checks there are enough bits of secret data to substitute
        r_new = r[:(8-bits)]+secret_bin[:bits]
        secret_bin = secret_bin[bits:]
    else: 
        # if not, however many bits are left of the secret data and sets end flag to True so that the LSB program will stop iterating through pixels
        less_bits = len(secret_bin)
        r_new = r[:(8-less_bits)]+secret_bin[:less_bits]
        secret_bin = ""
        end = True 

    if len(secret_bin)>=bits: 
        g_new = g[:(8-bits)]+secret_bin[:bits]
        secret_bin = secret_bin[bits:]
    else:
        less_bits = len(secret_bin)
        g_new = g[:(8-less_bits)]+secret_bin[:less_bits]
        secret_bin = ""
        end = True 
    
    if len(secret_bin)>=bits:  
        b_new = b[:(8-bits)]+secret_bin[:bits]
        secret_bin = secret_bin[bits:]
    else:
        less_bits = len(secret_bin)
        b_new = b[:(8-less_bits)]+secret_bin[:less_bits]
        secret_bin = ""
        end = True 


    r_new_d = bin_to_dec(r_new)
    g_new_d = bin_to_dec(g_new)
    b_new_d = bin_to_dec(b_new)

    # returns new pixel values, the secret binary string without the data that has now been embedded, end flag so LSB program can check whether to perform substitution on the next pixel 
    return r_new_d, g_new_d, b_new_d, secret_bin, end