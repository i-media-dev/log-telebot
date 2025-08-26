from logger.bot import LogMonitor


def main():
    loger = LogMonitor()
    loger.check_logs('nightly-processing')


if __name__ == '__main__':
    main()
