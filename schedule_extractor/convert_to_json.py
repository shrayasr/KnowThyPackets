#!/usr/bin/env python3
"""
Convert extracted PyCon India 2025 schedule HTML files to structured JSON format.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


def parse_time_range(time_str: str, date_str: str) -> tuple[str, str]:
    """
    Parse time range like '10:10 - 10:40' and convert to ISO8601 with timezone.
    
    Args:
        time_str: Time range string like '10:10 - 10:40'
        date_str: Date string like 'September 13th'
    
    Returns:
        Tuple of (start_time_iso, end_time_iso)
    """
    # Extract year from context (PyCon India 2025)
    year = 2025
    
    # Parse month and day from date string
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    # Extract month and day from date_str like "September 13th"
    date_match = re.match(r'(\w+)\s+(\d+)', date_str)
    if not date_match:
        raise ValueError(f"Could not parse date: {date_str}")
    
    month_name, day_str = date_match.groups()
    month = month_map[month_name]
    day = int(day_str)
    
    # Parse time range
    time_match = re.match(r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})', time_str)
    if not time_match:
        raise ValueError(f"Could not parse time range: {time_str}")
    
    start_hour, start_min, end_hour, end_min = map(int, time_match.groups())
    
    # Create datetime objects (assuming IST timezone UTC+5:30)
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    
    start_dt = datetime(year, month, day, start_hour, start_min, tzinfo=ist_offset)
    end_dt = datetime(year, month, day, end_hour, end_min, tzinfo=ist_offset)
    
    return start_dt.isoformat(), end_dt.isoformat()


def extract_session_info(session_element) -> Optional[Dict]:
    """
    Extract session information from a session element.
    
    Args:
        session_element: BeautifulSoup element containing session info
    
    Returns:
        Dictionary with session information or None if not a valid session
    """
    # Check if this is a session link (has href and contains session info)
    if session_element.name != 'a' or not session_element.get('href'):
        return None
    
    # Extract track information
    track_element = session_element.find('p', style=lambda x: x and 'background-color' in x)
    track = track_element.get_text(strip=True) if track_element else "Unknown Track"
    
    # Extract time
    time_elements = session_element.find_all('p', class_='mb-1 font-bold')
    time_str = time_elements[0].get_text(strip=True) if time_elements else ""
    
    # Extract session name
    name_elements = session_element.find_all('p', class_='mb-1 text-md line-clamp-2')
    name = name_elements[0].get_text(strip=True) if name_elements else ""
    
    # Extract speaker(s)
    speaker_elements = session_element.find_all('p', class_='font-semibold text-md text-pycon-blue')
    speaker = speaker_elements[0].get_text(strip=True) if speaker_elements else ""
    
    # Extract link
    link = session_element.get('href', '')
    
    # Skip if essential information is missing
    if not time_str or not name:
        return None
    
    return {
        'time_str': time_str,
        'name': name,
        'track': track,
        'speaker': speaker,
        'link': link
    }


def extract_break_info(break_element) -> Optional[Dict]:
    """
    Extract break/meal/keynote information from non-session elements.
    
    Args:
        break_element: BeautifulSoup element containing break info
    
    Returns:
        Dictionary with break information or None if not a valid break
    """
    if break_element.name != 'div':
        return None
    
    # Look for time and title information
    time_elements = break_element.find_all('p', class_='mb-0 font-bold')
    title_elements = break_element.find_all('p', class_='mb-0 text-lg')
    
    if not time_elements or not title_elements:
        return None
    
    time_str = time_elements[0].get_text(strip=True)
    title = title_elements[0].get_text(strip=True)
    
    return {
        'time_str': time_str,
        'name': title,
        'track': 'General',
        'speaker': '',
        'link': ''
    }


def process_schedule_div(div_content: str) -> Dict[str, List[Dict]]:
    """
    Process a schedule div and extract all sessions.
    
    Args:
        div_content: HTML content of the schedule div
    
    Returns:
        Dictionary with date as key and list of sessions as value
    """
    soup = BeautifulSoup(div_content, 'html.parser')
    
    # Find the date header
    date_header = soup.find('p', string=lambda text: text and ('September' in text and ('13th' in text or '14th' in text)))
    if not date_header:
        return {}
    
    date_str = date_header.get_text(strip=True)
    
    # Find all session and break elements
    all_events = []
    
    # Extract sessions (anchor tags with href)
    for session_link in soup.find_all('a', href=True):
        session_info = extract_session_info(session_link)
        if session_info:
            all_events.append(session_info)
    
    # Extract breaks/meals/keynotes (div tags with specific styling)
    for break_div in soup.find_all('div', style=lambda x: x and 'background-color' in x):
        break_info = extract_break_info(break_div)
        if break_info:
            all_events.append(break_info)
    
    # Convert to final format with ISO8601 timestamps
    sessions = []
    for event in all_events:
        try:
            start_time, end_time = parse_time_range(event['time_str'], date_str)
            sessions.append({
                'From': start_time,
                'To': end_time,
                'Name': event['name'],
                'Track': event['track'],
                'Speaker': event['speaker'],
                'Link': event['link']
            })
        except ValueError as e:
            print(f"[!] Skipping event due to time parsing error: {e}")
            continue
    
    # Remove duplicates (same time, name, track combination)
    seen = set()
    unique_sessions = []
    for session in sessions:
        # Create a unique key based on time, name, and track
        key = (session['From'], session['Name'], session['Track'])
        if key not in seen:
            seen.add(key)
            unique_sessions.append(session)
    
    # Sort sessions by start time
    unique_sessions.sort(key=lambda x: x['From'])
    
    return {date_str: unique_sessions}


def main():
    """Main function to convert HTML files to JSON."""
    extracted_dir = Path("extracted_divs")
    
    if not extracted_dir.exists():
        print("Error: extracted_divs directory not found!")
        return
    
    print("Converting HTML schedule files to JSON...")
    print("-" * 50)
    
    all_schedule_data = {}
    
    # Process each extracted HTML file
    for html_file in extracted_dir.glob("div_*.html"):
        print(f"Processing {html_file.name}...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the schedule div content (remove the wrapper HTML)
        soup = BeautifulSoup(content, 'html.parser')
        schedule_div = soup.find('div', class_='schedule-content')
        
        if schedule_div:
            schedule_data = process_schedule_div(str(schedule_div))
            all_schedule_data.update(schedule_data)
            
            # Count events processed
            total_events = sum(len(events) for events in schedule_data.values())
            print(f"  [+] Extracted {total_events} events")
        else:
            print(f"  [-] No schedule content found in {html_file.name}")
    
    # Save to JSON file
    output_file = "pycon_india_2025_schedule.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_schedule_data, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print(f"[+] Schedule data saved to {output_file}")
    
    # Print summary
    total_days = len(all_schedule_data)
    total_events = sum(len(events) for events in all_schedule_data.values())
    print(f"[+] Summary: {total_days} days, {total_events} events total")
    
    # Show a sample of the data
    print("\n[+] Sample data structure:")
    if all_schedule_data:
        first_date = list(all_schedule_data.keys())[0]
        sample_events = all_schedule_data[first_date][:2]  # Show first 2 events
        print(json.dumps({first_date: sample_events}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()