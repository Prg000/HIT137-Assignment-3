# HIT137 Group Assignment 3 - Spot the Difference Game

Group Members
- Pramod Gelal (Github: prg000)
- Bikash Acharya (Github: 9Bikash)

# What is this?
A computer-based game with two nearly identical pictures displayed side by side. By clicking on the differences in the altered image, you'll discover all 5 hidden differences

## How to install
```
pip install -r requirements.txt
```

## How to run
```
python main.py
```

# How to play
1. Click on "Load Image" and select any image on your computer.
2. Select the right picture in which you believe there is a difference.
3. Red circle will appear when you discover one
4. You have 3 guesses allowed per picture.
5. Click on "Reveal All" if you want to view all answersanswers

#Files
- alterations.py - contains the image alteration classes
- image_processor.py - handles image loading and modification
- game_state.py - tracks score and mistakes
- app.py - the main GUI window
- main.py - run this to start the game