from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import argparse

# Set up command line argument parsing
parser = argparse.ArgumentParser(description='Parse YouTube watch history HTML file and convert to CSV')
parser.add_argument('html_file', nargs='?', help='Path to the HTML file to parse')
args = parser.parse_args()

# Determine which HTML file to use
if args.html_file:
    # Use the file specified on command line
    html_file = args.html_file
else:
    # Fall back to checking for default files
    html_files = ['watch-history.html', 'sample_watch_history.html']
    html_file = None
    
    for file_path in html_files:
        if os.path.exists(file_path):
            html_file = file_path
            break
    
    if html_file is None:
        print("Error: No HTML file found.")
        print("")
        print("Usage:")
        print(f"  {sys.argv[0]} <path_to_html_file>")
        print("")
        print("Or place one of these files in the current directory:")
        for file_path in html_files:
            print(f"  - {file_path}")
        print("")
        print("You can drag and drop the HTML file into the terminal after typing:")
        print(f"  python {os.path.basename(sys.argv[0])} ")
        sys.exit(1)

# Check if the specified file exists
if not os.path.exists(html_file):
    print(f"Error: File '{html_file}' not found.")
    sys.exit(1)

print(f"Using HTML file: {html_file}")

# Load your HTML file
with open(html_file, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'lxml')

# Extract watch history entries (adjust selectors as needed)
entries = []
for entry in soup.find_all('div', class_='content-cell'):
    video_title = entry.find('a').text if entry.find('a') else 'Unknown Title'
    video_url = entry.find('a')['href'] if entry.find('a') else 'Unknown URL'
    timestamp = entry.find('br').next_sibling.strip() if entry.find('br') else 'Unknown Date'
    entries.append({'Title': video_title, 'URL': video_url, 'Date Watched': timestamp})

# Convert to DataFrame and save to CSV
df = pd.DataFrame(entries)
df.to_csv('watch_history.csv', index=False)

print(f"Successfully parsed {len(entries)} entries from watch history.")
print("Data saved to 'watch_history.csv'")
