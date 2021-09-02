from constants import *
import cv2
import numpy as np
import pyautogui
import keyboard
import sys
import math
from tkinter import *
from threading import Thread
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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
    img_h = int(width/img.shape[1] * img.shape[0])

    img = cv2.resize(img, (img_w, img_h), interpolation = cv2.INTER_AREA)
    return img

def rgb_to_hsv(color):
    arr = np.uint8([[color]])
    return cv2.cvtColor(arr,cv2.COLOR_RGB2HSV)[0][0]

def color_distance(c1, c2):
    # squared weighted euclidean distance between two colors
    return 0.30*(c1[0]-c2[0])**2 + 0.59*(c1[1]-c2[1])**2 + 0.11*(c1[2]-c2[2])**2
    
    # manhattan distance
    # return abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2]-c2[2])
    
    # compare hsv values
    '''hsv_1 = rgb_to_hsv(c1)
    hsv_2 = rgb_to_hsv(c2)
    d_h = min(abs(hsv_1[0]-hsv_2[0]), 180-abs(hsv_1[0]-hsv_2[0]))
    diff = 4*(d_h)**2 + 0.2*(hsv_1[1]-hsv_2[1])**2 + 0.3*(hsv_1[2]-hsv_2[2])**2 
    return diff'''

def similar(c1, c2):
    # tests if two colors are similar.
    t = COLOR_THRESHOLD
    # a = abs(c1[0]-c2[0]) < t and abs(c1[1]-c2[1]) < t and abs(c1[2]-c2[2]) < t
    return color_distance(c1, c2) < t*2

def findContours(img):
    # Run BFS flood fill on each pixel, if the filled region is large
    # enough, construct a contour for it.
    
    h, w, _ = img.shape
    polygons = [] # [[contour, color] ...]

    # stores which pixels have been visited
    visited = np.zeros((h, w), np.float32)

    for x in range(w):
        for y in range(h):
            if visited[y][x] == 0:
                visited[y][x] = 1
                color = img[y][x].tolist()

                queue = [(x,y)] # BFS queue
                bitmap = np.zeros((h, w, 3), dtype=np.uint8) # stores flood-filled region
                num_pixels = 0

                avg_color = [0,0,0]

                while len(queue) > 0:
                    #print(len(queue))
                    px, py = queue.pop(0)
                    #print(px,py)

                    num_pixels += 1
                    bitmap[py][px] = np.array([255,255,255])
                    
                    avg_color[0] += img[py][px][0]
                    avg_color[1] += img[py][px][1]
                    avg_color[2] += img[py][px][2]
                    #print(avg_color, img[py][px])
                    #color = img[py][px].tolist()

                    # for each neighbor, test if it is similar enough
                    if px > 0:
                        if visited[py][px-1] == 0 and similar(color, img[py][px-1].tolist()):
                            queue.append((px-1, py))
                            visited[py][px-1] = 1
                    if px < w-1:
                        if visited[py][px+1] == 0 and similar(color, img[py][px+1].tolist()):
                            queue.append((px+1, py))
                            visited[py][px+1] = 1
                    if py > 0:
                        if visited[py-1][px] == 0 and similar(color, img[py-1][px].tolist()):
                            queue.append((px, py-1))
                            visited[py-1][px] = 1
                    if py < h-1:
                        if visited[py+1][px] == 0 and similar(color, img[py+1][px].tolist()):
                            queue.append((px, py+1))
                            visited[py+1][px] = 1
            
                # test if region is large enough
                if num_pixels > PIXEL_THRESHOLD:
                    # get final average color
                    avg_color = [avg_color[0]/num_pixels, avg_color[1]/num_pixels, avg_color[2]/num_pixels]
                    
                    # erode segmented mask to clean it up
                    # bitmap = cv2.erode(bitmap, None, iterations=4)
                    # bitmap = cv2.dilate(bitmap, None, iterations=4)

                    # get polygons
                    imgray = cv2.cvtColor(bitmap, cv2.COLOR_BGR2GRAY)
                    #imgray = cv2.Canny(imgray,100,200)
                    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
                    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    
                    #cv2.drawContours(bitmap, contours, -1, (0,255,0), 3)
                    #cv2.imshow("bitmap",bitmap)
                    #cv2.waitKey(0)

                    for polygon in contours:
                        #epsilon = 0.01 * cv2.arcLength(polygon, True)
                        #polygon = cv2.approxPolyDP(polygon, epsilon, True)
                        #polygon = polygon.tolist()
                        polygons.append([polygon, avg_color])
                        #polygons.append(polygon)
                    #print(polygon)
    return polygons

def get_palette():
    # Finds the position and color of each item in the color palette.

    colors = []  # store rgb values of colors
    coords = []  # store coordinates of where to click on screen
    palette_img = cv2.imread(PALETTE_IMG_FILENAME)
    curr_row = 0
    for color_idx in range(PALETTE_DIMS[0] * PALETTE_DIMS[1]):
        # start next row
        if color_idx > 0 and color_idx % PALETTE_DIMS[1] == 0:
            curr_row += 1
        curr_col = color_idx % PALETTE_DIMS[1]
        i = int(curr_col * SINGLE_COLOR_SIZE + SINGLE_COLOR_SIZE / 2)
        j = int(curr_row * SINGLE_COLOR_SIZE + SINGLE_COLOR_SIZE / 2)
        rgb = palette_img[j][i].tolist()
        colors.append(rgb)
        x = PALETTE_POS[0] + i
        y = PALETTE_POS[1] + j
        coords.append((x, y))
    return colors, coords


