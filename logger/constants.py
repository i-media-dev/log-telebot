import os

from dotenv import load_dotenv


load_dotenv()


PROJECTS = {
    'wb_parser': {
        'log_path': os.getenv('LOG_PATH_WB'),
        'check_time': '00:15',
        'success_patterns': ['completed successfully', 'SUCCESS'],
        'error_patterns': ['ERROR', 'Exception', 'failed']
    },
    'citilink_feed_handler': {
        'log_path': os.getenv('LOG_PATH_CITILINK'),
        'check_time': '07:15',
        'success_patterns': ['Report generated', 'SUCCESS'],
        'error_patterns': ['ERROR', 'Exception', 'failed']
    }
}
