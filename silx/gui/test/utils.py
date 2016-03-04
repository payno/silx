# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""Helper class to write Qt widget unittests.

This module is NOT a test suite.
"""

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "02/03/2016"


import gc
import logging
import unittest

logging.basicConfig()
_logger = logging.getLogger(__name__)

from silx.gui import qt

if qt.BINDING == 'PySide':
    from PySide.QtTest import QTest
elif qt.BINDING == 'PyQt5':
    from PyQt5.QtTest import QTest
elif qt.BINDING == 'PyQt4':
    from PyQt4.QtTest import QTest
else:
    raise ImportError('Unsupported Qt bindings')

# Qt4/Qt5 compatibility wrapper
if qt.BINDING in ('PySide', 'PyQt4'):
    _logger.info("QTest.qWaitForWindowExposed not available," +
                 "using QTest.qWaitForWindowShown instead.")

    def _qWaitForWindowExposed(window, timeout=None):
        """Mimic QTest.qWaitForWindowExposed for Qt4."""
        QTest.qWaitForWindowShown(window)
        return True
else:
    _qWaitForWindowExposed = QTest.qWaitForWindowExposed


# Init QApplication once for all
_qapp = qt.QApplication([])


class TestCaseQt(unittest.TestCase):
    """Base class to write test for Qt stuff.

    It creates a QApplication before running the tests.
    WARNING: The QApplication is shared by all tests, which might have side
    effects.
    """

    DEFAULT_TIMEOUT_WAIT = 100
    """Default timeout for qWait"""

    TIMEOUT_WAIT = 0
    """Extra timeout in millisecond to add to qSleep, qWait and
    qWaitForWindowExposed.

    Intended purpose is for debugging, to add extra time to waits in order to
    allow to view the tested widgets.
    """

    QTest = QTest
    """The Qt QTest class from the used Qt binding."""

    def tearDown(self):
        """Test fixture checking that no more widgets exists."""
        gc.collect()

        widgets = [widget for widget in self.qapp.allWidgets()
                   if widget != self.qapp.desktop()]
        if widgets:
            raise RuntimeError(
                "Test ended with widgets alive: %s", str(widgets))

    @property
    def qapp(self):
        """The QApplication currently running."""
        return qt.QApplication.instance()

    # Proxy to QTest

    Press = QTest.Press
    """Key press action code"""

    Release = QTest.Release
    """Key release action code"""

    Click = QTest.Click
    """Key click action code"""

    @staticmethod
    def keyClick(widget, key, modifier=qt.Qt.NoModifier, delay=-1):
        """Simulate clicking a key.

        See QTest.keyClick for details.
        """
        QTest.keyClick(widget, key, modifier, delay)

    @staticmethod
    def keyClicks(widget, sequence, modifier=qt.Qt.NoModifier, delay=-1):
        """Simulate clicking a sequence of keys.

        See QTest.keyClick for details.
        """
        QTest.keyClicks(widget, sequence, modifier, delay)

    @staticmethod
    def keyEvent(action, widget, key, modifier=qt.Qt.NoModifier, delay=-1):
        """Sends a Qt key event.

        See QTest.keyEvent for details.
        """
        QTest.keyEvent(action, widget, key, modifier, delay)

    @staticmethod
    def keyPress(widget, key, modifier=qt.Qt.NoModifier, delay=-1):
        """Sends a Qt key press event.

        See QTest.keyPress for details.
        """
        QTest.keyPress(widget, key, modifier, delay)

    @staticmethod
    def keyRelease(widget, key, modifier=qt.Qt.NoModifier, delay=-1):
        """Sends a Qt key release event.

        See QTest.keyRelease for details.
        """
        QTest.keyRelease(widget, key, modifier, delay)

    @staticmethod
    def mouseClick(widget, button, modifier=0, pos=None, delay=-1):
        """Simulate clicking a mouse button.

        See QTest.mouseClick for details.
        """
        pos = qt.QPoint(pos[0], pos[1]) if pos is not None else qt.QPoint()
        QTest.mouseClick(widget, button, modifier, pos, delay)

    @staticmethod
    def mouseDClick(widget, button, modifier=0, pos=None, delay=-1):
        """Simulate double clicking a mouse button.

        See QTest.mouseDClick for details.
        """
        pos = qt.QPoint(pos[0], pos[1]) if pos is not None else qt.QPoint()
        QTest.mouseDClick(widget, button, modifier, pos, delay)

    @staticmethod
    def mouseMove(widget, pos=None, delay=-1):
        """Simulate moving the mouse.

        See QTest.mouseMove for details.
        """
        pos = qt.QPoint(pos[0], pos[1]) if pos is not None else qt.QPoint()
        QTest.mouseMove(widget, pos, delay)

    @staticmethod
    def mousePress(widget, button, modifier=0, pos=None, delay=-1):
        """Simulate pressing a mouse button.

        See QTest.mousePress for details.
        """
        pos = qt.QPoint(pos[0], pos[1]) if pos is not None else qt.QPoint()
        QTest.mousePress(widget, button, modifier, pos, delay)

    @staticmethod
    def mouseRelease(widget, button, modifier=0, pos=None, delay=-1):
        """Simulate releasing a mouse button.

        See QTest.mouseRelease for details.
        """
        pos = qt.QPoint(pos[0], pos[1]) if pos is not None else qt.QPoint()
        QTest.mouseRelease(widget, button, modifier, pos, delay)

    def qSleep(self, ms):
        """Sleep for ms milliseconds, blocking the execution of the test.

        See QTest.qSleep for details.
        """
        QTest.qSleep(ms + self.TIMEOUT_WAIT)

    def qWait(self, ms=None):
        """Waits for ms milliseconds, events will be processed.

        See QTest.qWait for details.
        """
        if ms is None:
            ms = self.DEFAULT_TIMEOUT_WAIT
        QTest.qWait(ms + self.TIMEOUT_WAIT)

    def qWaitForWindowExposed(self, window, timeout=None):
        """Waits until the window is shown in the screen.

        See QTest.qWaitForWindowExposed for details.
        """
        if timeout is None:
            result = _qWaitForWindowExposed(window)
        else:
            result = _qWaitForWindowExposed(window, timeout)

        if self.TIMEOUT_WAIT:
            QTest.qWait(self.TIMEOUT_WAIT)

        return result
