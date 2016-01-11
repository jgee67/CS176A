import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
#class of functions for our implementation of a sliding window
class Window(object):

  #initialize a window
  def __init__(self, n = 5):
    self.size = n
    self.dupACKs = {}
    self.packets = {}
    
  #returns length of a window
  def __len__(self):
    return len(self.packets)
    
  #checks if window is not filled
  def isNotFilled(self):
    return len(self.packets) < self.size
      
  #returns a specific packet in window
  def retrieve(self, seqno):
    return self.packets[seqno]
    
  #deletes and returns a specific packet from window
  def pop(self, seqno):
    packet = self.retrieve(seqno)
    del self.dupACKs[seqno]
    del self.packets[seqno]
    return packet
    
  #inserts a new packet in window
  def insert(self, seqno, packet):
    self.dupACKs[seqno] = 0
    self.packets[seqno] = packet


#========================================================================================
#=======================================SENDER===========================================
#========================================================================================


#class of functions for our sender
class Sender(BasicSender.BasicSender):
  
  #initialize Sender
  def __init__(self, dest, port, filename, debug=False, sackMode=False):
    super(Sender, self).__init__(dest, port, filename, debug)
    if sackMode:
      raise NotImplementedError # you do not need to implement SACK, ignore this
    self.window = Window()
    self.seqno = 0
    self.lastACKReceived = False
      
  # Main sending loop.
  def start(self):
    # raise NotImplementedError
    msg_type = None
    next_msg_type = None
    while not self.lastACKReceived:
      while self.window.isNotFilled() and next_msg_type != 'end':
        (next_msg_type, seqno, packet) = self.send()
      response = self.receive(.5)
      if response == None:
        self.handle_timeout()
      else:
        (msg_type, seqno, data, checksum) = self.split_packet(response)
      seqno = int(seqno)
      if Checksum.validate_checksum(response):
        self.handle_ack(seqno)
      if len(self.window) == 0:
        self.lastACKReceived = True
    self.infile.close()

  #override send function from superclass BasicSender
  def send(self):
    next_msg = self.infile.read(1472)
    msg_type = 'data'
    if self.seqno == 0:
      msg_type = 'start'
    elif next_msg == "":
      msg_type = 'end'
    packet = self.make_packet(msg_type, self.seqno, next_msg)
    self.window.insert(self.seqno, packet)
    super(Sender, self).send(packet)
    self.seqno += 1
    return (msg_type, self.seqno, packet)
    
  #reSend packet using superclass BasicSender
  def reSend(self, seqno, address = None):
    super(Sender, self).send(self.window.retrieve(seqno), address)
    
  #reSends all packets in window on timeout
  def handle_timeout(self):
    for packet in self.window.packets:
      self.reSend(packet)
      
  #determines if ACK is new or duplicate
  def handle_ack(self, ack):
    if ack not in self.window.dupACKs:
      self.window.dupACKs[ack] = 0
      self.handle_new_ack(ack)
    else:
      self.window.dupACKs[ack] += 1
      if self.window.dupACKs[ack] == 3:
        self.handle_dup_ack(ack)
			
  #increment the window if receives new ACK
  def handle_new_ack(self, ack):
    for seqno in self.window.packets.keys():
      if seqno < ack:
        self.window.pop(seqno)
    if self.window.isNotFilled():
      (msg_type, seqno, packet) = self.send()
      if msg_type == 'end':
        self.lastACKReceived = True
        
  #reSends ACK if duplicate
  def handle_dup_ack(self, ack):
    self.reSend(ack)

  #never used
  def log(self, msg):
    if self.debug:
      print msg

#========================================================================================
#========================================================================================
#========================================================================================

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
