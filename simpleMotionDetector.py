import argparse
import cv2
import time

# Arguments business
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-n", "--no_display", action='store_true', help="do not show video display")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# Global init
firstFrame = None
count      = 0

# Start video capture
cap = cv2.VideoCapture(0)

time.sleep(3)

while cap.isOpened() == True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # let go few frames and let camera to adjust to light
    if firstFrame is None and count < 30:
        count = count + 1
        continue

    # Convert image to grayscale and blur it to avoid 
    # false positives
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Feed the frames for motion detactor 
    if firstFrame is None and ret is not None:
        firstFrame = gray
        continue
    
    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
     
    # Quit logic for window and non window mode
    if args["no_display"] is not True:
        # Display the resulting frame
        cv2.imshow('frame',frame)
        #cv2.imshow('firstFrame',firstFrame)
        #cv2.imshow('framedelta',frameDelta)
        #cv2.imshow('threshold',thresh)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "Quitting"
            break;
    else:
        if len(cnts) != 0:
            print "May Day!!"

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
