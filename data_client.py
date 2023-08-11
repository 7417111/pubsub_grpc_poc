from threading import Thread
import queue
import sys
import grpc
import traceback
from google.protobuf import empty_pb2
from radar4d_api.data_access import data_access_pb2_grpc
from radar4d_api.data_access import data_description_pb2

from radar4d_api.data_access import data_output_notification_pb2_grpc

DEFAULT_HOST = "127.0.0.1"  
DEFAULT_NOTIFIER_PORT = "54321"  
DEFAULT_DATA_PORT = "54545"  
MAX_MESSAGE_LENGTH = 80000000  # limit size of the serialized protobuf message in bytes
TIMEOUT = 180 # seconds
def notif_monitoring(notification_queue, stop):
    notification_channel = grpc.insecure_channel(DEFAULT_HOST + ":" + DEFAULT_NOTIFIER_PORT)
    notification_stub = data_output_notification_pb2_grpc.DataNotifierStub(notification_channel)

    try:
        data_descriptions_stream = notification_stub.Subscribe(empty_pb2.Empty(), wait_for_ready=True, timeout=TIMEOUT)
        for data_description in data_descriptions_stream:
            notification_queue.put(data_description)
            if stop():
                data_descriptions_stream.cancel()
                break
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print("AVX server is not ready. Please check if AVX is running and relaunch this script", flush=True)
        else:
            print("rpc_error = %s", str(rpc_error), flush=True)
    print("Notification stream ended", flush=True)



def get_data_frame(data_description,data_stub):
    # AVX may send 'localhost', but the grpc channel creation function requires a numerical address
    print("===============================")
    print(f"last_notif = {data_description}")
        # print(f"data_description.data_by_identifiers[0].data_id={data_description.data_by_identifiers[0].data_id}", flush=True)
    try:
        data_buffer = data_stub.RequestData(data_description.data_id, wait_for_ready=True)
    except grpc.RpcError as rpc_error:
        print("rpc_error = %s", str(rpc_error), flush=True)

    print(f"data_buffer = {data_buffer}")
def main():
    # Start a thread to subscribe to AVX notification channel
    notification_queue = queue.Queue()  # FIFO buffer
    thread_stop_flag = False
    thread = Thread(target=notif_monitoring, args=(notification_queue, lambda: thread_stop_flag))
    thread.start()


    data_channel = grpc.insecure_channel(
        DEFAULT_HOST + ":" + DEFAULT_DATA_PORT,
        options=[
            ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ],
    )
    data_stub = data_access_pb2_grpc.DataAccessStub(data_channel)

    try:
        while thread.is_alive():
            if not notification_queue.empty():
                # In this sample code, we get only the last available data produced by AVX.
                # As a result, we need to unload all notifications in the notification buffer
                for i in range(notification_queue.qsize()):
                    last_notif = notification_queue.get()
                                # a dedicated new stub will be created every time by the get_data_frame() function
                get_data_frame(last_notif, data_stub)
        print("Notification thread ended", flush=True)
    except KeyboardInterrupt:
        thread_stop_flag = True
        print("Shutdown requested... exiting", flush=True)
    except Exception:
        traceback.print_exc(file=sys.stdout)
    thread.join()
    sys.exit(0)


if __name__ == "__main__":
    main()