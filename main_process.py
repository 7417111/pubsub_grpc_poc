from concurrent import futures
import logging
import grpc
import time

from radar4d_api.data_access import data_output_notification_pb2_grpc
from radar4d_api.data_access import data_description_pb2

class DataNotificationServicer(data_output_notification_pb2_grpc.DataNotifierServicer):

    def Subscribe(self, request, context):
        index = 0
        while True:
            data_description = data_description_pb2.DataDescription()
            data_description.data_id.data_id = "asdasdasd"
            data_description.produced_timestamp.seconds = index
            data_description.produced_timestamp.nanos = 0
            time.sleep(1)
            index +=1
            yield data_description


def serve():
    notification_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    data_output_notification_pb2_grpc.add_DataNotifierServicer_to_server(
        DataNotificationServicer(),notification_server
    )

    notification_server.add_insecure_port('127.0.0.1:54321')
    notification_server.start()
    notification_server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()