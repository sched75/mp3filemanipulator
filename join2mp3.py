
import os
from pydub import AudioSegment

def joinmp3(file1, file2, output_file):
    # Load the two MP3 files using Pydub
    sound1 = AudioSegment.from_mp3(file1)
    sound2 = AudioSegment.from_mp3(file2)

    # Concatenate the two MP3 files
    combined_sound = sound1 + sound2

    # Export the combined sound to the output file
    combined_sound.export(output_file, format="mp3")

def join_all_mp3(input_files, output_file):
    # If input_files is a directory path, get all MP3 files in the directory
    if os.path.isdir(input_files):
        mp3_files = [os.path.join(input_files, f) for f in os.listdir(input_files) if f.endswith(".mp3")]
    else:
        mp3_files = [f for f in input_files if f.endswith(".mp3")]

    # Sort the MP3 files alphabetically
    mp3_files.sort()

    # Join the MP3 files using the joinmp3 function
    for i, file in enumerate(mp3_files):
        if i == 0:
            joinmp3(file, file, output_file)
        else:
            joinmp3(output_file, file, output_file)

def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Join multiple MP3 files into a single file")
    parser.add_argument("input_file", help="Path to directory or list of MP3 files to join")
    parser.add_argument("output_file", help="Path to output file")
    args = parser.parse_args()

    # Call the join_all_mp3 function with the input and output files
    join_all_mp3(args.input_file, args.output_file)

if __name__ == "__main__":
    main()