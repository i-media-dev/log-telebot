import os

from dotenv import load_dotenv

load_dotenv()


PROJECTS = {
    'wb_parser': {
        'log_path': os.getenv('TEST_LOG_PATH_WB'),
        'check_time': '00:30',
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('TEST_LOG_PATH_CITILINK'),
        'check_time': '07:30',
    }
}
