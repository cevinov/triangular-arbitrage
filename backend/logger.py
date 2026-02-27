import sys
import queue

class LogManager:
    def __init__(self):
        # Saves the original standard output (console)
        self.terminal = sys.stdout
        self.log_queue = queue.Queue()

    def write(self, message):
        # Print to the real console immediately
        self.terminal.write(message)
        # Only queue non-empty messages to avoid spamming blank lines
        if message.strip() and not getattr(self, 'stopped', False): 
            self.log_queue.put(message)

    def flush(self):
        self.terminal.flush()
        
    def stop(self):
        self.stopped = True

log_manager = LogManager()
