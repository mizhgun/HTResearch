def enum(*sequential, **named):
    """ Implemented an enum based on: http://stackoverflow.com/a/1695250/1440310 """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    mapping = dict((key, value) for key, value in enums.iteritems())
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['mapping'] = mapping
    enums['reverse_mapping'] = reverse
    return type("Enum", (), enums)