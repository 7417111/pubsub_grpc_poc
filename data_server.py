import grpc
import logging
from concurrent import futures
import time
import random
import string
from multiprocessing import shared_memory
from radar4d_api.data_access import data_access_pb2_grpc
from radar4d_api.data_access import data_description_pb2

DEFAULT_HOST = "127.0.0.1"
DEFAULT_NOTIFIER_PORT = "54321"
DEFAULT_DATA_PORT = "54545"


class DataAccessServicer(data_access_pb2_grpc.DataAccessServicer):
    def RequestData(self, request, context):
        logging.info(f"data it requested = {request.data_id}")  # the request is of type DataIdentifier
        data_buffer = data_description_pb2.DataBuffer()
        shm_temp = shared_memory.SharedMemory(request.data_id)
        data_buffer.data = bytes(shm_temp.buf[:])
        shm_temp.close()
        # index = 0
        # data_buffer = data_description_pb2.DataBuffer()
        # sample_data = ''.join(random.choice(string.ascii_uppercase) for _ in range(12))
        # data_buffer.data = bytes(sample_data, 'utf-8')
        # index +=1
        return data_buffer


def serve():
    data_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    data_access_pb2_grpc.add_DataAccessServicer_to_server(DataAccessServicer(), data_server)

    data_server.add_insecure_port(DEFAULT_HOST + ":" + DEFAULT_DATA_PORT)
    data_server.start()
    data_server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
