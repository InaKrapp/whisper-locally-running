# whisper-locally-running
This is Wisp, a program I created to use OpenAIs Whisper model for speech-to-text-transcription. It runs locally. It includes a simple GUI and a basic recording functionality.

There is an English and a German version available. Their graphical user interface texts are written in English and German, respectively. Furthermore, they work with different folders as default: The English version will expect the voice recordings to be in a folder named 'Sound recordings', the German version expects the folder to be named 'Soundaufnahmen' instead. It will not fail if the recordings are not there, but the user will have to navigate to a different folder manually if they store their recordings in another directory. 

## Getting Started

### Running the program as python file
Download the 'Wisp_English.py' and 'requirements.txt' files and save them in the same folder on your computer. The system is primarily designed with the use of the 'Sound recordings' (in German: 'Soundaufnahmen') folder in mind, so I suggest you store them there, but it can be anywhere.
Use the windows powershell to navigate to this folder. For the folder 'Sound recordings', you can do this with the following code.
  ```sh
cd "Documents/Sound recordings"
 ```
Before you can run the program, you need to make sure python and the necessary dependencies are installed. You need Python and ffmpeg if you do not have them already. They can be downloaded from the internet.

Optional: Set up a virtual environment.
To install the python packages, it is recommended that you create a virtual environment. The code below creates a virtual environment named 'wispvenv'.
  ```sh
python3 -m venv wispvenv
 ```
Once it is created, you will have to activate it. On the windows powershell, you can do that with the following command:
  ```sh
wispvenv\Scripts\Activate.ps1
 ```

Install dependencies:
  ```sh
pip3 install -r requirements.txt
 ```
Once all dependencies have been successfully installed, you can start the program:
  ```sh
python3 Wisp_English.py
 ```
If you plan to run the German version, download 'Wisp_German' instead and 
likewise, replace 'Sound recordings' in the cd command above by 'Soundaufnahmen'.

Once the file has started to run, the GUI (graphical user interface) should open. The GUI has been designed to be as self-explanatory as possible.

## Turning the program into an .exe file

Wisp is designed with the idea in mind to have a program that can be used with a graphical user interface by non-programmers. 
With pyinstaller, it can easily be turned into an .exe file that can be opened by clicking on it. Once you have pyinstaller installed, be sure to activate the virtual environment if you have not done that already.
  ```sh
pyinstaller Wisp_English.py --onefile --windowed
 ```
Unfortunately, it is a known problem that many antivirus programs classify .exe-programs created with pyinstaller as a threat. Running the .py-file may be easier.

## Some notes of caution
This program was developed using Python 3.11.9 on Windows 10. It works with Python 3.12.3, but it has not been tested on other systems or with other Python versions, and I can not guarantee it will be compatible with Windows 11.

The program allows the user to record their own voice. But it might not work with all microphones. It only supports mono recordings.
If you'd like to use a microphone that does not work with Wisp, you can use any other software to record, and choose the files for transcription with Wisp afterwards.
Wisp supports transcription of .wav and .mp3-files. It can also handle .m4a-files, it will convert them to mp3 to transcribe them.

Wisp uses the OpenAI-software Whisper for the transcription. Whisper is an Artificial Intelligence program. To turn the speech into text, it uses neural networks. The largest ones are the most precise, but using such a large neural network may take up considerable computing power. If you have a very powerful computer, this most likely will not be an issue, but if your computer is mostly used for standard office work such as writing E-Mails, it may be. Text generation may be very slow with a large model in this case.
For this reason, the user can select less accurate transcriptions. They may not be as accurate as the ones generated by the largest model, but they will be finished much faster.
The user can choose between 4 models, from a fast, but less precise one to the largest and most accurate.
Errors can happen to all models. However, if the speaker has a clear pronounciation and there is not much background noise, from my experience, even small and fast models perform fairly well.

I believe that I caught the most common errors. But this software is still in its early stage, so it is very likely I missed something. If you encounter any errors, please inform me and I will see if I can resolve them.
Likewise, feel free to suggest any feature that you would like to see added. You can open an issue in this repository, or contact me by E-Mail: ina.krapp@freenet.de

## Related and similar projects

In implementing the recorder, this project was very helpful for me: [audio-recorder-pyqt](https://github.com/dv66/audio-recorder-pyqt)

Several other projects to run Whisper locally exist on Github. This project is not based on anyone of them in particular. Of the ones that I know of, [vink](https://github.com/ssciwr/vink) is probably the most similar. But it still has some differences, so it might be worth trying out both for the users to decide which one they like best. If you are interested in live transcription, [whispered-secrets](https://github.com/john-sandall/whispered-secrets) may be interesting for you.
