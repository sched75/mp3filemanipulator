#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <dirent.h>

#define MAX_FILENAME_LENGTH 256
#define MAX_MATCHES 10

int filter_filenames(const char* regex_pattern, const char* filenames[], int num_files, char** matched_files) {
    int i, j, status;
    regex_t regex;
    regmatch_t matches[MAX_MATCHES];
    char error_message[100];
    int num_matched_files = 0;
    
    // Compile the regular expression
    status = regcomp(&regex, regex_pattern, REG_EXTENDED | REG_ICASE);
    if (status != 0) {
        regerror(status, &regex, error_message, sizeof(error_message));
        fprintf(stderr, "Error compiling regular expression: %s\n", error_message);
        return -1;
    }
    
    // Loop through each filename and check if it matches the regular expression
    for (i = 0; i < num_files; i++) {
        status = regexec(&regex, filenames[i], MAX_MATCHES, matches, 0);
        if (status == 0) {
            // If the filename matches, add it to the list of matched files
            strncpy(matched_files[num_matched_files], filenames[i], MAX_FILENAME_LENGTH);
            num_matched_files++;
        }
        else if (status != REG_NOMATCH) {
            regerror(status, &regex, error_message, sizeof(error_message));
            fprintf(stderr, "Error matching regular expression: %s\n", error_message);
            return -1;
        }
    }
    
    // Free the memory used by the regular expression
    regfree(&regex);
    
    return num_matched_files;
}

// Function to compare two strings for sorting alphabetically
int compare_strings(const void* a, const void* b) {
    return strcmp(*(const char**)a, *(const char**)b);
}

void join_mp3_files(const char* input_filenames[], int num_input_files, const char* output_filename) {
    char** mp3_filenames = (char**)malloc(MAX_MATCHES * sizeof(char*));
    int num_mp3_files;
    int i;
    FILE* output_file;
    FILE* input_file;

    // Allocate memory for the matched MP3 filenames
    for (i = 0; i < MAX_MATCHES; i++) {
        mp3_filenames[i] = (char*)malloc(MAX_FILENAME_LENGTH * sizeof(char));
    }

    // Filter the input filenames to select only MP3 files
    num_mp3_files = filter_filenames("\\.mp3$", input_filenames, num_input_files, mp3_filenames);

    // Sort the MP3 filenames alphabetically
    qsort(mp3_filenames, num_mp3_files, sizeof(char*), compare_strings);

    // Open the output file for writing
    output_file = fopen(output_filename, "wb");
    if (!output_file) {
        fprintf(stderr, "Error opening output file for writing\n");
        return;
    }

    // Loop through each MP3 file and copy its contents to the output file
    for (i = 0; i < num_mp3_files; i++) {
        input_file = fopen(mp3_filenames[i], "rb");
        if (!input_file) {
            fprintf(stderr, "Error opening input file for reading: %s\n", mp3_filenames[i]);
            continue;
        }

        // Copy the contents of the input file to the output file
        int ch;
        while ((ch = fgetc(input_file)) != EOF) {
            fputc(ch, output_file);
        }

        // Close the input file
        fclose(input_file);
    }

    // Close the output file
    fclose(output_file);

    // Free the memory used by the matched MP3 filenames
    for (i = 0; i < MAX_MATCHES; i++) {
        free(mp3_filenames[i]);
    }
    free(mp3_filenames);
}


// Function to display a progress bar
void progress_bar(int percent, time_t start_time, int total_files, int completed_files) {
    time_t current_time = time(NULL);
    double elapsed_time = difftime(current_time, start_time);
    double estimated_time_remaining = (elapsed_time / completed_files) * (total_files - completed_files);

    printf("[");
    for (int i = 0; i < 50; i++) {
        if (i * 2 < percent) {
            printf("#");
        }
        else {
            printf("-");
        }
    }
    printf("] %d%% (%.0f/%.0f sec elapsed, %.0f/%.0f sec remaining)\r", percent, elapsed_time, elapsed_time + estimated_time_remaining, estimated_time_remaining, elapsed_time + estimated_time_remaining);
    fflush(stdout);
}

int main(int argc, char* argv[]) {
    char** input_filenames = (char**)malloc(MAX_FILENAME_LENGTH * sizeof(char*));
    int num_input_files = 0;
    char* output_filename = NULL;
    DIR* dir;
    struct dirent* ent;
    int i;

    // Allocate memory for input filenames
    for (i = 0; i < MAX_FILENAME_LENGTH; i++) {
        input_filenames[i] = (char*)malloc(MAX_FILENAME_LENGTH * sizeof(char));
    }

    // Parse command line arguments
    if (argc < 3) {
        fprintf(stderr, "Usage: %s [output_file] [input_files/directory]\n", argv[0]);
        return 1;
    }
    output_filename = argv[1];

    // If the second argument is a directory, add all MP3 files in the directory to the input filenames
    dir = opendir(argv[2]);
    if (dir != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (strstr(ent->d_name, ".mp3") != NULL) {
                snprintf(input_filenames[num_input_files], MAX_FILENAME_LENGTH, "%s/%s", argv[2], ent->d_name);
                num_input_files++;
            }
        }
        closedir(dir);
    }
    else {
        // Otherwise, assume the second argument is a list of input filenames
        for (i = 2; i < argc; i++) {
            strncpy(input_filenames[num_input_files], argv[i], MAX_FILENAME_LENGTH);
            num_input_files++;
        }
    }

    // Print the list of input filenames
    printf("Input filenames:\n");
    for (i = 0; i < num_input_files; i++) {
        printf("%s\n", input_filenames[i]);
    }

    // Join the MP3 files and display a progress bar
    printf("Output filename: %s\n", output_filename);
    printf("Joining files...\n");

    time_t start_time = time(NULL);

    for (i = 0; i < 101; i++) {
        progress_bar(i, start_time, num_input_files, i);

        join_mp3_files((const char**)input_filenames, num_input_files, output_filename);
    }

    printf("\nDone.\n");

    // Free the memory used by input filenames
    for (i = 0; i < MAX_FILENAME_LENGTH; i++) {
        free(input_filenames[i]);
    }
    free(input_filenames);

    return 0;
}