import csv

# Specify the path to your CSV file
file_path = 'eth/eth.scores'
file_path = 'all.txt'

counts = {i: 0 for i in range(5)}

# Open the CSV file
with open(file_path, mode='r', newline='') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)
    
    # Optionally, skip the header if there is one
    next(csv_reader)

    # Loop through the rows in the CSV file
    for row in csv_reader:
        total = int(row[1])
        counts[total] += 1

print(counts)
