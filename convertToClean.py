import csv
import re
from typing import List
from datetime import datetime


# Changes 45min + 45min + 45min to 135
# Also Changes 1hr15mins + 45min to 240 mins
def change_mins_to_real_time(entry) -> int:
    # Split the entry by '+'
    entry = entry.split('+')

    total_minutes = 0

    # Patterns to match different time formats
    min_pattern = re.compile(r'^\s*(\d+)\s*mins?$')
    hr_min_pattern = re.compile(r'^\s*(\d+)\s*hrs?\s*(\d+)\s*mins?$')
    hr_pattern = re.compile(r'^\s*(\d+)\s*hrs?$')

    for time_part in entry:
        time_part = time_part.strip()

        # Match minutes only, e.g., "45min"
        if min_match := min_pattern.match(time_part):
            total_minutes += int(min_match.group(1))

        # Match hours and minutes, e.g., "1hr15mins"
        elif hr_min_match := hr_min_pattern.match(time_part):
            total_minutes += int(hr_min_match.group(1)) * 60
            total_minutes += int(hr_min_match.group(2))

        # Match hours only, e.g., "2hrs"
        elif hr_match := hr_pattern.match(time_part):
            total_minutes += int(hr_match.group(1)) * 60

    return total_minutes


# Parses CSV data into arrays of arrays
# returns list of list that include strs and ints
def parse_csv_to_arrays(csv_content: str):
    # Split the input into lines
    lines = csv_content.strip().split('\n')
    
    # Initialize an array to hold the resulting data
    result = []
    
    # Patterns to match different time formats
    min_pattern = re.compile(r'(\d+)\s*min(?:s)?')
    hr_min_pattern = re.compile(r'(\d+)\s*hr(?:s)?(?:\s*(\d+)\s*min(?:s)?)?')
    
    for line in lines:
        # Split the line by commas
        cells = line.split(',')
        processed_cells = []
        
        for cell in cells:
            cell = cell.strip()
            total_minutes = 0
            
            # Check for time-related entries
            if '+' in cell or 'min' in cell or 'hr' in cell:
                time_parts = re.split(r'\+|=', cell)
                for part in time_parts:
                    part = part.strip()
                    if min_match := min_pattern.search(part):
                        total_minutes += int(min_match.group(1))
                    elif hr_min_match := hr_min_pattern.search(part):
                        hours = int(hr_min_match.group(1))
                        minutes = int(hr_min_match.group(2)) if hr_min_match.group(2) else 0
                        total_minutes += hours * 60 + minutes
                
                processed_cells.append(total_minutes)
            else:
                processed_cells.append(cell)
        
        result.append(processed_cells)
    
    return result


# Convert string into a List of lists
def extract_course_times(data):
    course_columns = {}
    time_data = {}
    
    # Iterate over each row in the data
    for row in data:
        if '20' in row[0]:  # Check if the first cell might contain a date
            date = row[0]
            date_obj = datetime.strptime(date, '%A %B %d %Y')
            for idx, time in enumerate(row[1:], start=1):
                if time and isinstance(time, int):  # Check if there is a time entry
                    course = course_columns.get(idx, "Unknown Course")
                    if course not in time_data:
                        time_data[course] = {}
                    if date_obj not in time_data[course]:
                        time_data[course][date_obj] = 0
                    time_data[course][date_obj] += time
        else:
            # Update course mappings for current columns
            for idx, title in enumerate(row):
                if title:  # There's a new course title in this column
                    course_columns[idx] = title
    
    return time_data


# First read the csv into a variable
csv_content = ""
with open("ST & Work Log - Coursework Log.csv", newline='') as imput_csv_file:
    csv_reader = csv.reader(imput_csv_file)
    for row in csv_reader:
        csv_content = csv_content + ','.join(row) + "\n"
        
# Turn the csv string into a list of lists
parsed_data = parse_csv_to_arrays(csv_content)
for row in parsed_data:
    print(row[0])

# Extract course times from the array into a dictionary of dictionaries
#  with format: {"Course": {"date": total_time}, ...}
# FIXME : Some kind of issue with the function? It truncates the date stored
time_data = extract_course_times(parsed_data)

# # Write time_data content into txt file
# with open("fileOne.txt", "a") as output_file:
#     # Write the modified rows into the output csv file
#     for course, dates in time_data.items():
#         output_file.write(f"Course: {course}\n")
#         for date, time in dates.items():
#             output_file.write(f"  Date: {date.strftime('%Y-%m-%d')}, Time Studied: {time} minutes\n")
#             # print(f"  Date: {date.strftime('%Y-%m-%d')}, Time Studied: {time} minutes")


print("Modified rows have successfully been written in output.csv")



