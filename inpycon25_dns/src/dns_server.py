"""
PyCon India 2025 DNS Schedule Server Demo
A fun way to query conference schedule using DNS!
"""

import json
from datetime import datetime, timedelta
from scapy.all import bind_layers, DNS, DNSQR, DNSRR, UDP, IP, send, sniff, IPv6, fragment

net_interface = "lo"



class PyConDNSDemo:
    def __init__(self, port = 3333, schedule_file='schedule.json'):
        """Load schedule and prepare for queries"""
        self.schedule = self.load_schedule(schedule_file)
        self.port = port  # Non-privileged port for demo
        bind_layers(UDP, DNS, dport=self.port)
        bind_layers(UDP, DNS, sport=self.port)
    def load_schedule(self, file_path):
        """Simple schedule loader"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Simplified parsing - just extract what we need
        return self.parse_talks(data)

    def get_time(self, start_time_str, track):
        start_time = datetime.fromisoformat(start_time_str)
        end_time = start_time + timedelta(minutes=30)
        end_time_str = end_time.isoformat()
        return start_time_str, end_time_str, track
    


    def talks_to_txt_rdata(self, talks_list):
        """
        Convert list of talk dicts to list of TXT strings for DNS RDATA.
        Each line format: Track | HH:MM–HH:MM | Title — Speakers
        """
        txt_records = []
        for t in talks_list:
            start_dt = datetime.fromisoformat(t["date"])
            end_dt = start_dt + timedelta(minutes=30)  # assume 30-min slots
            start_str = start_dt.strftime("%H:%M")
            end_str = end_dt.strftime("%H:%M")

            speakers = ", ".join(t.get("persons", [])) or "TBA"
            line = f'{t["track"]} | {start_str}–{end_str} | {t["title"]} — {speakers}'
            txt_records.append(line)
        return txt_records


    def parse_talks(self, data):
        """Extract talks in a simple format"""
        #talks = []

        #talks = data
        # Parse the schedule structure
        # Return list of dicts with: time, title, speaker, track
        time_wise_talk = {}
        talks = {} 
        single_talk = {}
        for day in [1,2]:
            for track in ['Track 1', 'Track 2', 'Track 3']:
                for talk in range(7):
                    temp_data = data['schedule']['conference']['days'][day]['rooms'][track][talk].copy()
                    #                    print(temp_data)
                    tup_time = self.get_time(temp_data['date'], track)
                    time_wise_talk[tup_time] = temp_data["guid"]
                    for _key in ['date', 'title', 'persons']:
                        if _key == 'persons' and len(temp_data['persons']) >= 0:
                            _count = len(temp_data['persons'])
                            single_talk[_key] = [temp_data['persons'][value]['public_name'] for value in range(_count)]
                        else:
                            single_talk[_key] = temp_data[_key]
                    single_talk['track'] = track
                        #print(single_talk.keys())
                    talks[temp_data["guid"]] = single_talk.copy()
                        #single_talk.clear()                    
                        
                        
        return time_wise_talk, talks
    
    def get_current_talks(self, now_str):
        """Return talks happening now"""
        # Simple time comparison
        # Return formatted strings
        #now = datetime.fromisoformat(now_str)  
        now = datetime.fromisoformat(now_str)
        time_wise = self.schedule[0]
        talks = self.schedule[1]
        result_talks = []
        for (start_str, end_str, track), talk_id in time_wise.items():
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
        
            if start <= now < end:
                result_talks.append(talks[talk_id])
                
        return result_talks

    
    def get_next_talks(self, now_str):
        """Return the very next talk"""
        # Find next chronological talk
        # Return single formatted string
        upcoming = []
        now = datetime.fromisoformat(now_str)
        time_wise = self.schedule[0]
        talks = self.schedule[1]
        result_talks = []

        for (start_str, end_str, track), talk_id in time_wise.items():
            start = datetime.fromisoformat(start_str)
            if start > now:
                upcoming.append((start, track, talk_id))

        if not upcoming:
            return {}

        # Find the earliest upcoming start time
        earliest_start = min(start for start, _, _ in upcoming)

        # Collect all talks starting at that exact time
        result = {track: talks[talk_id] for start, track, talk_id in upcoming if start == earliest_start}
        return result

    
    def get_track_talks(self, track_num):
        """Return all talks for a track"""
        # Filter by track
        # Return list of formatted strings
        time_wise = self.schedule[0]
        talks = self.schedule[1]
        result = []
        for (start_str, end_str, track), talk_id in time_wise.items():
            if track == track_num:
                result.append(talks[talk_id])

        return result
        
    
    def handle_dns_query(self, packet):
        """Main DNS query handler"""
        #print(packet.summary())
        if packet.haslayer(DNS):
            query = packet[DNSQR].qname.decode('utf-8').lower()
            print(query)
            # Simple query routing
            if 'now.talks' in query:
                answers = self.get_current_talks()
            elif 'next.talks' in query:
                answers = [self.get_next_talks()]
            elif 'track1.talks' in query:
#                print(query)
                answers = self.get_track_talks("Track 1")
            else:
                answers = ["Query the PyCon schedule with DNS!"]

            answers_txt = self.talks_to_txt_rdata(answers)
            # Build DNS response
            return self.create_dns_response(packet, answers_txt)
    
    def create_dns_response(self, query_packet, txt_records):
        """Create DNS TXT response"""
        # Build response packet with TXT records
        # Keep it simple but functional
        qname = query_packet[DNSQR].qname.decode()
        print(f"[+] Received DNS Request for: {qname}")
        print(query_packet.summary())
        # Build DNS response

        if query_packet.haslayer(IP):
            if query_packet[IP].src == "127.0.0.1" and query_packet[UDP].sport == self.port:
                return
            ip = IP(dst=query_packet[IP].src, src=query_packet[IP].dst)
        elif query_packet.haslayer(IPv6):
            if query_packet[IP].src == "::1" and query_packet[UDP].sport == self.port:
                return
 
            ip = IP(dst=query_packet[IPv6].src, src=query_packet[IPv6].dst)
        else:
            print("Invalid ip")
            return

        
        udp = UDP(dport=query_packet[UDP].sport, sport=query_packet[UDP].dport)
        txt_rrs = []
            
        for txt in txt_records:
            # Split long strings >255 bytes into multiple chunks for DNS TXT
            chunks = []
            encoded = txt.encode("utf-8")
            while encoded:
                chunks.append(encoded[:255].decode("utf-8", errors="ignore"))
                encoded = encoded[255:]
            # Add RR
            txt_rrs.append(DNSRR(rrname=qname, type="TXT", ttl=60, rdata=chunks if len(chunks) > 1 else chunks[0]))

        # Combine all TXT RRs into the answer section
 #       an_section = b"".join(bytes(rr) for rr in txt_rrs)


        dns= DNS(
            id=query_packet[DNS].id,
            qr=1,  # response
            aa=1,  # authoritative
            qd=query_packet[DNS].qd,
            an=txt_rrs
        )

        response = ip / udp / dns
        #        print(response.summary())
        frags = fragment(response, fragsize = 512)
        send(frags, verbose=0)
        print(f"[+] Sent spoofed reply: {qname} -> {ip}")

    
    def start(self):
        """Start the DNS server"""
        print(f"🚀 PyCon DNS Demo starting on port {self.port}")
        print(f"Try: dig @localhost -p {self.port} now.talks TXT")
        
        # Sniff and respond to DNS queries
        sniff(filter=f"udp port {self.port}", 
              prn=self.handle_dns_query, iface=net_interface, store=0)

if __name__ == "__main__":
    print("=" * 50)
    print("PyCon India 2025 - DNS Schedule Server Demo")
    print("=" * 50)
    
    server = PyConDNSDemo()
    server.start()


