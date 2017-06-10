def log_progress(task):
    def wrap(func):
        def wrapped_func(*args):
            print('{0}..'.format(task), end='\r')
            result = func(*args)
            print('{0}.. Done.'.format(task))
            return result
        return wrapped_func
    return wrap
