import argparse
import glob
import os
import sys
from pydub import AudioSegment
from tqdm import tqdm

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Join two or more MP3 files',add_help=False)
parser.add_argument('files', metavar='file', type=str, nargs='+',
                    help='Paths of the MP3 files to join in the order they should be concatenated.\
                          You can also use wildcards to specify multiple files.')
parser.add_argument('output', metavar='output', type=str, nargs=1,
                    help='Path and name of the output MP3 file')
parser.add_argument('--delete', action='store_true',
                    help='Delete the original MP3 files after combining them')
parser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                    help='Show this help message and exit')

# Set a custom help message
parser._optionals.title = "Options"
parser._positionals.title = "Arguments"
parser._positionals.description = "positional arguments:"
parser._optionals.description = "optional arguments:"
parser._positionals.help = "    file: Paths of the MP3 files to join in the order they should be concatenated.\
                          You can also use wildcards to specify multiple files."
parser._optionals.help = "    --help: Show this help message and exit.\n\
    --delete: Delete the original MP3 files after combining them."

# Parse the command-line arguments
args = parser.parse_args()

try:
    # Get a list of all the files that match the input pattern
    input_files = []
    for file_pattern in args.files:
        input_files += glob.glob(file_pattern)

    # Sort the input files alphabetically
    input_files = sorted(input_files)

    # Show the output file name before starting
    print(f"Joining files: {', '.join(input_files)}")
    print(f"Output file: {args.output[0]}")

    # Load the first MP3 file
    combined_song = AudioSegment.from_file(input_files[0], format="mp3")

    # Concatenate the rest of the MP3 files
    output_file = args.output[0]
    with tqdm(total=len(input_files) - 1, desc="Joining MP3 files") as pbar:
        for file in input_files[1:]:
            song = AudioSegment.from_file(file, format="mp3")
            combined_song += song

            # Save the combined audio data periodically to prevent overflow
            if len(combined_song) > 1000000:
                combined_song.export(output_file, format='mp3')
                combined_song = AudioSegment.from_file(output_file, format='mp3')

            pbar.update(1)

    # Export the combined MP3 file
    if output_file in input_files:
        raise Exception("Output file cannot be the same as the input files")
    combined_song.export(output_file, format='mp3')

    # Ask user for confirmation before deleting files
    if args.delete:
        prompt = f"Do you want to delete the original files? [y/n] "
        response = input(prompt).strip().lower()

        if response == "y":
            for file in input_files:
                os.remove(file)
        else:
            print("Original files were not deleted.")

except FileNotFoundError as e:
    print(f"Error: {str(e)}")
    print("Please make sure the file paths are correct and the files exist.")
except TypeError as e:
    print(f"Error: {str(e)}")
    print("Please make sure the input files are MP3 files and they exist.")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Please choose a different output file name.")
