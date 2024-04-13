# whisper-locally-running
This is a program I created to use OpenAIs Whisper model for speech-to-text-transcription. It runs locally. It includes a simple GUI and a basic recording functionality.

The user interface text is in German. I will add an English version as soon as it is finished. 

## Getting Started

### Running the program as python file
Download the 'Wisp_German.py' and 'requirements.txt' files and save them in a subfolder of the Documents folder on your computer. The system is primarily designed with the use of the 'Soundaufnahmen' folder in mind, but the subfolder can have any name.
Use the windows powershell to navigate to this folder. For the folder 'Soundaufnahmen', you can do this with the following code.
  ```sh
cd Documents/Soundaufnahmen
 ```
Before you can run the program, you need to make sure python and the necessary dependencies are installed.
Python can be downloaded from the internet, if you do not have it already.

Optional: Set up a virtual environment.
To install the python packages, it is recommended that you create a virtual environment. The code below creates a virtual environment named 'wispvenv'.
  ```sh
python3 -m venv wispvenv
 ```
Once it is created, you will have to activate it:
  ```sh
wispvenv\Scripts\Activate.ps1
 ```

Install dependencies:
  ```sh
pip3 install -r requirements.txt
 ```
Once all dependencies have been successfully installed, you can start the program:
  ```sh
python3 Wisp_German.py
 ```

