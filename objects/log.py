from datetime import datetime

class Log:
    
    def __init__(self, data, fixed_message, message):
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data = data
        self.fixed_message = fixed_message
        self.message = message
        
    def to_vars(self):
        return vars(self)