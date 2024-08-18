import argparse
import os
import sys
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Parse and filter log files.")
    parser.add_argument('log_file', help='Path to the log file.')
    parser.add_argument(
        'log_level',
        nargs='?',
        choices=['INFO', 'WARNING', 'ERROR'],
        help='Log level to filter by (INFO, WARNING, ERROR).'
    )
    parser.add_argument('--start_date', type=lambda d: validate_date(d, parser),
                        help='Start date in YYYY-MM-DD format.')
    parser.add_argument('--end_date', type=lambda d: validate_date(d, parser),
                        help='End date in YYYY-MM-DD format.')
    
    return parser.parse_args()

def validate_date(date_text, parser):
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        parser.error(f"Incorrect date format for '{date_text}'. Expected YYYY-MM-DD.")

def process_log_file(log_file_path, log_level=None, start_date=None, end_date=None):
    if not os.path.isfile(log_file_path):
        logging.error(f"The file '{log_file_path}' does not exist.")
        sys.exit(1)

    try:
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        logging.error(f"Error reading the file: {e}")
        sys.exit(1)

    for line in lines:
        line = line.strip()
        if not line:
            continue  

        try:
            if ']' not in line or ': ' not in line:
                logging.warning(f"Skipping malformed line: '{line}'")
                continue

            
            timestamp_str, rest = line.split('] ', 1)
            log_datetime = datetime.strptime(timestamp_str[1:], '%Y-%m-%d %H:%M:%S')

            log_level_colon_index = rest.find(':')
            entry_log_level = rest[:log_level_colon_index]
            message = rest[log_level_colon_index + 2:]

            
            if log_level and entry_log_level != log_level:
                continue

            if start_date and log_datetime < start_date:
                continue

            if end_date and log_datetime > end_date:
                continue

            
            print(line)

        except ValueError as ve:
            logging.warning(f"Skipping line with invalid date format: '{line}'. Error: {ve}")
        except Exception as e:
            logging.warning(f"Failed to parse line '{line}'. Error: {e}")

def main():
    args = parse_arguments()

    if args.start_date and not args.end_date:
        logging.error("Both --start_date and --end_date must be provided together.")
        sys.exit(1)

    process_log_file(args.log_file, args.log_level, args.start_date, args.end_date)

if __name__ == '__main__':
    main()
