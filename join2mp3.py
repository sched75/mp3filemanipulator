import argparse
import os
import sys
from pydub import AudioSegment

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Join two MP3 files')
parser.add_argument('file1', metavar='file1', type=str,
                    help='Path of the first MP3 file to join. Use "-" for stdin.')
parser.add_argument('file2', metavar='file2', type=str,
                    help='Path of the second MP3 file to join')
parser.add_argument('output', metavar='output', type=str,
                    help='Path and name of the output MP3 file. Use "-" for stdout.')
parser.add_argument('--delete', action='store_true',
                    help='Delete the original MP3 files after combining them')

# Parse the command-line arguments
args = parser.parse_args()

try:
    # Load the first MP3 file from stdin or from file
    if args.file1 == "-":
        song1 = AudioSegment.from_file(sys.stdin.buffer, format="mp3")
    else:
        song1 = AudioSegment.from_file(args.file1, format="mp3")

    # Load the second MP3 file from file
    song2 = AudioSegment.from_file(args.file2, format="mp3")

    # Concatenate the two MP3 files
    combined_song = song1 + song2

    # Export the combined MP3 file to stdout or to a file
    if args.output == "-":
        combined_song.export(sys.stdout.buffer, format='mp3')
    else:
        combined_song.export(args.output, format='mp3')

    # Ask user for confirmation before deleting files
    if args.delete:
        if args.file1 == "-":
            prompt = f"Do you want to delete the original file from stdin and '{args.file2}'? [y/n] "
        else:
            prompt = f"Do you want to delete the original files '{args.file1}' and '{args.file2}'? [y/n] "
        response = input(prompt).strip().lower()

        if response == "y":
            if args.file1 == "-":
                pass  # Cannot delete file from stdin
            else:
                os.remove(args.file1)
            os.remove(args.file2)
        else:
            print("Original files were not deleted.")

except FileNotFoundError as e:
    print(f"Error: {str(e)}")
    print("Please make sure the file paths are correct and the files exist.")
except TypeError as e:
    print(f"Error: {str(e)}")
    print("Please make sure the input files are in MP3 format.")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Please check your input and output files and try again.")
