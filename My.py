from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
import speech_recognition as sr
import pyaudio
import pyttsx3
import datetime
import wikipedia
import os
import cv2
import webbrowser as web
import random
import sqlite3
import shutil

Config.set('graphics','resizable',True)

class MyGrid(Widget):
    name = ObjectProperty(None)
    path = ObjectProperty(None)
    musicpath=ObjectProperty(None)

    counter=0
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    def btn(self):
        subName=self.name.text.lower()
        subPath=self.path.text
        con=sqlite3.connect('paths.db')
        if subPath!='' and subName!='':
            flag=1
            for row in con.execute("SELECT * FROM PATH"):
                if subName==row[0]:
                    flag=0
                    params=(subPath,subName)
                    con.execute("UPDATE PATH SET PATH=(?) WHERE NAME=(?)",params)
                    con.commit()
                    self.speak('path updated successfully, you can say open {} to open {}'.format(subName,subName))
            if flag:
                params = (subName, subPath)
                con.execute("INSERT INTO PATH VALUES(?,?)",params)
                con.commit()
                self.speak('path created successfully, you can say open {} to open {}'.format(subName,subName))
        con.close()
        self.name.text=''
        self.path.text=''

    def addMusic(self):
        subMusicPath=self.musicpath.text
        if subMusicPath!='':
            try:
                shutil.copy(subMusicPath,"Music")
                self.speak("Music Added successfully")
                self.musicpath.text=''
            except:
                self.speak("Try again please")
                self.musicpath.text=''


    def speak(self,audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def wishMe(self):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            self.speak("Good Morning!Sir")
        elif hour >= 12 and hour < 18:
            self.speak("Good Afternoon!Sir")
        else:
            self.speak("Good Evening!Sir")

    def takeCommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Listening")
            r.pause_threshold = .8
            audio = r.listen(source)
        try:
            self.speak("Recognizing")
            query = r.recognize_google(audio, language='en-in')
            print("User said: " + query)

        except Exception as e:
            self.speak("say again or check your internet connection")
            self.counter+=1
            return "None"
        return query

    def Pressed(self):
        self.wishMe()
        self.speak("I am Jarvis,How May i help you")

        while True:
            query = self.takeCommand().lower()
            if self.counter>5:
                break
            if 'wikipedia' in query:
                self.speak("Searching wikipedia...")
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                self.speak("According to wikipedia")
                self.speak(results)

            elif 'open youtube' in query:
                self.speak("here you go")
                try:
                    web.get('chrome').open('http://www.youtube.com')
                except:
                    web.open('http://www.youtube.com')

            elif 'open google' in query:
                self.speak("here you go")
                try:
                    web.get('chrome').open('https:\\www.google.com')
                except:
                    web.open('https:\\www.google.com')

            elif 'play music' in query:
                self.speak("have fun with music")
                music_dir = "Music"
                songs = os.listdir(music_dir)
                try:
                    os.startfile(os.path.join(music_dir, songs[0]))
                except:
                    self.speak("Add some music")


            elif 'picture' in query:
                maxTime = datetime.datetime.now() + datetime.timedelta(seconds=5)
                try:
                    camera=cv2.VideoCapture(0)
                    while (datetime.datetime.now() < maxTime):
                        return_value, image = camera.read()
                        cv2.imshow('camera', image)
                        cv2.waitKey(1)
                    cv2.imwrite('Pictures\\MyPicture'+str(random.randrange(0,100000000000000000000000))+'.jpeg',image)
                    cv2.destroyAllWindows()
                    del (camera)
                except:
                    self.speak("no camara found")

            elif 'exit' in query:
                self.speak("enjoy your day!")
                break
            else:
                con=sqlite3.connect('paths.db')
                for row in con.execute('SELECT * FROM PATH'):
                    if row[0] in query:
                        try:
                            os.startfile(row[1])
                        except:
                            self.speak("invalid path, update the path")


class MyApp(App):
    def build(self):
        return MyGrid()


if __name__ == '__main__':
    MyApp().run()
