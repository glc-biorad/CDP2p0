# standard library
import sys
import threading
from typing import Union
import time
import os
import os.path as osp
import shutil

# third party
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from scipy.signal import fftconvolve
from scipy import optimize
from scipy.interpolate import griddata
#import skimage.label as sk_label
#import skimage.regionprops as sk_regionprops
import traceback
import tifffile
# BioRad
import instrument_interface
import utils
# from fastapi_code.app.routers.reader_submodule import get_status_and_position
# external hardware



# default_e9000xposure = {'bf':350, 'alexa405':525000, 'fam':5000, 'hex':999999,
#     'atto':999999,'cy5':999999, 'cy55':999999, }

default_exposure = {'bf':1000, 'alexa405':200000, 'fam':400000, 'hex':999999,
    'atto':999999,'cy5':999999, 'cy55':999999, }
# default_exposure = {'bf':1000, 'alexa405':30000, 'fam':400000, 'hex':400000,
#     'atto':999999,'cy5':999999, 'cy55':999999, }

current_exposure = default_exposure.copy() # change this instead of default


def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) / 4 / stddev)**2)


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        # self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        # self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

class liveThread(QtCore.QThread):
    update_image = QtCore.pyqtSignal(QtGui.QImage)
    def __init__(self, instrument_interface, config_data, parent=None, debug=False):
        QtCore.QThread.__init__(self, parent)
        self.instrument_interface = instrument_interface
        self.camera = instrument_interface.reader.camcontroller.camera
        self.stop_imaging = False
        self.debug = debug
        self.config_data = config_data

    def run(self):
        # self.camera.BeginAcquisition()
        self.instrument_interface.reader.camcontroller.snap_continuous_prep()
        self.instrument_interface.moveFilterWheel('FAM')
        if self.config_data['LED_off_to_move']:
            time.sleep(self.config_data['motor_LED_delay'])
        self.instrument_interface.turnOnLED('HEX', intensity=50) # hex is now bf led
        self.instrument_interface.reader.camcontroller.setExposureTimeMicroseconds(current_exposure['bf'])
        while self.stop_imaging == False:
            if self.debug:
                print('Begin Imaging Loop Thread')
            try:
                time1 = time.time()
                image_result = self.camera.GetNextImage(1000)
                img = image_result.GetNDArray()
                time2 = time.time()
                # convert image to 8-bit for QImage
                img = img / (2**16-1)
                img *= 255
                qimg = QtGui.QImage(img.astype(np.uint8), img.shape[1],img.shape[0], QtGui.QImage.Format_Grayscale8)
                self.update_image.emit(qimg)
                image_result.Release()
                time3 = time.time()
                if self.debug:
                    print('Got image in {0}\n, displayed in {1}'.format(time2-time1, time3-time2))
                time.sleep(0.001)
            except:
                print('Error: %s' % sys.exc_info()[0])
                return False
        if self.debug:
            print('pre end acquisition')
        self.camera.EndAcquisition()
        if self.debug:
            print('ended acquisition')

# sample functions
class guiMethodList(QtGui.QStandardItem):
    def __init__(self, parent=None, text='Success'):
        super(guiMethodList, self).__init__(parent)
        self.pressure = 100
        # self.setText = QtCore.QStringConverterBase.QStringConverter(text)
        self.setText = text

    def type(self):
        return 1001

class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class testitemstd(QtGui.QStandardItem):
    def __init__(self, parent=None):
        super(testitemstd, self).__init__(parent)
        self.loc = 'PkUpTps'
        self.asp_vol = 1000
        self.disp_vol = 1000
        name = 'default, loc={0}, asp_vol={1}, disp_vol={2}'.format(self.loc, self.asp_vol, self.disp_vol)
        self.setText(name)


class testitem(QtWidgets.QListWidgetItem):
    def __init__(self, parent=None):
        super(testitem, self).__init__(parent)
        self.loc = 'PkUpTps'
        self.asp_vol = 1000
        self.disp_vol = 1000
        name = 'default, loc={0}, asp_vol={1}, disp_vol={2}'.format(self.loc, self.asp_vol, self.disp_vol)
        self.setText(name)

class ExposureDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ExposureDialog, self).__init__(parent)
        uic.loadUi('gui_exposureDialog.ui', self)
        self.sigmap = QtCore.QSignalMapper(self)
        self.expchanged = QtCore.pyqtSignal(int)
        self.fields = [self.lineEdit_exposureBF, self.lineEdit_exposureAlexa,
            self.lineEdit_exposureFAM, self.lineEdit_exposureHEX,
            self.lineEdit_exposureAtto, self.lineEdit_exposureCy5,
            self.lineEdit_exposureCy55]
        # connecting the following button with reset ALWAYS runs reset when
        # any action
        self.pushButton_Reset.clicked.connect(self.reset_exposures)
        self.sigmap.mapped[int].connect(self.update_exposuredict)
        for i, chan in enumerate(current_exposure.keys()):
            self.fields[i].setText(str(current_exposure[chan]))
            self.fields[i].returnPressed.connect(self.sigmap.map)
            self.sigmap.setMapping(self.fields[i], i)

    @QtCore.pyqtSlot(int)
    def update_exposuredict(self, ind):
        keymap = list(current_exposure.keys())
        key = keymap[ind]
        print(ind)
        try:
            exp = int(self.fields[ind].text())
            self.fields[ind].setText(str(exp))
            current_exposure[key] = exp
            print(exp, 'changing to this value')
        except:
            self.fields[ind].setText('Invalid Exposure')
            print('Invalid')
        for i, field in enumerate(self.fields):
            print(i, field.text())

    def reset_exposures(self):
        for i, chan in enumerate(current_exposure.keys()):
            exp = default_exposure[chan]
            current_exposure[chan] = exp
            self.fields[i].setText(str(exp))

class A100kScanDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(A100kScanDialog, self).__init__(parent)
        uic.loadUi('gui_a100kScanDialog.ui', self)
        self.fluor_chkbtns = [self.checkBox_BF, self.checkBox_Alexa, self.checkBox_FAM,
            self.checkBox_HEX, self.checkBox_Atto, self.checkBox_Cy5, self.checkBox_Cy55]
        self.fluor_labels = ['bf', 'alexa405', 'fam', 'hex',
                            'atto', 'cy5', 'cy55',]
        self.proceed_with_imaging = False # flag for in case we x'ed out window
        self.pushButton_okScan.clicked.connect(self.accept_parameters)
        for chkbtn in self.fluor_chkbtns:
            if chkbtn is self.checkBox_BF:
                continue
            chkbtn.setChecked(True)

        self.heater_chkbtns = {0: self.checkBox_hAenable, 1: self.checkBox_hBenable,
            2: self.checkBox_hCenable, 3: self.checkBox_hDenable}
        self.heater_ch_chkbtns = {0: [self.checkBox_hA1, self.checkBox_hA2, self.checkBox_hA3,
            self.checkBox_hA4, self.checkBox_hA5, self.checkBox_hA6, self.checkBox_hA7, self.checkBox_hA8],
            1: [self.checkBox_hB1, self.checkBox_hB2, self.checkBox_hB3, self.checkBox_hB4,
            self.checkBox_hB5, self.checkBox_hB6, self.checkBox_hB7, self.checkBox_hB8],
            2: [self.checkBox_hC1, self.checkBox_hC2, self.checkBox_hC3, self.checkBox_hC4,
            self.checkBox_hC5, self.checkBox_hC6, self.checkBox_hC7, self.checkBox_hC8],
            3: [self.checkBox_hD1, self.checkBox_hD2, self.checkBox_hD3, self.checkBox_hD4,
            self.checkBox_hD5, self.checkBox_hD6, self.checkBox_hD7, self.checkBox_hD8]}

        self.all_selections = {'fluor_channels': [], 'heaters_enabled': np.zeros(4, dtype=bool),
            'which_chambers': np.zeros((4, 8), dtype=bool),
            'proceed_with_imaging': self.proceed_with_imaging}

        self.sigmap = QtCore.QSignalMapper(self)
        self.sigmap.mapped[int].connect(self.checkbox_changed)
        for i in range(len(self.heater_chkbtns)):
            self.heater_chkbtns[i].stateChanged.connect(self.sigmap.map)
            self.sigmap.setMapping(self.heater_chkbtns[i], i)

    @QtCore.pyqtSlot(int) # this line is apparently not necessary?
    def checkbox_changed(self, which_heater):
        current_chkbox = self.heater_chkbtns[which_heater]
        if current_chkbox.isChecked():
            # going from unchecked to checked
            for chkbox in self.heater_ch_chkbtns[which_heater]:
                chkbox.setEnabled(True)
                chkbox.setChecked(True)
        else:
            # going from checked to unchecked
            for chkbox in self.heater_ch_chkbtns[which_heater]:
                chkbox.setEnabled(False)
                chkbox.setChecked(False)

    def accept_parameters(self):
        # self.proceed_with_imaging = 1
        self.all_selections['proceed_with_imaging'] = True
        self.close()

    def collect_selections(self):
        '''Collect Imaging Selection parameters and pass to main window.
        After we have made our selection for which heaters/chambers to use, we
        need to collect all of the selections and pass it ot the mainwindow so
        that we can pass the parameters to the scanning function.'''

        self.all_selections['fluor_channels'] = [label for label, chk_btn in zip(self.fluor_labels, self.fluor_chkbtns) if chk_btn.isChecked()]
        heaters_enabled = [self.heater_chkbtns[k].isChecked() for k in self.heater_chkbtns]
        self.all_selections['heaters_enabled'] = heaters_enabled
        for htrNum in range(len(self.heater_chkbtns)):
            if self.all_selections['heaters_enabled'][htrNum] == True: # comparing int to bool
                # store which chambers
                use_chambers = [chkbtn.isChecked() for chkbtn in self.heater_ch_chkbtns[htrNum]]
                self.all_selections['which_chambers'][htrNum, :] = use_chambers
            else:
                continue
        return self.all_selections









