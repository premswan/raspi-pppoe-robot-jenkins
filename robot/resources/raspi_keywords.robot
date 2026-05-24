*** Settings ***
Library      SSHLibrary
Library      Collections
Library      ../../libraries/PppoeParser.py
Resource     ../variables/raspi_vars.robot

*** Keywords ***
Open Raspberry Connection
    [Documentation]    Opens SSH connection to Raspberry Pi using SSH private key authentication from Jenkins credential raspi-ssh-key.
    Should Not Be Empty    ${RPI_KEY_FILE}    msg=RPI_KEY_FILE is empty. In Jenkins, use credential ID raspi-ssh-key with kind SSH Username with private key.
    Open Connection    ${RPI_HOST}    timeout=10s
    Login With Public Key    ${RPI_USER}    ${RPI_KEY_FILE}    ${RPI_KEY_PASSPHRASE}

Capture PPPoE Session Packets From Mirror
    [Documentation]    Captures PPPoE session packets from mirrored WAN traffic. Full tcpdump output is stored only in Robot log, not printed to Jenkins console. Uses -n, not -nn, so IPs stay numeric and ports may appear as names like domain/https.
    ${traffic_cmd}=    Set Variable If    '${GENERATE_TRAFFIC}' == 'True' or '${GENERATE_TRAFFIC}' == 'true'    ping -c ${PING_COUNT} ${PING_TARGET} > /tmp/pppoe_ping.txt 2>&1 || true    echo 'Traffic generation disabled' > /tmp/pppoe_ping.txt
    ${cmd}=    Set Variable    rm -f /tmp/pppoe_mirror_capture.txt /tmp/pppoe_ping.txt; (timeout ${CAPTURE_SECONDS} sudo -n tcpdump -i ${MIRROR_IFACE} -n -e -vv -s0 -c ${PACKET_COUNT} 'ether proto 0x8864' > /tmp/pppoe_mirror_capture.txt 2>&1 &); sleep 2; ${traffic_cmd}; sleep ${CAPTURE_SECONDS}; echo '---TCPDUMP---'; cat /tmp/pppoe_mirror_capture.txt; echo '---TRAFFIC---'; cat /tmp/pppoe_ping.txt
    ${out}=    Execute Command    ${cmd}
    Log    ${out}
    Should Contain    ${out}    ---TCPDUMP---
    RETURN    ${out}
