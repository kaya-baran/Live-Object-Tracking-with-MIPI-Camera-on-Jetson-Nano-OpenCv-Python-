import cv2
from pynput import mouse
from pynput import keyboard
import threading
import time


global X, Y, bbReady, coordList, isListening, bbox, isTracking, tracker, ok 
X=0
Y=0
coordList = []

def boundingBox():
    global X, Y, bbReady, coordList, isListening, bbox
    bbox = ()
    x1, y1 = coordList[0]
    x2, y2 = coordList[1]
    if x1 < x2 and y1 < y2:
        bbox = (x1-66 ,y1-53 ,x2-x1,y2-y1)
    if x1 < x2 and y1 > y2:
        bbox = (x1-66 ,y2-53 ,x2-x1,y1-y2)
    if x1 > x2 and y1 < y2:
        bbox = (x2-66 ,y1-53 ,x1-x2,y2-y1)
    if x1 > x2 and y1 > y2:
        bbox = (x2-66 ,y2-53 ,x1-x2,y1-y2)
    return bbox

def on_click(x, y, button, pressed):
    global X,Y
    if pressed:
        print("Click!")
        X = x
        Y = y
        print(X,Y)

def on_functionf8andf7(key):
    global X, Y, bbReady, coordList, isListening, bbox, isTracking, tracker, ok
    print("Key Pressed")
    if key==keyboard.Key.f8:
        isListening = True
        bbox = []
    elif key==keyboard.Key.f7:
        print("f7 is pressed")
        ok = False
        isTracking = False
        
def coordLister(name):
    global X, Y, bbReady, coordList, isListening
    tempY = None
    tempX = None
    isListening = False
    print("Start Coord Listener")
    while True:
        if isListening and tempX != X and tempY != Y:
            print("Coord Listen Update")
            coordList.append((X,Y))
            tempX = X
            tempY = Y
        
        if len(coordList) == 2:
            print("Coord Ready")
            bbReady = True
            isListening = False
            tempX = None
            tempY = None
            time.sleep(2)

pipeline = "nvarguscamerasrc sensor-id=0 bufapi-version=1 ! video/x-raw(memory:NVMM), width=(int)1280,height=(int)720, \
            format=(string)NV12 ! nvvideoconvert ! videoflip method=2 ! videoconvert n-threads=2 ! appsink"

tracker = cv2.TrackerKCF_create()
cap = cv2.VideoCapture(pipeline,cv2.CAP_GSTREAMER)

key_listener = keyboard.Listener(on_release=on_functionf8andf7)
key_listener.start()

listerThread = threading.Thread(target=coordLister, args=(1,))
listerThread.start()

bbox = None
ok = False
bbReady = False
isTracking = False

with mouse.Listener(on_click=on_click) as listener:
    while True:
        ret, frame = cap.read()

        if isTracking:
            ok, bbox = tracker.update(frame)

        if not ok and bbReady:
            tracker = cv2.TrackerKCF_create()
            bbox = boundingBox()
            ok = tracker.init(frame, bbox)
            isTracking = True
            bbReady = False
            coordList = []
        
        elif not ok and isTracking:
            isTracking = False
            del tracker

        if ok:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

        cv2.imshow('frame', frame)

        k= cv2.waitKey(1) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()