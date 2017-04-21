/*
* File:   main.cpp
* Author: sagar
*
* Created on 10 September, 2012, 7:48 PM
*/
 
#include "opencv2/opencv.hpp"
#include <iostream>
using namespace cv;
using namespace std;

// # define the lower and upper boundaries of the "green"
// # ball in the HSV color space
int low_h = 29, low_s = 86, low_v = 6;
int high_h = 64, high_s = 255, high_v = 255;

int main() {
	
	VideoCapture capture(0);   //0 is the id of video device.0 if you have only one camera.
	 
	if (!capture.isOpened()) { //check if video device has been initialised
		cout << " Cannot open camera";
	}
	
	capture.set(CV_CAP_PROP_FRAME_WIDTH , 600); 
	capture.set(CV_CAP_PROP_FRAME_HEIGHT , 330);  
	capture.set(CV_CAP_PROP_FOURCC, CV_FOURCC('B', 'G', 'R', '3'));

  
	Mat frame;
	Mat hsv;
	Mat mask;

	while (true) {
        // # grab the current frame
        capture >> frame;
        // # mirror image horizontally
        flip(frame,frame,1);
        // # change from BGR to HSV
        cvtColor(frame,hsv, CV_BGR2HSV);
        
        // # construct a mask for the color "green", then perform
		// # a series of dilations and erosions to remove any small
		// # blobs left in the mask
        inRange(hsv, Scalar(low_h, low_s, low_v), Scalar(high_h, high_s, high_v), mask);
        erode(mask, mask, NULL);

        // # show the frame to our screen and increment the frame counter
		imshow("Camera", frame);
        // # if the 'q' key is pressed, stop the loop
		if (char(waitKey(27)) == 27)
            break;              
	}
	
	return 0;
}