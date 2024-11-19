class Logger:
    is_debug = True

    def debug(*args):
        if Logger.is_debug:
            print('[DEBUG]\t', *args)

    def log(*args):
        print('[LOG]\t', *args)

    def error(*args):
        print('[ERROR]\t', *args)
