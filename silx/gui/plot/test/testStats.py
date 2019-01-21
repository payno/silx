# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2019 European Synchrotron Radiation Facility
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
"""Basic tests for CurvesROIWidget"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/03/2018"


from silx.gui import qt
from silx.gui.plot.stats import stats
from silx.gui.plot import StatsWidget
from silx.gui.plot.StatsLineWidget import BasicLineStatsWidget
from silx.gui.plot.stats import statshandler
from silx.gui.utils.testutils import TestCaseQt
from silx.gui.plot import Plot1D, Plot2D
import unittest
import logging
import numpy

_logger = logging.getLogger(__name__)


class TestStats(TestCaseQt):
    """
    Test :class:`BaseClass` class and inheriting classes
    """
    def setUp(self):
        TestCaseQt.setUp(self)
        self.createCurveContext()
        self.createImageContext()
        self.createScatterContext()

    def tearDown(self):
        self.plot1d.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot1d.close()
        self.plot2d.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot2d.close()
        self.scatterPlot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.scatterPlot.close()

    def createCurveContext(self):
        self.plot1d = Plot1D()
        x = range(20)
        y = range(20)
        self.plot1d.addCurve(x, y, legend='curve0')

        self.curveContext = stats._CurveContext(
            item=self.plot1d.getCurve('curve0'),
            plot=self.plot1d,
            onlimits=False)

    def createScatterContext(self):
        self.scatterPlot = Plot2D()
        lgd = 'scatter plot'
        self.xScatterData = numpy.array([0, 1, 2, 20, 50, 60, 36])
        self.yScatterData = numpy.array([2, 3, 4, 26, 69, 6, 18])
        self.valuesScatterData = numpy.array([5, 6, 7, 10, 90, 20, 5])
        self.scatterPlot.addScatter(self.xScatterData, self.yScatterData,
                                    self.valuesScatterData, legend=lgd)
        self.scatterContext = stats._ScatterContext(
            item=self.scatterPlot.getScatter(lgd),
            plot=self.scatterPlot,
            onlimits=False
        )

    def createImageContext(self):
        self.plot2d = Plot2D()
        self._imgLgd = 'test image'
        self.imageData = numpy.arange(32*128).reshape(32, 128)
        self.plot2d.addImage(data=self.imageData,
                             legend=self._imgLgd, replace=False)
        self.imageContext = stats._ImageContext(
            item=self.plot2d.getImage(self._imgLgd),
            plot=self.plot2d,
            onlimits=False
        )

    def getBasicStats(self):
        return {
            'min': stats.StatMin(),
            'minCoords': stats.StatCoordMin(),
            'max': stats.StatMax(),
            'maxCoords': stats.StatCoordMax(),
            'std': stats.Stat(name='std', fct=numpy.std),
            'mean': stats.Stat(name='mean', fct=numpy.mean),
            'com': stats.StatCOM()
        }

    def testBasicStatsCurve(self):
        """Test result for simple stats on a curve"""
        _stats = self.getBasicStats()
        xData = yData = numpy.array(range(20))
        self.assertEqual(_stats['min'].calculate(self.curveContext), 0)
        self.assertEqual(_stats['max'].calculate(self.curveContext), 19)
        self.assertEqual(_stats['minCoords'].calculate(self.curveContext), (0,))
        self.assertEqual(_stats['maxCoords'].calculate(self.curveContext), (19,))
        self.assertEqual(_stats['std'].calculate(self.curveContext), numpy.std(yData))
        self.assertEqual(_stats['mean'].calculate(self.curveContext), numpy.mean(yData))
        com = numpy.sum(xData * yData) / numpy.sum(yData)
        self.assertEqual(_stats['com'].calculate(self.curveContext), com)

    def testBasicStatsImage(self):
        """Test result for simple stats on an image"""
        _stats = self.getBasicStats()
        self.assertEqual(_stats['min'].calculate(self.imageContext), 0)
        self.assertEqual(_stats['max'].calculate(self.imageContext), 128 * 32 - 1)
        self.assertEqual(_stats['minCoords'].calculate(self.imageContext), (0, 0))
        self.assertEqual(_stats['maxCoords'].calculate(self.imageContext), (127, 31))
        self.assertEqual(_stats['std'].calculate(self.imageContext), numpy.std(self.imageData))
        self.assertEqual(_stats['mean'].calculate(self.imageContext), numpy.mean(self.imageData))

        yData = numpy.sum(self.imageData.astype(numpy.float64), axis=1)
        xData = numpy.sum(self.imageData.astype(numpy.float64), axis=0)
        dataXRange = range(self.imageData.shape[1])
        dataYRange = range(self.imageData.shape[0])

        ycom = numpy.sum(yData*dataYRange) / numpy.sum(yData)
        xcom = numpy.sum(xData*dataXRange) / numpy.sum(xData)

        self.assertEqual(_stats['com'].calculate(self.imageContext), (xcom, ycom))

    def testStatsImageAdv(self):
        """Test that scale and origin are taking into account for images"""

        image2Data = numpy.arange(32 * 128).reshape(32, 128)
        self.plot2d.addImage(data=image2Data, legend=self._imgLgd,
                             replace=True, origin=(100, 10), scale=(2, 0.5))
        image2Context = stats._ImageContext(
            item=self.plot2d.getImage(self._imgLgd),
            plot=self.plot2d,
            onlimits=False
        )
        _stats = self.getBasicStats()
        self.assertEqual(_stats['min'].calculate(image2Context), 0)
        self.assertEqual(
            _stats['max'].calculate(image2Context), 128 * 32 - 1)
        self.assertEqual(
            _stats['minCoords'].calculate(image2Context), (100, 10))
        self.assertEqual(
            _stats['maxCoords'].calculate(image2Context), (127*2. + 100,
                                                           31 * 0.5 + 10))
        self.assertEqual(_stats['std'].calculate(image2Context),
                         numpy.std(self.imageData))
        self.assertEqual(_stats['mean'].calculate(image2Context),
                         numpy.mean(self.imageData))

        yData = numpy.sum(self.imageData, axis=1)
        xData = numpy.sum(self.imageData, axis=0)
        dataXRange = numpy.arange(self.imageData.shape[1], dtype=numpy.float64)
        dataYRange = numpy.arange(self.imageData.shape[0], dtype=numpy.float64)

        ycom = numpy.sum(yData * dataYRange) / numpy.sum(yData)
        ycom = (ycom * 0.5) + 10
        xcom = numpy.sum(xData * dataXRange) / numpy.sum(xData)
        xcom = (xcom * 2.) + 100
        self.assertTrue(numpy.allclose(
            _stats['com'].calculate(image2Context), (xcom, ycom)))

    def testBasicStatsScatter(self):
        """Test result for simple stats on a scatter"""
        _stats = self.getBasicStats()
        self.assertEqual(_stats['min'].calculate(self.scatterContext), 5)
        self.assertEqual(_stats['max'].calculate(self.scatterContext), 90)
        self.assertEqual(_stats['minCoords'].calculate(self.scatterContext), (0, 2))
        self.assertEqual(_stats['maxCoords'].calculate(self.scatterContext), (50, 69))
        self.assertEqual(_stats['std'].calculate(self.scatterContext), numpy.std(self.valuesScatterData))
        self.assertEqual(_stats['mean'].calculate(self.scatterContext), numpy.mean(self.valuesScatterData))

        data = self.valuesScatterData.astype(numpy.float64)
        comx = numpy.sum(self.xScatterData * data) / numpy.sum(data)
        comy = numpy.sum(self.yScatterData * data) / numpy.sum(data)
        self.assertEqual(_stats['com'].calculate(self.scatterContext),
                         (comx, comy))

    def testKindNotManagedByStat(self):
        """Make sure an exception is raised if we try to execute calculate
        of the base class"""
        b = stats.StatBase(name='toto', compatibleKinds='curve')
        with self.assertRaises(NotImplementedError):
            b.calculate(self.imageContext)

    def testKindNotManagedByContext(self):
        """
        Make sure an error is raised if we try to calculate a statistic with
        a context not managed
        """
        myStat = stats.Stat(name='toto', fct=numpy.std, kinds=('curve'))
        myStat.calculate(self.curveContext)
        with self.assertRaises(ValueError):
            myStat.calculate(self.scatterContext)
        with self.assertRaises(ValueError):
            myStat.calculate(self.imageContext)

    def testOnLimits(self):
        stat = stats.StatMin()

        self.plot1d.getXAxis().setLimitsConstraints(minPos=2, maxPos=5)
        curveContextOnLimits = stats._CurveContext(
            item=self.plot1d.getCurve('curve0'),
            plot=self.plot1d,
            onlimits=True)
        self.assertEqual(stat.calculate(curveContextOnLimits), 2)

        self.plot2d.getXAxis().setLimitsConstraints(minPos=32)
        imageContextOnLimits = stats._ImageContext(
            item=self.plot2d.getImage('test image'),
            plot=self.plot2d,
            onlimits=True)
        self.assertEqual(stat.calculate(imageContextOnLimits), 32)

        self.scatterPlot.getXAxis().setLimitsConstraints(minPos=40)
        scatterContextOnLimits = stats._ScatterContext(
            item=self.scatterPlot.getScatter('scatter plot'),
            plot=self.scatterPlot,
            onlimits=True)
        self.assertEqual(stat.calculate(scatterContextOnLimits), 20)


class TestStatsFormatter(TestCaseQt):
    """Simple test to check usage of the :class:`StatsFormatter`"""
    def setUp(self):
        self.plot1d = Plot1D()
        x = range(20)
        y = range(20)
        self.plot1d.addCurve(x, y, legend='curve0')

        self.curveContext = stats._CurveContext(
            item=self.plot1d.getCurve('curve0'),
            plot=self.plot1d,
            onlimits=False)

        self.stat = stats.StatMin()

    def tearDown(self):
        self.plot1d.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot1d.close()

    def testEmptyFormatter(self):
        """Make sure a formatter with no formatter definition will return a
        simple cast to str"""
        emptyFormatter = statshandler.StatFormatter()
        self.assertEqual(
            emptyFormatter.format(self.stat.calculate(self.curveContext)), '0.000')

    def testSettedFormatter(self):
        """Make sure a formatter with no formatter definition will return a
        simple cast to str"""
        formatter= statshandler.StatFormatter(formatter='{0:.3f}')
        self.assertEqual(
            formatter.format(self.stat.calculate(self.curveContext)), '0.000')


class TestStatsHandler(unittest.TestCase):
    """Make sure the StatHandler is correctly making the link between 
    :class:`StatBase` and :class:`StatFormatter` and checking the API is valid
    """
    def setUp(self):
        self.plot1d = Plot1D()
        x = range(20)
        y = range(20)
        self.plot1d.addCurve(x, y, legend='curve0')
        self.curveItem = self.plot1d.getCurve('curve0')

        self.stat = stats.StatMin()

    def tearDown(self):
        self.plot1d.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot1d.close()

    def testConstructor(self):
        """Make sure the constructor can deal will all possible arguments:
        
        * tuple of :class:`StatBase` derivated classes
        * tuple of tuples (:class:`StatBase`, :class:`StatFormatter`)
        * tuple of tuples (str, pointer to function, kind)
        """
        handler0 = statshandler.StatsHandler(
            (stats.StatMin(), stats.StatMax())
        )

        res = handler0.calculate(item=self.curveItem, plot=self.plot1d,
                                 onlimits=False)
        self.assertTrue('min' in res)
        self.assertEqual(res['min'], '0')
        self.assertTrue('max' in res)
        self.assertEqual(res['max'], '19')

        handler1 = statshandler.StatsHandler(
            (
                (stats.StatMin(), statshandler.StatFormatter(formatter=None)),
                (stats.StatMax(), statshandler.StatFormatter())
            )
        )

        res = handler1.calculate(item=self.curveItem, plot=self.plot1d,
                                 onlimits=False)
        self.assertTrue('min' in res)
        self.assertEqual(res['min'], '0')
        self.assertTrue('max' in res)
        self.assertEqual(res['max'], '19.000')

        handler2 = statshandler.StatsHandler(
            (
                (stats.StatMin(), None),
                (stats.StatMax(), statshandler.StatFormatter())
        ))

        res = handler2.calculate(item=self.curveItem, plot=self.plot1d,
                                 onlimits=False)
        self.assertTrue('min' in res)
        self.assertEqual(res['min'], '0')
        self.assertTrue('max' in res)
        self.assertEqual(res['max'], '19.000')

        handler3 = statshandler.StatsHandler((
            (('amin', numpy.argmin), statshandler.StatFormatter()),
            ('amax', numpy.argmax)
        ))

        res = handler3.calculate(item=self.curveItem, plot=self.plot1d,
                                 onlimits=False)
        self.assertTrue('amin' in res)
        self.assertEqual(res['amin'], '0.000')
        self.assertTrue('amax' in res)
        self.assertEqual(res['amax'], '19')

        with self.assertRaises(ValueError):
            statshandler.StatsHandler(('name'))


class TestStatsWidgetWithCurves(TestCaseQt):
    """Basic test for StatsWidget with curves"""
    def setUp(self):
        TestCaseQt.setUp(self)
        self.plot = Plot1D()
        self.plot.show()
        x = range(20)
        y = range(20)
        self.plot.addCurve(x, y, legend='curve0')
        y = range(12, 32)
        self.plot.addCurve(x, y, legend='curve1')
        y = range(-2, 18)
        self.plot.addCurve(x, y, legend='curve2')
        self.widget = StatsWidget.StatsTable(plot=self.plot)

        mystats = statshandler.StatsHandler((
            stats.StatMin(),
            (stats.StatCoordMin(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            stats.StatMax(),
            (stats.StatCoordMax(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            stats.StatDelta(),
            ('std', numpy.std),
            ('mean', numpy.mean),
            stats.StatCOM()
        ))

        self.widget.setStats(mystats)

    def tearDown(self):
        self.plot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot.close()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        self.plot = None
        TestCaseQt.tearDown(self)

    def testInit(self):
        """Make sure all the curves are registred on initialization"""
        self.assertEqual(self.widget.rowCount(), 3)

    def testRemoveCurve(self):
        """Make sure the Curves stats take into account the curve removal from
        plot"""
        self.plot.removeCurve('curve2')
        self.assertEqual(self.widget.rowCount(), 2)
        for iRow in range(2):
            self.assertTrue(self.widget.item(iRow, 0).text() in ('curve0', 'curve1'))

        self.plot.removeCurve('curve0')
        self.assertEqual(self.widget.rowCount(), 1)
        self.plot.removeCurve('curve1')
        self.assertEqual(self.widget.rowCount(), 0)

    def testAddCurve(self):
        """Make sure the Curves stats take into account the add curve action"""
        self.plot.addCurve(legend='curve3', x=range(10), y=range(10))
        self.assertEqual(self.widget.rowCount(), 4)

    def testUpdateCurveFromAddCurve(self):
        """Make sure the stats of the cuve will be removed after updating a
        curve"""
        self.plot.addCurve(legend='curve0', x=range(10), y=range(10))
        self.qapp.processEvents()
        self.assertEqual(self.widget.rowCount(), 3)
        curve = self.plot._getItem(kind='curve', legend='curve0')
        tableItems = self.widget._itemToTableItems(curve)
        self.assertEqual(tableItems['max'].text(), '9')

    def testUpdateCurveFromCurveObj(self):
        self.plot.getCurve('curve0').setData(x=range(4), y=range(4))
        self.qapp.processEvents()
        self.assertEqual(self.widget.rowCount(), 3)
        curve = self.plot._getItem(kind='curve', legend='curve0')
        tableItems = self.widget._itemToTableItems(curve)
        self.assertEqual(tableItems['max'].text(), '3')

    def testSetAnotherPlot(self):
        plot2 = Plot1D()
        plot2.addCurve(x=range(26), y=range(26), legend='new curve')
        self.widget.setPlot(plot2)
        self.assertEqual(self.widget.rowCount(), 1)
        self.qapp.processEvents()
        plot2.setAttribute(qt.Qt.WA_DeleteOnClose)
        plot2.close()
        plot2 = None


class TestStatsWidgetWithImages(TestCaseQt):
    """Basic test for StatsWidget with images"""

    IMAGE_LEGEND = 'test image'

    def setUp(self):
        TestCaseQt.setUp(self)
        self.plot = Plot2D()

        self.plot.addImage(data=numpy.arange(128*128).reshape(128, 128),
                           legend=self.IMAGE_LEGEND, replace=False)

        self.widget = StatsWidget.StatsTable(plot=self.plot)

        mystats = statshandler.StatsHandler((
            (stats.StatMin(), statshandler.StatFormatter()),
            (stats.StatCoordMin(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            (stats.StatMax(), statshandler.StatFormatter()),
            (stats.StatCoordMax(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            (stats.StatDelta(), statshandler.StatFormatter()),
            ('std', numpy.std),
            ('mean', numpy.mean),
            (stats.StatCOM(), statshandler.StatFormatter(None))
        ))

        self.widget.setStats(mystats)

    def tearDown(self):
        self.plot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot.close()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        self.plot = None
        TestCaseQt.tearDown(self)

    def test(self):
        image = self.plot._getItem(
            kind='image', legend=self.IMAGE_LEGEND)
        tableItems = self.widget._itemToTableItems(image)

        maxText = '{0:.3f}'.format((128 * 128) - 1)
        self.assertEqual(tableItems['legend'].text(), self.IMAGE_LEGEND)
        self.assertEqual(tableItems['min'].text(), '0.000')
        self.assertEqual(tableItems['max'].text(), maxText)
        self.assertEqual(tableItems['delta'].text(), maxText)
        self.assertEqual(tableItems['coords min'].text(), '0.0, 0.0')
        self.assertEqual(tableItems['coords max'].text(), '127.0, 127.0')


class TestStatsWidgetWithScatters(TestCaseQt):

    SCATTER_LEGEND = 'scatter plot'

    def setUp(self):
        TestCaseQt.setUp(self)
        self.scatterPlot = Plot2D()
        self.scatterPlot.addScatter([0, 1, 2, 20, 50, 60],
                                    [2, 3, 4, 26, 69, 6],
                                    [5, 6, 7, 10, 90, 20],
                                    legend=self.SCATTER_LEGEND)
        self.widget = StatsWidget.StatsTable(plot=self.scatterPlot)

        mystats = statshandler.StatsHandler((
            stats.StatMin(),
            (stats.StatCoordMin(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            stats.StatMax(),
            (stats.StatCoordMax(), statshandler.StatFormatter(None, qt.QTableWidgetItem)),
            stats.StatDelta(),
            ('std', numpy.std),
            ('mean', numpy.mean),
            stats.StatCOM()
        ))

        self.widget.setStats(mystats)

    def tearDown(self):
        self.scatterPlot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.scatterPlot.close()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        self.scatterPlot = None
        TestCaseQt.tearDown(self)

    def testStats(self):
        scatter = self.scatterPlot._getItem(
            kind='scatter', legend=self.SCATTER_LEGEND)
        tableItems = self.widget._itemToTableItems(scatter)
        self.assertEqual(tableItems['legend'].text(), self.SCATTER_LEGEND)
        self.assertEqual(tableItems['min'].text(), '5')
        self.assertEqual(tableItems['coords min'].text(), '0, 2')
        self.assertEqual(tableItems['max'].text(), '90')
        self.assertEqual(tableItems['coords max'].text(), '50, 69')
        self.assertEqual(tableItems['delta'].text(), '85')


class TestEmptyStatsWidget(TestCaseQt):
    def test(self):
        widget = StatsWidget.StatsWidget()
        widget.show()


class TestLineWidget(TestCaseQt):
    """Some test for the StatsLineWidget."""
    def setUp(self):

        TestCaseQt.setUp(self)
        self.plot = Plot1D()
        self.plot.show()
        x = range(20)
        y = range(20)
        self.plot.addCurve(x, y, legend='curve0')
        y = range(12, 32)
        self.plot.addCurve(x, y, legend='curve1')
        y = range(-2, 18)
        self.plot.addCurve(x, y, legend='curve2')
        self.widget = BasicLineStatsWidget(plot=self.plot, kind='curve',
                                           statsOnVisibleData=False)

    def tearDown(self):
        self.plot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.plot.close()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        self.plot = None
        TestCaseQt.tearDown(self)

    def test(self):
        self.widget.setStatsOnVisibleData(False)
        self.qapp.processEvents()
        self.plot.setActiveCurve(legend='curve0')
        self.assertTrue(self.widget._statQlineEdit['min'].text() == '0.000')
        self.plot.setActiveCurve(legend='curve1')
        self.assertTrue(self.widget._statQlineEdit['min'].text() == '12.000')
        self.plot.getXAxis().setLimitsConstraints(minPos=2, maxPos=5)
        self.widget.setStatsOnVisibleData(True)
        self.qapp.processEvents()
        self.assertTrue(self.widget._statQlineEdit['min'].text() == '14.000')


def suite():
    test_suite = unittest.TestSuite()
    for TestClass in (TestStats, TestStatsHandler, TestStatsWidgetWithScatters,
                      TestStatsWidgetWithImages, TestStatsWidgetWithCurves,
                      TestStatsFormatter, TestEmptyStatsWidget, TestLineWidget):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(TestClass))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
