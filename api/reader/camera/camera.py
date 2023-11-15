
# Version: Test
try:
    import PySpin as pyspin
except:
    print("Need to pip install PySpin with the whl file, talk to D. Baur or G. Lopez-Candales")
import numpy

try:
    from api.util.logger import Logger
except:
    class Logger:
        def __init__(self, current_python_file_path, current_function_name_called, output_file_name=None):
            a = 1
        def log(self, message_type, message):
            a = 1

class CamController(object):
    def __init__(self):
        self.system = pyspin.System.GetInstance()
        # Retrieve list of cameras from the system
        self.cam_list = self.system.GetCameras()
        self.num_cameras = self.cam_list.GetSize()

        # Finish if there are no cameras
        if self.num_cameras == 0:

            # Clear camera list before releasing system
            self.cam_list.Clear()

            # Release system instance
            self.system.ReleaseInstance()
            logger = Logger(__file__, __name__)
            error_msg = 'No cameras detected! Please check that the camera is\n'
            '1) The camera is plugged into a USB3.0 port on the machine.\n'
            '2) The camera is not in use by another program eg SpinView.'
            logger.log('ERROR', error_msg)

            return False
        self.camera = self.cam_list[0]

        self.nodemap_tldevice = self.camera.GetTLDeviceNodeMap()
        self.camera.Init()
        self.nodemap = self.camera.GetNodeMap()

        # set to default exposure time, 50ms
        self.setExposureTimeMicroseconds(exp_time_microseconds=50000)
        self.set_pixelformat(format='Mono16')
        self.set_gain(gain=15.0)
        self.GammaEnabled = False

        result = True
        result &= self.print_device_info()




    def close(self):
        self.camera.DeInit()
        del self.camera
        self.cam_list.Clear()
        self.system.ReleaseInstance()



    def print_device_info(self):
        """
        This function prints the device information of the camera from the transport
        layer; please see NodeMapInfo example for more in-depth comments on printing
        device information from the nodemap.

        :param nodemap: Transport layer device nodemap.
        :type nodemap: INodeMap
        :returns: True if successful, False otherwise.
        :rtype: bool
        """

        #print('*** DEVICE INFORMATION ***\n')
        logger = Logger(__file__, __name__)
        logger.log('LOG-START', "Getting camera device information.")

        try:
            result = True
            node_device_information = pyspin.CCategoryPtr(self.nodemap.GetNode('DeviceInformation'))

            if pyspin.IsAvailable(node_device_information) and pyspin.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                for feature in features:
                    node_feature = pyspin.CValuePtr(feature)
                    print('%s: %s' % (node_feature.GetName(),
                                      node_feature.ToString() if pyspin.IsReadable(node_feature) else 'Node not readable'))

            else:
                logger.log('MESSAGE', "Device control information not available.")
                #print('Device control information not available.')

        except pyspin.SpinnakerException as ex:
            logger.log('ERROR', '%s' % ex)
            #print('Error: %s' % ex)
            return False

        return result

    def snap_single(self):
        self.sNodemap = self.camera.GetTLStreamNodeMap()
        logger = Logger(__file__, __name__)

        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = pyspin.CEnumerationPtr(self.sNodemap.GetNode('StreamBufferHandlingMode'))
        if not pyspin.IsAvailable(node_bufferhandling_mode) or not pyspin.IsWritable(node_bufferhandling_mode):
            #print('Unable to set stream buffer handling mode.. Aborting...')
            logger.log('ERROR', "Unable to set stream buffer handling mode.. Aborting...")
            return False

        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not pyspin.IsAvailable(node_newestonly) or not pyspin.IsReadable(node_newestonly):
            #print('Unable to set stream buffer handling mode.. Aborting...')
            logger.log('ERROR', "Unable to set stream buffer handling mode.. Aborting...")
            return False

        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        try:
            node_acquisition_mode = pyspin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
            if not pyspin.IsAvailable(node_acquisition_mode) or not pyspin.IsWritable(node_acquisition_mode):
                #print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                logger.log('ERROR', "Unable to set acquisition mode to continuous (enum retrieval). Aborting...")
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_singleframe = node_acquisition_mode.GetEntryByName('SingleFrame')
            if not pyspin.IsAvailable(node_acquisition_mode_singleframe) or not pyspin.IsReadable(
                    node_acquisition_mode_singleframe):
                #print('Unable to set acquisition mode to singleframe (entry retrieval). Aborting...')
                logger.log('ERROR', "Unable to set acquisition mode to singleframe (entry retrieval). Aborting...")
                return False

            # Retrieve integer value from entry node
            acquisition_mode_singleframe = node_acquisition_mode_singleframe.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_singleframe)

            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.camera.BeginAcquisition()
            print('a')
            image_result = self.camera.GetNextImage(6000)
            print('b')
            img = image_result.GetNDArray()
            print('c')
            image_result.Release()
            self.camera.EndAcquisition()
            print('d')
        except pyspin.SpinnakerException as ex:
            #print('Error: %s' % ex)
            logger.log('ERROR', '%s' % ex)
            return False

        return img

    def snap_continuous_prep(self):
        self.sNodemap = self.camera.GetTLStreamNodeMap()

        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = pyspin.CEnumerationPtr(self.sNodemap.GetNode('StreamBufferHandlingMode'))
        if not pyspin.IsAvailable(node_bufferhandling_mode) or not pyspin.IsWritable(node_bufferhandling_mode):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not pyspin.IsAvailable(node_newestonly) or not pyspin.IsReadable(node_newestonly):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False

        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        try:
            node_acquisition_mode = pyspin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
            if not pyspin.IsAvailable(node_acquisition_mode) or not pyspin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not pyspin.IsAvailable(node_acquisition_mode_continuous) or not pyspin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.camera.BeginAcquisition()
        except pyspin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return True

    def snap_continuous_cleanup(self):
            self.cam.EndAcquisition()


    def setExposureTimeMicroseconds(self, exp_time_microseconds=50000):
        max_exp = self.camera.ExposureTime.GetMax()
        min_exp = 100
        msg = 'Requested exposure {0} outside of bounds:\nLow:{1}\nHigh{2}'.format(exp_time_microseconds, min, max_exp)
        assert min_exp < exp_time_microseconds < max_exp, msg
        try:
            result = True
            # Turn off automatic exposure mode
            #
            # *** NOTES ***
            # Automatic exposure prevents the manual configuration of exposure
            # times and needs to be turned off for this example. Enumerations
            # representing entry nodes have been added to QuickSpin. This allows
            # for the much easier setting of enumeration nodes to new values.
            #
            # The naming convention of QuickSpin enums is the name of the
            # enumeration node followed by an underscore and the symbolic of
            # the entry node. Selecting "Off" on the "ExposureAuto" node is
            # thus named "ExposureAuto_Off".
            #
            # *** LATER ***
            # Exposure time can be set automatically or manually as needed. This
            # example turns automatic exposure off to set it manually and back
            # on to return the camera to its default state.

            if self.camera.ExposureAuto.GetAccessMode() != pyspin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False

            self.camera.ExposureAuto.SetValue(pyspin.ExposureAuto_Off)

            # Set exposure time manually; exposure time recorded in microseconds
            #
            # *** NOTES ***
            # Notice that the node is checked for availability and writability
            # prior to the setting of the node. In QuickSpin, availability and
            # writability are ensured by checking the access mode.
            #
            # Further, it is ensured that the desired exposure time does not exceed
            # the maximum. Exposure time is counted in microseconds - this can be
            # found out either by retrieving the unit with the GetUnit() method or
            # by checking SpinView.

            if self.camera.ExposureTime.GetAccessMode() != pyspin.RW:
                print('Unable to set exposure time. Aborting...')
                return False

            # Ensure desired exposure time does not exceed the maximum
            exp_time_microseconds = min(max_exp, exp_time_microseconds)
            exp_time_microseconds = max(min_exp, exp_time_microseconds)
            self.camera.ExposureTime.SetValue(exp_time_microseconds)

        except pyspin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def getExposureTime(self):
        exp_time_node = pyspin.CFloatPtr(self.camera.ExposureTime)
        return exp_time_node.GetValue()

    def set_gain(self, gain):
        node_gainauto = pyspin.CEnumerationPtr(self.nodemap.GetNode('GainAuto'))
        if pyspin.IsAvailable(node_gainauto) and pyspin.IsWritable(node_gainauto):

            # Retrieve the desired entry node from the enumeration node
            node_gainauto_requested = pyspin.CEnumEntryPtr(node_gainauto.GetEntryByName('Off'))
            if pyspin.IsAvailable(node_gainauto_requested) and pyspin.IsReadable(node_gainauto_requested):

                # Retrieve the integer value from the entry node
                gainauto_requested = node_gainauto_requested.GetValue()

                # Set integer as new value for enumeration node
                node_gainauto.SetIntValue(gainauto_requested)
        node_gain = pyspin.CFloatPtr(self.nodemap.GetNode('Gain'))
        if not pyspin.IsAvailable(node_gain) or not pyspin.IsWritable(node_gain):
            print('\nUnable to set Exposure Time (float retrieval). Aborting...\n')
            return False

        node_gain.SetValue(gain)


    def set_pixelformat(self, format='Mono16'):
        allowed_pixel_formats = ['Mono8', 'Mono16']
        msg = 'Please ensure that your requested pixel format is one of: {0}'
        assert format in allowed_pixel_formats, msg.format(', '.join(allowed_pixel_formats))
        try:
            result = True

            # Apply pixel format
            #
            # *** NOTES ***
            # Enumeration nodes are slightly more complicated to set than other
            # nodes. This is because setting an enumeration node requires working
            # with two nodes instead of the usual one.
            #
            # As such, there are a number of steps to setting an enumeration node:
            # retrieve the enumeration node from the nodemap, retrieve the desired
            # entry node from the enumeration node, retrieve the integer value from
            # the entry node, and set the new value of the enumeration node with
            # the integer value from the entry node.
            #
            # Retrieve the enumeration node from the nodemap
            node_pixel_format = pyspin.CEnumerationPtr(self.nodemap.GetNode('PixelFormat'))
            if pyspin.IsAvailable(node_pixel_format) and pyspin.IsWritable(node_pixel_format):

                # Retrieve the desired entry node from the enumeration node
                node_pixel_format_requested = pyspin.CEnumEntryPtr(node_pixel_format.GetEntryByName(format))
                if pyspin.IsAvailable(node_pixel_format_requested) and pyspin.IsReadable(node_pixel_format_requested):

                    # Retrieve the integer value from the entry node
                    pixel_format_requested = node_pixel_format_requested.GetValue()

                    # Set integer as new value for enumeration node
                    node_pixel_format.SetIntValue(pixel_format_requested)

                else:
                    print('Pixel format {0} not available...'.format(format))

            else:
                print('Pixel format not available...')
        except pyspin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False


if __name__ == "__main__":
    cc = CamController()
    img = cc.snap_single()
    print(img.shape)
    cc.close()
