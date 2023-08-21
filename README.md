# Requirements
Python 3
Vosk

# How this bot works?

Install python packages
```
pip install -r requirements.txt
```
Download and unpack chromedriver for [Selenium](https://chromedriver.chromium.org/downloads)

Download [Vosk model](https://alphacephei.com/vosk/models) and unpack it in the main directory.
**Note:** Folder should be called `model`.

Modify `config.py-example` and save it as `config.py`.

```
python main.py -p Joffre -t "Joffre Lakes - Trail" -d Monday
```

# Looking for Trail names?

## Joffre
Joffre Lakes - Trail

## Golden
Alouette Lake Boat Launch Parking - Parking

Alouette Lake South Beach Day-Use Parking Lot - Parking

Gold Creek Parking Lot - Parking

West Canyon Trailhead Parking Lot - Parking

## Garibaldi
Cheakamus - Parking

Diamond Head - Parking

Rubble Creek - Parking

# What about time options?
    visitTimeDAY <-- All day pass
    visitTimeAM  <-- AM pass
    visitTimePM  <-- PM pass
