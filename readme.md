# This is a PoC to illustrate the SubPub using gRPC and protobuf
- main_process.py: permanent loop, write to shared memory some data every second
- data_server.py: permanent service that waiting for request from client and get requested data on shared memory
- data_client.py: subcribe to the notification service. Connecting to Data server and request data frame when it is avaialble

## Dependency:
This PoC use protobuf and gRPC lib to simplify the notification streaming and data access rpc connection
these 2 lib are availalble as open source
These 2 libs containes a compilator (to generate tool code) and a library (that need to be compile with the app)
There are some risk that this library might be difficult to recompiled to specific target
## getting started:
Create a new virtual environement and install all dependency packagage in requirements.txt

```bash
(.venv)
pip install -r requirements.txt
```

To run the demo, you can start all these process independently, in different console, in order:

```bash
python .\main_process.py
python .\data_server.py
python .\data_client.py
```
Expected result: 
the data client
## Questions:
