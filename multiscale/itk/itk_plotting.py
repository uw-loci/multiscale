import matplotlib.pyplot as plt
import SimpleITK as sitk
import ipywidgets as widgets
import numpy as np
import matplotlib.ticker as plticker
from IPython.display import display, clear_output

import multiscale.itk.transform as trans
import multiscale.itk.metadata as meta
from multiscale import plotting as myplot


class RegistrationPlot:
        def __init__(self, fixed_image, moving_image, transform=sitk.AffineTransform(2)):
                self.fixed_image = fixed_image
                self.moving_image = moving_image
                self.metric_values = []
                self.idx_resolution_switch = []
                self.fig, (self.ax_img, self.ax_cost) = plt.subplots(1, 2, figsize=(16, 8))
                
                self.ax_img.axis('off')
                self.ax_cost.set_xlabel('Iteration Number', fontsize=12)
                self.ax_cost.set_title('Metric Value', fontsize=12)
                self.ax_cost.set_xlim(0, 1)
                self.ax_cost.set_ylim(-0.1, 0)
                
                loc = plticker.MaxNLocator(integer=True)  # this locator puts ticks at regular intervals
                self.ax_cost.xaxis.set_major_locator(loc)

                self.metric_plot, = self.ax_cost.plot(self.metric_values, 'r')
                self.multires_plot, = self.ax_cost.plot(self.idx_resolution_switch,
                                                        [self.metric_values[index] for index in
                                                         self.idx_resolution_switch],
                                                        'b*')
                self.final_plot, = self.ax_cost.plot([], [], 'g*')
                
                fixed_shape = np.shape(sitk.GetArrayFromImage(fixed_image))
                self.img = self.ax_img.imshow(np.zeros(fixed_shape))
                plot_overlay(self.fixed_image, self.moving_image, transform, continuous_update=True, img=self.img)

        def update_plot(self, new_metric_value, transform):
                """Event: Update and metric_plot new registration values"""
                
                self.metric_values.append(new_metric_value)
                self.metric_plot.set_data(range(len(self.metric_values)), self.metric_values)
                self.multires_plot.set_data(self.idx_resolution_switch,
                                            [self.metric_values[index] for index in self.idx_resolution_switch])
                self.ax_cost.set_xlim(0, len(self.metric_values))
                self.ax_cost.set_ylim(1.05*min(self.metric_values), 0.95*max(self.metric_values))
                
                plot_overlay(self.fixed_image, self.moving_image, transform, continuous_update=True, img=self.img)
        
        def plot_final_overlay(self, transform):
                final_idx = len(self.metric_values) - 1
                self.final_plot.set_data(final_idx, self.metric_values[final_idx])
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                plt.pause(0.01)
                
                print('Registration complete')
                plot_overlay(self.fixed_image, self.moving_image, transform,
                             downsample=False, img=self.img)

        
        def save_figure(self):
                file_path = 'F:\\Research\\Polarimetry\\Animation\\Registration' + str(len(self.metric_values)) + '.png'
                plt.savefig(file_path)
        
        def update_idx_resolution_switch(self):
                new_idx = len(self.metric_values)
                self.idx_resolution_switch.append(new_idx)


def plot_overlay(fixed_image: sitk.Image, moving_image: sitk.Image, transform: sitk.Transform,
                 downsample=True, downsample_target=5, continuous_update=False, img: plt.imshow=None):
                
        rotated_image = sitk.Resample(moving_image, fixed_image, transform,
                                      sitk.sitkLinear, 0.0, moving_image.GetPixelIDValue())
        meta.copy_relevant_metadata(rotated_image, moving_image)
        
        if downsample:
                fixed_shrunk = trans.resize_image(fixed_image, fixed_image.GetSpacing()[0], downsample_target)
                rotated_shrunk = trans.resize_image(rotated_image, fixed_image.GetSpacing()[0], downsample_target)
                spacing = fixed_shrunk.GetSpacing()
                
                overlay_array = overlay_images(fixed_shrunk, rotated_shrunk)
        else:
                spacing = fixed_image.GetSpacing()
                overlay_array = overlay_images(fixed_image, rotated_image)
        
        
        shape = np.shape(overlay_array)
        extent = [0, shape[1]*spacing[1], shape[0]*spacing[0], 0]
        
        if img is None:
                fig, ax = plt.subplots()
                ax.imshow(overlay_array, extent=extent)
        else:
                fig = plt.gcf()
                img.set_data(overlay_array)
                img.set_extent(extent)
        
        # todo: print tranform parameters to title?
        
        if continuous_update:
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.01)
        else:
                plt.show()


