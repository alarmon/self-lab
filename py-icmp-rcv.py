#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import struct
import select
import time
import ctypes

ICMP_ECHO_REQUEST = 8

def receive_ping(my_socket, timeout):
    """
    receive the ping from the socket
    """
    start_time = timeout
    while True:
        start_select = time.process_time()
        # select.select(rlist, wlist, xlist[, timeout])
        # wait until ready for read / write / exceptional condition
        # The return value is a triple of lists
        what_ready = select.select([my_socket], [], [], start_time)
        how_long = (time.process_time() - start_select)
        if what_ready[0] == []: #timeout
            return

        time_received = time.process_time()
        # socket.recvfrom(bufsize[, flags])
        # The return value is a pair (string, address)
        rec_packet, addr = my_socket.recvfrom(1024)
        icmp_header = rec_packet[20 : 28]
        icmp_buff= rec_packet[28 : ]
        ip_type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", icmp_header)
        #if ip_type != 8 and packet_ID == ID: # ip_type should be 0
        if ip_type != 8: # ip_type should be 0
            byte_in_double = struct.calcsize("d")
            time_sent = struct.unpack("d", rec_packet[28 : 28 + byte_in_double])[0]
            return time_received - time_sent
        else:
            print('Got icmp:')
            print(icmp_buff)
            return timeout
        start_time = start_time - how_long
        if start_time <= 0:
            return

def ping_wait(ip_addr, timeout):
    """
    return either delay (in second) or none on timeout.
    """
    # Translate an Internet protocol name to a constant suitable for
    # passing as the (optional) third argument to the socket() function.
    # This is usually only needed for sockets opened in “raw” mode.
    icmp = socket.getprotobyname('icmp')
    try:
        # socket.socket([family[, type[, proto]]])
        # Create a new socket using the given address family(default: AF_INET),
        # socket type(SOCK_STREAM) and protocol number(zero or may be omitted).
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error:
        raise

    #send_ping(my_socket, ip_addr, my_ID)
    delay = receive_ping(my_socket, timeout)
    my_socket.close()
    return delay


def icmp_ping(ip_addr, timeout = 6, count = 1024):
    """
    send ping to ip_addr for count times with the given timeout
    """
    for i in range(count):
        print('Ping wait:')
        try:
            delay = ping_wait(ip_addr, timeout)
        except socket.gaierror as e:
            print('Failed. (socket error: %s)' % e[1])
            break

        if delay == None:
            print('Failed. (timeout within %s second.)' % timeout)
        else:
            print('get ICMP in %0.4f ms' % (delay * 1000))


# main
if __name__ == '__main__':
    while True:
        try:
            cmd = "192.168.199.185"
            icmp_ping(cmd)
        except EOFError:
            break
