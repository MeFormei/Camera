# Camera Tracker

The project is part of the [MeFormei](https://www.github.com/MeFormei/) organization and processes images obtained from a camera to determine its position on the screen coordinates and send to interested listeners, making it possible to simulate a cursor or generate commands from the position variation enabled by triggers when limit areas are reached.

## Getting Started

These instructions will show how to configure your environment and how to have your project up and running.

### Prerequisites

What things you need to install the software and how to install them

Its necessary to use a Linux or other Unix based system to run the project (like Ubuntu, Debian, MacOS X and others). You can also use the available version to run on a [Raspberry Pi](https://www.raspberrypi.org/) running the [Raspibian](https://www.raspberrypi.org/downloads/raspbian/) system.

To run the project you also need to install its dependencies, listed above.

#### Python3

The first dependency is the Python, on version 3.4+. You can install it running following the instructions:

```
sudo apt-get install python3
```

You can check if the correct version was installed searching from Python 3.4+ version after running:

```
python --version
```

You also need to install some libraries listed in the *requirements.txt* file using the [Pip](https://pypi.python.org/pypi/pip), already included on Python 2.7.9+ or Python 3.4+ versions. You can install these dependencies running the command:

```
sudo pip install -r requirements.txt 
```

#### OpenCV

You also need to install OpenCV, on version 3+. You can install it following the instructions given in one of the following links:

* [Install OpenCV 3.0 and Python 3.4+ on Ubuntu](http://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/) - In this tutorial you need to compile the OpenCV code, but you can run the latest version available on its repository. 

After installing it, the following commands should work perfectly:
 
 ```
 python3
 >>> import cv2
 ```

#### Docker

You can run the [Mosquitto MQTT Broker](https://mosquitto.org/) in an easier way using [Docker](https://www.docker.com/). To install *Docker* you can following the [instructions](https://docs.docker.com/engine/installation/linux/ubuntu/) available on its website.


### Running

First you must download the image that will be used to run the MQTT broker. You can do it running the command:

```
docker pull toke/mosquitto
```

Now you can run the Mosquitto MQTT Broker with Docker using the following command:

```
docker run -ti -p 1883:1883 -p 9001:9001 --name mosquitto toke/mosquitto
```

In a new terminal window, navigate to the project folder and run the following command: 

```
python camera-tracker.py --mqtt <MOSQUITTO_IP>
```

On *MOSQUITTO_IP* value, given as argument to **--mqtt** (or -q) you should pass the IP from the MQTT Broker host. When running Docker on Linux, it will be **localhost** (or 127.0.0.1). On other systems it will be the **IP from the created VM** (e.g 192.168.99.100). You can omit this argument if you don't want to send the calculated information to the MQTT Broker (when checking the environment or running tests, for example).   

You can also pass the argument **--showimage** (or -i) to show the image output with the processing results.

## Built With

* [Python](https://www.python.org/) - The programming language used
* [OpenCV](http://opencv.org/) - Image processing library used
* [MQTT](http://mqtt.org/) - Connectivity protocol used

## Version

0.1.0

## Authors

* **Lucas Cristiano** - *Initial work* - [Github page](https://github.com/lucascriistiano)
* **Roberto Dantas** - *Initial work* - [Github page](https://github.com/7robertodantas)
* **Lucas Cristiano** - *Initial work* - [Github page](https://github.com/PCoelho07)

See also the list of [contributors](https://github.com/MeFormei/camera/contributors) who participated in this project.