def overlay_images(fixed_image: sitk.Image, moving_image: sitk.Image):
        """Create a numpy array that is a combination of two images
        
        Inputs:
        fixed_image -- Image one, using registration nomenclature
        moving_image -- Image two, using registration nomeclature
        alpha -- degree of weighting towards the moving image
        
        Output:
        combined_array -- A numpy array of overlaid images
        """
        
        fixed_array = sitk.GetArrayFromImage(fixed_image)
        fixed_windowed = myplot.auto_window_level(fixed_array)
        
        if fixed_image.GetSize() == moving_image.GetSize():
                moving_array = sitk.GetArrayFromImage(moving_image)
                moving_windowed = myplot.auto_window_level(moving_array)
        
        else: #Pre-registration
                initial_transform = sitk.Similarity2DTransform()
                moving_resampled = sitk.Resample(moving_image, fixed_image,
                                                 initial_transform, sitk.sitkLinear,
                                                 0.0, moving_image.GetPixelID())
                
                moving_array = sitk.GetArrayFromImage(moving_resampled)
                moving_windowed = myplot.auto_window_level(moving_array)

        
        # todo: Some form of window/level to get the intensities roughly matched
        
        combined_array = myplot.overlay_arrays_red_green(
                fixed_windowed, moving_windowed)
        
        return combined_array


class OverlayWidget(object):
        def __init__(self):
                return
        
        def temp(self):
                return
        

