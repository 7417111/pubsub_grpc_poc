from multiprocessing import shared_memory
import uuid
import sys
# # create=true to create a new shared memory instance, if it already exists with the same name, an exception is thrown
# shm_a = shared_memory.SharedMemory(name="example", create=True, size=10)

# shm_a.buf[:3] = bytearray([1, 2, 3])
# while True:
#     do_smt()
# shm_a.close()
# shm_b = shared_memory.SharedMemory(create=True, size=10)
# shm_b.name


#   from multiprocessing import shared_memory
#   # create=false, use existing
#   shm_a = shared_memory.SharedMemory(name="example", size=10)
#   print(bytes(shm.buf[:3]))
#   # [0x01, 0x02, 0x03]
#   while True:
#       do_smt()
#   shm_a.close()
# ===================================
# random_string_data = str(uuid.uuid4()) + str(uuid.uuid4())
# random_string_data
# data_size = len(random_string_data)
# data_size
# shm_b = shared_memory.SharedMemory(name='MyMemory',create=True, size=data_size)
# shm_b.buf[0:data_size] = bytes(random_string_data, 'utf-8')
# shm_b.name
# shm_b.close()

# # On another process
# from multiprocessing import shared_memory
# shm_a = shared_memory.SharedMemory(name='MyMemory', create=False)
# print(shm_a.buf[:])
# bytes(shm_a.buf[:]) 



# ======================
import threading
import queue

q = queue.Queue()

def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

# Send thirty task requests to the worker.
for item in range(30):
    q.put(item)

# Block until all tasks are done.
q.join()
print('All work completed')