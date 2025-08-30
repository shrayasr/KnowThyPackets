## Scaled-Down Implementation Plan: DNS Server Demo for PyCon India 2025

### Core Goal

To create a **single-file, easy-to-understand** toy DNS server. The focus is on clarity and demo-ability, stripping away production-level abstractions like multiple modules and classes in favor of a straightforward, functional script.

### What Stays the Same (The Essentials)

*   **Core Functionality:** The server will still answer the exact same queries (`now.talks`, `next.talks`, `day1.talks`, `track1.talks`, etc.).
*   **Response Format:** The TXT record format remains identical to maintain the desired output for the demo.
*   **Data Source:** It will read from the `schedule.json` file. The logic will be self-contained within the script.
*   **Core Dependencies:** `scapy` and `pytz` are still necessary.

### Key Simplifications for the Demo

1.  **Single-File Implementation:** All logic (DNS handling, schedule parsing, time utilities) will be consolidated into a single Python file, e.g., `toy_dns_server.py`. This makes it easy to show and explain the entire application at once.
2.  **Functional Approach:** We'll replace classes like `ScheduleParser` and `PyConDNSServer` with simple, well-named functions. This reduces boilerplate and makes the control flow more linear.
3.  **Simplified Project Structure:** No need for a `src/` directory or separate test files. The project will be flat, containing just the script and the schedule data.
4.  **No Formal Tests:** For a demo script, validation via `dig` commands is sufficient. The formal `tests/` directory is unnecessary overhead.

---

## Revised Implementation Plan

### 1. Project Setup

*   Create a new directory for the project (e.g., `pycon-dns-demo/`).
*   Inside the directory, create your `pyproject.toml` for UV.
*   Add dependencies using UV:
    ```bash
    uv add scapy pytz
    ```
*   Place the `schedule.json` file in the same directory.
*   Create the single script: `toy_dns_server.py`.

**Simplified Project Structure:**
```
pycon-dns-demo/
├── pyproject.toml
├── schedule.json
└── toy_dns_server.py
```

### 2. Script Implementation (`toy_dns_server.py`)

The script will be organized into logical sections using functions.

#### **Section 1: Imports and Constants**
```python
import json
from datetime import datetime, time
import pytz
from scapy.all import DNS, DNSQR, DNSRR, IP, UDP, sniff

# Constants
SCHEDULE_FILE = "schedule.json"
CONFERENCE_TZ = pytz.timezone("Asia/Kolkata")
CONFERENCE_DATES = [datetime(2025, 9, 13).date(), datetime(2025, 9, 14).date()]
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5353 # Use a high port for non-root execution
```

#### **Section 2: Schedule & Time Helper Functions**
These functions will handle loading the data and all time-related logic.

```python
def load_schedule(file_path):
    """Loads and pre-processes the schedule from the JSON file."""
    # Logic to open the file, parse JSON, and perhaps flatten the
    # day/room structure into a single list of talk dictionaries.
    # Each dictionary should contain pre-parsed start/end datetimes.
    pass

def get_current_time_in_kolkata():
    """Returns the current datetime object aware of the conference timezone."""
    return datetime.now(CONFERENCE_TZ)

def format_talk_for_dns(talk):
    """Formats a single talk dictionary into the specified TXT string."""
    # Takes a talk object and returns the string:
    # "[Track] [Start]-[End] - [Talk Name] by [Speaker(s)]"
    pass
```

#### **Section 3: Query Logic Functions**
These functions will filter the schedule data based on the query.

```python
def get_now_talks(schedule, current_time):
    """Filters the schedule for talks happening right now."""
    pass

def get_next_talks(schedule, current_time):
    """Finds the next talk(s) chronologically."""
    pass

def get_day_talks(schedule, day_index):
    """Filters talks for a specific day (1 or 2)."""
    pass

def get_track_talks(schedule, track_name):
    """Filters talks for a specific track."""
    pass
```

#### **Section 4: Core DNS Handler**
This is the main function that Scapy will call for each incoming packet.

```python
def handle_dns_request(packet):
    """
    Parses DNS queries and crafts the appropriate response.
    This is the heart of the server.
    """
    if DNS in packet and packet[DNS].opcode == 0 and packet[DNS].qr == 0: # Standard DNS query
        query_name = packet[DNSQR].qname.decode().lower().strip('.')
        
        # Check if we are within conference dates
        now = get_current_time_in_kolkata()
        if now.date() not in CONFERENCE_DATES:
            # Respond with "Conference ended" message
            # ... build and send response packet ...
            return

        # --- Query Routing Logic ---
        answers = []
        if query_name == "now.talks":
            talks = get_now_talks(SCHEDULE_DATA, now)
            answers = [format_talk_for_dns(t) for t in talks]
        elif query_name == "next.talks":
            # ... and so on for other queries ...
        elif query_name.startswith("day"):
            # ...
        elif query_name.startswith("track"):
            # ...

        # --- Response Packet Construction ---
        if answers:
            response_records = [DNSRR(rrname=query_name, type='TXT', rdata=ans.encode()) for ans in answers]
            dns_response = DNS(
                id=packet[DNS].id,
                qr=1,
                aa=1,
                qd=packet[DNSQR],
                an=DNSRR(rrname=query_name, type='TXT', rdata=answers[0].encode()) if len(answers) == 1 else None,
                ns=DNSRR(rrname=query_name, type='TXT', rdata=answers[1].encode()) if len(answers) > 1 else None,
                ar=DNSRR(rrname=query_name, type='TXT', rdata=answers[2].encode()) if len(answers) > 2 else None
            )
            # Note: Scapy's handling of multiple identical records can be tricky.
            # A simpler approach is to just send one record, or join them.
            # For the demo, sending multiple might be best achieved by crafting the packet carefully.
            # Let's refine this part if needed. A simple loop is better:
            
            # Simplified response construction
            response = IP(dst=packet[IP].src, src=SERVER_IP) / \
                       UDP(dport=packet[UDP].sport, sport=SERVER_PORT) / \
                       DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNSQR], ancount=len(answers), an=None)
            
            for ans in answers:
                response[DNS].an /= DNSRR(rrname=query_name, type='TXT', rdata=ans.encode())

            send(response, verbose=0)

```

#### **Section 5: Main Execution Block**
This loads the data and starts the server.

```python
if __name__ == "__main__":
    print("Loading schedule data...")
    # Since schedule.json can change, we load it once on startup.
    # For the demo, restarting the script is a simple way to pick up changes.
    SCHEDULE_DATA = load_schedule(SCHEDULE_FILE)
    
    if not SCHEDULE_DATA:
        print(f"Error: Could not load or parse {SCHEDULE_FILE}. Exiting.")
        exit(1)

    print(f"PyCon India 2025 DNS server starting on {SERVER_IP}:{SERVER_PORT}...")
    print("Ready to accept queries. Press Ctrl+C to stop.")
    
    # Start sniffing for DNS queries on the specified port
    sniff(filter=f"udp port {SERVER_PORT} and ip dst {SERVER_IP}", prn=handle_dns_request)
```

### 3. Testing and Validation

Your testing commands remain perfectly valid and are the ideal way to test this simplified server.

```bash
# Test current talks
dig @localhost -p 5353 now.talks TXT

# Test day queries
dig @localhost -p 5353 day1.talks TXT

# Test track queries
dig @localhost -p 5353 track1.talks TXT
```

This scaled-down plan gives you a single, coherent script that is much easier to present during a talk, while still delivering the full "wow" factor of a custom DNS server. Good luck with your presentation at PyCon India 2025
