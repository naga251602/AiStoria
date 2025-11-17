# gunicorn_config.py
import multiprocessing

# Bind to all interfaces on port 5000
bind = "0.0.0.0:5000"

# Number of worker processes. 
# Formula: (2 x CPUs) + 1. Good standard starting point.
workers = multiprocessing.cpu_count() * 2 + 1

# Threads per worker (good for handling I/O like AI requests)
threads = 2

# Timeout for requests (120s gives the AI time to "think" if needed)
timeout = 120

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"