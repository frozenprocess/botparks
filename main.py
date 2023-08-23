from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
import selenium.webdriver.support.expected_conditions as EC
import argparse
import os
import base64
import re
import speech_recognition as sr
from pydub import AudioSegment
import datetime as dt
import json
from text_to_num import alpha2digit

import config 

parser = argparse.ArgumentParser(prog="Bot park",description="Unlike chat-gpt and other useless AIs this one helps the humanity.",epilog="Helping humans since 2023")
parser.add_argument("--park","-p",default="Park name, (Garibaldi,Golden Ears,Joffre)",required=True)
parser.add_argument("--trail","-t",default="Trail name", required=True)
parser.add_argument("--visit_time",help="What time of day you like to visit the park? (eg. visitTimeDAY ,visitTimeAM ,visitTimePM)")
parser.add_argument("--day","-d",default="2",help="Name of the day that you like to book pass. (eg. Monday)",required=True)
parser.add_argument("--pass_count",default="1",help="In some cases you have to provide a pass count.")
parser.add_argument("--headless",default=False,help="Don't show me the browser.")

args = parser.parse_args()


first_name=config.first_name
last_name=config.last_name
email=config.email
captcha_folder=config.captcha_folder

service = Service("./chromedriver")
options = Options()

# No browser thank you.
if args.headless:
    options.add_argument("--headless=new")

driver = webdriver.Chrome(service=service,options=options)

driver.maximize_window()

driver.get("https://reserve.bcparks.ca/dayuse/")

# Wait for the page to load
wait = WebDriverWait(driver, timeout=10, poll_frequency=1)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-parks-list")))

# Get all them parks
parks = driver.find_element(By.TAG_NAME,"app-parks-list")

wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "booking-button")))

buttons = driver.find_elements(By.CLASS_NAME,"booking-button")
# Choices should be 1-3 days
# desired_date="Friday, August 18, 2023"
now = dt.datetime.now()
allowed_dates = [ now, now+dt.timedelta(days=+1), now+dt.timedelta(days=+2) ]

desired_date = None
for i in allowed_dates:
    if i.strftime('%A') == args.day:
        desired_date = i

if desired_date is None:
    print("Your desired day is is out of range, pick a day between %s and %s."%(allowed_dates[0].strftime('%A'),allowed_dates[2].strftime('%A')))
    exit()

redo = False
confirmation = False

