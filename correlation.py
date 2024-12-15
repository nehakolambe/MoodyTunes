import pandas as pd

def filter_columns_by_correlation(input_file, label_column='labels', threshold=0.05, start_index=18):
    # Load the Excel file
    data = pd.read_excel(input_file)
    
    # Ensure the label column exists
    if label_column not in data.columns:
        raise ValueError(f"Column '{label_column}' not found in the Excel file.")

    # Separate the first 18 columns and the rest
    first_columns = data.iloc[:, :start_index]
    columns_to_check = data.iloc[:, start_index:]
    
    # Calculate the correlation matrix for the subset of columns
    correlation_matrix = columns_to_check.corrwith(data[label_column])

    # Filter columns based on the correlation threshold
    valid_columns = correlation_matrix[
        (correlation_matrix >= threshold) | (correlation_matrix <= -threshold)
    ].index

    # Retain only relevant columns
    filtered_data = pd.concat([first_columns, data[valid_columns]], axis=1)

    # Save the filtered data to a new Excel file
    filtered_data.to_excel(input_file, index=False)

    print(f"\nFiltered columns saved to: {input_file}")

# Parameters
input_file = "<PROVIDE-INPUT-FILE>"
label_column = "labels"  # Replace with the column name for labels
threshold = 0.05  # Define your correlation threshold
start_index = 18  # Define the starting column index

# Call the function
filter_columns_by_correlation(input_file, label_column, threshold, start_index)