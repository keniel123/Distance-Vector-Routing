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
        self.port_table = {} # port:neighbour
        self.distance_table = {} # dst:[port, total cost, time, valid_bit]
        

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.port_table[port] = latency;
        for dst in self.distance_table.keys():
              p = basics.RoutePacket(dst, self.distance_table[dst][1])
              self.send(p, port)


    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        #poison the route then wait for replacement route via RoutePacket
        if port in self.port_table.keys():
            del self.port_table[port]

        to_remove = []
        if self.POISON_MODE:
          for dst in self.distance_table.keys():
            if self.distance_table[dst][0] == port:
              #send poison with INFINITY cost, delete local table[dst]
              p = basics.RoutePacket(dst, INFINITY)
              self.send(p, flood = True)
              to_remove.append(dst)
          for dst in to_remove:
            del self.distance_table[dst]

        else:
          to_remove = []
          for dst in self.distance_table.keys():
            if self.distance_table[dst][0] == port:
              to_remove.append(dst)

          for dst in to_remove:
            del self.distance_table[dst]
          for dst in self.distance_table.keys():
            p = basics.RoutePacket(dst, self.distance_table[dst][1])
            self.send(p, flood=True)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            dst = packet.destination
            cost = packet.latency 
            if self.POISON_MODE and cost == INFINITY:
                to_remove = []
                for target in self.distance_table.keys():
                  if self.distance_table[target][0] == port:
                    p = basics.RoutePacket(target, INFINITY)
                    self.send(p, port)
                    to_remove.append(target)
                for target in to_remove:
                  del self.distance_table[target]

            if dst not in self.distance_table.keys():
                if cost != INFINITY:
                  self.distance_table[dst] = [port, self.port_table[port] + cost, 0]
                  p = basics.RoutePacket(dst, self.distance_table[dst][1])
                  self.send(p, port, flood = True)

            else:
                #when new route/shortest path established
                if (self.port_table[port] + cost) < self.distance_table[dst][1]:
                  self.distance_table[dst] = [port, self.port_table[port] + cost, 0]
                  p = basics.RoutePacket(dst, self.distance_table[dst][1])
                  self.send(p, port, flood = True)

                #keep stable
                if (self.port_table[port] + cost == self.distance_table[dst][1]):
                  self.distance_table[dst] = [port, self.distance_table[dst][1], 0]

                #when receive a shortest route became longer
                if (self.distance_table[dst][0] == port) and (self.distance_table[dst][1] < cost + self.port_table[port]):
                  new_cost = cost + self.port_table[port]
                  self.distance_table[dst] = [port, cost + self.port_table[port], 0]
                  p = basics.RoutePacket(dst, self.distance_table[dst][1])
                  self.send(p, port, flood = True)


        elif isinstance(packet, basics.HostDiscoveryPacket):
          self.distance_table[packet.src] = [port, self.port_table[port], 0]

          #send whole table to all neighbour except PORT
          for target in self.distance_table.keys():
            p = basics.RoutePacket(target, self.distance_table[target][1])
            self.send(p, port, flood = True)

        else:
          if (packet.dst in self.distance_table.keys() and self.distance_table[packet.dst][0] != port):
            self.send(packet, self.distance_table[packet.dst][0])


    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
         # check through the routes and see if 15 seconds have passed if so remove route
        expire = []
        for dst in self.distance_table.keys():
          self.distance_table[dst][2] += self.DEFAULT_TIMER_INTERVAL
          if self.distance_table[dst][2] >= 15:
            expire.append(dst)

        for dst in expire:
          if self.distance_table[dst][0] in self.port_table.keys() and self.port_table[self.distance_table[dst][0]] == self.distance_table[dst][1]:
            self.distance_table[dst] = [self.distance_table[dst][0], self.distance_table[dst][1], 0]
          else:
            del self.distance_table[dst]

        # send table to all neighbour except that using
        for dst in self.distance_table.keys():
          p = basics.RoutePacket(dst, self.distance_table[dst][1])
          self.send(p, self.distance_table[dst][0], flood = True)

