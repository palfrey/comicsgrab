all: strips_pb2.py

strips_pb2.py: strips.proto
	protoc --python_out=. strips.proto

load::
	python loader.py strips.def

dump::
	python dumper.py > strips.def

