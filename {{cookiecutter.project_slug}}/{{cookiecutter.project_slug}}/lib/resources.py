class LocationAwareResource:
    __parent__ = None

    @property
    def __name__(self):
        return self.__class__.__name__
