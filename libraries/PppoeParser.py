import ipaddress
import re
from typing import Dict, List, Optional


class PppoeParser:
    """Robot Framework helper library for parsing tcpdump PPPoE mirror output.

    Raspberry Pi is a passive sniffer connected to a mirrored WAN port. This
    library extracts only clean PPPoE IPv4 flows such as:

        100.103.70.200.13227 > 117.96.122.77.domain:

    It intentionally ignores IP-like strings inside DNS PTR names, for example
    c.0.0...ip6.arpa or 88.71.111.3.in-addr.arpa.
    """

    _PPPOE_SESSION_RE = re.compile(
        r"PPPoE\s+\[ses\s+(0x[0-9a-fA-F]+|\d+)\]",
        re.IGNORECASE,
    )

    # Captures only the tcpdump source and destination tokens that immediately
    # follow "PPPoE [ses ...] IP".
    # Examples:
    #   IP 100.103.70.200.13227 > 117.96.122.77.domain:
    #   IP 100.103.70.200.50077 > 87.70.96.34.bc.googleusercontent.com.https:
    _PPPOE_IP_ENDPOINT_RE = re.compile(
        r"PPPoE\s+\[ses\s+(?:0x[0-9a-fA-F]+|\d+)\]\s+IP\s+"
        r"(?P<src>\S+)\s+>\s+(?P<dst>[^\s:]+):",
        re.IGNORECASE,
    )

    _IP_AT_START_RE = re.compile(
        r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})(?:\.(?P<suffix>.+))?$"
    )

    def extract_pppoe_session_id(self, tcpdump_output: str) -> str:
        """Return first PPPoE session ID, for example 0x2b58."""
        match = self._PPPOE_SESSION_RE.search(tcpdump_output or "")
        return match.group(1) if match else ""

    def extract_pppoe_session_ids(self, tcpdump_output: str) -> List[str]:
        """Return unique PPPoE session IDs seen in tcpdump output."""
        seen = set()
        sessions = []
        for match in self._PPPOE_SESSION_RE.finditer(tcpdump_output or ""):
            session = match.group(1)
            if session not in seen:
                seen.add(session)
                sessions.append(session)
        return sessions

    def extract_pppoe_public_ip_port_flows(self, tcpdump_output: str) -> List[str]:
        """Return unique CGNAT/global PPPoE IPv4 flows with source/destination ports.

        Output format:
            100.103.70.200.13227 > 117.96.122.77.domain:
            100.103.70.200.50077 > 87.70.96.34.https:

        The destination is normalized to <ip>.<port>. If tcpdump performs DNS
        reverse lookup and returns a host-like token such as
        87.70.96.34.bc.googleusercontent.com.https, this method keeps the IP
        and the final port/service label only: 87.70.96.34.https.
        """
        flows: List[str] = []
        seen = set()

        for line in (tcpdump_output or "").splitlines():
            match = self._PPPOE_IP_ENDPOINT_RE.search(line)
            if not match:
                continue

            src = self._normalize_endpoint(match.group("src"))
            dst = self._normalize_endpoint(match.group("dst"))
            if not src or not dst:
                continue

            # Keep only flows where at least one endpoint is CGNAT/global.
            # In your Airtel capture, 100.103.70.200 is CGNAT and the remote
            # DNS/HTTPS server is normally global.
            if not (
                self.classify_ipv4(src["ip"]) in {"cgnat", "global"}
                or self.classify_ipv4(dst["ip"]) in {"cgnat", "global"}
            ):
                continue

            flow = f"{src['ip']}.{src['port']} > {dst['ip']}.{dst['port']}:"
            if flow not in seen:
                seen.add(flow)
                flows.append(flow)

        return flows

    def extract_pppoe_ip_port_flows(self, tcpdump_output: str) -> List[str]:
        """Alias that returns all public/CGNAT PPPoE IPv4 flows with ports."""
        return self.extract_pppoe_public_ip_port_flows(tcpdump_output)

    def _normalize_endpoint(self, token: str) -> Optional[Dict[str, str]]:
        """Normalize a tcpdump endpoint token to {'ip': ip, 'port': port}.

        Supported input examples:
            100.103.70.200.13227
            117.96.122.77.domain
            87.70.96.34.bc.googleusercontent.com.https
            8.8.8.8.53
        """
        token = (token or "").strip().rstrip(":,;")
        match = self._IP_AT_START_RE.match(token)
        if not match:
            return None

        ip = match.group("ip")
        suffix = match.group("suffix") or ""

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return None

        if not suffix:
            return {"ip": ip, "port": "unknown"}

        # tcpdump source normally has only a numeric source port after the IP.
        # tcpdump destination may be ip.domain, ip.https, or ip.hostname.https.
        port = suffix.split(".")[-1]
        if not port:
            port = "unknown"

        return {"ip": ip, "port": port}

    def classify_ipv4(self, ip: str) -> str:
        """Classify IPv4 address for reporting/filtering."""
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            return "invalid"

        if address.version != 4:
            return "not_ipv4"

        if address in ipaddress.ip_network("100.64.0.0/10"):
            return "cgnat"

        if address.is_loopback:
            return "loopback"

        if address.is_link_local:
            return "link_local"

        if address.is_private:
            return "private"

        if address.is_multicast:
            return "multicast"

        if address.is_global:
            return "global"

        return "reserved_or_special"
