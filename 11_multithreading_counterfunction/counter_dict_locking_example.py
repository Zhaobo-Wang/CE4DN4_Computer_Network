#!/usr/bin/env python3

########################################################################

import threading
import time

########################################################################

# Illustration of the importance of locking when threads concurrently
# access a common variable. The correct answer is 

LOCKING_USED = False
# LOCKING_USED = True

INCREMENTS_PER_THREAD = 100
NUMBER_OF_THREADS = 10

counter = {
   "value" : 0
}

lock = threading.Lock()

def increment_counter(counter):
   for i in range(INCREMENTS_PER_THREAD):
      if LOCKING_USED:
         with lock:
            counter["value"] += 1
      else:
         v = counter["value"]
         v += 1
         counter["value"] = v

thread_list = []

for thread_count in range(NUMBER_OF_THREADS):
   thread = threading.Thread(target=increment_counter, args=(counter,))
   thread_list.append(thread)
   # thread.daemon =` True
   # thread.start()

for thread in thread_list:
   thread.start()
   
# Synchronize all the threads.   
for thread in thread_list:
   thread.join()

# Instead of keeping a thread list of our own, we can obtain one from
# threading.enumerate(). Then synchronize them. Note that this list
# includes the main thread that we need to test for.

# for thread in threading.enumerate():
#    if thread is threading.main_thread():
#       continue
#    else:
#       thread.join()
      
print(counter["value"], end='')
print(" (correct value is {})".format(INCREMENTS_PER_THREAD * NUMBER_OF_THREADS))



