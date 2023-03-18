
import os
import argparse
import glob
import tempfile
import subprocess

def join_all_mp3(input_files, output_file):
    # If input_files is a directory path or a list of filenames
    if isinstance(input_files, str):
        # If the input contains wildcards, use glob to get matching files
        if "*" in input_files or "?" in input_files:
            mp3_files = sorted(glob.glob(input_files))
        else:
            mp3_files = [os.path.join(input_files, f) for f in os.listdir(input_files) if f.endswith(".mp3")]
    else:
        mp3_files = input_files

    # Sort the MP3 files alphabetically
    mp3_files.sort()

    # Prefix each filename with "file " and wrap it in double quotes
    mp3_files = [f"file '{os.path.abspath(file)}'" for file in mp3_files]

    # Save the sorted list of filenames to a temporary text file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("\n".join(mp3_files))

    # Use ffmpeg to concatenate the MP3 files
    cmd = f'ffmpeg -f concat -safe 0 -i "{f.name}" -c copy "{output_file}"'
    subprocess.run(cmd, shell=True, check=True)

    # Delete the temporary text file
    os.remove(f.name)


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Join multiple MP3 files into a single file")
    parser.add_argument("input_file", nargs="+", help="Path to directory or list of MP3 files to join")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("-y", "--yes", action="store_true", help="Force overwrite output file without confirmation")
    args = parser.parse_args()

    # Check if the output file exists
    if os.path.exists(args.output_file) and not args.yes:
        # If the output file exists and --yes option is not provided, ask for confirmation before overwriting it
        overwrite = input("The output file already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != "y":
            print("Aborting.")
            return
    else:
        if os.path.exists(args.output_file):
            os.remove(args.output_file)

    # Call the join_all_mp3 function with the input and output files
    if len(args.input_file) == 1 and os.path.isdir(args.input_file[0]):
        input_dir = args.input_file[0]
        join_all_mp3(input_dir, args.output_file)
    else:
        input_files = args.input_file
        join_all_mp3(input_files, args.output_file)
        
if __name__ == "__main__":
    main()