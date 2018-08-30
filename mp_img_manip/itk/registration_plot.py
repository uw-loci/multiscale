import matplotlib.pyplot as plt
import SimpleITK as sitk
import mp_img_manip.itk.process as proc
import numpy as np
import matplotlib.ticker as plticker


class RegistrationPlot:
    def __init__(self, start_metric_value, fixed_image, moving_image, transform):
        self.metric_values = [start_metric_value]
        self.idx_resolution_switch = [0]
        self.fig, (self.ax_img, self.ax_cost) = plt.subplots(1, 2)

        self.fig.set_size_inches(16, 8)

        self.ax_img.axis('off')

        self.ax_cost.set_xlabel('Iteration Number', fontsize=12)
        self.ax_cost.set_title('Metric Value', fontsize=12)
        self.ax_cost.set_xlim(0, 1)
        self.ax_cost.set_ylim(start_metric_value*2, 0)

        loc = plticker.MultipleLocator(base=1.0)  # this locator puts ticks at regular intervals
        self.ax_cost.xaxis.set_major_locator(loc)

        moving_transformed = sitk.Resample(moving_image, fixed_image, transform,
                                           sitk.sitkLinear, 0.0,
                                           moving_image.GetPixelIDValue())
        combined_array = proc.overlay_images(fixed_image, moving_transformed)

        self.img = self.ax_img.imshow(combined_array)

        self.plot, = self.ax_cost.plot(self.metric_values, 'r')
        self.plot_multires, = self.ax_cost.plot(self.idx_resolution_switch,
                                                [self.metric_values[index] for index in self.idx_resolution_switch],
                                                'b*')

    def update_plot(self, new_metric_value, fixed_image, moving_image, transform):
        """Event: Update and plot new registration values"""

        self.metric_values.append(new_metric_value)
        self.plot.set_data(range(len(self.metric_values)), self.metric_values)
        self.ax_cost.set_xlim(0, len(self.metric_values))
        self.ax_cost.set_ylim(2*min(self.metric_values), 0)

        moving_transformed = sitk.Resample(moving_image, fixed_image, transform,
                                           sitk.sitkLinear, 0.0,
                                           moving_image.GetPixelIDValue())

        # Blend the registered and fixed images
        combined_array = proc.overlay_images(fixed_image, moving_transformed)
        self.img.set_data(combined_array)

        asp = np.diff(self.ax_cost.get_xlim())[0] / np.diff(self.ax_cost.get_ylim())[0]
        self.ax_cost.set_aspect(asp)

        plt.draw()
        plt.pause(0.02)

    def update_idx_resolution_switch(self):
        new_idx = len(self.metric_values)
        self.idx_resolution_switch.append(new_idx)






