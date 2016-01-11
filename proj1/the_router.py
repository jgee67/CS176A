from cs176.api import *
from cs176.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        self.rt = {} #dict that maps all routers (including self) as destinations to total path length from self to that destination
        self.rt.update({self: 0}) #initialize path to self = 0
        self.ft = {} #dict that maps all routers in network (destination) to the next router in the shortest path to that destination
        self.ft.update({self: -1}) #initialize port to self as

    def handle_rx (self, packet, port):
      
      
      
      
      
#========================DISCOVER PACKET==============================




        #if packet is a DiscoverPackets
        if type(packet) == DiscoverPackets:
          
          #if uplink, add new link to routing tables
          if packet.is_link_up:
            self.rt.update({packet.src: packet.latency})
            self.ft.update({packet.src: port})
            
          #if downlink, adjust routing table values and delete neighbor
          else:
            self.rt.update({packet.src: 50})
            self.ft.update({packet.src: 50})
            for dest in self.rt:
              if self.ft[dest] == port:
                self.rt.update({dest: 50})
                self.ft.update({dest: 50})
                
          #broadcast update to neighbors
          update = UpdateRouting()
          for router in self.rt:
            update.add_destination(router, self.rt[router])
          self.send(update, None, True)
            
            
            
            
            
            
            
#========================UPDATE PACKET==================================
            
            
        #if packet is an UpdateRouting
        elif type(packet) == UpdateRouting:
          update = UpdateRouting()
          helper = UpdateRouting()
          for dest in packet.paths:
            
            #if not in forwarding table, get from neighbor
            if self.ft.get(dest, 50) >= 50:
              self.rt.update({dest: self.rt[packet.src] + packet.paths[dest]})
              self.ft.update({dest: port})
              update.add_destination(dest, self.rt[dest])
              
            #if I depend on neighbor and neighbor went down update unreachable values to infinity
            elif self.ft[dest] == port:
              if packet.paths[dest] >= 50:
                self.rt.update({dest: 50})
                self.ft.update({dest: 50})
                update.add_destination(dest, self.rt[dest])
                
            #if I found a better path through a neighbor, take that
            elif self.rt.get(dest, 50) > self.rt[packet.src] + packet.paths[dest]:
              self.rt.update({dest: self.rt[packet.src] + packet.paths[dest]})
              self.ft.update({dest: port})
              update.add_destination(dest, self.rt[dest])
              
            #if my path is same as a neighbor, choose one with lowest port
            elif self.rt.get(dest, 50) == self.rt[packet.src] + packet.paths[dest]:
              if port < self.ft.get(dest, 50):
                self.ft.update({dest: port})
                
            elif packet.paths[dest] >= 50:
              if self.rt.get(dest, 50) < 50:
                helper.add_destination(dest, self.rt[dest])
                
          if update.paths != {}:
            self.send(update, port, True)
          if helper.paths != {}:
            self.send(helper, port, False)
            
            
            
            
#======================OTHER PACKET=============================
          
        #if packet is an Other
        else:
          self.send(packet, self.ft[packet.dst], False)
          
          
          
          
          
    
      
      
      
      
      
      
      
      
      
      
      
      
      
      