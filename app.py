from flask import Flask, render_template
import psycopg2
import psutil

app = Flask(__name__)

# Database connection
conn = psycopg2.connect(
    dbname="India_map",
    user="postgres",
    password="$Post++",  # Replace with your actual password
    host="localhost",
    port="5432"
)

@app.route('/')
def index():
    cur = conn.cursor()

    # Active connections
    cur.execute("SELECT COUNT(*) FROM pg_stat_activity;")
    active_connections = cur.fetchone()[0]

    # Total transactions
    cur.execute("SELECT sum(xact_commit + xact_rollback) FROM pg_stat_database;")
    transactions = cur.fetchone()[0]

    # Disk I/O
    cur.execute("SELECT pg_database_size(current_database());")
    disk_io = round(cur.fetchone()[0] / (1024 * 1024), 2)  # Convert to MB

    # Tuple activity
    cur.execute("""
        SELECT sum(n_tup_ins), sum(n_tup_upd), sum(n_tup_del)
        FROM pg_stat_user_tables;
    """)
    inserts, updates, deletes = cur.fetchone()

    # Fetch list of tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    table_names = [row[0] for row in cur.fetchall()]

    # Example table performance (replace with real queries if needed)
    table_performance = []
    for table in table_names:
        cur.execute(f"""
            SELECT 
                pg_total_relation_size('{table}')/1024/1024 AS size_mb,
                0.05 AS bloat,  -- Placeholder
                100 AS dead_tuples  -- Placeholder
        """)
        size_mb, bloat, dead_tuples = cur.fetchone()
        table_performance.append({
            "name": table,
            "size": f"{round(size_mb, 2)} MB",
            "bloat": f"{bloat * 100}%",
            "dead_tuples": dead_tuples
        })

    # System metrics
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    cur.close()

    return render_template("index.html",
                           active_connections=active_connections,
                           transactions=transactions,
                           disk_io=disk_io,
                           inserts=inserts,
                           updates=updates,
                           deletes=deletes,
                           cpu_usage=cpu_usage,
                           memory_usage=memory_usage,
                           disk_usage=disk_usage,
                           table_names=table_names,
                           table_performance=table_performance
                           )

if __name__ == '__main__':
    app.run(debug=True)



