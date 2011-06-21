"""
Test lldb Python API object's default constructor and make sure it is invalid
after initial construction.

There are two exceptions to the above general rules, though; the API objects are
SBCommadnReturnObject and SBStream.
"""

import os, time
import re
import unittest2
import lldb, lldbutil
from lldbtest import *

class APIDefaultConstructorTestCase(TestBase):

    mydir = os.path.join("python_api", "default-constructor")

    @python_api_test
    def test_SBAddress(self):
        obj = lldb.SBAddress()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBBlock(self):
        obj = lldb.SBBlock()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBBreakpoint(self):
        obj = lldb.SBBreakpoint()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBBreakpointLocation(self):
        obj = lldb.SBBreakpointLocation()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBBroadcaster(self):
        obj = lldb.SBBroadcaster()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBCommandReturnObject(self):
        """SBCommandReturnObject object is valid after default construction."""
        obj = lldb.SBCommandReturnObject()
        if self.TraceOn():
            print obj
        self.assertTrue(obj)

    @python_api_test
    def test_SBCommunication(self):
        obj = lldb.SBCommunication()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBCompileUnit(self):
        obj = lldb.SBCompileUnit()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBDebugger(self):
        obj = lldb.SBDebugger()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBError(self):
        obj = lldb.SBError()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBEvent(self):
        obj = lldb.SBEvent()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBFileSpec(self):
        obj = lldb.SBFileSpec()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBFrame(self):
        obj = lldb.SBFrame()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBFunction(self):
        obj = lldb.SBFunction()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBInputReader(self):
        obj = lldb.SBInputReader()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBInstruction(self):
        obj = lldb.SBInstruction()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBInstructionList(self):
        obj = lldb.SBInstructionList()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBLineEntry(self):
        obj = lldb.SBLineEntry()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBListener(self):
        obj = lldb.SBListener()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBModule(self):
        obj = lldb.SBModule()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBProcess(self):
        obj = lldb.SBProcess()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBStream(self):
        """SBStream object is valid after default construction."""
        obj = lldb.SBStream()
        if self.TraceOn():
            print obj
        self.assertTrue(obj)

    @python_api_test
    def test_SBStringList(self):
        obj = lldb.SBStringList()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBSymbol(self):
        obj = lldb.SBSymbol()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBSymbolContext(self):
        obj = lldb.SBSymbolContext()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBSymbolContextList(self):
        obj = lldb.SBSymbolContextList()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBTarget(self):
        obj = lldb.SBTarget()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBThread(self):
        obj = lldb.SBThread()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBType(self):
        obj = lldb.SBType()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBValue(self):
        obj = lldb.SBValue()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)

    @python_api_test
    def test_SBValueList(self):
        obj = lldb.SBValueList()
        if self.TraceOn():
            print obj
        self.assertFalse(obj)


if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()