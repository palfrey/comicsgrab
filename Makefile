all: strips_pb2.py

strips_pb2.py: strips.proto
	protoc --python_out=. strips.proto

load:: strips_pb2.py
	python loader.py strips.def

dump:: strips_pb2.py
	python dumper.py > strips.def

