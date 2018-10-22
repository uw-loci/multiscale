import matplotlib.pyplot as plt
import SimpleITK as sitk
import multiscale.itk.process as proc
import time
import numpy as np
import matplotlib.ticker as plticker
import multiprocessing as mp


class Plotter(object):
        def __init__(self):
                # , fixed_array, fixed_spacing, fixed_origin, moving_array, moving_spacing, moving_origin
                # self.fixed_image = sitk.GetImageFromArray(fixed_array)
                # self.fixed_image.SetSpacing(fixed_spacing)
                # self.fixed_image.SetOrigin(fixed_origin)
                #
                # self.moving_image = sitk.GetImageFromArray(moving_array)
                # self.moving_image.SetSpacing(moving_spacing)
                # self.moving_image.SetOrigin(moving_origin)
                
                self.metric_values = []
                self.idx_resolution_switch = []
                self.transform = sitk.AffineTransform(2)
        
        def __call__(self, pipe):
                print("starting plotter...")
                self.pipe = pipe
                self.setup_plots()
                timer = self.fig.canvas.new_timer(interval=10000)
                timer.add_callback(self.call_back)
                timer.start()
                
                print('...done')
                plt.show()
        
        def setup_plots(self):
                # self.fig, (self.ax_img, self.ax_cost) = plt.subplots(1, 2)
                self.fig, self.ax_cost = plt.subplots()
                self.fig.set_size_inches(16, 8)
                
                self.ax_img.axis('off')
                
                self.ax_cost.set_xlabel('Iteration Number', fontsize=12)
                self.ax_cost.set_title('Metric Value', fontsize=12)
                self.ax_cost.set_xlim(0, 1)
                self.ax_cost.set_ylim(-0.1, 0)
                
                loc = plticker.MaxNLocator(integer=True)  # this locator puts ticks at regular intervals
                self.ax_cost.xaxis.set_major_locator(loc)
                
                # moving_transformed = sitk.Resample(self.moving_image, self.fixed_image, self.transform,
                #                                    sitk.sitkLinear, 0.0,
                #                                    self.moving_image.GetPixelIDValue())
                # combined_array = proc.overlay_images(self.fixed_image, moving_transformed)
                #
                # self.img = self.ax_img.imshow(combined_array)
                
                self.plot, = self.ax_cost.plot(self.metric_values, 'r')
                self.plot_multires, = self.ax_cost.plot(self.idx_resolution_switch,
                                                        [self.metric_values[index] for index in
                                                         self.idx_resolution_switch],
                                                        'b*')
        
        def update_plots(self, new_metric_value):
                self.metric_values.append(new_metric_value)
                # self.transform.SetParameters(transform_parameters)
                
                self.plot.set_data(range(len(self.metric_values)), self.metric_values)
                self.plot_multires.set_data(self.idx_resolution_switch,
                                            [self.metric_values[index] for index in self.idx_resolution_switch])
                self.ax_cost.set_xlim(0, len(self.metric_values))
                self.ax_cost.set_ylim(1.1 * min(self.metric_values), 0)
                
                # moving_transformed = sitk.Resample(self.moving_image, self.fixed_image, self.transform,
                #                                    sitk.sitkLinear, 0.0,
                #                                    self.moving_image.GetPixelIDValue())
                #
                # # Blend the registered and fixed images
                # combined_array = proc.overlay_images(self.fixed_image, moving_transformed)
                # self.img.set_data(combined_array)
                
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                plt.pause(0.01)
        
        def call_back(self):
                old_commands = self.pipe.recv()
                new_metric_value = old_commands[0]
                transform_parameters = old_commands[1]
                self.update_plots(new_metric_value, transform_parameters)
                
                while self.pipe.poll():
                        commands = self.pipe.recv()
                        
                        if commands is None:
                                self.terminate()
                                return False
                        else:
                                new_metric_value = commands[0]
                                transform_parameters = commands[1]
                                self.update_plots(new_metric_value, transform_parameters)
                return True
        
        def update_resolution_switch(self):
                new_idx = len(self.metric_values)
                self.idx_resolution_switch.append(new_idx)
        
        def terminate(self):
                plt.close('all')


class RegistrationPlot(object):
        def __init__(self):
                
                self.plot_pipe, plotter_pipe = mp.Pipe()
                self.plotter = Plotter()
                # fixed_array, fixed_spacing, fixed_origin, moving_array, moving_spacing, moving_origin
                self.plot_process = mp.Process(target=self.plotter, args=(plotter_pipe,), daemon=True)
                self.plot_process.start()
        
        def plot(self, new_metric_value, finished=False):
                send = self.plot_pipe.send
                if finished:
                        send(None)
                else:
                        send(new_metric_value)


def main():
        fixed_array = np.random.random_integers(0, 255, [50, 50])
        moving_array = np.random.random_integers(0, 255, [50, 50])
        
        spacing = [1, 1]
        origin = [0, 0]
        
        transform = sitk.AffineTransform(2)
        
        reg_plot = RegistrationPlot()
        
        for i in range(50):
                transform.SetTranslation([i, i])
                reg_plot.plot((-i / 50))


if __name__ == '__main__':
        main()
