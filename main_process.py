from concurrent import futures
import logging
import grpc
import time
import queue
import sys
import string
import random

# import tempfile
import uuid
from threading import Thread
import numpy as np
from multiprocessing import shared_memory

from radar4d_api.data_access import data_output_notification_pb2_grpc
from radar4d_api.data_access import data_description_pb2

NOTIFICATION_HOST = "127.0.0.1"
NOTIFICATION_PORT = "54321"
DATA_ID_QUEUE_MAX_SIZE = 10

# global variable
data_id_queue = queue.Queue(maxsize=DATA_ID_QUEUE_MAX_SIZE)  # FIFO buffer


class DataNotificationServicer(data_output_notification_pb2_grpc.DataNotifierServicer):
    """ """

    def __init__(self):
        logging.info("init publiser")
        self.last_sent = ""

    # queue_updated
    def Subscribe(self, request, context):
        logging.info(f"Received subcription request from {context}")
        # ==========
        while True:
            try:
                data_id = data_id_queue.queue[data_id_queue.qsize() - 1]
                if data_id != self.last_sent:
                    logging.debug(f"in subscribe loop with data id = {data_id}")
                    data_description = data_description_pb2.DataDescription()
                    data_description.data_id.data_id = data_id
                    data_description.produced_timestamp.seconds = 1
                    data_description.produced_timestamp.nanos = 1
                    self.last_sent = data_id
                    yield data_description
            except Exception as e:
                print(e)
        # data_queue.task_done()
        # ==========
        # index = 0
        # monitoring data_id_queue
        # while True:
        # data_description = data_description_pb2.DataDescription()
        # data_description.data_id.data_id = "asdasdasd"
        # data_description.produced_timestamp.seconds = index
        # data_description.produced_timestamp.nanos = 0
        # time.sleep(1)
        # index +=1
        # yield data_description


def notification_serve():
    notification_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    data_output_notification_pb2_grpc.add_DataNotifierServicer_to_server(
        DataNotificationServicer(), notification_server
    )

    notification_server.add_insecure_port(NOTIFICATION_HOST + ":" + NOTIFICATION_PORT)
    notification_server.start()
    notification_server.wait_for_termination()


class MainProcess:
    def __init__(self, data_id_queue):
        self.data_id_queue = data_id_queue
        self.queue_max_size = DATA_ID_QUEUE_MAX_SIZE
        # self.data_id_queue = queue.Queue(self.queue_max_size)  # FIFO buffer
        self.shm_queue = queue.Queue(
            self.queue_max_size
        )  # the memory buffer that keep all data frame. This one is handle inside the main process
        #         # self.shm = shared_memory.SharedMemory(create=True, size=100)
        logging.info(f"init main process class")

    def random_data_generator(self):
        # create sample data and adding to the data queue
        logging.info(f"Processing time ...")
        time.sleep(0.5)

        # ===================
        # # generating data sample
        random_string_data = self.id_generator(size=30000)
        data_size = len(random_string_data)
        shm_temp = shared_memory.SharedMemory(create=True, size=data_size)
        shm_temp.buf[0:data_size] = bytes(random_string_data, "utf-8")

        if not self.data_id_queue.full():
            self.shm_queue.put(shm_temp, block=False)
            self.data_id_queue.put(shm_temp.name, block=False)
            logging.debug(f"data created with id: {shm_temp.name}")
        else:
            # # clean the unused data frame
            data_id_to_delete = self.data_id_queue.get(block=False)
            shm_to_delete = self.shm_queue.get(block=False)
            shm_to_delete.unlink()  # Call unlink only once to release the shared memory
            shm_to_delete.close()  # close the intance
            logging.info(f"data_it_to_delete = {data_id_to_delete}")
            # adding new fram to shm queue
            self.shm_queue.put(shm_temp, block=False)
            self.data_id_queue.put(shm_temp.name, block=False)
            logging.debug(f"data created with id: {shm_temp.name}")

    def run(self):
        while True:
            self.random_data_generator()

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))


def main():
    """main function that will try to emulate 2 thread"""
    # Notification service start
    thread_notification = Thread(target=notification_serve)
    thread_notification.start()

    # data provider start
    main_process = MainProcess(data_id_queue=data_id_queue)
    thread_main = Thread(target=main_process.run)
    thread_main.start()

    thread_notification.join()
    thread_main.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
