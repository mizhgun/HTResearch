import unittest

loader = unittest.TestLoader()
#grab any .py file with the word test in it ...
tests = loader.discover('.', pattern='*test*.py')
testRunner = unittest.TextTestRunner()
testRunner.run(tests)