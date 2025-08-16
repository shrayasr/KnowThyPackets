# DNS Server for PyCon India 2025 Schedule - Implementation Plan

## Project Overview

Build a DNS server that responds to schedule queries for PyCon India 2025 conference. The server will use Python, UV package manager, and Scapy for network packet handling to create a custom DNS server that responds with conference schedule information as TXT records.

## Target Functionality

The DNS server should respond to queries like:
- `dig now.talks @localhost`
- `dig next.talks @localhost`
- `dig day1.talks @localhost`
- `dig day2.talks @localhost`
- `dig track1.talks @localhost`
- `dig track2.talks @localhost`
- `dig track3.talks @localhost`
- `dig general.talks @localhost`

## Response Format Specification

### Format Pattern
- **With Speaker(s):** `"[Track] [Start]-[End] - [Talk Name] by [Speaker(s)]"`
- **Without Speaker:** `"[Track] [Start]-[End] - [Event Name]"`

### Format Details
- Times in 24-hour format (HH:MM)
- Multiple speakers separated by commas
- Track names: "Track 1", "Track 2", "Track 3", "General"
- Start/End times from the schedule JSON (converted from ISO format)

### Example Responses

#### Current talks query (`now.talks`) at 10:15 AM Sept 13:
```
now.talks.               300    IN    TXT    "Track 1 10:10-10:40 - MCP Unlocked: The Key to Smarter AI Contextualization by Sasidhar Donaparthi"
now.talks.               300    IN    TXT    "Track 2 10:10-10:40 - Is FastAPI really fast ? by Princekumar Dobariya"
now.talks.               300    IN    TXT    "Track 3 10:10-10:40 - Lint Like Lightning, Deploy Like a Ninja: Ruff + Dagger in Action by Urvashi Choubey"
```

#### Next talk query (`next.talks`) at 10:15 AM Sept 13:
```
next.talks.              300    IN    TXT    "Track 1 10:50-11:20 - Mastering Prompts with Feedback and Pydantic by Mahima Arora, Aarti Jha"
```

#### Track-specific query (`track2.talks`):
```
track2.talks.            300    IN    TXT    "Track 2 10:10-10:40 - Is FastAPI really fast ? by Princekumar Dobariya"
track2.talks.            300    IN    TXT    "Track 2 10:50-11:20 - Finding a Needle in the Haystack - Debugging Performance Issues by Puneet Khushwani"
track2.talks.            300    IN    TXT    "Track 2 11:30-12:00 - Implementing an MCP Server for DBMS in Python — YDB's Experience by Ivan Blinkov"
```

#### General track events (`general.talks`):
```
general.talks.           300    IN    TXT    "General 07:30-08:45 - REGISTRATIONS / BREAKFAST"
general.talks.           300    IN    TXT    "General 09:00-09:15 - OPENING ADDRESS"
general.talks.           300    IN    TXT    "General 09:20-10:00 - KEYNOTE 1"
general.talks.           300    IN    TXT    "General 12:40-14:00 - LUNCH"
```

## Data Source

The schedule data is available in `pycon_india_2025_schedule.json` with the following structure:
```json
{
  "September 13th": [
    {
      "From": "2025-09-13T07:30:00+05:30",
      "To": "2025-09-13T08:45:00+05:30",
      "Name": "REGISTRATIONS / BREAKFAST",
      "Track": "General",
      "Speaker": "",
      "Link": ""
    }
  ],
  "September 14th": [...]
}
```

## Technical Requirements

### Dependencies
- **Python 3.9+**
- **UV** for package management
- **Scapy** for DNS packet crafting and parsing
- **pytz** for timezone handling
- **datetime** for time operations
- **json** for schedule parsing

### Time Handling Specifications
1. **Timezone:** All operations in Asia/Kolkata timezone (UTC+05:30)
2. **Conference Dates:** September 13-14, 2025
3. **Current Time Logic:** Show talks that are currently happening (start time <= current time <= end time)
4. **Next Talk Logic:** Show the chronologically next talk after current time
5. **Outside Conference:** Return links to PyCon website when queried outside conference dates