for button in buttons:
        # Book a pass for Garibaldi Provincial Park
        # Book a pass for Golden Ears Provincial Park
        # Book a pass for Joffre Lakes Provincial Park
    if re.findall(args.park,button.accessible_name):
        wait.until(EC.element_to_be_clickable((By.XPATH,"//button[@aria-label='" + button.accessible_name + "']")))
        button.send_keys(Keys.ENTER)

        wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"date-input__calendar-btn")))

        date_picker = driver.find_element(By.CLASS_NAME,"date-input__calendar-btn")
        date_picker.click()

        wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@aria-label='" + desired_date.strftime("%A, %B %d, %Y") + "']")))

        date = driver.find_element(By.XPATH,"//div[@aria-label='" + desired_date.strftime("%A, %B %d, %Y") + "']")
        date.click()

        # There can be multiple trails whichi pass you like to take?
        pass_type = driver.find_element(By.ID,"passType")
        wait.until(EC.presence_of_all_elements_located((By.ID,"passType")))
        select = Select(pass_type)
        try:
            select.select_by_visible_text(args.trail)
        except:
            print("Please adjust your trail, possible options are")
            for option in select.options:
                if option.text == "--Select a pass type--":
                    continue
                print(option.text)
            exit()
        
        wait.until(EC.presence_of_all_elements_located((By.XPATH,"//input[@name='visitTime']")))
        tmp_visit = driver.find_elements(By.XPATH,"//input[@name='visitTime']")
        if args.visit_time is None:
            # lazy much ? pick the first available timeslot?
            visit_time = tmp_visit[0].get_property("id")
        else:
            # Somebody knows what he wants
            # visitTimeDAY
            # visitTimeAM
            # visitTimePM
            visit_time = argparse.visit_time

        wait.until(EC.presence_of_element_located((By.ID,visit_time)))
        if driver.find_element(By.ID,visit_time).get_attribute("disabled"):
            print(dt.datetime.now(),"Nothing available")
            exit()
        driver.find_element(By.XPATH,"//label[.//input[@id='" + visit_time + "']]").click()

        try:
            wait.until(EC.presence_of_element_located((By.ID,"passCount")))
            pass_count = driver.find_element(By.ID,'passCount')
            wait.until(EC.presence_of_all_elements_located((By.ID,"passCount")))
            select = Select(pass_count)
            select.select_by_visible_text(args.pass_count)
        except:
            print("no pass count")

        wait.until(EC.element_to_be_clickable((By.XPATH,'//button[normalize-space()="Next"]')))
        driver.find_element(By.XPATH,'//button[normalize-space()="Next"]').send_keys(Keys.ENTER)
        
        # EMAILS and STUFF
        driver.find_element(By.ID,"firstName").send_keys(first_name)
        driver.find_element(By.ID,"lastName").send_keys(last_name)
        driver.find_element(By.ID,"email").send_keys(email)
        driver.find_element(By.ID,"emailCheck").send_keys(email)

        wait.until(EC.presence_of_element_located((By.XPATH,"//label[contains(text(),'agree')]")))
        driver.find_element(By.XPATH,"//label[contains(text(),'agree')]").click()
        
        while confirmation is False: 

            if redo is True:
                # if Captcha solver failed then let's get a new one and save the attempt
                os.rename(captcha_folder+"captcha.mp3",captcha_solved+".mp3")
                wait.until(EC.presence_of_element_located((By.XPATH,"//button[.//span[normalize-space()='Try New Image']]")))
                driver.find_element(By.XPATH,"//button[.//span[normalize-space()='Try New Image']]").click()

            # play captcha
            wait.until(EC.presence_of_element_located((By.XPATH,"//button[.//span[normalize-space()='Play Audio']]")))
            driver.find_element(By.XPATH,"//button[.//span[normalize-space()='Play Audio']]").click()
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME,"audio")))
            captcha_unsolved = ""
            while re.match("^data:audio/mp3;",captcha_unsolved) is None:
                captcha_unsolved = driver.find_element(By.TAG_NAME,"audio").get_property("src")
            
            # Save captcha audio
            mp3 = re.match("^data:audio/mp3;base64,(.*?)$",captcha_unsolved)
            fh = open(captcha_folder+"captcha.mp3","wb")
            fh.write(base64.b64decode(mp3[1]))
            fh.close()
            
            # Convert the audio file to wave
            sound = AudioSegment.from_mp3(captcha_folder+"captcha.mp3")
            sound.export(captcha_folder+"captcha.wav", format="wav")
            
            # Solve Captcha 
            r = sr.Recognizer()
            file = sr.AudioFile(captcha_folder+"captcha.wav")
            with file as source:
                audio = r.record(source)
            
            # text = r.recognize_google(audio)
            text = json.loads(r.recognize_vosk(audio))['text']
            
            captcha_solved = re.match("please type in following letters or numbers (.*?)$",text)

            # Change numbers to Digigts and get rid of spaces
            captcha_solved = alpha2digit(captcha_solved[1],"en").replace("you","u").replace("kay","k").replace(" ","")

            driver.find_element(By.ID,"answer").send_keys(captcha_solved)
            # If captcha is solved then this shit pops out
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME,"captcha-valid")))
                break
            except:
                redo=True
        
        ## Captcha is valid let's submit
        wait.until(EC.element_to_be_clickable((By.XPATH,"//button[.//span[normalize-space()='Submit']]")))
        driver.find_element(By.XPATH,"//button[.//span[normalize-space()='Submit']]").click()

        ## I'm done whos the bot?
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH,"//div[.//h1[normalize-space()='Success, your reservation has been completed!']]")))
            confirmation = True
        except:
            confirmation = False

driver.quit()
