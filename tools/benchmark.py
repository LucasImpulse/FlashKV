import flashkv
import sqlite3
import time
import os
import matplotlib.pyplot as plt

# Configuration
OPERATIONS = 100000  # How many items to write/read
DB_FILE = "bench.db"
SQL_FILE = "bench.sqlite"

def benchmark_toy_redis():
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    
    # --- WRITE ---
    db = flashkv.Database(DB_FILE)
    start = time.time()
    for i in range(OPERATIONS):
        db.set(f"key_{i}", f"value_{i}")
    write_time = time.time() - start
    
    # --- READ ---
    start = time.time()
    for i in range(OPERATIONS):
        val = db.get(f"key_{i}")
    read_time = time.time() - start
    
    return write_time, read_time

def benchmark_sqlite():
    if os.path.exists(SQL_FILE): os.remove(SQL_FILE)
    
    conn = sqlite3.connect(SQL_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE kv (k TEXT PRIMARY KEY, v TEXT)")
    
    # --- WRITE (Use transaction for fairness) ---
    start = time.time()
    # SQLite is slow without transactions for mass inserts
    conn.execute("BEGIN TRANSACTION") 
    for i in range(OPERATIONS):
        c.execute("INSERT INTO kv VALUES (?, ?)", (f"key_{i}", f"value_{i}"))
    conn.commit()
    write_time = time.time() - start
    
    # --- READ ---
    start = time.time()
    for i in range(OPERATIONS):
        c.execute("SELECT v FROM kv WHERE k=?", (f"key_{i}",))
        val = c.fetchone()[0]
    read_time = time.time() - start
    
    conn.close()
    return write_time, read_time

def benchmark_python_dict():
    # Baseline speed (Pure RAM, no disk)
    d = {}
    
    # --- WRITE ---
    start = time.time()
    for i in range(OPERATIONS):
        d[f"key_{i}"] = f"value_{i}"
    write_time = time.time() - start
    
    # --- READ ---
    start = time.time()
    for i in range(OPERATIONS):
        val = d[f"key_{i}"]
    read_time = time.time() - start
    
    return write_time, read_time

print(f"Running benchmarks for {OPERATIONS} ops...")

t_write, t_read = benchmark_toy_redis()
print(f"Toy Redis: Write={t_write:.4f}s, Read={t_read:.4f}s")

s_write, s_read = benchmark_sqlite()
print(f"SQLite:    Write={s_write:.4f}s, Read={s_read:.4f}s")

p_write, p_read = benchmark_python_dict()
print(f"Py Dict:   Write={p_write:.4f}s, Read={p_read:.4f}s")

# --- PLOTTING ---
labels = ['Toy Redis', 'SQLite', 'Python Dict (RAM)']
writes = [OPERATIONS/t_write, OPERATIONS/s_write, OPERATIONS/p_write]
reads = [OPERATIONS/t_read, OPERATIONS/s_read, OPERATIONS/p_read]

x = range(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar([i - width/2 for i in x], writes, width, label='Writes/Sec')
rects2 = ax.bar([i + width/2 for i in x], reads, width, label='Reads/Sec')

ax.set_ylabel('Operations Per Second')
ax.set_title('Database Performance Benchmark')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Add counts on top
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.savefig("benchmark_results.png")
print("\nGraph saved to benchmark_results.png")