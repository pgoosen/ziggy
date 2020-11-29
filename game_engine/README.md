# Ziggy Game Engine :unicorn: :video_game:

## About the project:
The Ziggy Game Engine is the game engine library developed for use during the 2020 Investec Programmable Banking Hackathon. The game engine conists of classes to enable developers to work with the avatar, goals, transactions and the Investec OpenAPI :credit_card:. 

### Built with:
Python3.8


## Getting started:
### Development setup:
#### Install requires:
* [Python3](https://www.python.org/)
* [Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
* The remainder of the requirements can be found in [requirements.txt ](./requirements.txt)

#### Setup pipenv:
* Install pipenv:

    `pip install --user pipenv`
* Create the virtual environment:

    `pipenv install --dev --three`
* Activate environment:

    `pipenv shell`
* Exit environment:

    `exit` or CTRL+C
* Alternatively run commands in environment without activating shell:

    `pipenv run`
* Remove environment:

    `pipenv --rm`


#### Compile new version of the game engine:

For linux based systems such as Ubuntu or WSL:
1. Navigate to game_engine root directory
2. Increase version number in [./game_engine/__init__.py](./game_engine/__init__.py)
3. Run in console:
    ```
    sh build_setup.sh
    ```

For Windows based systems:
1. Navigate to the game_engine root directory
2. Increase version number in [./game_engine/__init__.py](./game_engine/__init__.py)
3. Run in console:
    ```
    pipenv lock
    pipenv lock -r > requirements.txt
    pipenv run python -m pip install --upgrade setuptools wheel
    ```

This will create a .whl file in the `dist` folder. The .whl file can be copied and used in other code bases such as GCP cloud functions.

#### To use a new version of game_engine wheel: THIS IS FOR CLOUD FUNCTIONS
1. Copy the wheel from `./dist` to `./dist` folder where needed
2. Update wheel version number in the requirements.txt file where game_eninge is added
3. If using pipenv where game_engine is to be added: 

    Update wheel version number in Pipfile where game_engine is used
4. Run:
    ``` 
    pipenv lock
    pipenv lock -r > requirements.txt
    pipenv install --dev --three
    ```



## Game engine structure

The game consists of 3 key components: the avatar, goals and transactions. Each of these components are vital to the operation of the game.

### Avatar class
The avatar class if used for all things avatar related. It contains the helth point, experience points and level of the avatar. The avatar class also contains functions to increase and decrease health points, experience points and the avatar level.

The avatar has a maximum health points count of 50. 


```json
current_hp: 50
current_xp: 0
level: 1
```


#### To use the avatar class:
```python
# Avatar information as a dictionary object as shown above
avatar_info = {}
# avatar_id is the document id from database
avatar_id = ""

avatar = Avatar(config=avatar_info, avatar_id=avatar_id)

# Increase health points
impact_hp = self.avatar.increase_hp()
# Decrease health points
impact_hp = self.avatar.decrease_hp(critical_hit=True, critical_details = critical_hit)

# Increase experience points
impact_xp = self.avatar.increase_xp(xp_increase=0.5)
# Decrease experience points
impact_xp = self.avatar.decrease_xp(xp_decrease=1)


```

### Goal class
The goals class is used to manage the different aspects of the players' goals. Each player can have multiple goals with varying outcomes. A player set budget goals to try control their spending, or set goals to curb their spending at specific stores. A player can also set savings goals. A player can set goals based on a total amount to target, or a total number of transactions.

The following goal is a total amount based goal for a specific budget category:
```json
active: true
end_date: "2020-11-30"
goal_details:
budget_category:
    category: "ef8bdc9f-5c10-471a-9362-3166ede16ea8"
    merchant_based: false
    progress_value: 0
    spending_type: "66f19410-345e-4b5a-95b8-a9dff3df1f68"
    value_limit: 10000
goal_type: "3cd3f1ab-0e7e-421e-bfac-31806d5dcde0"
start_date: "2020-11-01"
```

The goals class also contains functions to process transactions against goals and calculate the impact ot the avatar. 

#### To use the goal class:
```python
avatar = get_avatar()
transaction = Transaction(transaction=transaction_info, transaction_id=transaction_id)

goal = Goal(config=goal_value, doc_id=goal_id)
goal.set_avatar(avatar)

# Match the transaction to the goal and process the impact on the avatar
hp_impact, xp_impact = goal.match_transaction_to_goal(transaction)

# Update the avatar
update_avatar(goal.avatar)
```

### Transactions class
The transaction class is used to represent all the transactions made using the Investec Programmable Banking card. The transaction class is used to represent the transactions as they are saved in the database. Each transaction document in the database contains the following information:
```json
    accountNumber: "00000000000"
    budget_category: "e2cffbed-9d1b-4406-a17d-b22d23ea297d"
    card:
        id: "00000000000000000000000000000000000000000000000000000000000000000"
    centsAmount: 10000
    currencyCode: "zar"
    dateTime: "Thu, 12 Nov 2020 22:00:00 GMT"
    merchant:
        category:
            code: "5462"
            key: "bakeries"
            name: "Bakeries"
        city: "Cape Town"
        country:
            alpha3: "ZAF"
            code: "ZA"
            name: "South Africa"
        name: "The Coders Bakery"
    reference: "simulation"
    type: "card"
```
#### To use the transactions class:
```python
# Transaction information as a dictionary object as shown above
transaction_information = {} 
# transaction_id is the document id from database
transaction_id = "" 

transaction = Transaction(transaction=transaction_information, transaction_id=transaction_id)
```

### lookups
Lookups are Enum classes used to represent data such as goal types and budget categories. This information is used when processing transactions and goals to determine how each transaction should affect the player's avatar.

The lookups can be found [here](./game_engine/lookups.py).

### Investec OpenAPI Wrapper
To be completed.



