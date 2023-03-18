import sys
import os
import argparse
from pydub import AudioSegment
import mutagen
import tkinter as tk
from tkinter import filedialog

SUPPORTED_FORMATS = {
    ".mp3": "mp3",
    ".wav": "wav",
    ".ogg": "ogg",
    ".flac": "flac"
}

def join_audio_files(audio_files, output_file, bitrate_mode):
    combined_audio = None
    bitrates = []

    for audio_file in audio_files:
        file_extension = os.path.splitext(audio_file)[-1].lower()
        audio = AudioSegment.from_file(audio_file, file_extension[1:])

        if bitrate_mode:
            audio_info = mutagen.File(audio_file)
            bitrate = int(audio_info.info.bitrate // 1000)
            bitrates.append(bitrate)

        if combined_audio is None:
            combined_audio = audio
        else:
            combined_audio += audio

    export_args = {"format": output_file.split('.')[-1]}

    if bitrate_mode and bitrates:
        if bitrate_mode == "min":
            target_bitrate = min(bitrates)
        elif bitrate_mode == "mean":
            target_bitrate = int(sum(bitrates) / len(bitrates))
        elif bitrate_mode == "max":
            target_bitrate = max(bitrates)

        export_args["bitrate"] = f"{target_bitrate}k"

    combined_audio.export(output_file, **export_args)

def get_audio_files_from_directory(directory):
    audio_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if mutagen.File(os.path.join(root, file)):
                audio_files.append(os.path.join(root, file))

    return audio_files

def run_gui():
    def browse_directory():
        directory = filedialog.askdirectory()
        input_directory_var.set(directory)

    def browse_output_file():
        output_file = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("Audio files", "*.mp3;*.wav;*.ogg;*.flac")])
        output_file_var.set(output_file)

    def start_join():
        input_directory = input_directory_var.get()
        output_file = output_file_var.get()
        bitrate_mode = bitrate_var.get()
        ffmpeg_path = ffmpeg_path_var.get()
        avconv_path = avconv_path_var.get()

        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
        elif avconv_path:
            AudioSegment.converter = avconv_path

        if not input_directory or not output_file:
            return

        audio_files = get_audio_files_from_directory(input_directory)

        if audio_files:
            join_audio_files(audio_files, output_file, bitrate_mode)
        else:
            print("No audio files found in the specified directory.")

    root = tk.Tk()
    root.title("Join Audio Files")

    input_directory_var = tk.StringVar()
    output_file_var = tk.StringVar()
    bitrate_var = tk.StringVar()
    ffmpeg_path_var = tk.StringVar()
    avconv_path_var = tk.StringVar()

    tk.Label(root, text="FFmpeg path:").grid(row=3, column=0, sticky="e")
    tk.Entry(root, textvariable=ffmpeg_path_var).grid(row=3, column=1)

    tk.Label(root, text="avconv path:").grid(row=4, column=0, sticky="e")
    tk.Entry(root, textvariable=avconv_path_var).grid(row=4, column=1)
    tk.Label(root, text="Input directory:").grid(row=0, column=0, sticky="e")
    tk.Entry(root, textvariable=input_directory_var).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_directory).grid(row=0, column=2)

    tk.Label(root, text="Output file:").grid(row=1, column=0, sticky="e")
    tk.Entry(root, textvariable=output_file_var).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=browse_output_file).grid(row=1, column=2)

    tk.Label(root, text="Bitrate:").grid(row=2, column=0, sticky="e")
    bitrate_options = ["", "min", "mean", "max"]
    bitrate_menu = tk.OptionMenu(root, bitrate_var, *bitrate_options)
    bitrate_menu.grid(row=2, column=1, sticky="ew")

    tk.Button(root, text="Join Audio Files", command=start_join).grid(row=3, columnspan=3)

    root.mainloop()

def main():
    if len(sys.argv) == 1:
        run_gui()
    else:
        parser = argparse.ArgumentParser(description=__doc__.strip())
        parser.add_argument("input_directory", help="The input directory containing audio files.")
        parser.add_argument("output_file", help="The output audio file.")
        parser.add_argument("--bitrate", choices=["min", "mean", "max"],
                            help="Match the output file's bitrate to the min, mean, or max bitrate among the input files.")
        parser.add_argument("--ffmpeg-path", help="Specify the path to the FFmpeg executable.")
        parser.add_argument("--avconv-path", help="Specify the path to the avconv executable.")

        args = parser.parse_args()

        audio_files = get_audio_files_from_directory(args.input_directory)

        output_file_ext = os.path.splitext(args.output_file)[-1].lower()
        if output_file_ext not in SUPPORTED_FORMATS:
            print(f"Error: Unsupported output format '{output_file_ext}'. Supported formats are: {', '.join(SUPPORTED_FORMATS.keys())}")
            sys.exit(1)

        if audio_files:
            if args.ffmpeg_path:
                AudioSegment.converter = args.ffmpeg_path
            elif args.avconv_path:
                AudioSegment.converter = args.avconv_path
            join_audio_files(audio_files, args.output_file, args.bitrate)
        else:
            print("No audio files found in the specified directory.")

if __name__ == "__main__":
    main()
