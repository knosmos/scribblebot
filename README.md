# scribblebot
### A semi functional edge-detecting autodraw bot

![ezgif com-gif-maker (4)](https://user-images.githubusercontent.com/30610197/131764820-d83c5392-2cd8-4b2d-89c1-2fdbcdf16d96.gif)


Line drawing bot for skribbl/sketchful. While there are many autodraw programs available (most of which produce images of higher quality), scribblebot is designed to produce drawings with a more humanlike feel. It also features a simple GUI for easier usage.

## Requirements
- `opencv-python` for image processing
- `keyboard` for hotkey detection
- `shapely` for finding fill targets
- `pyautogui` for mouse/keyboard control

## Instructions
First, run `mousepos.py` to find all the necessary values for `constants.py` (this only has to be done once for your particular computer setup).

Run `draw.py` to draw an image. Press `r` to start the drawing after navigating to the desired window. Scribblebot works best with clipart images without outlines, but it usually produces a recognizable image, even for photographs.

## Showcase

![image](https://user-images.githubusercontent.com/30610197/131766185-23840a86-7e5a-4d90-9a9c-8b1578ec72e8.png)
On a photograph:
![image](https://user-images.githubusercontent.com/30610197/131765462-3561d2c8-6159-4940-9a8e-19d68907d3eb.png)
Clipart:
![image](https://user-images.githubusercontent.com/30610197/131766073-34c6a7b7-45ee-4c44-8ca9-1efb8da61bb5.png)
![image](https://user-images.githubusercontent.com/30610197/131766832-d5b73730-48d7-4238-83c8-30896c1c0275.png)
On more complex images, scribblebot tends to improperly fill the shapes:
![image](https://user-images.githubusercontent.com/30610197/131767361-7b75a0d0-9bec-4c09-af64-b1cdb3db9ef0.png)

## Roadmap
Scribblebot is a work in progress. Future features may include:
- Automatic image selection
- Better fill algorithms
- Faster drawing times
- Self-tuning image processing parameters