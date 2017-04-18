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
	
	capture.set(CV_CAP_PROP_FRAME_WIDTH , 640); 
	capture.set(CV_CAP_PROP_FRAME_HEIGHT , 480);  
	capture.set(CV_CAP_PROP_FOURCC, CV_FOURCC('B', 'G', 'R', '3'));

	while (true) {
		Mat frame;
		capture.read(frame);
		imshow("Camera", frame);
		if (char(waitKey(27)) == 27){
            break;      //If you hit ESC key loop will break.
        }
	}
	
	return 0;
}