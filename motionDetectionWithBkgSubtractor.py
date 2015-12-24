import argparse
import cv2
import time
import datetime
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


# Globals
moveQualified = 0

#Constants
COMMASPACE = ', '

# Functions
def sendGmail( username, password, from_address, to_address, subject, img_path ):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg.preamble = subject

    fp = open(img_path, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    # Send the email via our own SMTP server.
    server = smtplib.SMTP('smtp.mail.yahoo.com',587)
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()


# Arguments business
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-n", "--no_display", action='store_true', help="do not show video display")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
ap.add_argument("-e", "--email", help="email address")
ap.add_argument("-te", "--to_email", help="to email address")
ap.add_argument("-p", "--password", help="password")
ap.add_argument("-cn", "--cell_number", help="Cell number for SMS")
args = vars(ap.parse_args())

cap = cv2.VideoCapture(0)

fgbg = cv2.createBackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()
    
    fgmask = fgbg.apply(frame)

    (_, cnts, _) = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    moveQualified = 0
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

        moveQualified = 1
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Quit logic for window and non window mode
    if args["no_display"] is not True:
        # Display the resulting frame
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "Quitting"
            break;
    else:
        if moveQualified == 1:
                if args["email"] is not None and args["password"] is not None:
                    timestamp = datetime.datetime.now()
                    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
                    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.35, (0, 0, 255), 1)
                    img_path = "motion-" + timestamp.strftime("%A%d%B%Y%I:%M:%S%p") + ".jpg"
                    cv2.imwrite(img_path, frame)
                    sendGmail( args["email"], args["password"], args["email"], args["to_email"],'Motion detected', img_path ) 
                    #gv_cmd = "gvoice -e {0} -p {1} send_sms {2} 'Motion Detected'".format(args["g_email"], args["g_password"], args["cell_number"])
                    #os.system(gv_cmd)
                    #os.system("espeak 'Oye'")
                moveQualified = 0

cap.release()
cv2.destroyAllWindows()


