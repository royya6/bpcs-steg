import os
import numpy as np
import pytest
from PIL import Image
from bpcs_steg.bpcs import (
    en_bpcs, de_bpcs,
    complexity, conjugate,
    get_8x8_secret, get_8x8_image,
    pbc_to_cgc, cgc_to_pbc
)


# --- helpers ---

def make_cover(tmp_path, size=(64, 64)):
    # create a cover image with random noise (high complexity = good for embedding)
    img = Image.fromarray(np.random.randint(0, 255, (size[1], size[0], 3), dtype='uint8'), "RGB")
    path = tmp_path / "cover.png"
    img.save(str(path), format="PNG")
    return str(path)

def make_secret(tmp_path, data=b"Hello BPCS"):
    path = tmp_path / "secret.txt"
    path.write_bytes(data)
    return str(path)


# --- complexity ---

def test_complexity_checkerboard_is_max():
    # checkerboard 
    block = np.array([[0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0],
                      [0,1,0,1,0,1,0,1],
                      [1,0,1,0,1,0,1,0]], dtype='uint8')
    
    assert complexity(block, 8, 8) == 1.0

def test_complexity_uniform_is_zero():
    block = np.zeros((8, 8), dtype='uint8')
    assert complexity(block, 8, 8) == 0.0

def test_complexity_range():
    # complexity should always be between 0 and 1
    block = np.random.randint(0, 2, (8, 8), dtype='uint8')
    result = complexity(block, 8, 8)
    assert 0.0 <= result <= 1.0



# --- conjugate ---

def test_conjugate_output_shape():
    block = np.zeros((8, 8), dtype='uint8')
    conj = conjugate(block)
    assert conj.shape == (8, 8)

def test_conjugate_simple_increases_complexity():
    block = np.zeros((8, 8), dtype='uint8')
    conj = conjugate(block)
    assert complexity(conj, 8, 8) >= 0.3

def test_conjugate_sets_flag():
    block = np.zeros((8, 8), dtype='uint8')
    conj = conjugate(block)
    assert conj[0, 0] == 1

def test_conjugate_twice_returns_original():
    block = np.random.randint(0, 2, (8, 8), dtype='uint8')
    block[0, 0] = 0  # ensure flag is 0 before conjugating
    double_conj = conjugate(conjugate(block))
    double_conj[0, 0] = 0 
    assert np.array_equal(block, double_conj)




# --- get_8x8_secret ---

def test_get_8x8_secret_shape():
    secret_bin = "1" * 100
    block, remaining = get_8x8_secret(secret_bin)
    assert block.shape == (8, 8)

def test_get_8x8_secret_consumes_63_bits():
    secret_bin = "1" * 100
    block, remaining = get_8x8_secret(secret_bin)
    assert len(remaining) == 37  # 100 - 63 = 37

def test_get_8x8_secret_short_input_padded():
    # less than 63 bits should be padded to fill the block
    secret_bin = "1" * 10
    block, remaining = get_8x8_secret(secret_bin)
    assert block.shape == (8, 8)
    assert remaining == ""
    # flatten block and check values
    flat = block.flatten()
    assert flat[0] == 0          # conjugation flag
    assert all(flat[1:11] == 1)  # 10 secret bits
    assert all(flat[11:] == 0)   # padding zeros

def test_get_8x8_secret_empty_input():
    # empty input should return a zero-padded block
    block, remaining = get_8x8_secret("")
    assert block.shape == (8, 8)
    assert remaining == ""
    assert np.all(block == 0)  



# --- get_8x8_image ---

def test_get_8x8_image_shape():
    arr = np.random.randint(0, 2, (8, 64, 64), dtype='uint8')
    block = get_8x8_image(arr, 0, 0, 0)
    assert block.shape == (8, 8)

def test_get_8x8_image_correct_values():
    arr = np.ones((8, 64, 64), dtype='uint8')
    block = get_8x8_image(arr, 0, 0, 0)
    assert np.all(block == 1)


# --- pbc_to_cgc / cgc_to_pbc ---

def test_pbc_to_cgc_shape():
    arr = np.random.randint(0, 2, (8, 64, 64), dtype='uint8')
    result = pbc_to_cgc(arr, 64, 64)
    assert result.shape == (8, 64, 64)

def test_cgc_to_pbc_shape():
    arr = np.random.randint(0, 2, (8, 64, 64), dtype='uint8')
    result = cgc_to_pbc(arr, 64, 64)
    assert result.shape == (8, 64, 64)

def test_pbc_cgc_roundtrip():
    # converting PBC to CGC and back should return the original array
    arr = np.random.randint(0, 2, (8, 64, 64), dtype='uint8')
    cgc = pbc_to_cgc(arr, 64, 64)
    pbc = cgc_to_pbc(cgc, 64, 64)
    assert np.array_equal(arr, pbc)

def test_pbc_to_cgc_first_row_unchanged():
    # first row of each bitplane should be identical in PBC and CGC
    arr = np.random.randint(0, 2, (8, 64, 64), dtype='uint8')
    cgc = pbc_to_cgc(arr, 64, 64)
    for i in range(8):
        assert np.array_equal(arr[i][0], cgc[i][0])


# --- en_bpcs / de_bpcs roundtrip ---

def test_encode_creates_output(tmp_path):
    cover = make_cover(tmp_path)
    secret = make_secret(tmp_path)
    output = str(tmp_path / "stego")
    en_bpcs(cover, secret, output)
    assert os.path.exists(output + ".png")

def test_encode_output_is_same_size(tmp_path):
    # stego image should be the same dimensions as the cover
    cover = make_cover(tmp_path)
    secret = make_secret(tmp_path)
    output = str(tmp_path / "stego")
    en_bpcs(cover, secret, output)
    cover_img = Image.open(cover)
    stego_img = Image.open(output + ".png")
    assert cover_img.size == stego_img.size

def test_roundtrip_small_secret(tmp_path):
    cover = make_cover(tmp_path)
    secret_data = b"Hello BPCS"
    secret = make_secret(tmp_path, data=secret_data)
    stego = str(tmp_path / "stego")
    extracted = str(tmp_path / "extracted")

    en_bpcs(cover, secret, stego)
    de_bpcs(stego + ".png", extracted)

    # find the extracted file
    extracted_files = [f for f in os.listdir(tmp_path) if f.startswith("extracted")]
    assert len(extracted_files) > 0

    with open(str(tmp_path / extracted_files[0]), "rb") as f:
        result = f.read()

    assert result == secret_data

def test_roundtrip_larger_secret(tmp_path):
    cover = make_cover(tmp_path, size=(128, 128))
    secret_data = b"A" * 500
    secret = make_secret(tmp_path, data=secret_data)
    stego = str(tmp_path / "stego")
    extracted = str(tmp_path / "extracted")

    en_bpcs(cover, secret, stego)
    de_bpcs(stego + ".png", extracted)

    extracted_files = [f for f in os.listdir(tmp_path) if f.startswith("extracted")]
    assert len(extracted_files) > 0

    with open(str(tmp_path / extracted_files[0]), "rb") as f:
        result = f.read()

    assert result == secret_data