from bpcs_steg.get_bin import file_hex_to_bin, dec_to_bin, bin_to_dec, bitstring_to_bytes

#FILE_HEX_TO_BIN
def test_file_hex_to_bin_returns_string(tmp_path):
    path = tmp_path / "test.bin"
    path.write_bytes(b'\xff\x00')
    result = file_hex_to_bin(str(path))
    assert isinstance(result, str)
    assert set(result).issubset({"0", "1"})

def test_file_hex_to_bin_correct_length(tmp_path):
    path = tmp_path / "test.bin"
    path.write_bytes(b'\xff\x00')
    result = file_hex_to_bin(str(path))
    assert len(result) == 16

def test_file_hex_to_bin_correct_values(tmp_path):
    path = tmp_path / "test.bin"
    path.write_bytes(b'\xff\x00')
    result = file_hex_to_bin(str(path))
    assert result == "1111111100000000"

def test_file_hex_to_bin_roundtrip(tmp_path):
    original = b'\x48\x65\x6c\x6c\x6f'  # "Hello"
    path = tmp_path / "test.bin"
    path.write_bytes(original)
    result = file_hex_to_bin(str(path))
    assert bitstring_to_bytes(result) == original

#DEC_TO_BIN
def test_dec_to_bin_basic():
    assert dec_to_bin(0) == "00000000"
    assert dec_to_bin(255) == "11111111"
    assert dec_to_bin(1) == "00000001"

def test_dec_to_bin_midrange():
    assert dec_to_bin(128) == "10000000"
    assert dec_to_bin(127) == "01111111"

#BIN_TO_DEC
def test_bin_to_dec_basic():
    assert bin_to_dec("00000000") == 0
    assert bin_to_dec("11111111") == 255
    assert bin_to_dec("00000001") == 1


def test_roundtrip_dec_bin():
    # converting to binary and back should return the original number
    for n in [0, 1, 127, 128, 255]:
        assert bin_to_dec(dec_to_bin(n)) == n


#BITSRTING_TO_BYTES
def test_bitstring_to_bytes_padding():
    # input not divisible by 8 should be padded
    result = bitstring_to_bytes("1")
    assert isinstance(result, bytes)
    assert len(result) == 1

def test_bitstring_to_bytes_basic():
    assert bitstring_to_bytes("00000000") == b'\x00'
    assert bitstring_to_bytes("11111111") == b'\xff'

def test_bitstring_to_bytes_multiple_bytes():
    result = bitstring_to_bytes("0000000011111111")
    assert len(result) == 2
    assert result == b'\x00\xff'

def test_bitstring_to_bytes_roundtrip():
    original = b'\x48\x65\x6c\x6c\x6f'  # "Hello"
    bitstring = "".join("{:08b}".format(b) for b in original)
    assert bitstring_to_bytes(bitstring) == original