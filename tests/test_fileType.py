import pytest
from bpcs_steg.fileType import get_file_type

def test_jpg_detection(tmp_path):
    # create image
    from PIL import Image
    img = Image.new("RGB", (8, 8))
    path = tmp_path / "test.jpg"
    img.save(str(path), format="JPEG")

    found, filetype, header, trailer, likely = get_file_type(str(path))
    assert found == True
    assert filetype == ".jpg"

def test_png_detection(tmp_path):
    # create image
    from PIL import Image
    img = Image.new("RGB", (8, 8))
    path = tmp_path / "test.png"
    img.save(str(path), format="PNG")

    found, filetype, header, trailer, likely = get_file_type(str(path))
    assert found == True
    assert filetype == ".png"

def test_unknown_file_returns_txt(tmp_path):
    path = tmp_path / "unknown.bin"
    path.write_bytes(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08')
    found, filetype, header, trailer, likely = get_file_type(str(path))
    assert found == False
    assert filetype == ".txt"