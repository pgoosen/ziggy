<img src="avatar-images/Ziggy_Full_Logo.png" width="250">

# Overview
Thanks to an **Offerzen** hackathon, we designed a game using the **Investec Programmable Banking API**, the Google Cloud Platform for processing and Slack to facilitate communications.

# The rationale
Many people struggle to build good financial habits thanks to the ease of shopping online and the instant gratification they receive, which is more alluring than watching a savings account grow a few cents at time. We want to help users build better financial awareness, one habit at a time, using gamification to incentivise good habits. Our solution gives users a fun and practical way of developing better spending habits, through individualised objectives and instant progress feedback.

# Demo video
*post video link here*

# Design Diagram
![Systems Diagram](/design/systems_diagram.png)

# Gameplay

## Goals
1. Define a goal by stating a *volume* or *value target* for a certain period.
2. You can link the goal to a specific Merchant, or do a manual categorisation of the transaction.
<img src="avatar-images/transaction_1.png">

*Transaction notification with manual categorisation option*


## Levels
We created an avatar with 5 levels, which represents the game level in a visual way.

![Game Levels](/avatar-images/Levels_no_background.png)

Level **up** or **down** based on remaining on you goal's target.

<img src="avatar-images/Avatar_Downgrade_to_L3.png" width="250">



*Notification received when leveling down to Level 3.*

<img src="avatar-images/Avatar_Upgrade_to_L2.png" width="250">

*Notification received when leveling up to Level 2.*


## Game rules :video_game:

### Health points
Health points (HP) represents the health of a player. A player can have a maximum of 50 HP. T

#### Gaining/Losing HP
A player will gain HP daily.
If a player levels up, the HP will be reset to the maxiumum of 50.

A player will lose HP:
* If the end date is reached for a spendings goal and the payer has gone over the goal limits,
* If the end date is reached for a savings goal and the player has not reached the target,
* When a transaction is made and the transaction is matched to an active goal.

### Experience points
Experience points (XP) tracks a player's progress. Players gain eperience points primarily by setting and completing goals. 

A player can gain a level by gaining a certain amount of experience points. Once a player gains a level, the XP is reset to 0, however, any extra XP is carried over.

#### Gaining/Losing XP
A player will gain XP:
* If a transaction is made, matched to a spendings goal and the goal limits has not been reached,
* If a new goal is made,
* If a goal is completed and the player has managed to stay within limits (spending) or reached target (savings)
* 

A player will lose XP:
* If the end date of a spendings goal has been reached and the player has gone over the goal limits,
* If the end date of a savings goal has been reached and the player has not reached target,
* If a transaction is made, matched to a spendings goal and the goal limits has been reached,

### Levels
The game consists of 5 levels. A player will level up by reaching a certain amount of XP points.
