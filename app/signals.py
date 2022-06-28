import signal
import sys


def setup_graceful_shutdown(executor):
    def _shutdown(sig, frame):
        print(f"received signal {sig}, shutting down...")
        executor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
