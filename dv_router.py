"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    NO_LOG = True # Set to True on an instance to disable its logging
    POISON_MODE = True # Can override POISON_MODE here
    DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        super(DVRouter, self).__init__()
        self.port_table = {} # port:latency to neighbour
        self.distance_table = {} # dst:[port, total cost, time, valid_bit]
        

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.port_table[port] = latency

        #Send RoutePacket to every destination including itself
        for dst in self.distance_table:
            destination = dst
            latency = self.distance_table.get(dst)[0]
            packet = basics.RoutePacket(destination, latency)
            self.send(packet, port)


    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        for dst in self.distance_table.keys():
            if self.distance_table.get(dst)[1] == port:
                self.distance_table.get(dst)[0] = INFINITY
                packet = basics.RoutePacket(dst, INFINITY)
                self.send(packet, port, flood = True)

        del self.port_table[port]

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
       

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
         # check through the routes and see if 15 seconds have passed if so remove route
        