class MultiImageDisplay(object):
        """
        Class for displaying multiple images side by side, with sliders, in Ipython. Adapted from SimpleITK notebooks gui.py
        https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/gui.py
        """
        def __init__(self, image_list, axis=0, shared_slider=False, title_list=None, window_level_list=None,
                     figure_size=(9, 6), horizontal=True):
                self.get_window_level_numpy_array(image_list, window_level_list)
                if title_list:
                        if len(image_list) != len(title_list):
                                raise ValueError('Title list and image list lengths do not match')
                        self.title_list = list(title_list)
                else:
                        self.title_list = [''] * len(image_list)
                
                # Our dynamic slice, based on the axis the user specifies
                self.slc = [slice(None)] * 3
                self.axis = axis
                
                ui = self.create_ui(shared_slider)
                display(ui)
                
                # Create a figure.
                col_num, row_num = (len(image_list), 1) if horizontal else (1, len(image_list))
                self.fig, self.axes = plt.subplots(row_num, col_num, figsize=figure_size)
                if len(image_list) == 1:
                        self.axes = [self.axes]
                
                # Display the data and the controls, first time we display the image is outside the "update_display" method
                # as that method relies on the previous zoom factor which doesn't exist yet.
                for ax, npa, slider, min_intensity, max_intensity in zip(self.axes, self.npa_list, self.slider_list,
                                                                         self.min_intensity_list, self.max_intensity_list):
                        self.slc[self.axis] = slice(slider.value, slider.value + 1)
                        # Need to use squeeze to collapse degenerate dimension (e.g. RGB image size 124 124 1 3)
                        ax.imshow(np.squeeze(npa[tuple(self.slc)]),
                                  cmap=plt.cm.Greys_r,
                                  vmin=min_intensity,
                                  vmax=max_intensity)
                self.update_display()
                plt.tight_layout()
        
        def create_ui(self, shared_slider):
                # Create the active UI components. Height and width are specified in 'em' units. This is
                # a html size specification, size relative to current font size.
                ui = None
                
                if shared_slider:
                        # Validate that all the images have the same size along the axis which we scroll through
                        sz = self.npa_list[0].shape[self.axis]
                        for npa in self.npa_list:
                                if npa.shape[self.axis] != sz:
                                        raise ValueError(
                                                'Not all images have the same size along the specified axis, cannot share slider.')
                        
                        slider = widgets.IntSlider(description='image slice:',
                                                   min=0,
                                                   max=sz - 1,
                                                   step=1,
                                                   value=int((sz - 1) / 2),
                                                   width='20em')
                        slider.observe(self.on_slice_slider_value_change, names='value')
                        self.slider_list = [slider] * len(self.npa_list)
                        ui = widgets.Box(padding=7, children=[slider])
                else:
                        self.slider_list = []
                        for npa in self.npa_list:
                                slider = widgets.IntSlider(description='image slice:',
                                                           min=0,
                                                           max=npa.shape[self.axis] - 1,
                                                           step=1,
                                                           value=int((npa.shape[self.axis] - 1) / 2),
                                                           width='20em')
                                slider.observe(self.on_slice_slider_value_change, names='value')
                                self.slider_list.append(slider)
                        ui = widgets.Box(padding=7, children=self.slider_list)
                return ui
        
        def get_window_level_numpy_array(self, image_list, window_level_list):
                # Using GetArray and not GetArrayView because we don't keep references
                # to the original images. If they are deleted outside the view would become
                # invalid, so we use a copy wich guarentees that the gui is consistent.
                self.npa_list = list(map(sitk.GetArrayFromImage, image_list))
                if not window_level_list:
                        self.min_intensity_list = list(map(np.min, self.npa_list))
                        self.max_intensity_list = list(map(np.max, self.npa_list))
                else:
                        self.min_intensity_list = list(map(lambda x: x[1] - x[0] / 2.0, window_level_list))
                        self.max_intensity_list = list(map(lambda x: x[1] + x[0] / 2.0, window_level_list))
        
        def on_slice_slider_value_change(self, change):
                self.update_display()
        
        def update_display(self):
                # Draw the image(s)
                for ax, npa, title, slider, min_intensity, max_intensity in zip(self.axes, self.npa_list, self.title_list,
                                                                                self.slider_list, self.min_intensity_list,
                                                                                self.max_intensity_list):
                        # We want to keep the zoom factor which was set prior to display, so we log it before
                        # clearing the axes.
                        xlim = ax.get_xlim()
                        ylim = ax.get_ylim()
                        
                        self.slc[self.axis] = slice(slider.value, slider.value + 1)
                        ax.clear()
                        # Need to use squeeze to collapse degenerate dimension (e.g. RGB image size 124 124 1 3)
                        ax.imshow(np.squeeze(npa[tuple(self.slc)]),
                                  cmap=plt.cm.Greys_r,
                                  vmin=min_intensity,
                                  vmax=max_intensity)
                        ax.set_title(title)
                        ax.set_axis_off()
                        
                        # Set the zoom factor back to what it was before we cleared the axes, and rendered our data.
                        ax.set_xlim(xlim)
                        ax.set_ylim(ylim)
                
                self.fig.canvas.draw_idle()

