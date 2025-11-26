import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LogParseResult:
    """Датакласс с результатами парсинга лог-файла."""
    status: str
    date: str
    execution_time: float
    run_id: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    function_name: Optional[str] = None
    info_bot_messages: List[str] = field(default_factory=list)
    is_completed: bool = False


class LogParser:
    """Класс, предоставляющий интерфейс для парса логов."""

    @staticmethod
    def _find_json_record(content: str) -> Optional[dict]:
        """Защищенный метод находит JSON запись в логе."""
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return None

    @staticmethod
    def _extract_info_bot_messages(content: str) -> List[str]:
        """Защищенный метод извлекает INFO_BOT сообщения."""
        messages = []
        for line in content.split('\n'):
            if 'INFO_BOT' in line:
                parts = line.split('INFO_BOT,')
                if len(parts) > 1:
                    message = parts[1].split(', handler.')[0].strip()
                    if message:
                        messages.append(message)
        return messages

    @staticmethod
    def parse_log_content(content: str, filename: str) -> LogParseResult:
        """Метод парсит лог-файл с JSON записями."""
        if not content:
            return LogParseResult('NOTFOUND', '', 0.0, filename)

        run_id = filename.replace('.log', '')
        json_data = LogParser._find_json_record(content)

        if json_data:
            status = json_data.get('STATUS', 'UNKNOWN')
            date = json_data.get('DATE', '')
            execution_time = json_data.get('EXECUTION_TIME', 0.0)
            function_name = json_data.get('FUNCTION_NAME', '')
            error_type = json_data.get('ERROR_TYPE')
            error_message = json_data.get('ERROR_MESSAGE')
            is_completed = json_data.get('ENDLOGGING') == 1
        else:
            status = 'PENDING' if 'ENDLOGGING=1' not in content else 'UNKNOWN'
            date = ''
            execution_time = 0.0
            function_name = ''
            error_type = None
            error_message = None
            is_completed = 'ENDLOGGING=1' in content

        info_bot_messages = LogParser._extract_info_bot_messages(content)

        return LogParseResult(
            status=status,
            date=date,
            execution_time=execution_time,
            run_id=run_id,
            error_type=error_type,
            error_message=error_message,
            function_name=function_name,
            info_bot_messages=info_bot_messages,
            is_completed=is_completed
        )
