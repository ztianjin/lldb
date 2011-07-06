"""
Test lldb data formatter subsystem.
"""

import os, time
import unittest2
import lldb
from lldbtest import *

class DataFormatterTestCase(TestBase):

    mydir = os.path.join("functionalities", "data-formatter", "data-formatter-cpp")

    @unittest2.skipUnless(sys.platform.startswith("darwin"), "requires Darwin")
    def test_with_dsym_and_run_command(self):
        """Test data formatter commands."""
        self.buildDsym()
        self.data_formatter_commands()

    def test_with_dwarf_and_run_command(self):
        """Test data formatter commands."""
        self.buildDwarf()
        self.data_formatter_commands()

    def setUp(self):
        # Call super's setUp().
        TestBase.setUp(self)
        # Find the line number to break at.
        self.line = line_number('main.cpp', '// Set break point at this line.')

    def data_formatter_commands(self):
        """Test that that file and class static variables display correctly."""
        self.runCmd("file a.out", CURRENT_EXECUTABLE_SET)

        self.expect("breakpoint set -f main.cpp -l %d" % self.line,
                    BREAKPOINT_CREATED,
            startstr = "Breakpoint created: 1: file ='main.cpp', line = %d, locations = 1" %
                        self.line)

        self.runCmd("run", RUN_SUCCEEDED)

        # The stop reason of the thread should be breakpoint.
        self.expect("thread list", STOPPED_DUE_TO_BREAKPOINT,
            substrs = ['stopped',
                       'stop reason = breakpoint'])

        self.expect("frame variable",
            substrs = ['(Speed) SPILookHex = 5.55' # Speed by default is 5.55.
                        ]);

        # This is the function to remove the custom formats in order to have a
        # clean slate for the next test case.
        def cleanup():
            self.runCmd('type format clear', check=False)
            self.runCmd('type summary clear', check=False)

        # Execute the cleanup function during test case tear down.
        self.addTearDownHook(cleanup)

        self.runCmd("type format add -C yes -f x Speed BitField")
        self.runCmd("type format add -C no -f c RealNumber")
        self.runCmd("type format add -C no -f x Type2")
        self.runCmd("type format add -C yes -f c Type1")

        # The type format list should show our custom formats.
        self.expect("type format list",
            substrs = ['RealNumber',
                       'Speed',
                       'BitField',
                       'Type1',
                       'Type2'])

        self.expect("frame variable",
            patterns = ['\(Speed\) SPILookHex = 0x[0-9a-f]+' # Speed should look hex-ish now.
                        ]);

        # Now let's delete the 'Speed' custom format.
        self.runCmd("type format delete Speed")

        # The type format list should not show 'Speed' at this point.
        self.expect("type format list", matching=False,
            substrs = ['Speed'])

        # Delete type format for 'Speed', we should expect an error message.
        self.expect("type format delete Speed", error=True,
            substrs = ['no custom format for Speed'])
        
        self.runCmd("type summary add -c Point")
            
        self.expect("frame variable iAmSomewhere",
            substrs = ['x=4',
                       'y=6'])
        
        self.expect("type summary list",
            substrs = ['Point',
                       'one-line'])

        self.runCmd("type summary add -f \"y=${var.y%x}\" Point")

        self.expect("frame variable iAmSomewhere",
            substrs = ['y=0x'])

        self.runCmd("type summary add -f \"hello\" Point -e")

        self.expect("type summary list",
            substrs = ['Point',
                       'show children'])
        
        self.expect("frame variable iAmSomewhere",
            substrs = ['hello',
                       'x = 4',
                       '}'])

        self.runCmd("type summary add -f \"Sign: ${var[31]%B} Exponent: ${var[23-30]%x} Mantissa: ${var[0-22]%u}\" ShowMyGuts")

        self.expect("frame variable cool_pointer->floating",
            substrs = ['Sign: true',
                       'Exponent: 0x',
                       '80'])

        self.runCmd("type summary add -f \"a test\" i_am_cool")

        self.expect("frame variable cool_pointer",
            substrs = ['a test'])

        self.runCmd("type summary add -f \"a test\" i_am_cool --skip-pointers")
        
        self.expect("frame variable cool_pointer",
            substrs = ['a test'],
            matching = False)

        self.runCmd("type summary add -f \"${var[1-3]}\" \"int [5]\"")

        self.expect("frame variable int_array",
            substrs = ['2',
                       '3',
                       '4'])

        self.runCmd("type summary clear")

        self.runCmd("type summary add -f \"${var[0-2].integer}\" \"i_am_cool *\"")
        self.runCmd("type summary add -f \"${var[2-4].integer}\" \"i_am_cool [5]\"")

        self.expect("frame variable cool_array",
            substrs = ['1,1,6'])

        self.expect("frame variable cool_pointer",
            substrs = ['3,0,0'])

        

if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()