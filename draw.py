from constants import *
import cv2
import numpy as np
import pyautogui
import keyboard
import sys

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
    # squared euclidean distance between two colors
    return (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2

def similar(c1, c2):
    # tests if two colors are similar.
    t = COLOR_THRESHOLD
    # a = abs(c1[0]-c2[0]) < t and abs(c1[1]-c2[1]) < t and abs(c1[2]-c2[2]) < t
    return color_distance(c1, c2) < t

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
    # Code modified from github.com/dchen327/pictionary-autodraw/

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


def switch_color(color, colors, coords):
    # Find the color in palette closest to color
    # and switch to that color
        
    min_dist = float('inf')
    closest_idx = -1
    for idx, palette_color in enumerate(colors):
        if palette_color == [255,255,255]:
            continue # white is boring, ignore it
        dist = color_distance(color, palette_color)
        if dist < min_dist:
            min_dist = dist
            closest_idx = idx
    x, y = coords[closest_idx]
    pyautogui.click(x, y)

def removeNear(polygon):
    # removes points that are close together.
    # print(polygon)
    res = [(polygon[0][0][0], polygon[0][0][1])]
    for i in range(1,len(polygon)):
        x2, y2 = polygon[i-1][0]
        if (res[-1][0]-x2)**2 + (res[-1][1]-y2)**2 > MIN_POINT_DISTANCE:
            res.append((x2, y2))
    return res

def main():
    # Load image
    img = loadImage(input("Image filename: "))

    # Scale image to fit canvas
    min_dimension = min(CANVAS_W, CANVAS_H)
    if min_dimension == CANVAS_W:
        scale = CANVAS_W/img.shape[1]
    else:
        scale = CANVAS_H/img.shape[0]

    # Find colors/coords of palette
    colors, coords = get_palette()

    # Find contours
    polygons = findContours(img)[::-1]
    print("Contour calculation complete (%d polygons found)" % len(polygons))
    print("Navigate to desired window, then press [r] to start")
    detectStart()

    # Draw
    usedpolygons = set()
    prev_color = [-1, -1, -1]
    for shape in polygons:
        polygon = removeNear(shape[0])
        color = shape[1]
        if tuple(polygon) in usedpolygons:
            continue
        if (0,0) in polygon:
            continue
        if color[0] != prev_color[0] or color[1] != prev_color[1] or color[2] != prev_color[2]:
            switch_color(color, colors, coords)    
            prev_color = color
        usedpolygons.add(tuple(polygon))
        prev_point = polygon[-1]
        pyautogui.moveTo(prev_point[0]*scale + CANVAS[0], prev_point[1]*scale + CANVAS[1])
        pyautogui.mouseDown()
        for i, point in enumerate(polygon):       
            pyautogui.moveTo(point[0]*scale + CANVAS[0], point[1]*scale + CANVAS[1], duration = 0.05)
            prev_point = point
        pyautogui.mouseUp()

if __name__ == "__main__":
    main()