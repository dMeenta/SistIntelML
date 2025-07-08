class PredictionException(Exception):
    def __init__(self, message: str):
        self.message = message

class UnauthorizedException(Exception):
    def __init__(self, message: str):
        self.message = message
