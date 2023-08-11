@REM cd radar4d_api
@REM del /S /Q *.py
@REM cd ..


python -m grpc_tools.protoc -I. -Iradar4d_api --python_out=. --grpc_python_out=. radar4d_api\data_access\*.proto




