GAME = "sketchful"

PEN = "b" # keyboard shortcut for "pen"
FILL = "f" # keyboard shortcut for "fill"

# Sketchful
if GAME == "sketchful":
    CANVAS = [326, 210, 1364, 982] # x, y, x2, y2: dimensions of canvas
    CANVAS_W = CANVAS[2]-CANVAS[0]
    CANVAS_H = CANVAS[3]-CANVAS[1]

    PALETTE_POS = [0,0] # x, y: topleft corner of color palette
    PALETTE_DIMS = []

# Skribbl

# Image processing parameters
COLOR_THRESHOLD = 50 # maximum distance between two colors for them to be considered similar
PIXEL_THRESHOLD = 20 # how many similar pixels are needed for a contour to be contructed for the region