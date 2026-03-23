# bpcs-steg

![Tests](https://github.com/kimit/bpcs-steg/actions/workflows/test.yml/badge.svg)

A command line tool for hiding files inside images using **Bit-Plane Complexity Segmentation (BPCS)** steganography. 
Adapted from my A-level coursework project.

## What is BPCS?

BPCS steganography hides secret data inside the complex regions of an image's bit-planes. A colour image can be broken down into 8 bit-planes per channel (RGB).

**Complex** regions of a bit-plane are visually noisy enough that replacing them with secret data causes no perceptible change to the image. Simple (low-complexity) regions are left untouched to avoid visible distortion.

This gives BPCS a significantly higher embedding capacity than simpler methods like LSB substitution, while keeping the stego image visually identical to the original.

## Usage

### Encode — hide a file inside an image

```bash
python cli.py encode <cover_image> <secret_file> <output_name>
```

```bash
python cli.py encode samples/warholicon1.jpg samples/SecretMessage.pdf stego_output
```
saves stego_output.png to the current directory

### Decode — extract a hidden file from an image

```bash
python cli.py decode <stego_image> <output_name>
```

```bash
python cli.py decode stego_output.png extracted
```
saves extracted file with its original extension e.g. extracted.pdf

### Optional: specify an output directory

```bash
python cli.py --outdir ./outputs encode cover.jpg secret.pdf stego_output
python cli.py --outdir ./outputs decode stego_output.png extracted
```

#### Notes

- Cover image can be PNG or JPG — it will be converted to PNG automatically
- Secret file can be any file type (PDF, DOCX, ZIP, MP3, etc.)
- The larger and more complex the cover image, the more data it can hold
