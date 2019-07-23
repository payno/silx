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
"""Tests for ROIStatsWidget"""


from silx.gui.utils.testutils import TestCaseQt
from silx.gui import qt
from silx.gui.plot import PlotWindow
from silx.gui.plot.tools.ROIStatsWidget import RoiStatsWidget
from silx.gui.plot.CurvesROIWidget import ROI
from silx.gui.plot.items.roi import RectangleROI, PolygonROI
import numpy



class _TestRoiStatsBase(TestCaseQt):
    """Base class for several unittest relative to RoiStatsWidget"""
    def setUp(self):
        TestCaseQt.setUp(self)
        # define plot
        self.plot = PlotWindow()
        self.plot.addImage(numpy.arange(10000).reshape(100, 100),
                           legend='img1')
        self.img_item = self.plot.getImage('img1')
        self.plot.addCurve(x=numpy.linspace(0, 10, 56), y=numpy.arange(56),
                           legend='curve1')
        self.curve_item = self.plot.getCurve('curve1')
        self.plot.addHistogram(edges=numpy.linspace(0, 10, 56),
                               histogram=numpy.arange(56), legend='histo1')
        self.histogram_item = self.plot.getHistogram(legend='histo1')
        self.plot.addScatter(x=numpy.linspace(0, 10, 56),
                             y=numpy.linspace(0, 10, 56),
                             value=numpy.arange(56),
                             legend='scatter1')
        self.scatter_item = self.plot.getScatter(legend='scatter1')

        # stats widget
        self.statsWidget = RoiStatsWidget(plot=self.plot)

        # define stats
        stats = [
            ('sum', numpy.sum),
            ('mean', numpy.mean),
        ]
        self.statsWidget.setStats(stats=stats)

        # define rois
        self.roi1D = ROI(name='range1', fromdata=0, todata=4, type_='energy')
        self.rectangle_roi = RectangleROI()
        self.rectangle_roi.setGeometry(origin=(0, 0), size=(20, 20))
        self.rectangle_roi.setLabel('Initial ROI')
        self.polygon_roi = PolygonROI()
        points = numpy.array([[0, 5], [5, 0], [10, 5], [5, 10]])
        self.polygon_roi.setPoints(points)

    def statsTable(self):
        return self.statsWidget._statsROITable

    def tearDown(self):
        self.statsWidget.setAttribute(qt.Qt.WA_DeleteOnClose, True)
        self.statsWidget.close()
        self.statsWidget = None
        self.plot.setAttribute(qt.Qt.WA_DeleteOnClose, True)
        self.plot.close()
        self.plot = None
        TestCaseQt.tearDown(self)


class TestRoiStatsCouple(_TestRoiStatsBase):
    """
    Test different possible couple (roi, plotItem).
    Check that:
    
    * computation is correct if couple is valid
    * raise an error if couple is invalid
    """
    def testROICurve(self):
        """
        Test that the couple (ROI, curveItem) can be used for stats       
        """
        item = self.statsWidget.addItem(roi=self.roi1D,
                                        plotItem=self.curve_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '253')
        self.assertEqual(tableItems['mean'].text(), '11.0')

    def testRectangleImage(self):
        """
        Test that the couple (RectangleROI, imageItem) can be used for stats       
        """
        item = self.statsWidget.addItem(roi=self.rectangle_roi,
                                        plotItem=self.img_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '383800')
        self.assertEqual(tableItems['mean'].text(), '959.5')

    def testPolygonImage(self):
        """
        Test that the couple (PolygonROI, imageItem) can be used for stats       
        """
        item = self.statsWidget.addItem(roi=self.polygon_roi,
                                        plotItem=self.img_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '20225')
        self.assertEqual(tableItems['mean'].text(), '404.5')

    def testROIImage(self):
        """
        Test that the couple (ROI, imageItem) is raising an error       
        """
        with self.assertRaises(TypeError):
            self.statsWidget.addItem(roi=self.roi1D,
                                     plotItem=self.img_item)

    def testRectangleCurve(self):
        """
        Test that the couple (rectangleROI, curveItem) is raising an error       
        """
        with self.assertRaises(TypeError):
            self.statsWidget.addItem(roi=self.rectangle_roi,
                                     plotItem=self.curve_item)

    def testROIHistogram(self):
        """
        Test that the couple (PolygonROI, imageItem) can be used for stats       
        """
        item = self.statsWidget.addItem(roi=self.roi1D,
                                        plotItem=self.histogram_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '253')
        self.assertEqual(tableItems['mean'].text(), '11.0')

    def testROIScatter(self):
        """
        Test that the couple (PolygonROI, imageItem) can be used for stats       
        """
        item = self.statsWidget.addItem(roi=self.roi1D,
                                        plotItem=self.scatter_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '253')
        self.assertEqual(tableItems['mean'].text(), '11.0')


