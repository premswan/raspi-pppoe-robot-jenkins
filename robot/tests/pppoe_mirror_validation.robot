*** Settings ***
Documentation     Single-test PPPoE mirror validation. Raspberry Pi is a passive sniffer connected to a mirrored Airtel router WAN port on LAN4.
Library           SSHLibrary
Library           Collections
Library           ../../libraries/PppoeParser.py
Resource          ../resources/raspi_keywords.robot
Suite Setup       Open Raspberry Connection
Suite Teardown    Close All Connections

*** Test Cases ***
TC001 Print PPPoE Public IPs With Source And Destination Ports
    [Documentation]    Captures PPPoE session traffic and prints only normalized CGNAT/global IPv4 flows with source and destination ports, for example 100.103.70.200.13227 > 117.96.122.77.domain:
    [Tags]    pppoe    mirror    public-ip    src-dst-port
    ${capture}=    Capture PPPoE Session Packets From Mirror
    ${flows}=      Extract PPPoE Public IP Port Flows    ${capture}

    Log To Console    PPPoE public/CGNAT IP flows with ports: ${flows}

    Should Not Be Empty    ${flows}    msg=No PPPoE public/CGNAT IPv4 flow with source/destination ports was found. Generate internet traffic from a LAN client and confirm LAN4 mirror is forwarding WAN PPPoE session traffic to Raspberry Pi ${MIRROR_IFACE}.
