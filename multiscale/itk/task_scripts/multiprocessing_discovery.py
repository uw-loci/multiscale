import multiprocessing as mp
import time

import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk

# Fixing random state for reproducibility
np.random.seed(19680801)


class ProcessPlotter(object):
    def __init__(self, array):
        self.x = [array[0]]
        self.y = [array[1]]
    
    def terminate(self):
        plt.close('all')
    
    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                self.x.append(command[0])
                self.y.append(command[1])
                self.ax.plot(self.x, self.y, 'ro')
        self.fig.canvas.draw()
        return True
    
    def __call__(self, pipe):
        print('starting plotter...')
        
        self.pipe = pipe
        self.fig, self.ax = plt.subplots()
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()
        
        print('...done')
        plt.show()


class RegistrationPlot(object):
    def __init__(self, fixed_array, fixed_spacing, fixed_origin, moving_array, moving_spacing, moving_origin):
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter(fixed_spacing)
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe,), daemon=True)
        self.plot_process.start()
    
    def plot(self, data=None, finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        else:
            send(data)


def main():
    fixed_array = np.random.random_integers(0, 255, [50, 50])
    moving_array = np.random.random_integers(0, 255, [50, 50])
    
    spacing = [1, 1]
    origin = [0, 0]
    
    transform = sitk.AffineTransform(2)
    
    reg_plot = RegistrationPlot(fixed_array, spacing, origin, moving_array, spacing, origin)
    
    for i in range(50):
        transform.SetTranslation([i, i])
        reg_plot.plot(data=[i, i])
        time.sleep(0.5)


if __name__ == '__main__':
    main()