# Copied from gui.py in SimpleITK notebooks
class RegistrationPointDataAcquisition(object):
        """
        This class provides a GUI for localizing corresponding points in two images, and for evaluating registration results using a linked cursor
        approach, user clicks in one image and the corresponding point is added to the other image.
        """
        
        def __init__(self, fixed_image, moving_image, fixed_window_level=None, moving_window_level=None,
                     figure_size=(9, 6), known_transformation=None):
                self.fixed_image = fixed_image
                self.fixed_npa, self.fixed_min_intensity, self.fixed_max_intensity = self.get_window_level_numpy_array(
                        self.fixed_image, fixed_window_level)
                self.moving_image = moving_image
                self.moving_npa, self.moving_min_intensity, self.moving_max_intensity = self.get_window_level_numpy_array(
                        self.moving_image, moving_window_level)
                self.fixed_point_indexes = []
                self.moving_point_indexes = []
                self.click_history = []  # Keep a history of user point localizations, enabling undo of last localization.
                self.known_transformation = known_transformation  # If the transformation is valid (not None) then corresponding points are automatically added.
                self.text_and_marker_color = 'red'
                
                ui = self.create_ui()
                display(ui)
                
                # Create a figure with two axes for the fixed and moving images.
                self.fig, axes = plt.subplots(1, 2, figsize=figure_size)
                # self.fig.canvas.set_window_title('Registration Points Acquisition')
                self.fixed_axes = axes[0]
                self.moving_axes = axes[1]
                # Connect the mouse button press to the canvas (__call__ method is the invoked callback).
                self.fig.canvas.mpl_connect('button_press_event', self)
                
                # Display the data and the controls, first time we display the images is outside the "update_display" method
                # as that method relies on the previous zoom factor which doesn't exist yet.
                self.fixed_axes.imshow(self.fixed_npa[self.fixed_slider.value, :, :],
                                       cmap=plt.cm.Greys_r,
                                       vmin=self.fixed_min_intensity,
                                       vmax=self.fixed_max_intensity)
                self.moving_axes.imshow(self.moving_npa[self.moving_slider.value, :, :],
                                        cmap=plt.cm.Greys_r,
                                        vmin=self.moving_min_intensity,
                                        vmax=self.moving_max_intensity)
                self.update_display()
        
        def create_ui(self):
                # Create the active UI components. Height and width are specified in 'em' units. This is
                # a html size specification, size relative to current font size.
                self.viewing_checkbox = widgets.RadioButtons(description='Interaction mode:',
                                                             options=['edit', 'view'],
                                                             value='edit')
                
                self.clearlast_button = widgets.Button(description='Clear Last',
                                                       width='7em',
                                                       height='3em')
                self.clearlast_button.on_click(self.clear_last)
                
                self.clearall_button = widgets.Button(description='Clear All',
                                                      width='7em',
                                                      height='3em')
                self.clearall_button.on_click(self.clear_all)
                
                self.fixed_slider = widgets.IntSlider(description='fixed image z slice:',
                                                      min=0,
                                                      max=self.fixed_npa.shape[0] - 1,
                                                      step=1,
                                                      value=int((self.fixed_npa.shape[0] - 1) / 2),
                                                      width='20em')
                self.fixed_slider.observe(self.on_slice_slider_value_change, names='value')
                
                self.moving_slider = widgets.IntSlider(description='moving image z slice:',
                                                       min=0,
                                                       max=self.moving_npa.shape[0] - 1,
                                                       step=1,
                                                       value=int((self.moving_npa.shape[0] - 1) / 2),
                                                       width='19em')
                self.moving_slider.observe(self.on_slice_slider_value_change, names='value')
                
                # Layout of UI components. This is pure ugliness because we are not using a UI toolkit. Layout is done
                # using the box widget and padding so that the visible UI components are spaced nicely.
                bx0 = widgets.Box(padding=7, children=[self.fixed_slider, self.moving_slider])
                bx1 = widgets.Box(padding=7, children=[self.viewing_checkbox])
                bx2 = widgets.Box(padding=15, children=[self.clearlast_button])
                bx3 = widgets.Box(padding=15, children=[self.clearall_button])
                return widgets.HBox(children=[widgets.HBox(children=[bx1, bx2, bx3]), bx0])
        
        def get_window_level_numpy_array(self, image, window_level):
                """
                Get the numpy array representation of the image and the min and max of the intensities
                used for display.
                """
                npa = sitk.GetArrayViewFromImage(image)
                if not window_level:
                        return npa, npa.min(), npa.max()
                else:
                        return npa, window_level[1] - window_level[0] / 2.0, window_level[1] + window_level[0] / 2.0
        
        def on_slice_slider_value_change(self, change):
                self.update_display()
        
        def update_display(self):
                """
                Display the two images based on the slider values and the points which are on the
                displayed slices.
                """
                # We want to keep the zoom factor which was set prior to display, so we log it before
                # clearing the axes.
                fixed_xlim = self.fixed_axes.get_xlim()
                fixed_ylim = self.fixed_axes.get_ylim()
                moving_xlim = self.moving_axes.get_xlim()
                moving_ylim = self.moving_axes.get_ylim()
                
                # Draw the fixed image in the first subplot and the localized points.
                self.fixed_axes.clear()
                self.fixed_axes.imshow(self.fixed_npa[self.fixed_slider.value, :, :],
                                       cmap=plt.cm.Greys_r,
                                       vmin=self.fixed_min_intensity,
                                       vmax=self.fixed_max_intensity)
                # Positioning the text is a bit tricky, we position relative to the data coordinate system, but we
                # want to specify the shift in pixels as we are dealing with display. We therefore (a) get the data
                # point in the display coordinate system in pixel units (b) modify the point using pixel offset and
                # transform back to the data coordinate system for display.
                text_x_offset = -10
                text_y_offset = -10
                for i, pnt in enumerate(self.fixed_point_indexes):
                        if pnt[2] == self.fixed_slider.value:
                                self.fixed_axes.scatter(pnt[0], pnt[1], s=90, marker='+',
                                                        color=self.text_and_marker_color)
                                # Get point in pixels.
                                text_in_data_coords = self.fixed_axes.transData.transform([pnt[0], pnt[1]])
                                # Offset in pixels and get in data coordinates.
                                text_in_data_coords = self.fixed_axes.transData.inverted().transform((
                                                                                                     text_in_data_coords[
                                                                                                             0] + text_x_offset,
                                                                                                     text_in_data_coords[
                                                                                                             1] + text_y_offset))
                                self.fixed_axes.text(text_in_data_coords[0], text_in_data_coords[1], str(i),
                                                     color=self.text_and_marker_color)
                self.fixed_axes.set_title('fixed image - localized {0} points'.format(len(self.fixed_point_indexes)))
                self.fixed_axes.set_axis_off()
                
                # Draw the moving image in the second subplot and the localized points.
                self.moving_axes.clear()
                self.moving_axes.imshow(self.moving_npa[self.moving_slider.value, :, :],
                                        cmap=plt.cm.Greys_r,
                                        vmin=self.moving_min_intensity,
                                        vmax=self.moving_max_intensity)
                for i, pnt in enumerate(self.moving_point_indexes):
                        if pnt[2] == self.moving_slider.value:
                                self.moving_axes.scatter(pnt[0], pnt[1], s=90, marker='+',
                                                         color=self.text_and_marker_color)
                                text_in_data_coords = self.moving_axes.transData.transform([pnt[0], pnt[1]])
                                text_in_data_coords = self.moving_axes.transData.inverted().transform((
                                                                                                      text_in_data_coords[
                                                                                                              0] + text_x_offset,
                                                                                                      text_in_data_coords[
                                                                                                              1] + text_y_offset))
                                self.moving_axes.text(text_in_data_coords[0], text_in_data_coords[1], str(i),
                                                      color=self.text_and_marker_color)
                self.moving_axes.set_title('moving image - localized {0} points'.format(len(self.moving_point_indexes)))
                self.moving_axes.set_axis_off()
                
                # Set the zoom factor back to what it was before we cleared the axes, and rendered our data.
                self.fixed_axes.set_xlim(fixed_xlim)
                self.fixed_axes.set_ylim(fixed_ylim)
                self.moving_axes.set_xlim(moving_xlim)
                self.moving_axes.set_ylim(moving_ylim)
                
                self.fig.canvas.draw_idle()
        
        def clear_all(self, button):
                """
                Get rid of all the data.
                """
                del self.fixed_point_indexes[:]
                del self.moving_point_indexes[:]
                del self.click_history[:]
                self.update_display()
        
        def clear_last(self, button):
                """
                Remove last point or point-pair addition (depends on whether the interface is used for localizing point pairs or
                evaluation of registration).
                """
                if self.click_history:
                        if self.known_transformation:
                                self.click_history.pop().pop()
                        self.click_history.pop().pop()
                        self.update_display()
        
        def get_points(self):
                """
                Get the points in the image coordinate systems.
                """
                if (len(self.fixed_point_indexes) != len(self.moving_point_indexes)):
                        raise Exception('Number of localized points in fixed and moving images does not match.')
                fixed_point_list = [self.fixed_image.TransformContinuousIndexToPhysicalPoint(pnt) for pnt in
                                    self.fixed_point_indexes]
                moving_point_list = [self.moving_image.TransformContinuousIndexToPhysicalPoint(pnt) for pnt in
                                     self.moving_point_indexes]
                return fixed_point_list, moving_point_list
        
        def __call__(self, event):
                """
                Callback invoked when the user clicks inside the figure.
                """
                # We add points only in 'edit' mode. If the spatial transformation between the two images is known, self.known_transformation was set,
                # then every button_press_event will generate a point in each of the images. Finally, we enforce that all points have a corresponding
                # point in the other image by not allowing the user to add multiple points in the same image, they have to add points by switching between
                # the two images.
                if self.viewing_checkbox.value == 'edit':
                        if event.inaxes == self.fixed_axes:
                                if len(self.fixed_point_indexes) - len(self.moving_point_indexes) <= 0:
                                        self.fixed_point_indexes.append(
                                                (event.xdata, event.ydata, self.fixed_slider.value))
                                        self.click_history.append(self.fixed_point_indexes)
                                        if self.known_transformation:
                                                moving_point_physical = self.known_transformation.TransformPoint(
                                                        self.fixed_image.TransformContinuousIndexToPhysicalPoint(
                                                                self.fixed_point_indexes[-1]))
                                                moving_point_indexes = self.moving_image.TransformPhysicalPointToIndex(
                                                        moving_point_physical)
                                                self.moving_point_indexes.append(moving_point_indexes)
                                                self.click_history.append(self.moving_point_indexes)
                                                if self.moving_slider.max >= moving_point_indexes[
                                                        2] and self.moving_slider.min <= moving_point_indexes[2]:
                                                        self.moving_slider.value = moving_point_indexes[2]
                                        self.update_display()
                        if event.inaxes == self.moving_axes:
                                if len(self.moving_point_indexes) - len(self.fixed_point_indexes) <= 0:
                                        self.moving_point_indexes.append(
                                                (event.xdata, event.ydata, self.moving_slider.value))
                                        self.click_history.append(self.moving_point_indexes)
                                        if self.known_transformation:
                                                inverse_transform = self.known_transformation.GetInverse()
                                                fixed_point_physical = inverse_transform.TransformPoint(
                                                        self.moving_image.TransformContinuousIndexToPhysicalPoint(
                                                                self.moving_point_indexes[-1]))
                                                fixed_point_indexes = self.fixed_image.TransformPhysicalPointToIndex(
                                                        fixed_point_physical)
                                                self.fixed_point_indexes.append(fixed_point_indexes)
                                                self.click_history.append(self.fixed_point_indexes)
                                                if self.fixed_slider.max >= fixed_point_indexes[
                                                        2] and self.fixed_slider.min <= fixed_point_indexes[2]:
                                                        self.fixed_slider.value = fixed_point_indexes[2]
                                        self.update_display()

