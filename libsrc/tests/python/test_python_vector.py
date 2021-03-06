
from base_ports  import *
from  bulkio import *


class Test_Python_Int8(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Int8', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname  )
        pass

class Test_Python_Int16(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Int16', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname,  bio_in_module=InShortPort, bio_out_module=OutShortPort )
        pass

class Test_Python_Int32(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Int32', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname, bio_in_module=InLongPort, bio_out_module=OutLongPort )
        pass

class Test_Python_Int64(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Int64', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname,  bio_in_module=InLongLongPort, bio_out_module=OutLongLongPort )
        pass

class Test_Python_Float(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Float', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname,  bio_in_module=InFloatPort, bio_out_module=OutFloatPort )
        pass

class Test_Python_Double(BaseVectorPort):
    def __init__(self, methodName='runTest', ptype='Double', cname='Python_Ports' ):
        BaseVectorPort.__init__(self, methodName, ptype, cname,  bio_in_module=InDoublePort, bio_out_module=OutDoublePort )
        pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    for x in [ Test_Python_Int8, Test_Python_Int16,  Test_Python_Int32, Test_Python_Int64, Test_Python_Float, Test_Python_Double ]:
        tests = unittest.TestLoader().loadTestsFromTestCase(x)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)



##python -m unittest test_module1 test_module2
##python -m unittest test_module.TestClass
##python -m unittest test_module.TestClass.test_method
##You can pass in a list with any combination of module names, and fully qualified class or method names.
##You can run tests with more detail (higher verbosity) by passing in the -v flag:
##python -m unittest -v test_module
##For a list of all the command-line options:
##python -m unittest -h

