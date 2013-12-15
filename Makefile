all: strips_pb2.py

strips_pb2.py: strips.proto
	protoc --python_out=. strips.proto

load_users::strips_pb2.py
	python loader.py -u users.def

load::strips_pb2.py
	python loader.py strips/

dump_users::strips_pb2.py
	python dumper.py -u > users.def

dump::strips_pb2.py
	python dumper.py strips

