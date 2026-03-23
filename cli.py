import os 
import argparse
from bpcs_steg.bpcs import en_bpcs, de_bpcs

def main():
    parser = argparse.ArgumentParser(
        description="BPCS Steganography — hide files inside images"
    )
    parser.add_argument(
        "--outdir",
        default=".",
        help="Directory to save output files (default: current directory)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encode subcommand
    encode = subparsers.add_parser("encode", help="Hide a secret file inside a cover image")
    encode.add_argument("cover",  help="Path to the cover image (PNG/JPG)")
    encode.add_argument("secret", help="Path to the secret file to hide")
    encode.add_argument("output", help="Output filename (without extension)")

    # Decode subcommand
    decode = subparsers.add_parser("decode", help="Extract a hidden file from a stego image")
    decode.add_argument("image",  help="Path to the stego image")
    decode.add_argument("output", help="Output filename (without extension)")

    args = parser.parse_args()

    # build full output path from --outdir and output argument
    os.makedirs(args.outdir, exist_ok=True)
    output_path = os.path.join(args.outdir, args.output)

    if args.command == "encode":
        result, error = en_bpcs(args.cover, args.secret, output_path)
        if error != "": 
            print(f"Error: {error}")
        else: 
            print(f"Output saved to: {result}")

    elif args.command == "decode":
        result, error = de_bpcs(args.image, output_path)
        if error != "": 
            print(f"Error: {error}")
        else: 
            print(f"Output saved to: {result}")

if __name__ == "__main__":
    main()