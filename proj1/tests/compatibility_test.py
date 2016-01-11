#!/bin/env python
# This is a basic compatibility test to make sure you're using the built-in
# classes properly.
#
# If this crashes, or you get an error message, or you never get any messages,
# you're likely
# using the built-ins (particularly: UpdateRouting) in such a way that your
# implementation will fail the grading scripts - make sure you fix before
# turning in!

import sys, os, time
sys.path.append('.')

from cs176.api import *
from cs176.basics import *
import cs176.topo as topo
import cs176.core
from the_router import DVRouter
from hub import Hub as switch
import logging

class FakeEntity (Entity):
    def __init__(self, expected, to_announce):
        self.expect = expected
        self.announce = to_announce
        self.num_rx = 0
        if self.announce:
            self.timer = create_timer(5, self.send_announce)

    def handle_rx(self, packet, port):
        if self.expect:
            if isinstance(packet, UpdateRouting):
                print "Received Packet: ", packet
                for i in packet.all_dests():
                    print i, packet.get_distance(i)
                self.num_rx += 1
                if(self.expect[0] in packet.all_dests() and packet.get_distance(self.expect[0]) == (self.expect[1])):
                    print "Congrats! You Passed Compatibility Test!"
                    os._exit(0)
                elif(self.num_rx > 3):
                    os._exit(-1)

    def send_announce(self):
        if(self.announce):
            update = UpdateRouting()
            update.add_destination(self.announce[0], self.announce[1])
            print "Announcing from", self
            for i in update.all_dests():
                print i, update.get_distance(i)
            self.send(update, flood=True)

def create (switch_type = FakeEntity, host_type = FakeEntity, n = 2):
    DVRouter.create('student')
    BasicHost.create('dest')
    FakeEntity.create('sender', None, [dest, 10])
    FakeEntity.create('receiver', [dest, 11], None)

    topo.link(student, sender)
    topo.link(student, receiver)
    
    topo.show_ports(sender)
    topo.show_ports(receiver)

simlog.setLevel(logging.DEBUG)
userlog.setLevel(logging.DEBUG)

_DISABLE_CONSOLE_LOG = True

create(switch)
start = cs176.core.simulate
start()
time.sleep(80)
os._exit(-2)
