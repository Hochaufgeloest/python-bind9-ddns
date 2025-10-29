import subprocess
from enum import Enum

class RecordType(Enum):
    A = "A"
    AAAA = "AAAA"
    TXT = "TXT"
    CNAME = "CNAME"
    MX = "MX"
    SRV = "SRV"

class DNSUpdater:
    def __init__(self, dns_server: str, key_file_path: str, nsupdate_binary_path = "/usr/bin/nsupdate"):
        self.dns_server = dns_server
        self.key_file_path = key_file_path
        self.nsupdate_binary_path = nsupdate_binary_path

    def _run_nsupdate_commands(self, command_string: str):
        process = subprocess.run(
            [self.nsupdate_binary_path, "-k", f"{self.key_file_path}"],
            input=command_string,
            text=True,
            capture_output=True
        )

        if process.stderr:
            raise Exception(f"An error occoured while executing nsupdate commands - {str(process.stderr)}")

    def add_record(self, zone: str, hostname: str, ttl: int, record_type: RecordType, value: str):
        add_commands = f"""
        server {self.dns_server}
        zone {zone}
        update add {hostname}.{zone} {ttl} IN {record_type.value} {value}
        send
        quit
        """
        self._run_nsupdate_commands(add_commands)

    def delete_record(self, zone: str, hostname: str, record_type: RecordType):
        del_commands = f"""
        server {self.dns_server}
        zone {zone}
        update delete {hostname}.{zone} {record_type.value}
        send
        quit
        """
        self._run_nsupdate_commands(del_commands)

    def update_record(self, zone: str, hostname: str, record_type: RecordType, new_value: str, ttl: int = 3600):
        self.delete_record(zone, hostname, record_type)
        self.add_record(zone, hostname, ttl, record_type, new_value)