class TestRoiStatsAddRemoveItem(_TestRoiStatsBase):
    """Test adding and removing (roi, plotItem) items"""
    def testAddRemoveItems(self):
        item1 = self.statsWidget.addItem(roi=self.roi1D,
                                         plotItem=self.scatter_item)
        self.assertTrue(item1 is not None)
        self.assertEqual(self.statsTable().rowCount(), 1)
        item2 = self.statsWidget.addItem(roi=self.roi1D,
                                         plotItem=self.histogram_item)
        self.assertTrue(item2 is not None)
        self.assertEqual(self.statsTable().rowCount(), 2)
        # try to add twice the same item
        item3 = self.statsWidget.addItem(roi=self.roi1D,
                                         plotItem=self.histogram_item)
        self.assertTrue(item3 is None)
        self.assertEqual(self.statsTable().rowCount(), 2)
        item4 = self.statsWidget.addItem(roi=self.roi1D,
                                         plotItem=self.curve_item)
        self.assertTrue(item4 is not None)
        self.assertEqual(self.statsTable().rowCount(), 3)

        self.statsWidget.removeItem(plotItem=item4._plot_item,
                                    roi=item4._roi)
        self.assertEqual(self.statsTable().rowCount(), 2)
        # try to remove twice the same item
        self.statsWidget.removeItem(plotItem=item4._plot_item,
                                    roi=item4._roi)
        self.assertEqual(self.statsTable().rowCount(), 2)
        self.statsWidget.removeItem(plotItem=item2._plot_item,
                                    roi=item2._roi)
        self.statsWidget.removeItem(plotItem=item1._plot_item,
                                    roi=item1._roi)
        self.assertEqual(self.statsTable().rowCount(), 0)


class TestRoiStatsRoiUpdate(_TestRoiStatsBase):
    """Test that the stats will be updated if the roi is updated"""
    def testChangeRoi(self):
        item = self.statsWidget.addItem(roi=self.rectangle_roi,
                                        plotItem=self.img_item)
        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '383800')
        self.assertEqual(tableItems['mean'].text(), '959.5')

        # update roi
        self.rectangle_roi.setOrigin(position=(10, 10))
        self.assertNotEqual(tableItems['sum'].text(), '383800')
        self.assertNotEqual(tableItems['mean'].text(), '959.5')


class TestRoiStatsPlotItemUpdate(_TestRoiStatsBase):
    """Test that the stats will be updated if the plot item is updated"""
    def testChangeImage(self):
        item = self.statsWidget.addItem(roi=self.rectangle_roi,
                                        plotItem=self.img_item)

        assert item is not None
        tableItems = self.statsTable()._itemToTableItems(item)
        self.assertEqual(tableItems['sum'].text(), '383800')
        self.assertEqual(tableItems['mean'].text(), '959.5')

        # update plot
        self.plot.addImage(numpy.arange(100, 10100).reshape(100, 100),
                           legend='img1')
        self.assertNotEqual(tableItems['mean'].text(), '1059.5')


class TestUpdateMode(TestCaseQt):
    """Test the behavior according to the update mode"""
    def setUp(self):
        pass

    def tearDown(self):
        pass


def suite():
    test_suite = unittest.TestSuite()
    for TestClass in (TestRoiStatsCouple, TestRoiStatsRoiUpdate,
                      TestRoiStatsPlotItemUpdate, TestUpdateMode):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(TestClass))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
