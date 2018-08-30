import matplotlib.pyplot as plt

class RegistrationPlot:
    def __init__(self):
        self.metric_values = []
        self.idx_resolution_switch = []
        self.fig, self.ax_cost, self.ax_img = plt.subplots(1, 2)

    def update_plot(self, new_metric_value, fixed_image, moving_image, transform):
        self.metric_values = self.metric_values.append(new_value)

        #
        #     """Event: Update and plot new registration values"""
        #
        #     global metric_values, multires_iterations
        #
        #     metric_values.append(registration_method.GetMetricValue())
        #
        #     # Clear the output area (wait=True, to reduce flickering)
        #     clear_output(wait=True)
        #
        #     moving_transformed = sitk.Resample(moving_image, fixed_image, transform,
        #                                        sitk.sitkLinear, 0.0,
        #                                        moving_image.GetPixelIDValue())
        #
        #     # Blend the registered and fixed images
        #     combined_array = proc.overlay_images(fixed_image, moving_transformed)
        #
        #     # plot the current image
        #     fig, (ax, ax2) = plt.subplots(ncols=2)
        #     fig.tight_layout()
        #
        #     ax.imshow(combined_array)
        #     ax.axis('off')
        #
        #     ax2.plot(metric_values, 'r')
        #     ax2.plot(multires_iterations,
        #              [metric_values[index] for index in multires_iterations], 'b*')
        #
        #     ax2.set_xlabel('Iteration Number', fontsize=12)
        #     ax2.set_ylabel('Metric Value', fontsize=12, rotation='90')
        #
        #     asp = np.diff(ax2.get_xlim())[0] / np.diff(ax2.get_ylim())[0]
        #     ax2.set_aspect(asp)
        #
        # # Callback invoked when the sitkMultiResolutionIterationEvent happens,
        # # update the index into the metric_values list.


    def update_idx_resolution_switch(self, new_idx):
        self.idx_resolution_switch = self.idx_resolution_switch.append(new_idx)

    def start_plot(self):

    def end_plot(self):



