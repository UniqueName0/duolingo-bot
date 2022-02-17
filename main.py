from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import keyboard
import os


from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller as Con
mouse = Controller()
keyboard1 = Con()

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}


options = webdriver.ChromeOptions()
userPath = os.path.expanduser("~")
options.add_argument(f"--user-data-dir={userPath}\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument(r'--profile-directory=Profile 1')
#    ^used for logging into a specific chrome profile^


s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, desired_capabilities=caps, options=options)
driver.maximize_window()


driver.get('https://www.duolingo.com/')


skipPos = (284, 659)

while True:
    try:
        if keyboard.is_pressed('q'):    #wait for q key press
            logs_raw = driver.get_log("performance")
            logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

            def log_filter(log_):
                return (
                    log_["method"] == "Network.responseReceived"
                    and "json" in log_["params"]["response"]["mimeType"]
                )
            global sessions
            for log in filter(log_filter, logs):
                request_id = log["params"]["requestId"]
                resp_url = log["params"]["response"]["url"]
                x = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                if "sessions" in resp_url:   # sets variable sessions equal to network request "sessions" if found
                    sessions = x  # "sessions" network request contains duolingo question properties

            # with open("sessions.json", "w") as outfile:
            #    outfile.write(json.dumps(sessions))   # dumps sessions output to file, only really needed for debugging

            mouse.position = (713, 494)   # position of text box, could use bot without it
            time.sleep(0.5)
            mouse.click(Button.left)

            sBody = json.loads(sessions["body"])
            challenges = sBody["challenges"]  # contains questions and their properties
            for i in range(len(challenges)):
                try:
                    if challenges[i]["challengeGeneratorIdentifier"]["specificType"] == "speak":
                        print("speaking problem, skipping")   # bot can't do speaking problems
                        mouse.position = skipPos
                        time.sleep(.5)
                        mouse.click(Button.left)
                        for q in range(3):
                            keyboard1.type("\n")
                            time.sleep(1.5)
                        time.sleep(1)
                        raise KeyError
                    print(challenges[i]["correctSolutions"])
                    keyboard1.type(challenges[i]["correctSolutions"][0])
                    time.sleep(1)
                    for q in range(3):
                        keyboard1.type("\n")
                        time.sleep(1)
                    time.sleep(1)
                except KeyError:
                    try:
                        print(challenges[i]["correctIndex"])
                        keyboard1.type(str(challenges[i]["correctIndex"]+1))
                        time.sleep(1)
                        for q in range(3):
                            keyboard1.type("\n")
                            time.sleep(1)
                        time.sleep(1)
                    except KeyError:
                        try:
                            print(challenges[i]["correctIndices"])
                            if challenges[i]["correctIndices"][0] == 0 and challenges[i]["correctIndices"][1] == 1:
                                raise KeyError
                            keyboard1.type(str(challenges[i]["correctIndices"][0] + 1))
                            time.sleep(1)
                            for q in range(3):
                                keyboard1.type("\n")
                                time.sleep(1)
                            time.sleep(1)
                        except KeyError:
                            try:
                                print(challenges[i]["correctTokens"])
                                if challenges[i]["correctTokens"][0] == 0 and challenges[i]["correctIndices"][1] == 1:
                                    raise KeyError
                                for token in challenges[i]["correctTokens"]:
                                    keyboard1.type(token + " ")
                                time.sleep(1)
                                for q in range(3):
                                    keyboard1.type("\n")
                                    time.sleep(1)
                                time.sleep(1)
                            except KeyError:
                                print("couldn't read answer, skipping")
                                mouse.position = skipPos
                                time.sleep(.5)
                                mouse.click(Button.left)
                                for q in range(3):
                                    keyboard1.type("\n")
                                    time.sleep(1)
                                time.sleep(1)
            break
    except Exception as e:
        print(e)
        break