class CDP2p0_GUI(QtWidgets.QMainWindow):
    ''' This is the main class. Purpose is to create a GUI interface for running
    the appropriate functions to control the instrument. This class should
    provide an interface both to interact with the instrument in a live manner,
    like a live imaging system, and in a pre-programmed way, like creating
    protocol files that you can share with other users.
    '''
    def __init__(self, parent=None):
        super(CDP2p0_GUI, self).__init__(parent)
        uic.loadUi('gui_mainwindow.ui', self)

        try:
            self.instrument_interface = instrument_interface.Connection_Interface()
        except Exception as e:
            print('*'*40)
            print('Could not connect to instrument interface.')
            print('*'*40)
            print(e)
            self.instrument_interface = instrument_interface.Dummy_Interface()


        # load config file
        self.config_data = utils.import_config_file('unit_config.json')
        self.label_unitDisplay.setText(self.config_data['unit'])

        # init thread pool
        self.threadpool = QtCore.QThreadPool().globalInstance()
        self.threadpool.setMaxThreadCount(2)

        self.stop_imaging = False
        self.live_imaging = liveThread(self.instrument_interface, self.config_data)
        # self.live_imaging = liveThread_nocam()
        self.live_imaging.update_image.connect(lambda qimg: self.update_display(qimg))

        # test button push, test
        self.pushButton_RunProtocol.clicked.connect(lambda: print('button pressed'))
        # self.pushButton_RunProtocol.clicked.connect(self.fastapi_webserver_test)

        # test on item added
        self.listWidget_ProtocolBuilder.itemChanged.connect(lambda:print('item added'))
        self.listWidget_ProtocolBuilder.itemChanged.connect(self.getParameters)
        self.listWidget_ProtocolBuilder.itemChanged.connect(self.listitems)

        # guiitem = guiMethodList() # this didn't work
        modellistview = QtGui.QStandardItemModel()
        self.listView_test.setModel(modellistview)
        guiitem = guiMethodList()
        modellistview.appendRow(guiitem)
        guiitem2 = QtGui.QStandardItem('TestItem2')
        modellistview.appendRow(guiitem2)
        testitem_instance = testitemstd()
        modellistview.appendRow(testitem_instance)
        # self.listView_test.addItem(guiitem)

        # init state dict
        self.state_dict = {'leds': {
        'alexa405': 0, 'fam': 0, 'hex': 0, 'atto': 0, 'cy5': 0, 'cy55':0 , 'bf':0},
        'trays': {'AB': 0, 'CD':0},
        'heaters': {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        }



        # check for chassis board response
        self.label_chassisError.hide()
        x_now, y_now, z_now, fw_now = self.instrument_interface.reader.get_position() # x, y, z, fw
        for val in [x_now, y_now, z_now, fw_now]:
            if val == None:
                self.label_chassisError.enabled = True
                self.label_chassisError.show()

        # init large scale repositioning picture tool
        self.comboBox_heater.addItem('A')
        self.comboBox_heater.addItem('B')
        self.comboBox_heater.addItem('C')
        self.comboBox_heater.addItem('D')
        im = tifffile.imread(osp.join('GUI', 'test_image_rightsize1.tif'))
        qimg = QtGui.QImage(im, im.shape[1], im.shape[0], QtGui.QImage.Format_Grayscale8)
        self.label_testImage.setPixmap(QtGui.QPixmap.fromImage(qimg))
        self.label_testImage.setScaledContents(True)
        self.label_testImage.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)


        self.label_testImage.mousePressEvent = self.moveImager_PBRS

        # init timer for updating thermocyclers
        self.timer_TCs = QtCore.QTimer()
        self.timer_TCs.setInterval(1000) # 1 second
        # self.timer_TCs.timeout.connect(lambda: self.create_worker_add_threadpool(self.update_TCplots))
        self.timer_counter = 0

        # init graphics/plots for plotting thermocycler data
        self._init_TCplots()

        # initialize timers, threads, etc
        self.timer_TCs.start()

        # ---------------------------------------------------
        # ------------- LIVE IMAGER BUTTONS -----------------
        # ---------------------------------------------------
        # self._init_Heaterpositions()
        self.fluor_chkbtns = [self.checkBox_BF, self.checkBox_Alexa, self.checkBox_FAM,
            self.checkBox_HEX, self.checkBox_Atto, self.checkBox_Cy5, self.checkBox_Cy55]
        self.fluor_labels = ['bf', 'alexa405', 'fam', 'hex',
                            'atto', 'cy5', 'cy55',]

        # stage navigation buttons
        self.pushButton_Left.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='-x'))
        self.pushButton_Right.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='x'))
        self.pushButton_Top.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='-y'))
        self.pushButton_Bottom.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='y'))
        self.pushButton_Up.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='z'))
        self.pushButton_Down.clicked.connect(lambda: self.create_worker_add_threadpool(self.moveImager, dir='-z'))

        # self.pushButton_toggleTrayBC.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.open_tray('CD')))
        # self.pushButton_closeTrayBC.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.close_tray('CD')))
        # Tray buttons
        self.pushButton_toggleTrayAB.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('AB')))
        self.pushButton_toggleTrayCD.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('CD')))
        self.pushButton_toggleHeaterA.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('A')))
        self.pushButton_toggleHeaterB.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('B')))
        self.pushButton_toggleHeaterC.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('C')))
        self.pushButton_toggleHeaterD.clicked.connect(lambda: self.create_worker_add_threadpool(self.toggleReaderSubmodule('D')))
        # self.pushButton_homeReader.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.homeImager))

        # FW buttons
        self.pushButton_FWBF.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('FAM')))
        self.pushButton_FWAlexa405.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('ALEXA405')))
        self.pushButton_FWFAM.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('FAM')))
        self.pushButton_FWHEX.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('HEX')))
        self.pushButton_FWAtto590.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('ATTO')))
        self.pushButton_FWCy5.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('CY5')))
        self.pushButton_FWCy55.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.moveFilterWheel('CY55')))
        self.pushButton_homeFW.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.home_component('Filter Wheel')))

        # LED buttons
        self.pushButton_LEDBF.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('FAM')))
        self.pushButton_LEDAlexa405.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('ALEXA405')))
        self.pushButton_LEDFAM.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('FAM')))
        self.pushButton_LEDHEX.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('HEX')))
        self.pushButton_LEDAtto590.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('ATTO')))
        self.pushButton_LEDCy5.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('CY5')))
        self.pushButton_LEDCy55.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOnLED('CY55')))
        self.pushButton_turnOffLEDs.clicked.connect(lambda: self.create_worker_add_threadpool(self.instrument_interface.turnOffLEDs()))

        # scanning and imaging buttons
        self.pushButton_toggleLive.clicked.connect(self.liveImage_toggle)
        self.pushButton_ConfigExposure.clicked.connect(self.loadexposureDialog)
        self.pushButton_SnapAll.clicked.connect(self.snap_BRADX_channels)
        self.pushButton_experimental.clicked.connect(lambda: self.create_worker_add_threadpool(self.map_focal_plane(heater='A')))
        self.pushButton_microwellScan.clicked.connect(self.microwell_scan)
        self.pushButton_A100K_Scan.clicked.connect(self.loadA100KScanDialog)
        self.pushButton_Vantiva_Scan.clicked.connect(lambda: self.create_worker_add_threadpool(self.loadGenericScanDialog(scantype='Vantiva')))
        self.pushButton_Vantiva2x_Scan.clicked.connect(lambda: self.create_worker_add_threadpool(self.loadGenericScanDialog(scantype='Vantiva2x')))

        self.testpb()



        # make inivisble for poster test
        self.listView_test.hide()
        # load GUI
        self.show()



    # -------------------------------------------------------------------
    # ---------------- BEGIN FUNCTIONS/METHODS --------------------------
    # -------------------------------------------------------------------

    # -------------------------------------------------------------------
    # ---------------- test protocol builder functions ------------------
    # -------------------------------------------------------------------
    def testpb(self):
        t1 = testitem()
        self.listWidget_ProtocolBuilder.addItem(t1)

        # LIVE IMAGER
    def get_distance(self, dir):
        if 'y' in dir or 'x' in dir:
            distance = self.lineEdit_moveDistXY.text()
        elif 'z' in dir:
            distance = self.lineEdit_moveDistZ.text()
        else:
            distance = 0
        try:
            distance = float(distance)
            return distance
        except:
            print(distance)
            print('ERROR CONVERTING')

    def moveImager(self, dir):
        if self.config_data['LED_off_to_move']:
            self.instrument_interface.turnOffLED('HEX')
        if 'x' in dir:
            if dir[0] == '-':
                dist = self.get_distance('x')
            else:
                dist = 0 - self.get_distance('x')
            target = [dist, 0, 0, 0]
        elif 'y' in dir:
            if dir[0] == '-':
                dist = self.get_distance('y')
            else:
                dist = 0 - self.get_distance('y')
            target = [0, dist, 0, 0]
        elif 'z' in dir:
            if dir[0] == '-':
                dist = self.get_distance('z')
            else:
                dist = 0 - self.get_distance('z')
            target = [0, 0, dist, 0]
        print(target, type(target))

        self.instrument_interface.moveImager_relative(target)
        if self.config_data['LED_off_to_move']:
            time.sleep(3)
            self.instrument_interface.turnOnLED('HEX', intensity=50)

    def moveImager_PBRS(self, event):
        # Picture Based Repositioning System

        # get x y cursor point
        x_cursor = event.pos().x()
        y_cursor = event.pos().y()
        pt = (x_cursor, y_cursor)

        # get params
        htr = self.comboBox_heater.currentText()
        geom = self.label_testImage.geometry()
        w, h = geom.width(), geom.height()
        x, y = utils.getXY_from_click(pt, (w, h), htr, self.config_data['unit'])

        print(x, y)
        # move to the approximate location
        self.instrument_interface.moveImagerXY([x, y])

    def liveImage_toggle(self):
        if self.live_imaging.isRunning() == False:
            self.live_imaging.stop_imaging = False
            # self.err_msg.setText('Live Imaging Started.')
            self.pushButton_toggleLive.setText('Stop Live')
            self.live_imaging.start()
        else:
            try:
                self.stop_liveImage_thread()
                self.pushButton_toggleLive.setText('Start Live')
                print('finished toggle')
            except Exception as e:
                print(e)


    def stop_liveImage_thread(self):
        if self.live_imaging.isRunning() == True:
            self.live_imaging.running = False
            self.live_imaging.stop_imaging = True
            self.live_imaging.quit()
            self.err_msg.setText('Live Imaging Stopped.')
            self.instrument_interface.turnOffLED('HEX')

    def liveImage_TP_toggle(self):
        update_image = QtCore.pyqtSignal(QtGui.QImage)
        if self.stop_imaging == True:
            pass
        else:
            self.instrument_interface.reader.camcontroller.snap_continuous_prep()
            self.instrument_interface.moveFilterWheel('FAM')
            self.instrument_interface.turnOnLED('HEX', intensity=20) # hex is now bf led
            self.instrument_interface.reader.camcontroller.setExposureTimeMicroseconds(current_exposure['bf'])
            self.pushButton_toggleLive.setText('Stop Live')
        while self.stop_imaging == False:
            if self.debug:
                print('Begin Imaging Loop Thread')
            try:
                time1 = time.time()
                image_result = self.camera.GetNextImage(1000)
                img = image_result.GetNDArray()
                time2 = time.time()
                # convert image to 8-bit for QImage
                img = img / (2**16-1)
                img *= 255
                qimg = QtGui.QImage(img.astype(np.uint8), img.shape[1],img.shape[0], QtGui.QImage.Format_Grayscale8)
                update_image.emit(qimg)
                image_result.Release()
                time3 = time.time()
                if self.debug:
                    print('Got image in {0}\n, displayed in {1}'.format(time2-time1, time3-time2))
                time.sleep(0.001)
            except:
                print('Error: %s' % sys.exc_info()[0])
                return False
        if self.debug:
            print('pre end acquisition')
        img_result = self.camera.GetNextImage(1000)
        img_result.Release()
        self.camera.EndAcquisition()
        if self.debug:
            print('ended acquisition')
        self.pushButton_toggleLive.setText('Start Live')
        self.turnOffLED('HEX')

    def update_display(self, qimg):
        self.display.setPhoto(QtGui.QPixmap.fromImage(qimg))


    def image_selected_channels(self, fdir: str, fname_prefix: str,
        addtl_components=[], loc_meta=None, return_images: bool=False):
        '''generic funciton to image channels and save them with appropriate
            filename. to be used in conjuction with query_and_parse_filename.

        INPUTS:
            fdir: str. the full path of the directory in which we are going to
                save the filename.
            fname_prefix: str. the string that will be prepended to the saved file.
            addtl_components: list. optional argument that will append the
                components of the list to the fdir and fname arguments before
                saving
        OUTPUTS:
            No outputs.
        '''
        if len(addtl_components) > 0:
            # build out additional components to append/prepend to filename and directory
            str_addtl_components = '_'.join(addtl_components)
            fname = '{0}___{1}'.format(fname_prefix, str_addtl_components)

            # print(addtl_components, 'components fname')
        image_these_channels = [label for label, chk_btn in zip(self.fluor_labels, self.fluor_chkbtns) if chk_btn.isChecked()]

        # initialize array for returning images if return_images
        if return_images:
            all_images = np.zeros((len(image_these_channels), 3648, 5472), dtype=np.uint16)

        for chan_num, chan in enumerate(image_these_channels):
            # change exposure to correct exposure
            exp_time_microseconds = current_exposure[chan]
            if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
                try:
                    self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                    self.load_exposure()
                except:
                    msg = 'Could not set exposure.'
                    self.err_msg.setText(msg)
            # IMAGE: move filter wheel, turn on LED, image, turn off LED
            self.instrument_interface.moveFilterWheel(chan)
            time.sleep(self.config_data['motor_LED_delay']) # may not be necessary
            self.instrument_interface.turnOnLED(chan)
            img = self.instrument_interface.captureImage()
            self.instrument_interface.turnOffLED(chan)
            # save image only if we are not returning the images
            if return_images == False:
                str_exp = str(current_exposure[chan] // 1000)
                # BUILD DIRECTORY STRUCTURE
                # ., exp name, heaterlbl, chamber, fov, fname
                if loc_meta != None:
                    # probably using a scanning function, build pathname
                    htrlbl = 'heater{0}'.format(loc_meta['heater'])
                    chmbrlbl = 'chamber{0}'.format(loc_meta['chamber'])
                    fovlbl = 'FOV{0}'.format(loc_meta['colFOV'])
                    scan_fdir = osp.join(fdir, fname_prefix, htrlbl, chmbrlbl, fovlbl)
                    if not osp.isdir(scan_fdir):
                        os.makedirs(scan_fdir)
                    img_fname = "{0}_{1}.tif".format(chan, str_exp)
                    img_fpath = osp.join(scan_fdir, img_fname)
                    tifffile.imwrite(img_fpath, img)
                else:
                    # probably using FOV base
                    img_fname = "{0}___{1}_{2}.tif".format(fname, chan, str_exp)
                    scan_fdir = osp.join(fdir, fname)
                    img_fpath = osp.join(scan_fdir, img_fname)
                    if (img_fpath[0] == ':'):
                        img_fpath = img_fpath[1:]   # Casued OSError
                    if (fdir[0] == ':'):
                        fdir = fdir[1:]             # Casued OSError
                    if not osp.isdir(osp.join(fdir, fname)):
                        os.makedirs(osp.join(fdir, fname))
                    tifffile.imwrite(img_fpath, img)
            else:
                all_images[chan_num] = img
            # scale image for display
            img = img / (2**16)
            img *= 255
            qimg = QtGui.QImage(img.astype(np.uint8), img.shape[1],img.shape[0], QtGui.QImage.Format_Grayscale8)
            self.update_display(qimg)
        # write to file
        x_now, y_now, z_now, fw_now = self.instrument_interface.reader.get_position()
        imager_loc_fname = '{0}.txt'.format(fname)
        imager_loc_pathname = osp.join(scan_fdir, imager_loc_fname)
        if not osp.isdir(scan_fdir):
            os.makedirs(scan_fdir)
        with open(imager_loc_pathname, 'w') as wf:
            wf.write('X,Y,Z,FW\n')
            wf.write('{0},{1},{2},{3}\n'.format(x_now, y_now, z_now, fw_now))
        if return_images:
            return all_images

    def query_and_parse_filename(self):
        '''this should be the general function to get a filename from use and
            parse it for use.
        INPUTS:
            no inputs
        OUTPUTS:
            fdir: str. the full path of the directory in which we are going to
                save the filename.
            fname: str. the string that will be prepended to the saved file.
            '''
        self.stop_liveImage_thread()
        fpath = self.query_filename()
        if fpath == '':
            return None, None
        # NOTE: query filename returns a path using '/' as directory separator,
        # even on windows systems
        fparts = fpath.split('/')
        fname = fparts[-1]
        fname.replace('_', '-') # avoid confusion in path parsing

        fdir = fpath.rstrip(fname)
        if fname == '':
            return
        elif osp.isfile(fpath):
            msg = 'Cannot overwrite file.'
            self.err_msg.setText(msg)
            return
        if not osp.isdir(fdir):
            os.makedirs(fdir)
            # pass
        print(fdir, fname, 'fdir, fname in query_and_parse')
        return fdir, fname

    def snap_BRADX_channels(self):
        self.stop_liveImage_thread()
        fpath = self.query_filename()
        # NOTE: query filename returns a path using '/' as directory separator,
        # even on windows systems
        fparts = fpath.split('/')
        fname = fparts[-1]

        fdir = fpath.rstrip(fname)
        if fname == '':
            return
        elif osp.isfile(fpath):
            msg = 'Cannot overwrite file.'
            self.err_msg.setText(msg)
            return
        if not osp.isdir(fdir):
            # os.makedirs(fdir)
            pass

        image_these_channels = [label for label, chk_btn in zip(self.fluor_labels, self.fluor_chkbtns) if chk_btn.isChecked()]

        for chan in image_these_channels:
            # change exposure
            exp_time_microseconds = current_exposure[chan]
            if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
                try:
                    self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                    self.load_exposure()
                except:
                    msg = 'Could not set exposure.'
                    self.err_msg.setText(msg)
            # move filter wheel
            self.instrument_interface.moveFilterWheel(chan)
            time.sleep(2.5) # may not be necessary
            self.instrument_interface.turnOnLED(chan)
            img = self.instrument_interface.captureImage()
            self.instrument_interface.turnOffLED(chan)
            str_exp = str(current_exposure[chan] // 1000)
            img_fname = "{0}___{1}_{2}.tif".format(fname, chan, str_exp)
            img_fpath = osp.join(fdir, fname, img_fname)
            if (img_fpath[0] == ':'):
                img_fpath = img_fpath[1:]   # Casued OSError
            if (fdir[0] == ':'):
                fdir = fdir[1:]             # Casued OSError
            if not osp.isdir(osp.join(fdir, fname)):
                os.makedirs(osp.join(fdir, fname))
            tifffile.imwrite(img_fpath, img)
            img = img / (2**16)
            img *= 255
            qimg = QtGui.QImage(img.astype(np.uint8), img.shape[1],img.shape[0], QtGui.QImage.Format_Grayscale8)
            self.update_display(qimg)


    def genericScan(self, scantype='Vantiva', heater='C', use_chambers='all', autofocus=True, debug=False,):
        fdir, fname = self.query_and_parse_filename()
        # set parameters
        xconv = self.config_data['motor2mm']['x']
        yconv = self.config_data['motor2mm']['y']
        zconv = self.config_data['motor2mm']['z']
        convmat = np.array((xconv, yconv, zconv)).reshape(1, -1) # convert steps to mm

        Nchambers = 8
        # ncol_FOVS can be calculated based on parameters that should be in a configuration file.
        allowed_scantypes = ['A100K', 'Vantiva', 'Parallel', 'S100K', 'Vantiva2x']
        err_msg = '{0} not in allowed scan types. Use one of {1}'.format(scantype, allowed_scantypes)
        assert scantype in allowed_scantypes, err_msg


        if use_chambers == 'all':
            use_chambers = list(range(Nchambers))
        elif type(use_chambers) == list or type(use_chambers) == np.ndarray:
            if np.max(use_chambers) >= Nchambers:
                raise IndexError('Tried to index chamber 8 with max of 7. Label Chambers starting at 0.')
        elif type(use_chambers) == int:
            use_chambers = [use_chambers]
        else:
            raise TypeError('use_chambers must be one of: \'all\', list of chambers, or integer of single chamber.')

        if scantype in self.config_data['ncol_FOVS']:
            ncol_FOVS = self.config_data['ncol_FOVS'][scantype]

        # if scantype == 'Vantiva':
        #     ncol_FOVS = self.config_data['ncol_FOVS_Vantiva']
        #     # ncol_FOVS = 5
        else:
            # fill in for other chips
            ncol_FOVS = 5


        DOF = 0.1 # mm, Depth of Field

        # import data
        s100k_coords_fname = 'BX375 S100K w Holder Coordinate Mapping Unit D.csv'
        unit = self.config_data['unit']
        coords_fname = 'Unit{0}_{1}_CoordinateMap.csv'.format(unit, scantype)

        err_msg = 'Could not find {0}. Please ensure coordinate map exists before selecting scantype: {1}'.format(coords_fname, scantype)
        assert osp.isfile(coords_fname), err_msg


        data = np.loadtxt(coords_fname, skiprows=1, usecols=(2, 3),
                            delimiter=',', dtype=np.int32)
        # pull out individual heater data
        hA = data[:8, :] #/ convmat
        hB = data[8:16, :] #/ convmat
        hC = data[16:24, :] #/ convmat
        hD = data[24:, :] #/ convmat



        if heater == 'A':
            locdata = hA
        elif heater == 'B':
            locdata = hB
        elif heater == 'C':
            locdata = hC
        elif heater == 'D':
            locdata = hD

        # define corners for navigating
        topleft = (locdata[4, 0], locdata[4, 1])
        topright = (locdata[5, 0], locdata[5, 1])
        botleft = (locdata[6, 0], locdata[6, 1])
        botright = (locdata[7, 0], locdata[7, 1])


        # calculate steps to move between rows and cols
        chamber_delta_y = (botleft[1] - topleft[1]) / (Nchambers - 1)
        chamber_delta_x = (topright[0] - topleft[0]) / (ncol_FOVS - 1) # this will be different on different units. subtract 1 to get spaces

        # loop over rows
        config_dir = osp.join(fdir, fname, 'config')
        config_pathname = osp.join(config_dir, 'unit_config.json')
        if not osp.isdir(config_dir):
            os.makedirs(config_dir)
        shutil.copy('unit_config.json', config_pathname)
        for row, rowlbl in enumerate(range(1, Nchambers+1)):
            # only image rows/chambers that we have specified
            if row in use_chambers:
                pass
            else:
                continue
            # move to row relative to topmost row
            current_row = topleft[1] + chamber_delta_y*row
            start_col = topleft[0]
            # loop over columns needed to image all FOVs
            for colFOV in range(ncol_FOVS):
                # move to col relative to the leftmost col
                current_col = start_col + chamber_delta_x*colFOV
                targetXY = [current_col, current_row]
                self.instrument_interface.moveImagerXY(targetXY)
                if self.config_data['LED_off_to_move']:
                    time.sleep(7) # there could be huge movements, delay to make sure imager gets there
                if autofocus:
                    self.grad_mag_autofocus(debug=debug)
                addtl_components = ['heater{0}'.format(heater), 'chamber{0}'.format(rowlbl), 'colFOV{0}'.format(colFOV)]
                loc_meta = {'instrument': unit, 'heater': heater, 'chamber': rowlbl, 'colFOV': colFOV}
                self.image_selected_channels(fdir, fname, addtl_components, loc_meta)


    def A100KScan(self, heater='C', use_chambers='all', autofocus=False, debug=False):
        fdir, fname = self.query_and_parse_filename()
        # set parameters
        xconv = self.config_data['motor2mm']['x']
        yconv = self.config_data['motor2mm']['y']
        zconv = self.config_data['motor2mm']['z']
        convmat = np.array((xconv, yconv, zconv)).reshape(1, -1) # convert steps to mm

        Nchambers = 8
        # ncol_FOVS can be calculated based on parameters that should be in a configuration file.
        ncol_FOVS = self.config_data['ncol_FOVS']

        if use_chambers == 'all':
            use_chambers = list(range(Nchambers))
        elif type(use_chambers) == list or type(use_chambers) == np.ndarray:
            if np.max(use_chambers) >= Nchambers:
                raise IndexError('Tried to index chamber 8 with max of 7. Label Chambers starting at 0.')
        elif type(use_chambers) == int:
            use_chambers = [use_chambers]
        else:
            raise TypeError('use_chambers must be one of: \'all\', list of chambers, or integer of single chamber.')


        DOF = 0.1 # mm, Depth of Field

        # import data
        s100k_coords_fname = 'BX375 S100K w Holder Coordinate Mapping Unit D.csv'
        unit = self.config_data['unit']
        a100k_coords_fname = 'Unit{0}_A100K_CoordinateMap.csv'.format(unit)
        if osp.isfile(a100k_coords_fname):
            using_a100k_coords = True
        else:
            using_a100k_coords = False

        if using_a100k_coords:
            # use a100k coordinates
            # import A100k data
            data = np.loadtxt(a100k_coords_fname, skiprows=1, usecols=(2, 3),
                              delimiter=',', dtype=np.int32)
            # pull out individual heater data
            hA = data[:8, :] #/ convmat
            hB = data[8:16, :] #/ convmat
            hC = data[16:24, :] #/ convmat
            hD = data[24:, :] #/ convmat
        else:
            # use s100k data instead
            data = np.loadtxt(s100k_coords_fname, skiprows=1, usecols=(1,2,3),
                              delimiter=',', dtype=np.int32)
            # pull out individual heater data
            hA = data[:11, :] #/ convmat
            hB = data[12:23, :] #/ convmat
            hC = data[24:35, :] #/ convmat
            hD = data[36:, :] #/ convmat


        if heater == 'A':
            locdata = hA
        elif heater == 'B':
            locdata = hB
        elif heater == 'C':
            locdata = hC
        elif heater == 'D':
            locdata = hD

        # define corners for navigating
        if using_a100k_coords:
            topleft = (locdata[4, 0], locdata[4, 1])
            topright = (locdata[5, 0], locdata[5, 1])
            botleft = (locdata[6, 0], locdata[6, 1])
            botright = (locdata[7, 0], locdata[7, 1])
        else:
            # using s100k coords
            topleft = (np.max(locdata[:, 0]), np.max(locdata[:, 1]))
            topright = (np.min(locdata[:, 0]), np.max(locdata[:, 1]))
            botleft = (np.max(locdata[:, 0]), np.min(locdata[:, 1]))
            botright = (np.min(locdata[:, 0]), np.min(locdata[:, 1]))


        # calculate steps to move between rows and cols
        chamber_delta_y = (botleft[1] - topleft[1]) / (Nchambers - 1)
        chamber_delta_x = (topright[0] - topleft[0]) / (ncol_FOVS - 1) # this will be different on different units. subtract 1 to get spaces

        # loop over rows
        config_dir = osp.join(fdir, fname, 'config')
        config_pathname = osp.join(config_dir, 'unit_config.json')
        if not osp.isdir(config_dir):
            os.makedirs(config_dir)
        shutil.copy('unit_config.json', config_pathname)
        for row, rowlbl in enumerate(range(1, Nchambers+1)):
            # only image rows/chambers that we have specified
            if row in use_chambers:
                pass
            else:
                continue
            # move to row relative to topmost row
            current_row = topleft[1] + chamber_delta_y*row
            start_col = topleft[0]
            # loop over columns needed to image all FOVs
            for colFOV in range(ncol_FOVS):
                # move to col relative to the leftmost col
                current_col = start_col + chamber_delta_x*colFOV
                targetXY = [current_col, current_row]
                self.instrument_interface.moveImagerXY(targetXY)
                if autofocus:
                    self.grad_mag_autofocus(debug=debug)
                addtl_components = ['heater{0}'.format(heater), 'chamber{0}'.format(rowlbl), 'colFOV{0}'.format(colFOV)]
                loc_meta = {'instrument': unit, 'heater': heater, 'chamber': rowlbl, 'colFOV': colFOV}
                self.image_selected_channels(fdir, fname, addtl_components, loc_meta)


    def microwell_scan(self, heater: str='D', debug: bool=False) -> None:
        # for now assume that we are in focus in the top left corner
        # this is entirely FOV based
        #chamber_delta_y = (botleft[1] - topleft[1]) / 7 # 7 spaces, not 8
        #chamber_delta_x = (topright[0] - topleft[0]) / (ncol_FOVS - 1) # this will be different on different units. subtract 1 to get spaces
        fdir, fname = self.query_and_parse_filename()
        if fname == None:
            return
        x_now, y_now, z_now, fw_now = self.instrument_interface.reader.get_position()
        print(x_now, y_now)
        topleft = (x_now, y_now)
        chamber_delta_x = -7 * 8157 # 7mm x 8157 steps / mm
        chamber_delta_y = -10 * 2604 # 10mm x 2604 steps / mm

        Nrows = 7
        ncol_FOVS = 13
        #Nrows = 2
        #ncol_FOVS = 2
        for row in range(Nrows):
            # only image rows/chambers that we have specified
            # move to row relative to topmost row
            current_row = topleft[1] + chamber_delta_y*row
            start_col = topleft[0]
            # loop over columns needed to image all FOVs
            for colFOV in range(ncol_FOVS):
                # move to col relative to the leftmost col
                current_col = start_col + chamber_delta_x*colFOV
                targetXY = [current_col, current_row]
                print(targetXY)
                self.instrument_interface.moveImagerXY(targetXY)
                self.grad_mag_autofocus(bf_exp=500, debug=debug)
                addtl_components = ['rowFOV{0}'.format(row), 'colFOV{0}'.format(colFOV)]
                print(fdir, fname, addtl_components, 'fdir, fname, addtl components')
                self.image_selected_channels(fdir, fname, addtl_components)


    def map_focal_plane(self, heater: str, bf_exp: int=3000, debug: bool=True) -> None:
        ''' Autofocuses at fiducials and fits a plane to gradient maxima '''
        #
        a100k_coords_fname = 'UnitD_A100K_CoordinateMap.csv' # TODO config file
        ncol_FOVS = 8
        Nchambers = 8
        data = np.loadtxt(a100k_coords_fname, skiprows=1, usecols=(2, 3),
                              delimiter=',', dtype=np.int32)
        # pull out individual heater data
        hA = data[:8, :] #/ convmat
        hB = data[8:16, :] #/ convmat
        hC = data[16:24, :] #/ convmat
        hD = data[24:, :] #/ convmat

        if heater == 'A':
            locdata = hA
        elif heater == 'B':
            locdata = hB
        elif heater == 'C':
            locdata = hC
        elif heater == 'D':
            locdata = hD

        # initialize z-steps through entire z-range of stage
        conv = self.config_data['motor2mm']['z']
        step_size = 15000
        bottom_plane = 300000
        n_steps = 1 + bottom_plane // step_size # 1 + total range / step size
        z_steps = [0]
        for s in range(n_steps-1):
            z_steps.append(-step_size / conv)
        step_values = np.cumsum(z_steps)

        # set up grid to interpolate over
        # calculate steps to move between rows and cols
        topleft = (locdata[4, 0], locdata[4, 1])
        topright = (locdata[5, 0], locdata[5, 1])
        botleft = (locdata[6, 0], locdata[6, 1])
        botright = (locdata[7, 0], locdata[7, 1])
        chamber_delta_y = (botleft[1] - topleft[1]) / (Nchambers - 1) # 7 spaces, not 8
        chamber_delta_x = (topright[0] - topleft[0]) / (ncol_FOVS - 1) # this will be different on different units. subtract 1 to get spaces
        interp_gridx, interp_gridy = np.mgrid[topleft[0]:topright[0]:chamber_delta_x, topleft[1]:botleft[1]:chamber_delta_y]





        # initialize array for storing in-focus z-locations
        corner_zlocs_infocus = np.zeros(4)

        # set up sobel operators
        sx = np.array([[1, 0, -1,], [2, 0, -2], [1, 0, -1]])
        sy = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])

        # initialize exposure for bf imaging
        # exp_time_microseconds = current_exposure['bf'] # maybe include default setting here
        exp_time_microseconds = bf_exp
        if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
            try:
                self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                self.load_exposure()
            except:
                msg = 'Could not set exposure.'
                self.err_msg.setText(msg)

        # move filter wheel for BF imgaing
        self.instrument_interface.moveFilterWheel('fam')

        # begin looping through fiducial marks
        for corner_ind in range(4):
            # go to target corner
            targetXY = locdata[corner_ind, :2]
            self.instrument_interface.moveImagerXY(targetXY)

            # home z-axis
            self.instrument_interface.homeImagerComponent('Z')
            time.sleep(10) # until we can confirm that it is/isn't blocking

            # image the entire z-axis

            ## prep image
            #mask_img = tifffile.imread('a100k_focusmask_topleft.tif')
            #rs, re = np.argmin(mask_img[3648//2, :]), np.argmax(mask_img[3648//2, :])
            #cs, ce = np.argmin(mask_img[:, 5472//2]), np.argmax(mask_img[:, 5472//2])
            cs, ce = 0, 5472
            rs, re = 0, 3648
            #masked_shape = mask_img[rs:re, cs:ce].shape


            #all_imgs = np.zeros((n_steps, *masked_shape), dtype=np.uint8)

            # intialize array where images and grad mags will be stored
            all_imgs = np.zeros((n_steps, re-rs, ce-cs), dtype=np.uint8)
            grad_mags = np.zeros(n_steps)


            # loop through zsteps
            for i, z_loc in enumerate(z_steps):
                # move imager to correct z location
                target = [0, 0, z_loc, 0]
                self.instrument_interface.moveImager_relative(target)

                # take bf image
                self.instrument_interface.turnOnLED('hex', intensity=50)
                img = self.instrument_interface.captureImage()
                self.instrument_interface.turnOffLED('hex')

                img = img[rs:re, cs:ce] / 65408 * 255.0 # convert to uint8
                img = img.astype(np.uint8)
                all_imgs[i, rs:re, cs:ce] = img

                # compute sobel filters with decimation
                gx = fftconvolve(img[::10], sx)
                gy = fftconvolve(img[::10], sy)
                gmag = np.sqrt(gx**2 + gy**2)
                grad_mags[i] = np.sum(gmag)

            # lookup what mm step value had highest gradient,
            current_infocus_z = step_values[np.argmax(grad_mags)]
            corner_zlocs_infocus[corner_ind] = current_infocus_z * conv
            if debug:
                tifffile.imwrite('debug_MapFocalPlane_corner{0}.tif'.format(corner_ind), all_imgs)
                fig, ax = plt.subplots()
                ax.scatter(np.arange(grad_mags.shape[0]), grad_mags)
                plt.savefig('grad_mags_corner{0}.png'.format(corner_ind))
                plt.close('all')

        self.focal_plane = griddata(points=locdata[:4, :2], values=corner_zlocs_infocus, xi=(interp_gridx, interp_gridy), method='linear')
        if debug:
            fig, ax = plt.subplots()
            ax.imshow(self.focal_plane)
            plt.savefig('fitted focal plane')
            plt.show()



        # fit 4 corners to plane


        # for debug
        tifffile.imwrite(osp.join('BX486_a100k_autofocus', 'all_imgs.tif'), all_imgs)




    def grad_mag_autofocus(self, center_guess: float=0, num_steps: int=5,
        step_size: float=0.08, bf_exp: Union[str, int]='default', debug: bool=False) -> float:
        '''software autofocus based on gradient magnitude.
        This function is an automation tool, and will not find an accurate focus
        unless you are very close to the focal plane already.
        INPUTS:
            center_guess: float. best guess of the z displacement to ideal focal
                plane. based on measured focal planes, we may know which
                direction to move the imager, so we want to sample that region
                more than the other.
        OUTPUTS:
            focal_shift: float. number of mm to move '''


        # set up sobel operators
        sx = np.array([[1, 0, -1,], [2, 0, -2], [1, 0, -1]])
        sy = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])


        # set up loop
        # num_steps = 5 # 5 sample images during testing, later 3. must be odd
        # step_size = 0.15 # mm
        # build steps through which we search for focal plane
        # TODO: incorporate center_guess variable
        steps = [-(num_steps-1) // 2 * step_size] # first motion is to bottom of range
        for n in range(num_steps - 1):
            steps.append(step_size) # append remaining steps to step list

        print(steps)

        grad_mags = np.zeros(num_steps) # grad mags will go here
        # set exposure for bf
        # exp_time_microseconds = current_exposure['bf']
        if bf_exp == 'default':
            exp_time_microseconds = 1500 # this is what was used in testing
        else:
            exp_time_microseconds = bf_exp
        if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
            try:
                self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                self.load_exposure()
            except:
                msg = 'Could not set exposure.'
                self.err_msg.setText(msg)
        # move filter wheel for BF imgaing
        self.instrument_interface.moveFilterWheel('fam')
        if debug:
            all_imgs = np.zeros((num_steps, 3648, 5472), dtype=np.uint8)

        # loop through zsteps
        for i, z_loc in enumerate(steps):
            # move imager to correct z location
            target = [0, 0, z_loc, 0]
            self.instrument_interface.moveImager_relative(target)

            # take bf image
            self.instrument_interface.turnOnLED('hex', intensity=50)
            img = self.instrument_interface.captureImage()
            self.instrument_interface.turnOffLED('hex')

            # take grad mag
            img = img / 65408 * 255.0 # convert to uint8
            img = img.astype(np.uint8)
            if debug:
                all_imgs[i, :, :] = img

            # compute sobel filters with decimation
            gx = fftconvolve(img[::10], sx)
            gy = fftconvolve(img[::10], sy)
            gmag = np.sqrt(gx**2 + gy**2)
            grad_mags[i] = np.sum(gmag)

        # calculate optimal focus from grad mag
        # fit gradients to gaussian/curve
        p0 = [1e8, 0, 0.3] # initial guesses
        # set up "x-data" points to feed into curve fitting
        zdata = np.arange(-(num_steps-1) // 2 * step_size,
            (num_steps+1) // 2*step_size, step=step_size)
        # fit gaussian (or parabola? what shape should this be??)
        try:
            popt, _ = optimize.curve_fit(gaussian, zdata, grad_mags, p0=p0)
        except RuntimeError:
            # could not find optimal parameters
            print('COULD NOT FIND OPTIMAL PARAMETERS, JUST GUESSING')
            popt = p0

        # we have a fit, we need to more finely sample our fitting parameters
        # so that we may interpolate the best z-locatio6
        zfit_data = np.linspace(zdata[0], zdata[-1], num=100)
        yfit_data = gaussian(zfit_data, *popt)
        # we will shift to where the grad mag is maximal
        z_shift = zfit_data[np.argmax(yfit_data)]
        # move back to original position
        total_move = np.sum(steps)
        mv_to_orig = -total_move
        target = [0, 0, mv_to_orig, 0]
        self.instrument_interface.moveImager_relative(target)
        if debug:
            # save img stack
            tifffile.imwrite('debug_grad_mag_allimgs.tif', all_imgs)
            # show grad mag plot
            fig, ax = plt.subplots(1, 2)
            ax[0].scatter(zdata, grad_mags)
            ax[1].plot(zfit_data, yfit_data)
            ax[0].set_title('Gradient Magnitudes')
            ax[1].set_title('Fitted Curve to Grad Mags')
            plt.show()
        return z_shift


    def query_filename(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self,
            'QFileDialog.getSaveFileName()',
            '',
            'All Files (*);;Text Files (*.txt)',
            options=options)
        return fpath


    def update_display(self, qimg):
        self.graphicsView_ImagerDisplay.setPhoto(QtGui.QPixmap.fromImage(qimg))

    def load_exposure(self):
        camera_exp_time_us = self.instrument_interface.getExposureTime()
        camera_exp_time_us = int(round(camera_exp_time_us))
        self.lineEdit_exposuretimeus.setText(str(camera_exp_time_us))

    def set_exposure(self):
        exp_time_microseconds = self.lineEdit_exposuretimeus.text()
        # sanitize
        try:
            exp_time_microseconds = int(round(float(exp_time_microseconds)))
        except:
            msg = 'Could not convert to integer.\nPlease enter valid integer.'
            self.err_msg.setText(msg)
            self.load_exposure()
            return
        # TODO: find real min and max exposuretimes
        if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
            try:
                self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                self.load_exposure()
            except:
                msg = 'Could not set exposure.'
                self.err_msg.setText(msg)


    def experimental_acquire_autofocusdata(self):

        conv = self.config_data['motor2mm']['z']
        step_size = 15000
        n_steps = 300000 // step_size # total range / step size
        z_locs = np.arange(-300000, 1, step_size)
        z_steps = [-300000 / conv]
        for s in range(n_steps-1):
            z_steps.append(step_size / conv)

        # set exposure for bf
        # exp_time_microseconds = current_exposure['bf']
        exp_time_microseconds = 500 # this is what was used in testing
        if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
            try:
                self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                self.load_exposure()
            except:
                msg = 'Could not set exposure.'
                self.err_msg.setText(msg)

        # prep image
        mask_img = tifffile.imread('a100k_focusmask_topleft.tif')
        rs, re = np.argmin(mask_img[3648//2, :]), np.argmax(mask_img[3648//2, :])
        cs, ce = np.argmin(mask_img[:, 5472//2]), np.argmax(mask_img[:, 5472//2])
        cs, ce = 1950, 4110
        rs, re = 155, 3492
        masked_shape = mask_img[rs:re, cs:ce].shape

        # move filter wheel for BF imgaing
        self.instrument_interface.moveFilterWheel('fam')
        #all_imgs = np.zeros((n_steps, *masked_shape), dtype=np.uint8)
        all_imgs = np.zeros((n_steps, 3648, 5472), dtype=np.uint16)

        # loop through zsteps
        for i, z_loc in enumerate(z_steps):
            # move imager to correct z location
            target = [0, 0, z_loc, 0]
            self.instrument_interface.moveImager_relative(target)

            # take bf image
            self.instrument_interface.turnOnLED('hex', intensity=50)
            img = self.instrument_interface.captureImage()
            self.instrument_interface.turnOffLED('hex')
            print(img)

            #img = img / 65408 # convert to uint8
            #img = img.astype(np.uint8)
            #all_imgs[i, :, :] = img[rs:re, cs:ce]
            all_imgs[i, :, :] = img

        tifffile.imwrite(osp.join('BX486_a100k_autofocus', 'all_imgs.tif'), all_imgs)






    def experimental_autofocus(self):
        # assume you start in the in focus position, then move to lowest and
        # step up each time to highest location
        n_steps = 21
        step_size = 0.04 # mm
        z_locs_init = -(n_steps//2) * step_size
        z_locs = np.array([step_size for k in range(n_steps)])
        z_locs_in_stepsize = np.array([-(n_steps // 2) + k for k in range(n_steps)])

        target = [0, 0, z_locs_init - step_size, 0]
        self.instrument_interface.moveImager_relative(target, debug=True)
        fname = 'loc1'
        for i, z_loc in enumerate(z_locs):
            # move imager to z location
            target = [0, 0, z_loc, 0]
            print(target)
            self.instrument_interface.moveImager_relative(target, debug=True)

            # Replace with function from snapbradxchannels below this line, but utnil then...

            image_these_channels = [label for label, chk_btn in zip(self.fluor_labels, self.fluor_chkbtns) if chk_btn.isChecked()]

            for chan in image_these_channels:
                # change exposure
                exp_time_microseconds = current_exposure[chan]
                if exp_time_microseconds < 2000000 and exp_time_microseconds > 1:
                    try:
                        self.instrument_interface.setExposureTimeMicroseconds(exp_time_microseconds)
                        self.load_exposure()
                    except:
                        msg = 'Could not set exposure.'
                        self.err_msg.setText(msg)
                # move filter wheel
                if chan == 'bf':
                    self.instrument_interface.moveFilterWheel('fam')
                else:
                    self.instrument_interface.moveFilterWheel(chan)
                time.sleep(0.5) # may not be necessary
                self.instrument_interface.turnOnLED(chan, intensity=100)
                img = self.instrument_interface.captureImage()
                self.instrument_interface.turnOffLED(chan)
                if chan == 'bf':
                    str_exp = str(current_exposure[chan])
                else:
                    str_exp = str(current_exposure[chan] // 1000)
                zlis = z_locs_in_stepsize[i]
                if zlis < 0:
                    str_z = 'n{0}'.format(abs(int(zlis)))
                else:
                    str_z = 'p{0}'.format(abs(int(zlis)))
                img_fname = "{0}_z{3}___{1}_{2}.tif".format(fname, chan, str_exp, str_z.zfill(2))
                img_fpath = osp.join(fname, img_fname)
                if (img_fpath[0] == ':'):
                    img_fpath = img_fpath[1:]   # Casued OSError
                if not osp.isdir(fname):
                    os.makedirs(fname)
                tifffile.imwrite(img_fpath, img)
                img = img / (2**16-1)
                img *= 255
                qimg = QtGui.QImage(img.astype(np.uint8), img.shape[1],img.shape[0], QtGui.QImage.Format_Grayscale8)
                self.update_display(qimg)
            # move back to initial positition
        target = [0, 0, z_locs_init, 0]
        self.instrument_interface.moveImager_relative(target)

    def toggleReaderSubmodule(self, submodule):
        pos = self.instrument_interface.get_pos_reader_submodule(submodule)
        if pos < 0:
            state = 1
        else:
            state = 0
        if len(submodule) > 1: # this is a tray
            self.state_dict['trays'][submodule] = state
            if state == 1:
                self.instrument_interface.open_tray(submodule)
            else:
                self.instrument_interface.close_tray(submodule)
        else: # this is a heater
            self.state_dict['heaters'][submodule] = state
            if state == 1:
                self.instrument_interface.raise_heater(submodule)
            else:
                self.instrument_interface.lower_heater(submodule)


    def autoexposure(self):
        lbls_selected = [label for label, chk_btn in zip(self.fluor_labels, self.fluor_chkbtns) if chk_btn.isChecked()]
        test_images = self.image_these_channels(fdir='delete_this', fname='delete_this', return_images=True)
        for chan_num, chan in enumerate(lbls_selected):
            # check for overexposed areas
            pass
        # reduce/increase exposures iteratively until we find exposures that
        # don't overexpose the image, or until we give up

        # change exposures to optimal values found





    def _init_TCplots(self,):
        # # OLD CODE WE PROLLY DONT NEED ANYMORE
        # scene1 = QtWidgets.QGraphicsScene()
        # view1 = self.graphicsView_dPCR_TC1.setScene(scene1)
        # # make matplotlib figure
        # self.fig1, self.ax1 = plt.subplots()
        # self.ax1.scatter(np.arange(100), np.random.randint(0, 255, size=100))
        # canvas = FigureCanvas(self.fig1)
        # proxy_widget = scene1.addWidget(canvas)
        self.timer_counter += 1
        self.TC_plots = {}
        for i in range(4):
            self.TC_plots[i] = {}
            # get object
            self.TC_plots[i]['gfxView'] = getattr(self, 'graphicsView_dPCR_TC{0}'.format(i+1))
            # initialize scene for display
            self.TC_plots[i]['scene'] = QtWidgets.QGraphicsScene()
            # assign scene to graphicsview
            self.TC_plots[i]['gfxView'].setScene(self.TC_plots[i]['scene'])
            # initialize figure
            self.TC_plots[i]['fig'], self.TC_plots[i]['ax'] = plt.subplots()
            self.TC_plots[i]['fig'].tight_layout()
            # get data
            self.TC_plots[i]['data'] = self.get_TCtemps(i)
            # make figure
            ax = self.TC_plots[i]['ax']
            ax.scatter(np.arange(self.timer_counter), self.TC_plots[i]['data'])
            ax.set_ylabel('Temperature (°C)')
            ax.set_xlabel('Seconds')
            ax.set_position([0, 0, 0.5, 0.5])
            # add figure to scene
            self.TC_plots[i]['scene'].addWidget(FigureCanvas(self.TC_plots[i]['fig']))
            # self.TC_plots[i]['gfxView'].resize(640, 480)
            # self.TC_plots[i]['gfxView'].fitInView(QtCore.QRectF(75, 75, 150, 50))

    def _init_Heaterpositions(self,):
        trays = ['AB', 'CD']
        heaters = ['A', 'B', 'C', 'D']
        pushbtns_t = [self.pushButton_toggleTrayAB, self.pushButton_toggleTrayCD]
        pushbtns_h = [self.pushButton_toggleHeaterA, self.pushButton_toggleHeaterB,
            self.pushButton_toggleHeaterC, self.pushButton_toggleHeaterD]
        for tray, pushbtn in zip(trays, pushbtns_t):
            traypos = self.instrument_interface.get_pos_reader_submodule(tray)
            tray_state = (1 if traypos < 0 else 0)
            self.state_dict['trays'][tray] = tray_state
            if tray_state == 1:
                txt = 'Open Tray {0}'.format(tray)
            else:
                txt = 'Close Tray {0}'.format(tray)
            pushbtn.setText(txt)
        for heater, pushbtn in zip(heaters, pushbtns_h):
            heaterpos = self.instrument_interface.get_pos_reader_submodule(heater)
            heater_state = (1 if heaterpos < 0 else 0)
            self.state_dict['heaters'][heater] = heater_state
            if heater_state < 0:
                txt = 'Raise Heater {0}'.format(heater)
            else:
                txt = 'Lower Heater {0}'.format(heater)
            pushbtn.setText(txt)

    def create_worker_add_threadpool(self, fn, **kwargs):
        ''' Use this function to run basically anything so that it is
        non-blocking for the gui. You must specify the name of all arguments.
        '''
        worker = Worker(fn, **kwargs)
        self.threadpool.start(worker)


    def update_TCplots(self,):
        # we are redrawing the entire figure every time here, we may want to
        # look into "blitting" to save time
        self.timer_counter += 1
        for i in range(4):
            ax = self.TC_plots[i]['ax']
            ax.cla()
            self.TC_plots[i]['data'] = np.append(self.TC_plots[i]['data'], self.get_TCtemps(i))
            ax.scatter(np.arange(self.timer_counter), self.TC_plots[i]['data'])
            ax.set_ylabel('Temperature (°C)')
            ax.set_xlabel('Seconds')
            ax.set_position([0.2, 0.2, 0.5, 0.5])
            self.TC_plots[i]['fig'].canvas.draw_idle()

    def get_TCtemps(self, TC_i):
        # return a random number for now
        return np.random.randint(0, 110)

    def safe_close(self):
        # turn off LEDs
        # tell thermocyclers to room temp
        # self.instrument_interface.turnOffLEDs()
        # for color in ['ALEXA405', 'FAM', 'HEX', 'ATTO', 'CY5', 'CY55']:
        for color in ['HEX']:
            self.instrument_interface.turnOffLED(color)
        self.threadpool.waitForDone(500)


    def closeEvent(self, event):
        # close functions
        print('safe close')
        self.safe_close()
        event.accept()

    def loadexposureDialog(self):
        expD = ExposureDialog()
        expD.exec_()

    def loadA100KScanDialog(self):
        scanD = A100kScanDialog()
        scanD.exec_()
        selections = scanD.collect_selections()
        if selections['proceed_with_imaging'] == True:
            # call a100kscan
            # maybe this is a bit silly, but we'll call a100kscan for every time
            #'fluor_channels': [], 'heaters_enabled': np.zeros(4, dtype=bool),
                # 'which_chambers': np.zeros((4, 8), dtype=bool),
                # 'proceed_with_imaging': self.proceed_with_imaging
            heaters = ['A', 'B', 'C', 'D']
            # update imaging channels
            self.update_image_channels(selections['fluor_channels'])
            for htrNum, htrEnabled in enumerate(selections['heaters_enabled']):
                if htrEnabled:
                    # which chambers is boolean
                    which_chambers = selections['which_chambers'][htrNum, :]
                    # chamber_indices is list of chambers to use
                    chamber_indices = np.arange(8)[which_chambers]
                    print(chamber_indices)
                    # self, heater='C', use_chambers='all', debug=False
                    self.A100KScan(heater=heaters[htrNum],
                        use_chambers=chamber_indices, debug=False)
        else:
            pass

    def loadGenericScanDialog(self, scantype):
        scanD = A100kScanDialog()
        scanD.exec_()
        selections = scanD.collect_selections()
        if selections['proceed_with_imaging'] == True:
            heaters = ['A', 'B', 'C', 'D']
            # update imaging channels
            self.update_image_channels(selections['fluor_channels'])
            for htrNum, htrEnabled in enumerate(selections['heaters_enabled']):
                if htrEnabled:
                    # which chambers is boolean
                    which_chambers = selections['which_chambers'][htrNum, :]
                    # chamber_indices is list of chambers to use
                    chamber_indices = np.arange(8)[which_chambers]
                    print(chamber_indices)
                    # self, heater='C', use_chambers='all', debug=False
                    self.genericScan(scantype=scantype, heater=heaters[htrNum],
                        use_chambers=chamber_indices, debug=False)

    def update_image_channels(self, channels):
        for lbl, chkbtn in zip(self.fluor_labels, self.fluor_chkbtns):
            chkbtn.setChecked(False)
            if lbl in channels:
                chkbtn.setChecked(True)

    # ---------------------
    # ----------TEST FUNCITONS------------
    # -----------------------

    def listitems(self,):
        items = []
        for i in range(self.listWidget_ProtocolBuilder.count()):
            items.append(self.listWidget_ProtocolBuilder.item(i).text())
        print(items)

    def getParameters(self, paramtype=None):
        # this doesn't work yet
        cr = self.listWidget_ProtocolBuilder.currentRow()
        name = self.listWidget_ProtocolBuilder.item(cr)
        print(cr, 'this doesn\'t work yet')

    def getPosMouse(self , event):
        x = event.pos().x()
        y = event.pos().y()
        print(x, y, 'mouse click detected here')
        print(self.comboBox_heater.currentText())





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = CDP2p0_GUI()
    sys.exit(app.exec_())
