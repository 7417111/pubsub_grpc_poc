import grpc
import logging
from concurrent import futures
import time
import random
import string
from radar4d_api.data_access import data_access_pb2_grpc
from radar4d_api.data_access import data_description_pb2

class DataAccessServicer(data_access_pb2_grpc.DataAccessServicer):

    def RequestData(self, request, context):
        print(f"data_it = {request.data_id}") #the request is of type DataIdentifier
        data_buffer = data_description_pb2.DataBuffer()
        index = 0
        data_buffer = data_description_pb2.DataBuffer()
        sample_data = ''.join(random.choice(string.ascii_uppercase) for _ in range(12))
        data_buffer.data = bytes(sample_data, 'utf-8')
        time.sleep(1)
        index +=1
        return data_buffer
def serve():
    data_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    data_access_pb2_grpc.add_DataAccessServicer_to_server(
        DataAccessServicer(),data_server
    )

    data_server.add_insecure_port('127.0.0.1:54545')
    data_server.start()
    data_server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()