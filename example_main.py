'''
This script contains an example workflow for ingesting and analyzing HDF5 data from MTS Multipurpose Elite

'''

# Import our custom functions:
import functions as f

# Import matplotlib for plotting:
import matplotlib.pyplot as plt



# Assign file locations:

low_freq_cycles_path = '/media/sam/METALS extl/DATA/METALS/Fatigue/MTS/Sample 27/Specimen 1/maybe 10mil h5/cyclicDaqActivity2-Daq(1).h5'
high_freq_cycles_path = '/media/sam/METALS extl/DATA/METALS/Fatigue/MTS/Sample 27/Specimen 1/maybe 10mil h5/cyclicDaqActivity1-Daq(1).h5'
output_file_path = '/media/sam/METALS extl/DATA/METALS/Fatigue/MTS/Sample 27/Specimen 1/maybe 10mil h5/combined_sorted_data.h5'

# Quickly check that the databases are in a valid format:

# f.check_h5_file(low_freq_cycles_path, output_file="low_freq_h5_check.txt")
# f.check_h5_file(high_freq_cycles_path, output_file="high_freq_h5_check.txt")
#     # NOTE: If these two text files contain similar outputs, and you can `ctrl+f` search for a field, like "Running Time" and find it, that's a good sign that the datafiles are correctly formatted.



# # Combine databases into one file and sort by running time:

# f.combine_and_sort_h5_files([low_freq_cycles_path, high_freq_cycles_path], output_file_path)


# # Extract and print the avialiable signals in the combined file:

# print("\nChecking signals in the combined file:")
# signal_names, signal_units = f.extract_and_print_signal_info(output_file_path)

# if signal_names and signal_units:
#     print("Available signal names:", signal_names)
#     print("Corresponding units:", signal_units)


# Make a basic plot of force vs. time:

# Use `get_h5_plot_stuff` to extract data columns from the database:
x_data, y_data, x_label, y_label, title_str, x_unit, y_unit = f.get_h5_plot_stuff(output_file_path, x_signal_name=b"Running Time", y_signal_name=b"Axial Force")

# set figure save path:
output_plot_path = '/media/sam/METALS extl/DATA/METALS/Fatigue/MTS/Sample 27/Specimen 1/maybe 10mil h5/axial_force_vs_time.png'

# Set Matplotlib to use LaTeX for all text rendering
# plt.rcParams.update({
#     "text.usetex": True,  # Enable LaTeX rendering
#     "font.family": "serif",  # Use a serif font family
#     "font.serif": ["Computer Modern Roman"],  # Or "Times New Roman", "Palatino", etc.
#     # For sans-serif, you might use:
#     # "font.family": "sans-serif",
#     # "font.sans-serif": ["Computer Modern Sans serif"], # Or "Helvetica", "Arial", etc.
#     "axes.unicode_minus": False,  # Ensure minus signs are handled correctly by LaTeX
# })

# Generate the plot:
if x_data is not None and y_data is not None:
    print(f"Generating plot: {title_str}")
    plt.figure(figsize=(12,6))
    plt.plot(x_data, y_data, linestyle='-', marker=None, color='b', linewidth=0.5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title_str)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_plot_path)
    print(f"Plot saved to: {output_plot_path}")
else:
    print("Error: Data extraction failed.")
