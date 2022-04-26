import questionary
import hashlib
from db_logic import connect_to_db, add_habit, remove_habit, \
    update_habit_streaks, get_habit_by_name, get_all_habits
from user_logic import add_user, get_user_by_name, validate_password, get_all_users, remove_user
from analysis import analyse_habits
from custom_exceptions import HabitSaveError, HabitDeletionError
from habit import Habit
from user import User
from datetime import datetime, timedelta

feedback_style = "bold fg:cyan"
custom_style = questionary.Style([
    ("qmark", "red bold"),
    ("question", "white bold"),
    ("pointer", "red bold")])

stop = False
enter = False
logged_in_as = ""


def cli():
    db = connect_to_db(":memory:")  # ":memory:"

    cur = db.cursor()
    cur.execute("""INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)""",
                {
                    "user_id": "some id",
                    "user_name": "some user",
                    "password": "some password",
                    "is_admin": "False"
                })
    cur.execute("""INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)""",
                {
                    "user_id": "some id",
                    "user_name": "other user",
                    "password": "user password",
                    "is_admin": "False"
                })
    cur.execute("""INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)""",
                {
                    "user_id": "some id",
                    "user_name": "admin",
                    "password": "789cf532419e99b67093f10b9059465900d073c466c25efd00771189d38f7e66",  # "debug"
                    "is_admin": "True"
                })

    questionary.print("Hello there and welcome to the Habit Tracker! 🤖", style=feedback_style)
    global stop
    while not stop:
        login = questionary.select("Please choose:", style=custom_style, choices=["Login", "Sign Up", "Exit"]).ask()
        if login == "Login":
            __login(db)
        elif login == "Sign Up":
            __sign_up(db)
        else:
            pass
        global enter
        while enter:
            choice = __show_home_screen(db, logged_in_as)
            if choice == "Add a new habit":
                __add_a_new_habit(db, logged_in_as)
            elif choice == "Complete a task":
                __complete_a_task(db, logged_in_as)
            elif choice == "Remove a habit":
                __remove_habit(db, logged_in_as)
            elif choice == "Analyse my habits":
                __analyse_all_my_habits(db, logged_in_as)
            elif choice == "Exit program":
                __exit_program()
        else:
            stop = True


def __login(db):
    valid = False
    while not valid:
        questions = [
            {
                "type": "text",
                "name": "user_name",
                "message": "Enter your name to login:",
                "validate": lambda name: True if len(name) > 0 else "Please enter a name!"
            },
            {
                "type": "password",
                "name": "password",
                "message": "Please enter your password:",
                "validate": lambda password: True if len(password) else "Please enter a password!"
            }
        ]
        answers = questionary.prompt(questions)
        if validate_password(db, answers.get("user_name"),
                             hashlib.sha3_256(answers.get("password").encode()).hexdigest()
                             ):
            global logged_in_as
            logged_in_as = answers.get("user_name")
            global enter
            enter = True
            valid = True
        else:
            questionary.print("Name or password are incorrect.", style=feedback_style)


def __sign_up(db):
    user_name = questionary.text(
        "Please enter your name:",
        validate=lambda name: True if len(name) > 0 else "Enter a name!"
    ).ask()
    valid = False
    password = ""
    while not valid:
        first_entry = questionary.password(
            "Please enter a password:",
            validate=lambda phrase: True if len(phrase) > 0 else "Enter a password!"
        ).ask()
        second_entry = questionary.password(
            "Please enter the password again:",
            validate=lambda phrase: True if len(phrase) > 0 else "Enter a password!"
        ).ask()
        if first_entry == second_entry:
            password = hashlib.sha3_256(second_entry.encode()).hexdigest()
            valid = True
        else:
            questionary.print("Your passwords did not match.", style=feedback_style)
    new_user = User(user_name, password)
    add_user(db, new_user)
    if get_user_by_name(db, new_user.user_name):
        questionary.print("You have successfully signed up! Welcome 🖖", style=feedback_style)
        __login(db)
    else:
        questionary.print("Something went wrong...", style=feedback_style)


def __show_home_screen(db, user_name):
    """Function that shows all stored habits and possible actions to user. It returns user's choice as :var choice"""
    if get_user_by_name(db, user_name).is_admin == "True":
        __admin_tasks(db, active_user=user_name)
    elif __create_list_of_habits_properties(db, user_name):
        questionary.print(
            f"Alright {user_name}, let's go..! 🦾\nThese are your currently tracked habits:", style=feedback_style
        )
        for habit in __create_list_of_habits_properties(db, user_name):
            questionary.print(
                f"{habit[0]}. Deadline: {habit[1]}.", style="pink bold")
        answer = questionary.select("What do you want to do?", style=custom_style, choices=[
            "Add a new habit",
            "Complete a task",
            "Remove a habit",
            "Analyse my habits",
            "Exit program"
        ]).ask()
        return answer
    else:
        questionary.print("Alright, let's go..! 🦾\nCurrently you are not tracking any habits.",
                          style=feedback_style)
        answer = questionary.select("What do you want to do?", style=custom_style, choices=[
            "Add a new habit",
            "Exit program"
        ]).ask()
        return answer


