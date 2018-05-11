import os


class UserExceptions(Exception):
    def __init__(self, message, *args):
        super.__init__()
        self.message = message
        self.args = args
    

    def __str__(self):
        return 'message: ' + self.message + os.linesep + 'args: ' + self.args


class CatalogError(UserExceptions):
    def __init__(self, message, *args):
        super.__init__(message, args)


class RepoError(UserExceptions):
    def __init__(self, message, *args):
        super.__init__(message, args)