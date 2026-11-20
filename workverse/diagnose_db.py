"""
WorkVerse - Database Connectivity Diagnostic Tool
Safely diagnoses database connection issues without exposing credentials.
Reads parameters from environment variables or command-line options.
"""

import os
import sys
import socket
import time
import ssl

def mask_credential(val):
    if not val:
        return "<not set>"
    if len(val) <= 4:
        return "****"
    return val[:2] + "****" + val[-2:]

def run_diagnostics():
    print("=" * 60)
    print("WorkVerse Database Connection Diagnostic Tool")
    print("=" * 60)

    # 1. Read Environment Variables
    db_host = os.environ.get('DB_HOST')
    db_port_str = os.environ.get('DB_PORT')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')
    db_ssl = os.environ.get('DB_SSL', 'auto').lower()

    print("\n[Step 1] Configuration Inspection:")
    print(f"  DB_HOST     : {db_host or '<MISSING>'}")
    print(f"  DB_PORT     : {db_port_str or '<MISSING (will default to 3306)>'}")
    print(f"  DB_USER     : {db_user or '<MISSING>'}")
    print(f"  DB_PASSWORD : {'<SET>' if db_password else '<MISSING>'}")
    print(f"  DB_NAME     : {db_name or '<MISSING>'}")
    print(f"  DB_SSL      : {db_ssl}")

    errors = []
    if not db_host:
        errors.append("DB_HOST environment variable is missing.")
    if not db_user:
        errors.append("DB_USER environment variable is missing.")
    if db_password is None:
        errors.append("DB_PASSWORD environment variable is missing.")
    if not db_name:
        errors.append("DB_NAME environment variable is missing.")

    try:
        db_port = int(db_port_str) if db_port_str else 3306
    except ValueError:
        errors.append(f"DB_PORT '{db_port_str}' is not a valid integer.")
        db_port = 3306

    if errors:
        print("\n[!] Configuration errors detected:")
        for err in errors:
            print(f"    - {err}")
        print("\nPlease set the required environment variables and re-run.")
        print("Example (PowerShell):")
        print('  $env:DB_HOST="mainline.proxy.rlwy.net"')
        print('  $env:DB_PORT="43679"')
        print('  $env:DB_USER="root"')
        print('  $env:DB_PASSWORD="your_password"')
        print('  $env:DB_NAME="railway"')
        print("=" * 60)
        return False

    # 2. DNS Resolution Test
    print(f"\n[Step 2] DNS Resolution for '{db_host}'...")
    try:
        resolved_ips = socket.gethostbyname_ex(db_host)[2]
        print(f"  [PASS] Resolved successfully to: {', '.join(resolved_ips)}")
    except socket.gaierror as e:
        print(f"  [FAIL] DNS resolution failed: {e}")
        print("  Check if DB_HOST is misspelled or no longer valid.")
        return False

    # 3. TCP Connectivity Test
    target_ip = resolved_ips[0]
    print(f"\n[Step 3] TCP Connection to {target_ip}:{db_port}...")
    tcp_connected = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        t0 = time.time()
        sock.connect((target_ip, db_port))
        elapsed = time.time() - t0
        print(f"  [PASS] TCP handshake succeeded in {elapsed:.2f}s.")
        tcp_connected = True
    except socket.timeout:
        print("  [FAIL] TCP connection timed out (10s). Port may be blocked or host unreachable.")
        sock.close()
        return False
    except Exception as e:
        print(f"  [FAIL] TCP connection failed: {e}")
        sock.close()
        return False

    # 4. MySQL Handshake Packet Test (Low-level)
    print("\n[Step 4] Checking Initial MySQL Handshake Packet...")
    try:
        sock.settimeout(10)
        initial_bytes = sock.recv(1024)
        if len(initial_bytes) == 0:
            print("  [FAIL] Remote endpoint immediately closed the connection (0 bytes / EOF).")
            print("  Diagnostic Analysis:")
            print("  - If this is Railway Serverless, the service may be asleep or waking up.")
            print("  - Or Railway's TCP proxy port may have changed / no longer routes to MySQL.")
            print("  - Or the MySQL service container crashed upon connection.")
            handshake_packet_received = False
        else:
            print(f"  [PASS] Received {len(initial_bytes)} bytes from server greeting.")
            handshake_packet_received = True
    except socket.timeout:
        print("  [FAIL] Timed out waiting for MySQL handshake packet.")
        handshake_packet_received = False
    except Exception as e:
        print(f"  [FAIL] Error reading handshake: {e}")
        handshake_packet_received = False
    finally:
        sock.close()

    # 5. PyMySQL Connection Test (with retry for serverless wake-up)
    print("\n[Step 5] PyMySQL Connection & Authentication Test...")
    try:
        import pymysql
    except ImportError:
        print("  [FAIL] PyMySQL is not installed in the current environment.")
        return False

    # Test SSL variations: ssl={} vs ssl=None
    ssl_options = []
    if db_ssl in ('true', '1', 'yes', 'require', 'required'):
        ssl_options = [{'ssl': {}}]
    elif db_ssl in ('false', '0', 'no', 'disable'):
        ssl_options = [{'ssl': None}]
    else:
        # Auto: try with SSL first, then without SSL
        ssl_options = [{'ssl': {}}, {'ssl': None}]

    conn = None
    last_err = None
    max_retries = 5
    backoff = 3

    for ssl_config in ssl_options:
        ssl_desc = "with SSL (ssl={})" if ssl_config['ssl'] is not None else "without SSL"
        print(f"\n  Attempting connection {ssl_desc} with up to {max_retries} wake-up retries...")

        for attempt in range(1, max_retries + 1):
            try:
                connect_kwargs = {
                    'host': db_host,
                    'port': db_port,
                    'user': db_user,
                    'password': db_password,
                    'database': db_name,
                    'connect_timeout': 15,
                    'read_timeout': 15,
                    'write_timeout': 15,
                    'cursorclass': pymysql.cursors.DictCursor,
                    'charset': 'utf8mb4'
                }
                if ssl_config['ssl'] is not None:
                    connect_kwargs['ssl'] = ssl_config['ssl']

                conn = pymysql.connect(**connect_kwargs)
                print(f"  [PASS] Successfully connected on attempt {attempt}!")
                break
            except pymysql.err.OperationalError as e:
                last_err = e
                err_code = e.args[0] if e.args else None
                err_msg = e.args[1] if len(e.args) > 1 else str(e)
                print(f"    Attempt {attempt}/{max_retries} failed: [{err_code}] {err_msg}")

                # Immediate fatal errors that should NOT be retried:
                if err_code == 1045:  # Access denied (bad user/password)
                    print("    -> Authentication failed. Check DB_USER and DB_PASSWORD.")
                    break
                elif err_code == 1049:  # Unknown database
                    print(f"    -> Database '{db_name}' does not exist on this MySQL server.")
                    break

                if attempt < max_retries:
                    sleep_time = backoff * attempt
                    print(f"    -> Sleeping container may be booting. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
            except Exception as e:
                last_err = e
                print(f"    Attempt {attempt}/{max_retries} error: {type(e).__name__}: {e}")
                break

        if conn is not None:
            break

    if conn is None:
        print(f"\n  [FAIL] Could not establish MySQL connection. Last error: {last_err}")
        return False

    # 6. Database and Table Inspection
    print("\n[Step 6] Inspecting Server, Databases, and Tables...")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS ver, DATABASE() AS cur_db")
            info = cursor.fetchone()
            print(f"  MySQL Server Version : {info.get('ver')}")
            print(f"  Connected Database   : {info.get('cur_db')}")

            # List databases
            cursor.execute("SHOW DATABASES")
            all_dbs = [row['Database'] for row in cursor.fetchall()]
            print(f"  Available Databases  : {', '.join(all_dbs)}")

            # List tables in current database
            cursor.execute("SHOW TABLES")
            table_key = f"Tables_in_{db_name}"
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            print(f"  Tables in '{db_name}': {', '.join(tables) if tables else '<NO TABLES FOUND>'}")

            # Check required WorkVerse tables
            expected_tables = {'users', 'simulations', 'quizzes', 'progress', 'submissions'}
            found_expected = expected_tables.intersection(set(tables))
            missing_expected = expected_tables - set(tables)

            print(f"\n[Step 7] WorkVerse Schema Verification:")
            print(f"  Expected tables found : {len(found_expected)}/{len(expected_tables)} ({', '.join(found_expected)})")
            if missing_expected:
                print(f"  Missing tables        : {', '.join(missing_expected)}")
                if 'workverse_db' in all_dbs and db_name != 'workverse_db':
                    print("  [NOTE] 'workverse_db' database exists! The tables might be inside 'workverse_db' instead of 'railway'.")
            else:
                print("  [PASS] All core WorkVerse tables are present!")

            # 7. Test query
            if 'simulations' in tables:
                cursor.execute("SELECT COUNT(*) AS cnt FROM simulations")
                sim_count = cursor.fetchone().get('cnt', 0)
                print(f"  Simulations count in DB: {sim_count}")
                cursor.execute("SELECT title FROM simulations LIMIT 3")
                sample_sims = [row['title'] for row in cursor.fetchall()]
                print(f"  Sample simulations     : {', '.join(sample_sims)}")

            if 'users' in tables:
                cursor.execute("SELECT COUNT(*) AS cnt FROM users")
                user_count = cursor.fetchone().get('cnt', 0)
                print(f"  Registered users count : {user_count}")

        conn.close()
        print("\n" + "=" * 60)
        print("DIAGNOSTIC RESULT: SUCCESS! Database is fully accessible.")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"  [FAIL] Error during inspection: {e}")
        if conn:
            conn.close()
        return False

if __name__ == '__main__':
    run_diagnostics()
