import sys
sys.path.append('/var/www/biblionline/servidor/grpc')

import grpc
import helloworld_pb2
import helloworld_pb2_grpc

def run():
    channel = grpc.insecure_channel('192.168.246.26:50051')
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name="Guilherme"))
    print("Resposta gRPC:", response.message)

if __name__ == '__main__':
    run()