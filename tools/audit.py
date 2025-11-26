import json
import struct
import glob
import os

def verify_logs():
    print("--- 1. AUDITING RAFT LOGS (JSON) ---")
    log_files = sorted(glob.glob("node_*.log.json"))
    
    if not log_files:
        print("No log files found!")
        return

    first_log = None
    first_name = ""
    
    for f in log_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                # filter out null entries (term == 0)
                clean_log = [e for e in data if e['term'] != 0]
                
                print(f"{f}: {len(clean_log)} committed entries.")
                
                if first_log is None:
                    first_log = clean_log
                    first_name = f
                else:
                    # compare strict equality
                    if clean_log == first_log:
                        print(f"   ✅ MATCHES {first_name}")
                    else:
                        print(f"   ❌ DIVERGENCE DETECTED!")
                        # simple diff to show where it breaks
                        for i in range(min(len(clean_log), len(first_log))):
                            if clean_log[i] != first_log[i]:
                                print(f"      Difference at Index {i+1}: {clean_log[i]} vs {first_log[i]}")
                                break
        except Exception as e:
            print(f"{f}: Corrupt ({e})")
    print("")

def parse_cpp_db(filename):
    """
    Python implementation of your C++ load_from_file logic.
    Format: [KeyLen (4b)][Key Bytes][ValLen (4b)][Val Bytes]...
    """
    store = {}
    with open(filename, "rb") as f:
        while True:
            # read key length (4 bytes int)
            # 'i' = integer, 4 bytes
            chunk = f.read(4)
            if not chunk: break # EOF
            
            key_len = struct.unpack('i', chunk)[0]
            
            # read key
            key = f.read(key_len).decode('utf-8')
            
            # read value length
            chunk = f.read(4)
            val_len = struct.unpack('i', chunk)[0]
            
            # read value
            val = f.read(val_len).decode('utf-8')
            
            # update map (replay the log)
            store[key] = val
            
    return store

def verify_dbs():
    print("--- 2. AUDITING STORAGE ENGINE (BINARY .DB) ---")
    db_files = sorted(glob.glob("node_*.db"))
    
    if not db_files:
        print("No .db files found!")
        return

    first_db = None
    first_name = ""

    for f in db_files:
        try:
            # decode the binary file
            data = parse_cpp_db(f)
            
            # calculate a simple hash of the state for comparison
            # (sorting keys ensures {a:1, b:2} equals {b:2, a:1})
            state_str = json.dumps(data, sort_keys=True)
            import hashlib
            checksum = hashlib.md5(state_str.encode()).hexdigest()
            
            print(f"{f:<12} | Keys: {len(data):<5} | Size: {os.path.getsize(f):<8} bytes | Hash: {checksum}")
            
            if first_db is None:
                first_db = data
                first_name = f
            else:
                if data == first_db:
                    print(f"   ✅ LOGICAL MATCH with {first_name}")
                else:
                    print(f"   ❌ LOGICAL DIVERGENCE!")
                    # find missing keys
                    set1 = set(first_db.items())
                    set2 = set(data.items())
                    diff = set1 ^ set2
                    print(f"      Differences: {diff}")

        except Exception as e:
            print(f"{f}: Failed to parse ({e})")

if __name__ == "__main__":
    verify_logs()
    verify_dbs()