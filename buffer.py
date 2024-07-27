import threading
import time

class Buffer:
    def __init__(self) -> None:
        """Initialize the buffer with an initial data value."""
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        # Types: -1 empty, 0 request discard, 1 request action, 2 signal discard, 3 signal action
        self.type = -1
        self.data = []

    def is_request(self) -> bool:
        """Check if the buffer is in a request state."""
        return self.type in (0, 1)

    def is_signal(self) -> bool:
        """Check if the buffer is in a signal state."""
        return self.type in (2, 3)

    def isEmpty(self):
        return self.type == -1
    
    def request(self, request_type: int, request_data: list) -> list:
        """
        Request an action with a specific type and data.
        
        Waits for the buffer to receive a signal type in response and returns the signal type and data.
        """
        with self.condition:
            # Set request type and data
            self.type = request_type
            self.data = request_data
            self.condition.notify_all()  # Notify any waiting thread

            # Wait for a signal type (2 or 3)
            while not self.is_signal():
                self.condition.wait()
            
            # Return the signaled type and data after being notified
            return self.data

    def signal(self, signal_type: int, signal_data: list):
        """
        Signal an action with a specific type and data.
        
        Waits for the buffer to receive a request type in response and returns the request type and data.
        """
        with self.condition:
            # Set signal type and data
            self.type = signal_type
            self.data = signal_data
            self.condition.notify_all()  # Notify any waiting thread


    def get_request(self) -> tuple:
        """
        Check if the buffer is in a request state and return the type and data.
        """
        with self.lock:
            if self.is_request():
                # Return the type and data if it's a request
                return self.type, self.data
            else:
                # Return a default value or handle the case when there is no request
                return None, None
        

    def get_data(self) -> tuple:
        """
        Get the current type and data from the buffer.
        
        Returns a tuple of the current type and data.
        """
        with self.lock:
            return self.type, self.data

    def __str__(self) -> str:
        """Return a string representation of the buffer."""
        with self.lock:
            return f"Buffer(type={self.type}, data={self.data})"


if __name__ == "__main__":
    buffer = Buffer()


    def request_thread_func(buffer, request_type, request_data):
        time.sleep(1)  # Simulate some delay
        response_type, response_data = buffer.request(request_type, request_data)
        print(f"Request thread received signal: type={response_type}, data={response_data}")

    # Function for a thread that signals
    def signal_thread_func(buffer, signal_type, signal_data):
        buffer.get_request()  # Wait for a request to arrive
        time.sleep(1)  # Simulate processing time
        buffer.signal(signal_type, signal_data)
        print(f"Signal thread completed signaling: type={signal_type}, data={signal_data}")

    # Create threads
    request_thread = threading.Thread(target=request_thread_func, args=(buffer, 1, [10, 20, 30]))
    signal_thread = threading.Thread(target=signal_thread_func, args=(buffer, 2, [40, 50, 60]))

    # Start threads
    request_thread.start()
    signal_thread.start()

    # Wait for threads to finish
    request_thread.join()
    signal_thread.join()

    print("Final buffer state:", buffer)