def __add_a_new_habit(db, user_name: str):
    """Function that adds a new habit after user confirmation and gives feedback from database"""
    questions = [
        {
            "type": "text",
            "name": "name",
            "message": "Name of new habit?",
            "validate": lambda name: True if len(name) > 0 else "Please enter a name!"
        },
        {
            "type": "text",
            "name": "period",
            "message": "Length of period in days?",
            "validate": lambda number: True if number.isnumeric() else "Please enter natural number!"
        }
    ]
    answers = questionary.prompt(questions)
    habit_name = answers.get('name')
    habit_period = int(answers.get('period'))
    habit_deadline = datetime.now().replace(microsecond=0) + timedelta(days=habit_period)
    new_habit = Habit(name=habit_name, period=habit_period, deadline=habit_deadline)
    save = questionary.confirm(
        f"Save {new_habit.name} with length of period {new_habit.period} days?",
        style=custom_style,
        auto_enter=False
    ).ask()
    if save:
        add_habit(db, new_habit, user_name)
        __check_saved_successfully(db, new_habit.name, user_name)
    else:
        questionary.print("Changes have been discarded.", style=feedback_style)


def __complete_a_task(db, user_name: str):
    habit_to_update = questionary.select("Select a habit you want to complete a task for:",
                                         choices=[habit[0] for habit in
                                                  __create_list_of_habits_properties(db, user_name)]
                                         ).ask()
    update = questionary.confirm(
        f"Complete task for {habit_to_update}?", style=custom_style, auto_enter=False
    ).ask()
    if update:
        update_habit_streaks(db, habit_to_update, user_name)
    else:
        questionary.print("Habit has not been updated", style=feedback_style)


def __remove_habit(db, user_name: str):
    """Function that removes a habit after user confirmation and gives feedback from database"""
    old_habit = questionary.select("Select a habit you want to remove:",
                                   choices=[habit[0] for habit in __create_list_of_habits_properties(db, user_name)]
                                   ).ask()
    delete = questionary.confirm(f"Delete {old_habit}?", style=custom_style, auto_enter=False).ask()
    if delete:
        remove_habit(db, old_habit, user_name)
        __check_deleted_successfully(db, old_habit, user_name)
    else:
        questionary.print("Habit has not been deleted.", style=feedback_style)


def __analyse_all_my_habits(db, user_name: str):
    in_analysis = True
    while in_analysis:
        task = questionary.select("What would you like to see?", style=custom_style,
                                  choices=["Show currently tracked habits.",
                                           "Show all habits with same period.",
                                           "Show habit with longest streak.",
                                           "Return to home screen."]
                                  ).ask()
        if task == "Show currently tracked habits.":
            __print_result(analyse_habits(db, task, user_name))
        elif task == "Show all habits with same period.":
            period = questionary.text("Enter period:",
                                      validate=lambda number: True if number.isnumeric()
                                      else "Please enter a natural number!",
                                      style=custom_style
                                      ).ask()
            output = analyse_habits(db, task, user_name, period=int(period))
            if output:
                __print_result(output)
            else:
                questionary.print(f"You are not tracking any habits with a period of {period} days.",
                                  style=feedback_style
                                  )
        elif task == "Show habit with longest streak.":
            __print_result(analyse_habits(db, task, user_name))
        else:
            in_analysis = False


def __exit_program():
    """Function that terminates the program after asking for user confirmation"""
    if questionary.confirm("Are you sure you want to exit?", style=custom_style, auto_enter=False).ask():
        questionary.print("Bye Bye! 🦄", style=feedback_style)
        global enter
        enter = False


def __admin_tasks(db, active_user):
    in_admin_tasks = True
    while in_admin_tasks:
        all_users = get_all_users(db)
        for user in all_users:
            questionary.print(f"{user.user_name}. Is admin: {user.is_admin}", style=feedback_style)
        task = questionary.select("What do you want to do?", choices=["Delete user", "Exit"], style=custom_style).ask()
        if task == "Delete user":
            user_name = questionary.select("Select user you want to delete:",
                                           choices=[user.user_name for user in all_users]
                                           ).ask()
            if questionary.confirm(f"Are you sure you want to delete {user_name}?", auto_enter=False).ask():
                remove_user(db, active_user, user_name)
        else:
            in_admin_tasks = False
            __exit_program()


def __create_list_of_habits_properties(db, user_name: str):
    """Function that creates a list of names of all habits stored in the given database"""
    all_habits = get_all_habits(db, user_name)
    if len(all_habits) != 0:
        return [[habit.name, habit.deadline, habit.current_streak, habit.longest_streak] for habit in all_habits]


def __check_saved_successfully(db, habit_name: str, user_name: str):
    """Function that checks if the item is saved in database"""
    if type(get_habit_by_name(db, habit_name, user_name)) is Habit:
        questionary.print("New habit saved successfully!", style="bold fg:cyan")
    else:
        raise HabitSaveError


def __check_deleted_successfully(db, habit_name: str, user_name: str):
    """Function that checks if the item is deleted from database"""
    if get_habit_by_name(db, habit_name, user_name) is None:
        questionary.print("Habit deleted successfully!", style="bold fg:cyan")
    else:
        raise HabitDeletionError


def __print_result(result):
    """Function that prints output from the analysis module"""
    for habit in result:
        questionary.print(habit, style=feedback_style)


if __name__ == "__main__":
    cli()
