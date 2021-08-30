from constants import *
import cv2
import numpy as np
import pyautogui
import keyboard

def detectStart():
    # pauses until r key is pressed
    keyboard.wait("r")

def loadImage(filename):
    # loads cv2 image from file
    img = cv2.imread(filename)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # resize
    width = 100
    img_w = width
    img_h = int(width/img.shape[0] * img.shape[1])

    img = cv2.resize(img, (img_w, img_h), interpolation = cv2.INTER_AREA)
    return img

def color_distance(c1, c2):
    # euclidean distance between two colors.
    pass


def similar(c1, c2):
    # tests if two colors are similar.
    t = COLOR_THRESHOLD
    a = abs(c1[0]-c2[0]) < t and abs(c1[1]-c2[1]) < t and abs(c1[2]-c2[2]) < t
    return a

def findContours(img):
    # get polygons
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgray = cv2.Canny(imgray,100,200)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #cv2.drawContours(bitmap, contours, -1, (0,255,0), 3)
    #cv2.imshow("bitmap",bitmap)
    #cv2.waitKey(0)
    polygons = []
    for polygon in contours:
        polygon = polygon.tolist()
        #polygons.append([polygon, avg_color])
        polygons.append(polygon)
    #print(polygon)
    return polygons

def nearestColor(color, usable_colors):
    # given a color, return the color in usable_colors closest to it
    pass

def changeFillColor(color):
    pass

def drawPolygon(polygon, color):
    pass

def draw():
    pass

def removeNear(polygon):
    # removes points that are close together.
    print(polygon)
    res = [[[polygon[0][0][0], polygon[0][0][1]]]]
    for i in range(1,len(polygon)):
        x2, y2 = polygon[i-1][0]
        if (res[-1][0][0]-x2)**2 + (res[-1][0][1]-y2)**2 > 10:
            res.append([[x2, y2]])
    return res

# Load image
img = loadImage("rubik.jpg")

# Scale image to fit canvas
min_dimension = min(CANVAS_W, CANVAS_H)
if min_dimension == CANVAS_W:
    scale = CANVAS_W/img.shape[1]
else:
    scale = CANVAS_H/img.shape[0]

# Find contours
polygons = findContours(img)
#contours = np.asarray(findContours(img))
#cv2.drawContours(img, contours, -1, (0,255,0), 1)
#cv2.imshow("test",img)
#cv2.waitKey(0)
#print(polygons)
print(len(polygons))
detectStart()
speed = 1 # the higher the number, the less points are drawn
for polygon in polygons:
    pyautogui.mouseDown()
    polygon = removeNear(polygon)
    prev_point = polygon[-1][0]
    pyautogui.moveTo(prev_point[0]*scale + CANVAS[0], prev_point[1]*scale + CANVAS[1])
    for i, point in enumerate(polygon):
        print(i)
        if i%speed == 0:
            point = point[0]
            pyautogui.dragTo(point[0]*scale + CANVAS[0], point[1]*scale + CANVAS[1])
            prev_point = point
    pyautogui.mouseUp()