### Error Handling
- **Outside Conference Dates:** Return TXT records with:
  - `"Conference ended! Visit https://in.pycon.org/2025/ for info"`
  - `"Schedule: https://in.pycon.org/2025/program/schedule/"`
- **Invalid Queries:** Return appropriate DNS error responses
- **No Current/Next Talks:** Return empty response or informational message

## Implementation Tasks

### 1. Project Setup
- Initialize UV project structure
- Add dependencies: scapy, pytz
- Create main DNS server script
- Set up basic project structure

### 2. Schedule Parser Module (`schedule_parser.py`)
```python
class ScheduleParser:
    def __init__(self, json_file_path):
        # Load and parse the JSON schedule
        
    def get_current_talks(self, current_time):
        # Return talks happening at current_time
        
    def get_next_talk(self, current_time):
        # Return the next chronological talk
        
    def get_day_talks(self, day_number):
        # Return all talks for day 1 or 2
        
    def get_track_talks(self, track_name):
        # Return all talks for specified track
        
    def format_talk_response(self, talk):
        # Format talk data into TXT record string
```

### 3. Time Utilities Module (`time_utils.py`)
```python
import pytz
from datetime import datetime

def get_kolkata_time():
    # Get current time in Asia/Kolkata timezone
    
def is_conference_date(date):
    # Check if date is Sept 13 or 14, 2025
    
def parse_schedule_time(iso_time_string):
    # Parse ISO format time from schedule JSON
    
def is_time_in_range(current, start, end):
    # Check if current time falls within start-end range
```

### 4. DNS Server Core (`dns_server.py`)
```python
from scapy.all import *

class PyConDNSServer:
    def __init__(self, schedule_parser, port=5353):
        # Initialize DNS server
        
    def parse_query(self, packet):
        # Extract DNS query from packet
        
    def handle_query(self, query_name):
        # Route query to appropriate handler
        
    def create_txt_response(self, query, answers):
        # Create DNS TXT response packet
        
    def start_server(self):
        # Start UDP server and listen for DNS queries
```

### 5. Query Handlers
Implement specific handlers for each query type:
- `handle_now_talks()`
- `handle_next_talks()`
- `handle_day_talks(day_num)`
- `handle_track_talks(track_name)`

### 6. Main Server Script (`main.py`)
```python
def main():
    # Initialize schedule parser
    # Create DNS server instance
    # Start server with proper error handling and logging
```

### 7. Testing and Validation
- Test with `dig` commands locally
- Verify timezone handling
- Test edge cases (outside conference dates, no current talks)
- Validate DNS packet format compliance

## Project Structure
```
inpycon25_dns/
├── pyproject.toml
├── implementation_plan.md
├── pycon_india_2025_schedule.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── dns_server.py
│   ├── schedule_parser.py
│   ├── time_utils.py
│   └── query_handlers.py
├── tests/
│   ├── test_schedule_parser.py
│   ├── test_time_utils.py
│   └── test_dns_server.py
└── README.md
```

## Testing Commands

Once implemented, test with these commands:
```bash
# Test current talks
dig @localhost -p 5353 now.talks TXT

# Test next talk
dig @localhost -p 5353 next.talks TXT

# Test day queries
dig @localhost -p 5353 day1.talks TXT
dig @localhost -p 5353 day2.talks TXT

# Test track queries
dig @localhost -p 5353 track1.talks TXT
dig @localhost -p 5353 track2.talks TXT
dig @localhost -p 5353 track3.talks TXT
dig @localhost -p 5353 general.talks TXT
```

## Development Notes

1. **Port Selection:** Use port 5353 for local testing (avoids requiring root privileges for port 53)
2. **Logging:** Implement comprehensive logging for debugging DNS queries
3. **Performance:** Cache parsed schedule data for better response times
4. **DNS Compliance:** Ensure responses follow DNS TXT record standards
5. **Error Resilience:** Handle malformed queries gracefully

## Deployment Considerations

For future deployment to actually respond to queries against `inpy25.chennaipy.org`:
1. Set up proper DNS delegation
2. Configure server to run on port 53
3. Implement proper security measures
4. Add monitoring and health checks

This implementation plan provides a complete roadmap for building the PyCon India 2025 DNS schedule server that will make for an impressive conference demonstration!