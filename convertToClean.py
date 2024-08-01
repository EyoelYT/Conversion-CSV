import csv
import re
from typing import List
from datetime import datetime


# Changes 45min + 45min + 45min to 135
# Also Changes 1hr15mins + 45min to 240 mins
def change_mins_to_real_time(entry: str) -> int:
    # Removing any text within parentheses and any text following '='
    entry = re.sub(r'\(.*?\)', '', entry)  # Removes any text in parentheses
    entry = re.sub(r'=.+$', '', entry)  # Removes any text after '='

    # Split the cleaned entry by '+'
    entry_parts = entry.split('+')

    total_minutes = 0

    # Patterns to match different time formats
    min_pattern = re.compile(r'^\s*(\d+)\s*mins?$')
    hr_min_pattern = re.compile(r'^\s*(\d+)\s*hrs?\s*(\d+)\s*mins?$')
    hr_pattern = re.compile(r'^\s*(\d+)\s*hrs?$')

    for time_part in entry_parts:
        time_part = time_part.strip()

        # Match minutes only, e.g., "45min"
        if min_match := min_pattern.match(time_part):
            total_minutes += int(min_match.group(1))

        # Match hours and minutes, e.g., "1hr15mins"
        elif hr_min_match := hr_min_pattern.match(time_part):
            total_minutes += int(hr_min_match.group(1)) * 60
            if hr_min_match.group(2):
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
            # Remove any text after an equals sign
            cell = cell.split('=')[0].strip()
            total_minutes = 0

            # Check for time-related entries
            if '+' in cell or 'min' in cell or 'hr' in cell:
                time_parts = re.split(r'\+', cell)
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

# Convert List of lists into a structured data where we can ask questions like:
  # counts total mins in total, for title/course
  # can query the total time spent each day
  # can query the time spent for each activity: per day, per month, per year, ...
def extract_course_times(data):
    course_columns = {}
    time_data = {}

    # Compile a pattern to detect date strings reliably
    date_pattern = re.compile(r'\w+\s+\w+\s+\d+\s+\d+')

    for row in data:
        # Assume the first cell might contain a date if it matches the date pattern
        if date_pattern.match(row[0]):
            date_str = row[0]
            date_obj = datetime.strptime(date_str, '%A %B %d %Y')
            # Parse time data for this date
            for idx, cell in enumerate(row[1:], start=1):
                if isinstance(cell, int) and cell > 0:  # Checking if the cell has time data
                    course = course_columns.get(idx, "Unknown Course")
                    if course not in time_data:
                        time_data[course] = {}
                    if date_obj not in time_data[course]:
                        time_data[course][date_obj] = 0
                    time_data[course][date_obj] += cell
                elif isinstance(cell, str) and cell != '':
                    course_columns[idx] = cell
        else:
            # Update or validate course mappings for current columns
            for idx, title in enumerate(row):
                if title and title != '':  # Non-empty means a potential title
                    course_columns[idx] = title

    return time_data

# First read the csv into a variable
csv_file_to_be_read = "ST & Work Log - Coursework Log.csv"
csv_content = ""
with open(csv_file_to_be_read, newline='') as imput_csv_file:
    csv_reader = csv.reader(imput_csv_file)
    for row in csv_reader:
        csv_content = csv_content + ','.join(row) + "\n"

#TESTING
# csv_content = ",Quantitative Analysis - MAT-136,,English Composition I - ENG-122,,\n\nFriday September 3 2021,50min + 50min + 50min + 50min + 50min + 50min,,,,\nSaturday September 4 2021,,,,,\nSunday September 5 2021,,,(Morn) 50min + 50min + 50min + 50 min + 50 min + 43min = 4hr53min,,\nMonday September 6 2021,,,,,\n,Precalculus - MAT-140,,English Composition II - ENG-123,,\nMonday October 25 2021,,,,,\nTuesday October 26 2021,(Morn) 45min +  45min = 1hr30min,,,,\nWednesday October 27 2021,,,,,\nThursday October 28 2021,(AfteN) 45min + 35min + 45min + 45min + 45min + 45min,,(AfteN) 35min + 45min,,\nFriday October 29 2021,,,,,\nMonday January 10 2022,,,,,Drivers Ed\nTuesday January 11 2022,23min,,,,45min + 45min = 1hr30min\nWednesday January 12 2022,35min,,,,"

# Turn the csv string into a list of lists
parsed_data = parse_csv_to_arrays(csv_content)

#TESTING
# for row in parsed_data:
#     print(row)
# print(parsed_data)

# Extract course times from the array into a dictionary of dictionaries
#  with format: {"Course": {"date": total_time}, ...}
# FIXME : Some kind of issue with the function? It truncates the date stored
time_data = extract_course_times(parsed_data)
# print(time_data)

file_to_write_in = "fileOne.txt"
# Write time_data content into txt file
with open(file_to_write_in, "a") as output_file:
    # Write the modified rows into the output csv file
    for course, dates in time_data.items():
        output_file.write(f"Course: {course}\n")
        print(f"\nCourse: {course}")
        for date, time in dates.items():
            output_file.write(f"  Date: {date.strftime('%Y-%m-%d')}, Time Studied: {time} minutes\n")
            print(f"  Date: {date.strftime('%Y-%m-%d')}, Time Studied: {time} minutes")


print(f"\nModified rows have successfully been written in {file_to_write_in}")
