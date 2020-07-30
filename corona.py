import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time


API_Key = "tqNcZJuSXRJD"
PROJECT_TOKEN = "tPMBmKUYHinw"
RUN_TOKEN = "tTC4fQjqDvat"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key" : self.api_key
        }
        self.data = self.get_data()
    
    def get_data(self):
        response = requests.get(f"http://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data", params= self.params)
        data = json.loads(response.text)
        return data
    
    def get_total_cases(self):
        data = self.data['Total']
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['values']

    def get_total_deaths(self):
        data = self.data['Total']
        for content in data:
            if content['name'] == "Deaths:":
                return content['values']
    def get_total_recovered(self):
        data = self.data['Total']
        for content in data:
            if content['name'] == "Recovered:":
                return content['values']
        return "0"
    def get_country_data(self,country):
        data = self.data['Country']
        for content in data:
            if content['name'].lower() == country.lower():
                return content
        return "0"
    
    def get_country_list(self):
        countries =[]
        for country in self.data['Country']:
            countries.append(country['name'].lower())
        return countries

    def update_data(self):
        response = requests.post(f"http://www.parsehub.com/api/v2/projects/{self.project_token}/run", params= self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(5)


        t = threading.Thread(target=poll)
        t.start()


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("voice", "com.apple.speech.synthesis.voice.veena")
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception: ", str(e))
    return said.lower()

def main():
    print("Program started.")
    data = Data(API_Key, PROJECT_TOKEN)
    endP = "stop"
    country_list = data.get_country_list()

    TOTAL_PATTERNS = {
                    re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
                    re.compile("[\w\s]+ total cases"): data.get_total_cases,
                    re.compile("total cases [\w\s]"): data.get_total_cases,
                    re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
                    re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
                    re.compile("total deaths [\w\s]"): data.get_total_deaths,
                    }
    COUNTRY_PATTERNS = {
                    re.compile("[\w\s]+ cases [\w\s]+"): lambda Country: data.get_country_data(Country)['total_country_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda Country: data.get_country_data(Country)['total_country_deaths'],
                    }
    UPDATE_COMMAND = "update"
    loop_number = 0
    while True:
        
        if loop_number ==0:
            speak("Hello, how may i help you?")
            loop_number+=1
        else:
            time.sleep(2)
            speak("I am Listening")
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
        
        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment!"
            data.update_data()
            
        if result:
            speak(result)
        elif ((text.find(endP) != -1) or text == ""):  
            print("exit")    #stop loop
            speak("Thank you for using my service.")
            break
        else:
            speak("I am sorry. i cannot help you with that!")

        

main()