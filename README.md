# Habit Tracking App
**Create, manage, and analyse user defined habits.**


## How to get started
This application runs with Pyton 3.x and is controlled through a command line interface.
To install the latest version of Python 3 please visit [Python Downloads](https://www.python.org/downloads/)
and follow the instructions.

### Installation and program start:
Now you are ready to install the application.
1. Clone the repository into a folder of your choice:

```
git clone https://github.com/LennartSchwier/habit_tracker.git
```

2. Initialize a virtual environment to install all requirements: 

```
TODO
```

3. Run the program: 

```
python3 main.py
```

### First steps:
Create a new account by selecting *Sign Up* on the login screen and enter a username and password when prompted.
If you have an existing account just go to *Log In*. Once logged in you can add your first habit.
Go to *Add a new habit* and enter a descriptive name and the repetition period in days.


## Features

### Deadlines
The habits are created with a user defined periodicity in days. 
The first deadline is the moment of creation plus the periodicity. 
Once the user has completed a task the new deadline of the corresponding habit is
that exact moment plus the periodicity.

### Streaks
Each habit has two different streaks: a current streak and a record or longest streak.
When the user completes the task of a habit within the deadline, the current streak is increased by one.
If the current streak is longer than the longest streak saved for this habit, 
the current streak becomes the new longest streak.
Should the deadline be missed the current streak is reset to zero.

### Pause/Reactivate Habits
It is possible to pause and reactivate stored habits. 
If a habit is paused, the deadline is pushed to the far future (i.e., end of the year 9999). 
Thus, the deadline will not be missed and the current streak will be saved.
Upon reactivation of the habit the next deadline is the exact moment of reactivation plus the defined periodicity.

### Administrator tasks
Registered administrators can delete user accounts. 
If a user account is removed, all user information, stored habits, and completed tasks of that user are 
permanently deleted.
An administrator can not use the normal functionalities of the habit tracker app.


## Testing/Demonstration
All unit tests can be found in the test_project.py file. They can be executed with

```
pytest .
```

For demonstration purpose this program also has a demo mode. 
When in demo mode, the program connects to a database that already contains different users and
various habits.
To see the user with predefined habits log in as *test user 1* with password *test user 1*. 
For testing the administrator functionality log in as *Admin* with password *Admin*.
The database will always be deleted upon program termination.
To start the program in demo mode enter the command:
```
python3 demo.py
```