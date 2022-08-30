from pickle import HIGHEST_PROTOCOL
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
    def __init__(self, w=1500, h=500, name="plot", x_granularity=5, y_granularity=10, history_size=100):
        self.w               = w
        self.h               = h
        self.x               = []
        self.data            = {} # {"name1" : [], "name2" : []}
        self.params          = {"color" : {}, "thickness" : {}}
        self.running         = False
        self.t               = None
        self.name            = name
        self.plot            = np.ones((self.h, self.w, 3))*0.85
        self.x_granularity   = x_granularity
        self.y_granularity   = y_granularity
        self.y_min           = 10000000000
        self.y_max           = 0.01
        self.history_size    = history_size

        self.callbackSet     = False
        self.mouse_x         = 0
        self.mouse_y         = 0
        self.mouse_l_clicked = False

    def mouseCallback(self, event, x, y, flags, param):
        self.mouse_x = x
        self.mouse_y = y 

    def mouse(self):
        cv2.circle(self.plot, (self.mouse_x, self.mouse_y), 5, [1, 0, 0], thickness=-1)

    def start(self):
        self.running = True
        self.t = threading.Thread(target=self.run, name=self.name+"_thread")
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()

    def run(self):        
        while self.running:
            self.makePlot()

            cv2.imshow(self.name, self.plot)
            cv2.waitKey(1)

            if not self.callbackSet:
                cv2.setMouseCallback(self.name, self.mouseCallback)   
                self.callbackSet = True

    
    def save(self, path):
        cv2.imwrite(path, (self.plot*255).astype(np.uint8))

    def drawVerticalLine(self, x, text=None, color=[0.7, 0.7, 0.7], thickness=2, font_size=0.45):
        cv2.line(self.plot, (x, self.h-1), (x, 0), color, thickness)
        if text is not None:
            cv2.putText(self.plot, str(round(text, 2)), (x+thickness, self.h-1), cv2.FONT_HERSHEY_SIMPLEX, font_size, color)

    def drawHorizontalLine(self, y, text=None, color=[0.7, 0.7, 0.7], thickness=2, font_size=0.45):
        cv2.line(self.plot, (0, y), (self.w-1, y), color, thickness)
        if text is not None:
            cv2.putText(self.plot, str(round(text, 2)), (thickness, y-thickness), cv2.FONT_HERSHEY_SIMPLEX, font_size, color)

    def makePlot(self):
        prev = {}
        self.plot = np.ones((self.h, self.w, 3))*0.85

        # Draw horizontal lines
        for y in range(round(self.y_min*100), round(self.y_max*100), int(self.y_granularity*100)):
            y = y/100
            y_print = self.h-int(((y - self.y_min)/(self.y_max - self.y_min))*self.h)
            self.drawHorizontalLine(y_print, text=y)

        for i in range(len(self.x) -1):
            i_print = int(i/len(self.x) * self.w)

            # Draw vertical lines
            if i%self.x_granularity == 0:
                self.drawVerticalLine(i_print, text=self.x[i])

            for key in self.data.keys():
                y = self.data[key][i]
                y_print = self.h-int(((y - self.y_min)/(self.y_max - self.y_min))*self.h)
                point = (i_print, y_print)

                if i > 0:
                    self.plot = cv2.line(self.plot, prev[key], point, self.params["color"][key], self.params["thickness"][key])

                if key not in prev:
                    prev[key] = None

                prev[key] = point

        self.legend()
        self.mouse()

    def legend(self):
        pos = (40, 20)
        for i, name in enumerate(self.data.keys()):
            color     = self.params["color"][name]
            thickness = 2
            pt1 = (pos[0], pos[1]+i*20)
            pt2 = (pos[0]+50, pos[1]+i*20)
            pt3 = (pt2[0]+10, pt2[1]+5)

            cv2.line(self.plot, pt1, pt2, color, thickness)

            cv2.putText(self.plot, name, pt3, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)


    # TODO interactive show, where we can hover the graphs and see the values
    # def _show(self):      
    #     while True:
    #         cv2.imshow(self.name, self.plot)
    #         cv2.waitKey(1)

    # def show(self):
    #     self.ts = threading.Thread(target=self._show, name="show_thread")
    #     self.ts.daemon = True
    #     self.ts.start()

    def pushArray(self, t, y, name, color=None, thickness=2):
        assert len(t) == len(y)

        for i in range(len(t)):
            self.push(t[i], y[i], name, color=color, thickness=thickness)

    def push(self, t, y, name, color=None, thickness=2):
        if name not in self.data:
            self.data[name] = []

            if color is None:
                color = tuple(random.random() for _ in range(3))

            self.params["color"][name] = color
            self.params["thickness"][name] = thickness
            
        if t not in self.x:
            self.x.append(t)

        self.data[name].append(y)

        if y > self.y_max:
            self.y_max = y

        if y < self.y_min:
            self.y_min = y

        if len(self.x) > self.history_size:
            self.x = self.x[-self.history_size:]
            for name in self.data.keys():
                self.data[name] = self.data[name][-self.history_size:]

if __name__ == "__main__":
    plot = Plotter()
    plot.start()
    i = 0
    while True:
        j = random.randint(-100, 100)
        z = random.randint(-100, 100)
        plot.push(i, j, "test1", thickness=2)
        plot.push(i, z, "test2", thickness=2)
        time.sleep(0.01)
        i += 1

