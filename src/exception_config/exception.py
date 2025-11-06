import traceback
from src.logger_config.logger import logging


def format_exception(error:Exception)->str:
    error_type=type(error).__name__
    error_message=str(error)
    error_traceback="".join(traceback.format_tb(error.__traceback__))

    formated=(
        f"Exception type: {error_type}\n"
        f"Message: {error_message}\n"
        f"Traceback: {error_traceback}\n"

    )

    logging.error(formated)

    return formated

class CustomException(Exception):
    def __init__(self, error:Exception):
        super().__init__(str(error))
        self.details=format_exception(error)
    
    def __str__(self):
        return self.details