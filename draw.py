from constants import *
import cv2
import numpy as np
import pyautogui

def detectStart():
    # pauses until enter key is pressed
    pass

def loadImage(filename):
    # loads cv2 image from file
    img = cv2.imread(filename)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def color_distance(c1, c2):
    # euclidean distance between two colors.


def similar(c1, c2):
    # tests if two colors are similar.
    t = COLOR_THRESHOLD
    a = abs(c1[0]-c2[0]) < t and abs(c1[1]-c2[1]) < t and abs(c1[2]-c2[2]) < t
    return a

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
                ret, thresh = cv2.threshold(imgray, 127, 255, 0)
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                #cv2.drawContours(bitmap, contours, -1, (0,255,0), 3)
                #cv2.imshow("bitmap",bitmap)
                #cv2.waitKey(0)

                for polygon in contours:
                    #polygon = polygon.tolist()
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

# Load image
img = loadImage("rubik.jpg")

# Scale image to fit canvas
min_dimension = min(CANVAS_W, CANVAS_H)
if min_dimension = CANVAS_W:
    scale_percent = CANVAS_W/img.shape[1]
else:
    scale_percent = CANVAS_H/img.shape[0]


# Find contours
contours = np.asarray(findContours(img))
cv2.drawContours(img, contours, -1, (0,255,0), 1)

cv2.imshow("test",img)
cv2.waitKey(0)