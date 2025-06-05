import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import h5py
import numpy as np
import os

def get_h5_plot_stuff(file_path, x_signal_name=b"Running Time", y_signal_name=b"Axial Force"):
    """
    Extracts X and Y data columns, their units, and suggested plot labels/title
    from an HDF5 file. Finds the first group containing 'Signals'
    (with x_signal_name and y_signal_name) and a 'Scans' dataset.

    Args:
        file_path (str): Path to the HDF5 file.
        x_signal_name (bytes or str): Name of the signal for the x-axis
                                      (e.g., b"Running Time" or "Running Time").
        y_signal_name (bytes or str): Name of the signal for the y-axis
                                      (e.g., b"Axial Force" or "Axial Force").

    Returns:
        tuple: (x_data, y_data, x_label, y_label, title_str, x_unit, y_unit)
               Returns (None, None, None, None, None, None, None) if an error occurs or
               data cannot be found.
    """

    # Ensure signal names are bytes for internal comparison and consistent decoding
    if isinstance(x_signal_name, str):
        x_signal_b = x_signal_name.encode('utf-8')
    elif isinstance(x_signal_name, bytes):
        x_signal_b = x_signal_name
    else:
        print(f"Error: x_signal_name must be a string or bytes, but got {type(x_signal_name)}.")
        return None, None, None, None, None, None, None

    if isinstance(y_signal_name, str):
        y_signal_b = y_signal_name.encode('utf-8')
    elif isinstance(y_signal_name, bytes):
        y_signal_b = y_signal_name
    else:
        print(f"Error: y_signal_name must be a string or bytes, but got {type(y_signal_name)}.")
        return None, None, None, None, None, None, None

    print(f"Attempting to extract data for '{y_signal_b.decode('utf-8')}' vs. '{x_signal_b.decode('utf-8')}' from: {os.path.basename(file_path)}")

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None, None, None, None, None, None, None

    potential_groups_info = []

    try:
        with h5py.File(file_path, 'r') as hf:
            for item_name in hf.keys(): # Iterate over top-level items (groups/datasets)
                if isinstance(hf[item_name], h5py.Group):
                    group = hf[item_name]
                    if 'Signals' in group and isinstance(group['Signals'], h5py.Dataset) and \
                       'Scans' in group and isinstance(group['Scans'], h5py.Dataset):
                        try:
                            signals_data_arr = group['Signals'][:]
                            current_x_idx = -1
                            current_y_idx = -1
                            
                            for i, signal_entry in enumerate(signals_data_arr):
                                if signal_entry['Name'] == x_signal_b:
                                    current_x_idx = i
                                if signal_entry['Name'] == y_signal_b:
                                    current_y_idx = i
                            
                            if current_x_idx != -1 and current_y_idx != -1:
                                potential_groups_info.append({
                                    'group_name': item_name,
                                    'x_idx': current_x_idx,
                                    'y_idx': current_y_idx,
                                    'signals_dataset_arr': signals_data_arr,
                                })
                        except Exception as e:
                            print(f"Warning: Could not fully process 'Signals' in group '{item_name}': {e}")
            
            if not potential_groups_info:
                print(f"Error: No group found in '{os.path.basename(file_path)}' that contains all of the following:")
                print(f"  1. A 'Signals' dataset with both '{x_signal_b.decode('utf-8')}' and '{y_signal_b.decode('utf-8')}'.")
                print(f"  2. A 'Scans' dataset.")
                return None, None, None, None, None, None, None

            chosen_group_info = potential_groups_info[0]
            if len(potential_groups_info) > 1:
                group_names_found = [g['group_name'] for g in potential_groups_info]
                print(f"Warning: Target signals and 'Scans' dataset found in multiple groups: {group_names_found}.")
                print(f"Using data from the first suitable group found: '{chosen_group_info['group_name']}'.")

            group_name = chosen_group_info['group_name']
            x_col_idx = chosen_group_info['x_idx']
            y_col_idx = chosen_group_info['y_idx']
            signals_metadata = chosen_group_info['signals_dataset_arr']
            
            target_group = hf[group_name]

            print(f"\nProcessing data from group: '{group_name}'")
            print(f"  '{x_signal_b.decode('utf-8')}' (X-axis) found at column index: {x_col_idx}")
            print(f"  '{y_signal_b.decode('utf-8')}' (Y-axis) found at column index: {y_col_idx}")
                
            print("Reading 'Scans' data columns...")
            try:
                x_data = target_group['Scans'][:, x_col_idx]
                y_data = target_group['Scans'][:, y_col_idx]
            except Exception as e:
                print(f"Error reading 'Scans' data columns from group '{group_name}': {e}")
                return None, None, None, None, None, None, None
            
            print(f"Data read. X-data points: {len(x_data)}, Y-data points: {len(y_data)}")

            # --- Prepare metadata for plotting ---
            x_unit = signals_metadata[x_col_idx]['Unit'].decode('utf-8')
            y_unit = signals_metadata[y_col_idx]['Unit'].decode('utf-8')

            # Using rf-strings for potential LaTeX in labels/titles if matplotlib's rcParams for usetex is True
            x_label_str = rf"{x_signal_b.decode('utf-8')} ({x_unit})"
            y_label_str = rf"{y_signal_b.decode('utf-8')} ({y_unit})"
            title_str = rf"{y_signal_b.decode('utf-8')} vs. {x_signal_b.decode('utf-8')}"
            
            print("Data and metadata extraction complete.")
            return x_data, y_data, x_label_str, y_label_str, title_str, x_unit, y_unit

    except Exception as e:
        print(f"An unexpected error occurred during HDF5 processing: {e}")
        return None, None, None, None, None, None, None

