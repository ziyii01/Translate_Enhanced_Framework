import enum
import datetime


class log:
    class LogLevel(enum.Enum):
        info = enum.auto()
        warning = enum.auto()
        error = enum.auto()

    @staticmethod
    def _print_log(log_level: LogLevel, message):
        time_now = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")[:-4]
        message = str(message)

        match log_level:
            case log.LogLevel.info:
                print(f"\033[32m{time_now}\033[34m [INFO] {message}\033[0m")

            case log.LogLevel.warning:
                print(f"\033[32m{time_now}\033[33m [WARNING] {message}\033[0m")

            case log.LogLevel.error:
                print(f"\033[32m{time_now}\033[31m [ERROR] {message}\033[0m")

    @staticmethod
    def info(message):
        log._print_log(log.LogLevel.info, message)

    @staticmethod
    def warning(message, *vals, is_format: bool = True):
        log._print_log(log.LogLevel.warning, message)

    @staticmethod
    def error(message, *vals, is_format: bool = True):
        log._print_log(log.LogLevel.error, message)