def switch_color(color, colors, coords, outline=False):
    # Find the color in palette closest to color
    # and switch to that color

    # outline=True makes the color darker (as in an outline)
    
    if outline:
        c = [max(0,k-60) for k in color]
    else:
        c = color
    min_dist = float('inf')
    closest_idx = -1
    for idx, palette_color in enumerate(colors):
        # if palette_color == [255,255,255]:
        #    continue # white is boring, ignore it
        dist = color_distance(c, palette_color)
        if dist < min_dist:
            min_dist = dist
            closest_idx = idx
    x, y = coords[closest_idx]
    pyautogui.click(x, y)
    return True

def findFillPoint(polygon):
    # finds the point farthest from the polygon boundary inside the polygon.
    poly = Polygon(polygon)
    max_dist = 0
    point = False
    for i in range(len(polygon)):
        for j in range(i):
            distance = math.sqrt((polygon[i][0]-polygon[j][0])**2 + (polygon[i][1]-polygon[j][1])**2)
            if distance > max_dist:
                x = (polygon[i][0]+polygon[j][0])/2
                y = (polygon[i][1]+polygon[j][1])/2
                midpoint = Point(x, y)
                if poly.contains(midpoint):
                    max_dist = distance
                    point = [x,y]
    return point

def removeNear(polygon):
    # removes points that are close together.
    # print(polygon)
    res = [(polygon[0][0][0], polygon[0][0][1])]
    for i in range(1,len(polygon)):
        x2, y2 = polygon[i-1][0]
        if (res[-1][0]-x2)**2 + (res[-1][1]-y2)**2 > MIN_POINT_DISTANCE:
            res.append((x2, y2))
    return res

# Create tkinter interface
root = Tk()
root["bg"] = "#2C363F"
root.title('scribblebot')

Label(root, text="scribblebot", font=("Verdana", 16), padx = 100, pady = 5, bg="#2C363F", fg="#00BBF9").pack()

filenameTextbox = Entry(root, font=("Verdana", 12), bg="#58687D", fg="#FFFFFF", relief="flat")
filenameTextbox.insert(0, 'image filepath')
filenameTextbox.pack()

startButton = Button(root, text="start", font=("Verdana", 12), bg="#00BBF9", fg="#FFFFFF", relief="flat")
startButton.pack(pady=5)

statusLabel = Label(root, text="press start to begin", font=("Verdana", 12), padx = 5, pady = 5, bg="#2C363F", fg="#E75A7C")
statusLabel.pack()

root.wm_attributes("-topmost", 1)

# Drawing image
def draw():
    # Load image
    filename = filenameTextbox.get()
    img = loadImage(filename)

    # Scale image to fit canvas
    if CANVAS_W-img.shape[1] < CANVAS_H-img.shape[0]:
        scale = CANVAS_W/img.shape[1]
    else:
        scale = CANVAS_H/img.shape[0]

    # Find colors/coords of palette
    colors, coords = get_palette()
    print(colors)

    # Find contours
    polygons = findContours(img)
    statusLabel["text"] = "Contour calculation complete (%d polygons found)\nNavigate to desired window, then press [r] to start" % len(polygons)
    detectStart()

    # Draw
    usedpolygons = set()
    prev_color = [-1, -1, -1]
    for i, shape in enumerate(polygons):
        statusLabel["text"] = "Drawing polygon %d of %d" % (i, len(polygons))
        polygon = removeNear(shape[0])
        color = shape[1]
        print(color)
        
        if tuple(polygon) in usedpolygons:
            continue
        
        if (0,0) in polygon:
            continue

        if len(polygon) <= 2:
            continue

        switch_color(color, colors, coords, outline = True)
        # if color[0] != prev_color[0] or color[1] != prev_color[1] or color[2] != prev_color[2]:
        #    r = switch_color(color, colors, coords)
        #    if not r:
        #        continue
        #    prev_color = color
        
        usedpolygons.add(tuple(polygon))
        
        if (polygon[0][0]-polygon[-1][0])**2 + (polygon[0][1]-polygon[-1][1])**2 > 300:
            prev_point = polygon[0]
            fill_poly = False
        else:
            prev_point = polygon[-1]
            fill_poly = True

        pyautogui.moveTo(prev_point[0]*scale + CANVAS[0], prev_point[1]*scale + CANVAS[1])
        pyautogui.mouseDown()
        
        for i, point in enumerate(polygon):       
            pyautogui.moveTo(point[0]*scale + CANVAS[0], point[1]*scale + CANVAS[1], duration = 0.0)
            prev_point = point
        pyautogui.mouseUp()

        if len(polygon) >= 3 and fill_poly:
            pyautogui.press(FILL_KEY)
            point = findFillPoint(polygon)
            switch_color(color, colors, coords, outline = False)
            if point:
                pyautogui.click(point[0]*scale + CANVAS[0], point[1]*scale + CANVAS[1])
            pyautogui.press(PEN_KEY)

    statusLabel["text"] = "Drawing complete"

def main():
    def startDraw():
        drawThread = Thread(target=draw)
        drawThread.daemon = True
        drawThread.start()
    startButton["command"] = startDraw
    root.mainloop()

if __name__ == "__main__":
    main()