def check_h5_file(filepath, output_file=None):
    """
    Attempts to open and inspect an HDF5 file.
    Reports if it's a valid HDF5 file and lists its contents.
    
    Args:
        filepath (str): Path to the HDF5 file.
        output_file (str, optional): Path to a text file to write output. 
                                     If None, prompts the user to select a file.
    """
    if not os.path.exists(filepath):
        message = f"Error: File not found at '{filepath}'"
        print(message) if output_file is None else _write_to_output(message, output_file)
        return

    if not h5py.is_hdf5(filepath):
        message = f"'{filepath}' is NOT a valid HDF5 file according to h5py.\nThis could mean it's heavily encrypted or not an HDF5 file at all."
        print(message) if output_file is None else _write_to_output(message, output_file)
        return

    if output_file is None:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Select output file"
        )
        if not output_file:
            print("No output file selected.")
            return  # Exit if the user cancels the dialog

    try:
        with h5py.File(filepath, 'r') as f:
            message = f"'{filepath}' is a valid HDF5 file.\n\n--- Contents ---"
            print(message) if output_file is None else _write_to_output(message, output_file)
            
            def print_h5_items(name, obj):
                if isinstance(obj, h5py.Group):
                    message = f"Group: /{name}/"
                    print(message) if output_file is None else _write_to_output(message, output_file)
                    if obj.attrs:
                        message = "  Attributes:"
                        print(message) if output_file is None else _write_to_output(message, output_file)
                        for attr_name, attr_value in obj.attrs.items():
                            message = f"    {attr_name}: {attr_value}"
                            print(message) if output_file is None else _write_to_output(message, output_file)
                elif isinstance(obj, h5py.Dataset):
                    message = f"  Dataset: /{name}/ (Shape: {obj.shape}, Dtype: {obj.dtype})"
                    print(message) if output_file is None else _write_to_output(message, output_file)
                    try:
                        if obj.shape: # If the dataset has a shape (is not scalar)
                            # Check if it's a 1D structured array of small size (e.g., for signal definitions)
                            if obj.ndim == 1 and obj.dtype.names and 0 < obj.shape[0] <= 20:
                                message = f"    Data entries (all {obj.shape[0]}):"
                                print(message) if output_file is None else _write_to_output(message, output_file)
                                for i in range(obj.shape[0]):
                                    message = f"      [{i}]: {obj[i]}"
                                    print(message) if output_file is None else _write_to_output(message, output_file)
                            else: # For other datasets, show only a sample of the first element
                                sample_data = obj[0] if obj.ndim == 1 else obj[tuple(0 for _ in obj.shape)]
                                message = f"    Sample data: {sample_data}"
                                print(message) if output_file is None else _write_to_output(message, output_file)
                        else:
                            message = f"    Scalar data: {obj[()]}"
                            print(message) if output_file is None else _write_to_output(message, output_file)
                    except Exception as e:
                        message = f"    Could not read sample data (possibly encrypted): {e}"
                        print(message) if output_file is None else _write_to_output(message, output_file)
                    
                    if obj.compression or obj.compression_opts or obj.id.get_create_plist().get_nfilters() > 0:
                        message = f"    Note: Dataset '{name}' uses compression/filters."
                        print(message) if output_file is None else _write_to_output(message, output_file)
                        try:
                            plist = obj.id.get_create_plist()
                            num_filters = plist.get_nfilters()
                            for i in range(num_filters):
                                filter_id, cd_elements, name, flags = plist.get_filter(i)
                                message = f"      Filter {i}: ID={filter_id}, Name='{name}', Flags={flags}"
                                print(message) if output_file is None else _write_to_output(message, output_file)
                        except Exception as e:
                            message = f"      Could not retrieve detailed filter info: {e}"
                            print(message) if output_file is None else _write_to_output(message, output_file)

            f.visititems(print_h5_items)

            message = "\n--- End of Contents ---"
            print(message) if output_file is None else _write_to_output(message, output_file)

    except OSError as e:
        message = f"Error opening '{filepath}' with h5py: {e}"
        print(message) if output_file is None else _write_to_output(message, output_file)
        if "unable to open file" in str(e).lower() or "not a HDF5 file" in str(e).lower():
            message = "This often indicates a fundamental issue like file corruption,\nor it's not an HDF5 file at all, or it's encrypted at a lower level."
            print(message) if output_file is None else _write_to_output(message, output_file)
        elif "unable to initialize object" in str(e).lower() or "read failed" in str(e).lower():
            message = "This might indicate that the data within is encrypted with an unknown filter."
            print(message) if output_file is None else _write_to_output(message, output_file)
        else:
            message = "The error suggests potential encryption, a proprietary HDF5 variant, or corruption."
            print(message) if output_file is None else _write_to_output(message, output_file)
    except Exception as e:
        message = f"An unexpected error occurred while reading '{filepath}': {e}"
        print(message) if output_file is None else _write_to_output(message, output_file)

