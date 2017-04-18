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

	while (true) {
        // # grab the current frame
        capture >> frame;
        // # mirror image horizontally
        flip(frame,frame,1);
        // # change from BGR to HSV
        cvtColor(frame,hsv, CV_BGR2HSV);
        // # show the frame to our screen and increment the frame counter
		imshow("Camera", frame);
        // # if the 'q' key is pressed, stop the loop
		if (char(waitKey(27)) == 27)
            break;              
	}
	
	return 0;
}