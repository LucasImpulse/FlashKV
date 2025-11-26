import grpc
import sys
import os
import time
import random

# path hack
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir := os.path.join(current_dir, ".."))
from cluster import raft_pb2, raft_pb2_grpc

PORTS = [5000, 5001, 5002]

def find_leader():
    """Polls nodes until one admits to being the leader."""
    for port in PORTS:
        try:
            channel = grpc.insecure_channel(f'localhost:{port}')
            stub = raft_pb2_grpc.RaftNodeStub(channel)
            # read to check status
            resp = stub.Get(raft_pb2.Key(key="probe"))
            if resp.leaderHint: 
                # if they gave us a hint, follow it
                return int(resp.leaderHint)
            # if successful (even if key not found), this IS the leader
            return 5000 + (int(port) - 5000) # return the leader ID
        except:
            continue
    return None

def run_demo():
    leader_id = 1 # start guessing node 1
    
    print("--- RAFT CLUSTER DEMO ---")
    print("1. Start 3 nodes.")
    print("2. I will write keys continuously.")
    print("3. KILL THE LEADER whenever you want.")
    print("-------------------------")
    time.sleep(2)

    counter = 1
    while True:
        key = f"launch_code_{counter}"
        val = f"SECRET_{random.randint(1000, 9999)}"
        
        # try to write to current known leader
        target_port = 5000 + (leader_id - 1)
        try:
            with grpc.insecure_channel(f'localhost:{target_port}') as channel:
                stub = raft_pb2_grpc.RaftNodeStub(channel)
                print(f"Sending {key} -> Node {leader_id}...", end=" ")
                
                response = stub.Set(raft_pb2.KeyValue(key=key, value=val))
                
                if response.success:
                    print(f"✅ SUCCESS (Committed)")
                    counter += 1
                    time.sleep(1.5) # slow enough to read logs
                else:
                    print(f"❌ FAILURE: {response.message}")
                    # if redirect, update leader_id
                    if "Try Node" in response.message:
                        leader_id = int(response.message.split("Try Node ")[1].replace(")", ""))
                        print(f"   -> Switching to Node {leader_id}")
                        
        except grpc.RpcError:
            print(f"💀 Node {leader_id} is DEAD. Hunting for new Leader...")
            time.sleep(1)
            # simple failover logic: try next node
            leader_id = (leader_id % 3) + 1 

if __name__ == '__main__':
    run_demo()