import os
import csv

def save_list_to_csv(data, csv_file_path):
    directory = os.path.dirname(csv_file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)