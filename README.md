# XX. Stemcell
**Cellname/Stem cell is a theoretical cell used for developing purposes**.  The cell contains snippets, sample code and the basic structure strictly necessary for a cell.

This file specifically is showing the structure of this README geared to give a general view of the cell for support as well as development. Uses example of itself, sharkbay, tilt and maps.
This section is like the brief description at the top of the game file. Describe basic setting of the cell and core mechanisms/gameplay.

Game design doc example:

This is what th team see entering the room.
This is what you can do/progress.
Maybe note stages.
You win by doing x.
You fail by doing y.


> [!IMPORTANT]
> Please replace all content with cell specific. Use general structure of header order.
> Will likely be trimmed down later when having used this structure more.

## Level 1/No Levels: A Pressing Matter / [Classic] Battle of the Bates
Press the three first buttons at the same time to get points and light up the second set of three buttons.
Press the second set's buttons at the same time also to get points and win maxpoints.

## Level 2: Matchmaker
The game begins with the buttons lightning up one by one and showing the associated animal on screen.
The player needs to match the animal seen with the right button when shown on screen. They get plus points if correct and negative if wrong, they need to gather to maxpoints.

## Level 3: Who in the Sea
The team is once more presented with the buttons, sounds and images. But this time the screen will ask a playful text question in style of "who in the room" and
the team has to answer by pressing the associated button. Once more they need to gather maxpoints.

# References
## Database parameters

| CellId | CellName     | Category | IPaddress         |
|:-------| :------------|:---------|:------------------|
| -      | -            | 0        | 192.168.14.cellid |
| 89     | WHACK A MOLE | 0        | 192.168.14.89     |



| MaxTime         | MinTime                          | Lights | After | MaxPoints | State |
|:----------------|:---------------------------------|:-------|:------|:----------|:------|
| seconds to fail | sec required not to assume cheat | -      | -     | -         | -     |
| 140             | 10                               | 15     | 60    | 100       | READY |



| ComputerModel | ComputerOS | ComputerMemory |
|:--------------|:-----------|:---------------|
| -             | -          | -              |
| -             | -          | -              |

## CSV Animals
1- Seagull
2- Seal
3- Dolphin
4- Walrus
5- Orca
6- Shark
(sharkbay)

## Images
The naming convention for the images is prisonername_TAG tags always in the order IM(age of the prisoner's face), NN(nickname), RN(Real Name) (tilt)

examples: GB_IM_RN

## Prisoners info
| Cellnumber | Image               | Nickname     | Realname          |
|:-----------| :-------------------|:-------------|:------------------|
|     1121   |                     |  codebreaker |(GB) Glenn Berger  |

# Testing
> [!NOTE]
> Sometimes one or more levels can't be properly tested from office.
> (keyboard enabled set 0 to be 10 and q being 11)
> OBS: Does not work properly with level 3 (maps) due to button values being different. (Cannot for example change your mind with choices. with buttons you can change ountries ny time by not pressing/pressing)

## Level 1 / No levels
* Pressing a (gui) button will print id in Info field
  (stemcell)
## Level 2
* Correct answer + 10pts
* Wrong answer - 20pts
* animal sound plays when pressing a button, regardless of right/wrong (standard points sounds signal right/wrong)
  (sharkbay)
## Level 3
* Correct answer + 10pts
* image is shown when pressing a button,regardless of right/wrong.
* Right/wrong answer is indicated both by green/red overlay of the image, as well as the standard points sounds.
  (sharkbay)
### Stages
| total pts. | pts/prisoner      | (stage) info/clue                 |
|:-----------|:------------------|:----------------------------------|
|     0-29   |  15               |(0)     image, nickname, realname  |
|     30-59  |  -                |(1)     image, nickname            |
|     60-79  |  10               |(2)     image                      |
|   80-100   |  -                |(3)     realname                   |
(tilt)


# Customization
## Config
(highlights what is possible to config to site in config file. explanation of usage in config file. source sharkbay.)
* The time before the buttons are presented
* Number of questions per game

## Resources
(can probably see in references, but sometimes even when wanting to change a single image/sound asset it needs to adhere to specific cell rules.)

# Notes
> [!NOTE]
> Actual buttons associated will differ for each game.

> [!TIP]
> set debug_text_on_screen to true in code to see the correct animal/button to press.

*Only english questions available

*Shark sound is called Thrash because they don't vocalize much

**Alternative idea to descriptions of levels could be to use the specification/walkthrough style in proposed game design document:**
1. When the game starts, all sensors lights are lit orange and the ambience sound is set to arcade music.
2. All the starts orange sensors are available to “collect” for points.
3. Team needs to figure out how to physically get the ball rolling over any of the sensors.
4. When a sensor is activated, a pinball impact sound is heard and the team is awarded 15 points (standard sound)…
5. … and the sensor’s light turns green and the ceiling cell light turns off for a second….
6. … to then turn on again and the sensors return to be fully reactivated to be available for points,and lit orange.
7. If team gathered over 100 points, the game is won.
8. If time is less than 0, the game is lost.
9.
_it would follow a chronological flow closer to the actual code structure, but likely be worse to parse for the more casual reader._

## Further Development
> [!NOTE] 
> General guides should not be put here, but in det doc folder.
> Snippets that used to be in game file is now in [Snippets doc](./../../../../../doc/Snippets.md)
> All data in here is on need to know basis, but header structure should stay.

> [!NOTE]  
> In another cell, this may contain how to safely do a resource upgrade of new images/questions,etc.

## Snippets
### Flags that git supports
> [!NOTE]  
> Highlights information that users should take into account, even when skimming.

> [!TIP]
> Optional information to help a user be more successful.

> [!IMPORTANT]  
> Crucial information necessary for users to succeed.

> [!WARNING]  
> Critical content demanding immediate user attention due to potential risks.

> [!CAUTION]
> Negative potential consequences of an action.