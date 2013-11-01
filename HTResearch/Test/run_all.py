import sys
import unittest

if __name__ == '__main__':
    try:
        loader = unittest.TestLoader()
        #grab any .py file with the word test in it ...
        tests = loader.discover('.', pattern='*[test|tests].py')
        testRunner = unittest.TextTestRunner(verbosity=2)
        result = testRunner.run(tests)
        sys.exit(len(result.errors) + len(result.failures))
    except SystemExit as inst:
        if inst.args[0]:
            raise

