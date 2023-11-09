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
