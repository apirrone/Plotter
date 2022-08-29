import numpy as np
import cv2
import threading
import time
import random
import backtrace

backtrace.hook(
    reverse=False, 
    align=True, 
    strip_path=True, 
    enable_on_envvar_only=False, 
    on_tty=False, 
    conservative=False, 
    styles={}
)

class Plotter():
    def __init__(self, w=1500, h=500, name="plot", x_granularity=10, y_granularity=0.1, history_size = 1000):
        self.w             = w
        self.h             = h
        self.x             = []
        self.data          = {} # {"name1" : [], "name2" : []}
        self.params        = {"color" : {}, "thickness" : {}}
        self.running       = False
        self.t             = None
        self.name          = name
        self.plot          = np.ones((self.h, self.w, 3))*0.85
        self.x_granularity = x_granularity
        self.y_granularity = y_granularity
        self.y_min         = 10000000000
        self.y_max         = 0.01
        self.t_max         = 0.01
        self.history_size  = history_size
        self.lastPlot      = None

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self.run, name="plot_thread")
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.running = False

    def makePlot(self):
        prev = {}

        self.lastPlot = self.plot.copy()
        self.plot = np.ones((self.h, self.w, 3))*0.85

        # Horizontal lines
        for j in range(0, int(self.y_max*100), int(self.y_granularity*100)):
            j = j/100
            y_print = (self.h-1)-int(j / self.y_max * self.h-1)

            cv2.line(self.plot, (0, y_print), (self.w-1, y_print), [0.5, 0.5, 0.5], 1)



        # actual plotting
        for i in range(len(self.x)-1):
            t = self.x[i]
            t_print = int((i/len(self.x)) * self.w-1)

            # vertical lines
            if round(t)%self.x_granularity == 0:
                cv2.line(self.plot, (t_print, self.h-1), (t_print, 0), [0.5, 0.5, 0.5], 1)
                cv2.putText(self.plot, str(round(t, 2)), (t_print, self.h-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [0, 0, 0])

            for key in self.data.keys():
                y = self.data[key][i]
                y_print = (self.h-1)-int((y / self.y_max) * self.h-1)
                point = (t_print, y_print)

                if i > 0:
                    self.plot = cv2.line(self.plot, prev[key], point, self.params["color"][key], self.params["thickness"][key])

                if key not in prev:
                    prev[key] = None

                prev[key] = point

        # y values
        for j in range(0, int(self.y_max*100), int(self.y_granularity*100)):
            j = j/100
            y_print = (self.h-1)-int(j / self.y_max * self.h-1)

            cv2.putText(self.plot, str(round(j, 2)), (0, y_print), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [0, 0, 0])

    def legend(self):
        pos = (20, 20)
        for i, name in enumerate(self.data.keys()):
            color     = self.params["color"][name]
            thickness = 2
            pt1 = (pos[0], pos[1]+i*20)
            pt2 = (pos[0]+50, pos[1]+i*20)
            pt3 = (pt2[0]+10, pt2[1]+5)

            cv2.line(self.plot, pt1, pt2, color, thickness)

            cv2.putText(self.plot, name, pt3, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)


    def run(self):
        while self.running:
            self.makePlot()
            self.legend()

            cv2.imshow(self.name, self.plot)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

    def push(self, t, y, name, color=[0, 0, 0], thickness=2):
        if name not in self.data:
            self.data[name] = []
            self.params["color"][name] = color
            self.params["thickness"][name] = thickness
            
        if t not in self.x:
            self.x.append(t)

        self.data[name].append(y)

        if y > self.y_max:
            self.y_max = y

        if y < self.y_min:
            self.y_min = y

        if t > self.t_max:
            self.t_max = t

        if len(self.x) > self.history_size:
            self.x = self.x[-self.history_size:]
            for name in self.data.keys():
                self.data[name] = self.data[name][-self.history_size:]

    def save(self, path):
        cv2.imwrite(path, (self.lastPlot*255).astype(np.uint8))