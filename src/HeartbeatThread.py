import datetime

import threading

class HeartbeatThread(threading.Thread):
  def __init__(self, network_object):
    threading.Thread.__init__(self)
    self.stop = False
    self.network_object = network_object
  
  def stop_tracker(self):
    self.stop = True

  def run(self):
    endTime = datetime.datetime.now() + datetime.timedelta(seconds=20)
    while True:
      if datetime.datetime.now() >= endTime:
        try:
          self.network_object.send_message(f"PING")
          endTime = datetime.datetime.now() + datetime.timedelta(seconds=120)
        except:
          break
      if self.network_object.end_thread or self.stop: 
        print("ENDED HEARTBEAT thread")
        break