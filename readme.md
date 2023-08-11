# This is a PoC to illustrate the SubPub using gRPC and protobuf
- main_process.py: permanent loop the write to shared memory some data every second
- data_server.py: permanent service that waiting for request from client and get requested data on shared memory
- data_client.py: 

Dependency:
This PoC use protobuf and gRPC lib to simplify the notification streaming and data access rpc connection
these 2 lib are availalble as open source
These 2 libs containes a compilator (to generate tool code) and a library (that need to be compile with the app)
There are some risk that this library might be difficult to recompiled to specific target
## getting started:
