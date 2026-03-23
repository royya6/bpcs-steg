from bpcs_steg.sub_bits import sub_bits
from bpcs_steg.get_bin import dec_to_bin

# helper to convert decimal RGB to binary strings
def rgb_to_bin(r, g, b):
    return dec_to_bin(r), dec_to_bin(g), dec_to_bin(b)



def test_sub_more_bits_than_available():
    # 8 bits of secret, substituting 2 bits per channel 
    r, g, b = rgb_to_bin(255, 255, 255)
    secret = "10011010"
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 2)
    assert end == False
    assert remaining == "10"  
    assert r_new == 254  # 11111110
    assert g_new == 253  # 11111101
    assert b_new == 254  # 11111110


def test_sub_less_bits_than_available_1channel():
    r, g, b = rgb_to_bin(255, 255, 255)
    secret = "0"
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 2)
    assert end == True
    assert remaining == ""
    assert r_new == 254  # 11111110 
    assert g_new == 255  
    assert b_new == 255  

def test_sub_less_bits_than_available_2channel():
    r, g, b = rgb_to_bin(0, 255, 0)
    secret = "110"  
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 2)
    assert end == True
    assert remaining == ""
    assert r_new == 3   # 00000011
    assert g_new == 254 # 11111110
    assert b_new == 0   



def test_sub_bits_all_channels_1bit():
    r, g, b = rgb_to_bin(0, 0, 0)
    secret = "111"
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 1)
    assert end == False
    assert remaining == ""
    assert r_new == 1   # 00000001
    assert g_new == 1   # 00000001
    assert b_new == 1   # 00000001

def test_sub_bits_all_channels_2bit():
    r, g, b = rgb_to_bin(0, 0, 0)
    secret = "11011000"  
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 2)
    assert end == False
    assert remaining == "00"
    assert r_new == 3   # 00000011
    assert g_new == 1   # 00000001
    assert b_new == 2   # 00000010


def test_sub_bits_empty_secret_sets_end():
    r, g, b = rgb_to_bin(100, 150, 200)
    secret = ""
    r_new, g_new, b_new, remaining, end = sub_bits(r, g, b, secret, 1)
    assert end == True
    assert remaining == ""
    assert r_new == 100  
    assert g_new == 150  
    assert b_new == 200  

