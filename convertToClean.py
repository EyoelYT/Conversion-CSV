import csv
import re
from typing import List
from datetime import datetime
"""
For every row in the csv
    For every entry in a cell (after a comma)
        If the entry is a title: 
            Add to the list of titles (It is a title if it doesnt start with a number)
        If the entry has the format "nnmin + ...":


"""

'''
Changes 45min + 45min + 45min to 135
Also Changes 1hr15mins + 45min to 240 mins
'''
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

'''
Parses CSV data into arrays of arrays
returns list of list that include strs and ints
'''
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


with open("ST & Work Log - Coursework Log.csv", newline='') as imput_csv_file:
    csv_reader = csv.reader(imput_csv_file)
    modified_rows = []
    set_of_days = set(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

    # # Get Titles
    # list_of_titles = []
    # for line in csv_reader:
    #     modified_row = []
    #     for word in line:
    #         # If title material
    #         if len(word) > 1 and not word[0].isdigit() and word[0] != "(" and word.split(' ')[0] not in set_of_days:
    #             if ("=" in word):
    #                 word = word.partition("=")[0]
    #             if (":" in word):
    #                 word = word.partition(":")[0]
    #             list_of_titles.append(word)
    #             print(word)
    #         # If minute material
    #         if len(word) > 1 and word[0].isdigit():
    #             print("This is digit entry", word)
    current_titles = [0] * 10
    database = dict() # key = title, value = total mins

    for line in csv_reader:
        # line[0] is Date
        for column, entry in enumerate(line):
            # If title material
            if len(entry) > 1 and not entry[0].isdigit() and entry[0] != "(" and entry.split(' ')[0] not in set_of_days:
                if ("=" in entry):
                    entry = entry.partition("=")[0]
                if (":" in entry):
                    entry = entry.partition(":")[0]
                current_titles[column] = entry
                database[entry] = 0
            # If minute material
            if len(entry) > 1 and entry[0].isdigit():
                database[current_titles[column]] += change_mins_to_real_time(entry)
                
    print(current_titles)

with open("output.csv", mode="w", newline="") as output_csv_file:
    csv_writer = csv.writer(output_csv_file)

    # Write the modified rows into the output csv file
    for modified_row in modified_rows:
        csv_writer.writerow(modified_row)

print("Modified rows have successfully been written in output.csv")



