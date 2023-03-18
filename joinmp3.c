#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <libgen.h>
#include <stdbool.h>

#define BUFFER_SIZE 4096

bool is_mp3_file(char *filename)
{
    char *ext = strrchr(filename, '.');
    if (ext != NULL && strcmp(ext, ".mp3") == 0)
    {
        return true;
    }
    return false;
}

void join_files(char **input_files, int num_files, char *output_file)
{
    FILE *fout = fopen(output_file, "wb");
    if (fout == NULL)
    {
        perror("Error opening output file");
        exit(EXIT_FAILURE);
    }

    char buffer[BUFFER_SIZE];

    for (int i = 0; i < num_files; i++)
    {
        FILE *fin = fopen(input_files[i], "rb");
        if (fin == NULL)
        {
            perror("Error opening input file");
            exit(EXIT_FAILURE);
        }

        while (1)
        {
            size_t bytes_read = fread(buffer, 1, BUFFER_SIZE, fin);
            if (bytes_read == 0)
            {
                break;
            }

            size_t bytes_written = fwrite(buffer, 1, bytes_read, fout);
            if (bytes_written != bytes_read)
            {
                perror("Error writing to output file");
                exit(EXIT_FAILURE);
            }
        }

        fclose(fin);
    }

    fclose(fout);
}

int main(int argc, char **argv)
{
    if (argc < 3)
    {
        printf("Usage: %s output_file input_file1 [input_file2 ... input_fileN]\n", basename(argv[0]));
        exit(EXIT_FAILURE);
    }

    char *output_file = argv[1];

    int num_files = argc - 2;
    char **input_files = (char **)malloc(sizeof(char *) * num_files);
    if (input_files == NULL)
    {
        perror("Error allocating memory");
        exit(EXIT_FAILURE);
    }

    // Copy input files to an array
    for (int i = 0; i < num_files; i++)
    {
        input_files[i] = argv[i + 2];
    }

    // Validate input files
    for (int i = 0; i < num_files; i++)
    {
        struct stat file_stat;
        if (stat(input_files[i], &file_stat) != 0)
        {
            perror("Error reading input file");
            exit(EXIT_FAILURE);
        }

        if (!S_ISREG(file_stat.st_mode))
        {
            printf("Error: %s is not a regular file\n", input_files[i]);
            exit(EXIT_FAILURE);
        }

        if (!is_mp3_file(input_files[i]))
        {
            printf("Error: %s is not an MP3 file\n", input_files[i]);
            exit(EXIT_FAILURE);
        }
    }

    // Join the input files
    join_files(input_files, num_files, output_file);

    // Delete input files
    for (int i = 0; i < num_files; i++)
    {
        if (remove(input_files[i]) != 0)
        {
            printf("Error deleting input file: %s\n", input_files[i]);
        }
    }

    free(input_files);

    return 0;
}
