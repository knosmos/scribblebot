import cv2
from matplotlib import pyplot as plt

# loading the image
image = cv2.imread("rubiks.jpg")

# convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print(gray)

# create a binary thresholded image
_, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)
print(binary)
cv2.imshow("test",binary)
cv2.waitKey(0)

# contours from the thresholded image
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# draw all contours
image = cv2.drawContours(image, contours, -1, (255, 0, 0), 4)

cv2.imshow("test",image)
cv2.waitKey(0)