def _write_to_output(message, output_file):
    """Helper function to write to the output file."""
    try:
        with open(output_file, 'a') as f:  # Append mode
            f.write(message + '\n')
    except Exception as e:
        print(f"Error writing to file '{output_file}': {e}")

def get_session_names(h5_file_obj):
    """Extracts and sorts session names from an HDF5 file object."""
    session_names = [name for name in h5_file_obj.keys() if name.startswith("Session")]
    session_names.sort() # Sorts lexicographically, which works for "Session000...", "Session000...A"
    return session_names

def extract_data_from_h5(file_path, running_time_signal_name=b"Running Time"):
    """
    Extracts 'Scans', 'Signals', attributes, and 'Triggers' data from an HDF5 file.
    """
    all_scans_list = []
    signals_data = None
    running_time_col_idx = -1
    file_attributes = None
    triggers_data = None
    
    print(f"Processing file: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None, None, -1, None, None

    with h5py.File(file_path, 'r') as hf:
        session_names = get_session_names(hf)

        if not session_names:
            print(f"Warning: No 'Session' groups found in {file_path}.")
            return None, None, -1, None, None

        # Assume Signals, Triggers, and root attributes are consistent across sessions;
        # take from the first available session.
        first_session_name = session_names[0]
        first_session_group = hf[first_session_name]

        if 'Signals' in first_session_group:
            signals_data = first_session_group['Signals'][:]
            for i, signal_entry in enumerate(signals_data):
                if signal_entry['Name'] == running_time_signal_name:
                    running_time_col_idx = i
                    break
            if running_time_col_idx == -1:
                print(f"Warning: '{running_time_signal_name.decode()}' signal not found in {first_session_name} of {file_path}.")
        else:
            print(f"Warning: 'Signals' dataset not found in {first_session_name} of {file_path}.")

        file_attributes = dict(first_session_group.attrs)
        if 'Triggers' in first_session_group:
            triggers_data = first_session_group['Triggers'][:]
        else:
            print(f"Warning: 'Triggers' dataset not found in {first_session_name} of {file_path}.")
            
        # Extract Scans from all sessions
        for session_name in session_names:
            session_group = hf[session_name]
            if 'Scans' in session_group:
                scans = session_group['Scans'][:]
                all_scans_list.append(scans)
            else:
                print(f"Warning: 'Scans' dataset not found in {session_name} of {file_path}.")
    
    if not all_scans_list:
        print(f"No 'Scans' data extracted from {file_path}.")
        return None, signals_data, running_time_col_idx, file_attributes, triggers_data
    
    combined_scans_for_file = np.concatenate(all_scans_list, axis=0)
    return combined_scans_for_file, signals_data, running_time_col_idx, file_attributes, triggers_data

def combine_and_sort_h5_files(file_paths, output_file_path):
    """
    Combines data from two HDF5 files into a single file, sorted by running time.
    Assumes the first file in the list provides the primary metadata (Signals, Attributes).

    Args:
        file_paths (list): A list containing exactly two paths to the input HDF5 files.
        output_file_path (str): The path for the combined output HDF5 file.
    """
    if len(file_paths) != 2:
        print("Error: combine_h5_files requires exactly two input file paths.")
        return

    file_path_high = file_paths[0]
    file_path_low = file_paths[1]

    # Extract data
    scans_high, signals_high, rt_idx_high, attrs_high, triggers_high = extract_data_from_h5(file_path_high)
    scans_low, signals_low, rt_idx_low, attrs_low, triggers_low = extract_data_from_h5(file_path_low)

    # Determine which signals metadata and running time column index to use
    signals_to_write = None
    running_time_idx = -1
    attributes_to_write = None
    triggers_to_write = None

    if signals_high is not None and rt_idx_high != -1:
        signals_to_write = signals_high
        running_time_idx = rt_idx_high
        attributes_to_write = attrs_high
        triggers_to_write = triggers_high
        print(f"Using metadata (Signals, Attributes, Triggers) from: {file_path_high}")
        if signals_low is not None and not np.array_equal(signals_high, signals_low):
            print(f"Warning: 'Signals' metadata differs between files. Prioritizing {os.path.basename(file_path_high)}.")
    elif signals_low is not None and rt_idx_low != -1:
        signals_to_write = signals_low
        running_time_idx = rt_idx_low
        attributes_to_write = attrs_low
        triggers_to_write = triggers_low
        print(f"Using metadata (Signals, Attributes, Triggers) from: {file_path_low} (as {os.path.basename(file_path_high)} was incomplete).")
    else:
        print("Error: Could not determine a valid 'Signals' dataset or 'Running Time' column index from either file. Exiting.")
        exit()

    if running_time_idx == -1:
        print("Error: 'Running Time' column index could not be determined. Exiting.")
        exit()

    # Combine 'Scans' data
    all_scans_list_combined = []
    if scans_high is not None:
        all_scans_list_combined.append(scans_high)
    if scans_low is not None:
        all_scans_list_combined.append(scans_low)

    if not all_scans_list_combined:
        print("Error: No 'Scans' data available to combine. Exiting.")
        exit()

    combined_scans = np.concatenate(all_scans_list_combined, axis=0)
    print(f"Total 'Scans' rows combined: {combined_scans.shape[0]}")

    # Sort by 'Running Time'
    print(f"Sorting combined 'Scans' data by 'Running Time' (column index {running_time_idx})...")
    sort_indices = combined_scans[:, running_time_idx].argsort()
    sorted_scans = combined_scans[sort_indices]
    print("Sorting complete.")

    # Write to new HDF5 file
    print(f"Writing combined and sorted data to: {output_file_path}")
    with h5py.File(output_file_path, 'w') as hf_out:
        # Create a main group for the combined data
        main_group = hf_out.create_group('CombinedDataSession')

        # Write datasets
        main_group.create_dataset('Scans', data=sorted_scans, compression="gzip")
        if signals_to_write is not None:
            main_group.create_dataset('Signals', data=signals_to_write, compression="gzip")
        if triggers_to_write is not None:
            main_group.create_dataset('Triggers', data=triggers_to_write, compression="gzip")

        # Write attributes
        if attributes_to_write:
            for attr_name, attr_val in attributes_to_write.items():
                main_group.attrs[attr_name] = attr_val
        # Update specific attributes for the new combined dataset
        main_group.attrs['DisplayName'] = 'Combined High and Low Frequency Data (Sorted by Running Time)'
        main_group.attrs['Name'] = 'combinedCyclicDaqActivity'
        main_group.attrs['SessionIndex'] = 0 # Representing as a single new session
        main_group.attrs['OriginalFileHigh'] = os.path.basename(file_path_high)
        main_group.attrs['OriginalFileLow'] = os.path.basename(file_path_low)

        # Create a simplified 'Groups' dataset for the combined data
        # This will point to all scans in the new 'Scans' dataset
        # Attempt to use dtype from an original 'Groups' dataset if possible
        groups_dtype = None
        try:
            with h5py.File(file_path_high, 'r') as hf_temp: # or file_path_low
                temp_session_names = get_session_names(hf_temp)
                if temp_session_names and f'{temp_session_names[0]}/Groups' in hf_temp:
                    groups_dtype = hf_temp[f'{temp_session_names[0]}/Groups'].dtype
        except Exception as e:
            print(f"Could not read Groups dtype from original files: {e}")

        if groups_dtype is None: # Fallback dtype if original cannot be read
            groups_dtype = np.dtype([('[Id]', '<i8'), ('[ScanStart]', '<i8'), ('[ScanCount]', '<i8'), ('[Tag]', 'S10')]) # S10 for bytestring tag
            print("Warning: Using fallback dtype for 'Groups' dataset.")

        num_total_scans = sorted_scans.shape[0]
        group_entry_data = np.array([(1, 0, num_total_scans, b'Combined')], dtype=groups_dtype) # Example Tag
        main_group.create_dataset('Groups', data=group_entry_data, compression="gzip")

    print(f"Successfully created combined and sorted HDF5 file: {output_file_path}")

def extract_and_print_signal_info(h5_filepath):
    """
    Extracts and prints signal names and units from the HDF5 file.

    Args:
        h5_filepath (str): Path to the HDF5 file.

    Returns:
        tuple: A tuple containing two lists: (signal_names, signal_units).
               Returns (None, None) if an error occurs.
    """
    signal_names = []
    signal_units = []

    if not os.path.exists(h5_filepath):
        print(f"Error: File not found at '{h5_filepath}'")
        return None, None

    try:
        with h5py.File(h5_filepath, 'r') as hf:
            if 'CombinedDataSession' not in hf:
                print(f"Error: 'CombinedDataSession' group not found in '{h5_filepath}'.")
                return None, None
            
            combined_group = hf['CombinedDataSession']

            if 'Signals' not in combined_group:
                print(f"Error: 'Signals' dataset not found in 'CombinedDataSession' in '{h5_filepath}'.")
                return None, None
            
            signals_data = combined_group['Signals'][:]
            
            print(f"\n--- Signals Information from: {os.path.basename(h5_filepath)} ---")
            if len(signals_data) == 0:
                print("No signals found in the 'Signals' dataset.")
            else:
                print(f"{'Index':<6} {'Signal Name':<30} {'Unit':<15}")
                print("-" * 55)
                for i, entry in enumerate(signals_data):
                    name = entry['Name'].decode('utf-8') if isinstance(entry['Name'], bytes) else entry['Name']
                    unit = entry['Unit'].decode('utf-8') if isinstance(entry['Unit'], bytes) else entry['Unit']
                    signal_names.append(name)
                    signal_units.append(unit)
                    print(f"{i:<6} {name:<30} {unit:<15}")
            print("--- End of Signals Information ---\n")
            
            return signal_names, signal_units

    except Exception as e:
        print(f"An error occurred while reading '{h5_filepath}': {e}")
        return None, None
