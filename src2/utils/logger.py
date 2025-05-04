from typing import List
import datetime

class Logger:
    """Handles game messages and logging."""
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[str] = []
        self.max_messages = max_messages
        
    def add_message(self, message: str, turn: int = None) -> None:
        """Add a message to the log and print to stdout with a turn separator if turn is provided."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.messages.append(log_entry)
        
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
            
        if turn is not None:
            print(f"== turn ({turn}) =============")
        print(log_entry)
        
    def get_messages(self, count: int = 10) -> List[str]:
        """Get the most recent messages."""
        return self.messages[-count:]
        
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        
    def save_to_file(self, filename: str) -> None:
        """Save messages to a file."""
        with open(filename, 'w') as f:
            for message in self.messages:
                f.write(f"{message}\n")
                
    def load_from_file(self, filename: str) -> None:
        """Load messages from a file."""
        try:
            with open(filename, 'r') as f:
                self.messages = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.messages = [] 