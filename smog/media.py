class Media(object):
    def __init__(self, param_dict):
        self.__dict__.update(param_dict)

    def __repr__(self):
        return str(self.__dict__)
