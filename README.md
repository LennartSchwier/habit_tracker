# Habit Tracking App
**Create, manage, and analyse user defined habits.**

## How to get started
This application runs with Pyton 3.x and is controlled through a command line interface.
To install the latest version of Python 3 please visit [Python Downloads](https://www.python.org/downloads/)
and follow the instructions.

### Installation and program start:
Now you are ready to install the application.
1. Clone the repository into a folder of your choice:

```git clone https://github.com/LennartSchwier/habit_tracker.git```

2. Initialize a virtual environment to install all requirements: 

```TODO requirements```

3. Run the program: 

```python3 main.py```


### First steps:
Create a new account by selecting *Sign Up* on the login screen and enter a username and password when prompted.
If you have an existing account just go to *Log In*. Once logged in you can add your first habit.
Go to *Add a new habit* and enter a descriptive name and the repetition period in days.


## Features

### Deadlines
The habits are created with a user defined periodicity in days. 
The first deadline is the moment of creation plus the periodicity. 


## Testing
All unit tests can be found in the test_project.py file. They can be executed with

```pytest .```

This program also comes with a database with predefined users and habits. 
The database is created on program start and will be deleted once the program is exited.
To see the user with predefined habits log in as *test user 1* with password *test user 1*. 
For testing the administrator functionality log in as *Admin* with password *Admin*.