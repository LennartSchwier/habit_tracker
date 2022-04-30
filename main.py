import questionary
import hashlib
import uuid
from setup import setup_db, teardown_db
from db_logic import add_habit, remove_habit, \
    update_streaks, get_habit_by_name, get_all_habits, update_active_status, get_all_tasks
from user_logic import add_user, get_user_by_name, validate_password, get_all_users, remove_user
from analysis import analyse_habits
from custom_exceptions import HabitSaveError, HabitUpdateError, HabitDeletionError
from habit import Habit
from user import User
from datetime import datetime, timedelta

feedback_style = "bold fg:cyan"
custom_style = questionary.Style([
    ("qmark", "red bold"),
    ("question", "bold"),
    ("pointer", "red bold")])

stop = False
enter = False
logged_in_as = ""
all_active_habits = []
all_inactive_habits = []


# TODO put choices strings in variables
# TODO make global lists of all active and all inactive habits

def cli():
    # db = connect_to_db()  # ":memory:"
    db = setup_db()

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
            elif choice == "Pause/Reactivate a habit":
                __pause_reactivate_habit(db, logged_in_as)
            elif choice == "Remove a habit":
                __remove_habit(db, logged_in_as)
            elif choice == "Analyse my habits":
                __analyse_all_my_habits(db)
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
    user_name = ""
    password = ""
    valid_user_name = False
    valid_password = False
    while not valid_user_name:
        user_name = questionary.text(
            "Please enter your name:",
            validate=lambda name: True if len(name) > 0 else "Enter a name!"
        ).ask()
        if get_user_by_name(db, user_name) is None:
            valid_user_name = True
        else:
            questionary.print(f"Sorry, the name '{user_name}' already exists.", style=feedback_style)
    while not valid_password:
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
            valid_password = True
        else:
            questionary.print("Your passwords did not match.", style=feedback_style)
    new_user = User(user_name, password)
    if password == "789cf532419e99b67093f10b9059465900d073c466c25efd00771189d38f7e66":  # TODO remove
        new_user.is_admin = "True"
    add_user(db, new_user)
    if get_user_by_name(db, new_user.user_name):
        questionary.print("You have successfully signed up! Welcome 🖖", style=feedback_style)
        __login(db)
    else:
        questionary.print("Something went wrong...", style=feedback_style)


def __show_home_screen(db, user_name):
    """Function that shows all stored habits and possible actions to user. It returns user's choice as :var choice"""
    global all_active_habits
    all_active_habits = get_all_habits(db, user_name, True)
    global all_inactive_habits
    all_inactive_habits = get_all_habits(db, user_name, False)
    if get_user_by_name(db, user_name).is_admin == "True":
        __admin_tasks(db, active_user=user_name)
    elif all_active_habits:
        questionary.print(
            f"Alright {user_name}, let's go..! 🦾\nThese are your currently tracked habits:", style=feedback_style
        )
        for habit in __create_list_of_habits_properties(db, user_name, True):
            questionary.print(
                f"{habit[0]}. Deadline: {habit[2]}.", style="pink bold")
        answer = questionary.select("What do you want to do?", style=custom_style, choices=[
            "Add a new habit",
            "Complete a task",
            "Pause/Reactivate a habit",
            "Remove a habit",
            "Analyse my habits",
            "Exit program"
        ]).ask()
        return answer
    elif all_inactive_habits:
        questionary.print(f"Alright {user_name}, let's go..! 🦾\nCurrently you only have paused habits.",
                          style=feedback_style)
        answer = questionary.select("What do you want to do?", style=custom_style, choices=[
            "Add a new habit",
            "Pause/Reactivate a habit",
            "Analyse my habits",
            "Exit program"
        ]).ask()
        return answer
    else:
        questionary.print(f"Alright {user_name}, let's go..! 🦾\nCurrently you are not tracking any habits.",
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
            "message": "Length of repetition period in days?",
            "validate": lambda num: True if num.isnumeric() and int(num) > 0 else "Please enter a natural number!"
        }
    ]
    answers = questionary.prompt(questions)
    habit_name = answers.get('name')
    habit_period = int(answers.get('period'))
    habit_deadline = datetime.now().replace(microsecond=0) + timedelta(days=habit_period)
    new_habit = Habit(
        habit_id=str(uuid.uuid4()),
        name=habit_name,
        created=datetime.now().replace(microsecond=0),
        period=habit_period,
        deadline=habit_deadline,
        is_active=True)
    save = questionary.confirm(
        f"Save {new_habit.name} with a repetition period of {new_habit.period} days?",
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
                                         choices=[habit.name for habit in all_active_habits]
                                         ).ask()
    old_streak_length = get_habit_by_name(db, habit_to_update, user_name).current_streak
    update = questionary.confirm(
        f"Complete task for '{habit_to_update}'?", style=custom_style, auto_enter=False
    ).ask()
    if update:
        update_streaks(db, habit_to_update, user_name)
        new_streak_length = get_habit_by_name(db, habit_to_update, user_name).current_streak
        if old_streak_length + 1 == new_streak_length:
            questionary.print(
                f"'{habit_to_update}' has been updated. Your current streak length is {new_streak_length}.",
                style=feedback_style
            )

    else:
        questionary.print(f"'{habit_to_update}' has not been updated", style=feedback_style)


def __pause_reactivate_habit(db, user_name):
    # TODO check that "reactivate a habit" is only shown when a paused habit exists
    in_pause = True
    while in_pause:
        global all_active_habits
        all_active_habits = get_all_habits(db, user_name, True)
        global all_inactive_habits
        all_inactive_habits = get_all_habits(db, user_name, False)
        if not all_active_habits and all_inactive_habits:
            task = questionary.select("Please select:",
                                      choices=["Reactivate a habit.", "Return to home screen."]).ask()
        elif all_active_habits and not all_inactive_habits:
            task = questionary.select("Please select:",
                                      choices=["Pause a habit.", "Return to home screen."]).ask()
        else:
            task = questionary.select("Please select:",
                                      choices=["Pause a habit.", "Reactivate a habit.", "Return to home screen."]).ask()
        if task == "Pause a habit.":
            new_status = False
            habit = questionary.select("Select a habit you want to pause:",
                                       choices=[habit.name for habit in all_active_habits]
                                       ).ask()
            pause = questionary.confirm(f"Pause {habit}?", style=custom_style, auto_enter=False).ask()
            if pause:
                update_active_status(db, habit, user_name, new_status)
                __check_updated_successfully(db, habit, user_name, new_status)
            else:
                questionary.print("Habit has not been paused.", style=feedback_style)
        elif task == "Reactivate a habit.":
            new_status = True
            habit = questionary.select("Select a habit you want to reactivate:",
                                       choices=[habit.name for habit in all_inactive_habits]
                                       ).ask()
            reactivate = questionary.confirm(f"Reactivate {habit}?", style=custom_style, auto_enter=False).ask()
            if reactivate:
                update_active_status(db, habit, user_name, new_status)
                __check_updated_successfully(db, habit, user_name, new_status)
            else:
                questionary.print("Habit has not been reactivated.", style=feedback_style)
        else:
            in_pause = False


def __remove_habit(db, user_name: str):
    """Function that removes a habit after user confirmation and gives feedback from database"""
    old_habit = questionary.select("Select a habit you want to remove:",
                                   choices=[habit.name for habit in all_active_habits]
                                   ).ask()
    delete = questionary.confirm(f"Delete {old_habit}?", style=custom_style, auto_enter=False).ask()
    if delete:
        remove_habit(db, old_habit, user_name)
        __check_deleted_successfully(db, old_habit, user_name)
    else:
        questionary.print("Habit has not been deleted.", style=feedback_style)


def __analyse_all_my_habits(db):
    in_analysis = True
    while in_analysis:
        if all_active_habits and all_inactive_habits:
            task = questionary.select("What would you like to see?", style=custom_style,
                                      choices=["Currently tracked habits.",
                                               "Paused habits.",
                                               "All habits with same period.",
                                               "Habit with longest streak.",
                                               "Completed tasks.",
                                               "Return to home screen."]
                                      ).ask()
        elif all_active_habits and not all_inactive_habits:
            task = questionary.select("What would you like to see?", style=custom_style,
                                      choices=["Currently tracked habits.",
                                               "All habits with same period.",
                                               "Habit with longest streak.",
                                               "Completed tasks.",
                                               "Return to home screen."]
                                      ).ask()
        else:
            task = questionary.select("What would you like to see?", style=custom_style,
                                      choices=["Paused habits.",
                                               "Return to home screen."]
                                      ).ask()

        if task == "Currently tracked habits.":
            __print_result(analyse_habits(task, active_habits=all_active_habits))
        elif task == "Paused habits.":
            __print_result(analyse_habits(task, inactive_habits=all_inactive_habits))
        elif task == "All habits with same period.":
            period = questionary.text("Enter period:",
                                      validate=lambda num: True if num.isnumeric() and int(num) > 0
                                      else "Please enter a natural number!",
                                      style=custom_style
                                      ).ask()
            output = analyse_habits(task, active_habits=all_active_habits, period=int(period))
            if output:
                __print_result(output)
            else:
                questionary.print(f"You are not tracking any habits with a period of {period} days.",
                                  style=feedback_style
                                  )
        elif task == "Habit with longest streak.":
            __print_result(analyse_habits(task, active_habits=all_active_habits))

        elif task == "Completed tasks.":
            habit_name = questionary.select("Select a habit you want to see the completed tasks for:",
                                            choices=[habit.name for habit in all_active_habits]).ask()
            questionary.print("Here should be some tasks...")
            output = analyse_habits(task, completed_tasks=get_all_tasks(db, habit_name))
            __print_result(output)
        else:
            in_analysis = False


def __exit_program():
    """Function that terminates the program after asking for user confirmation"""
    if questionary.confirm("Are you sure you want to exit?", style=custom_style, auto_enter=False).ask():
        questionary.print("Bye Bye! 🦄", style=feedback_style)
        teardown_db()
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


def __create_list_of_habits_properties(db, user_name: str, is_active):
    """Function that creates a list of names of all habits stored in the given database"""
    all_habits = get_all_habits(db, user_name, is_active)
    if len(all_habits) != 0:
        return [[habit.name, habit.period, habit.deadline, habit.current_streak, habit.longest_streak]
                for habit in all_habits]


def __check_saved_successfully(db, habit_name: str, user_name: str):
    """Function that checks if the item is saved in database"""
    if type(get_habit_by_name(db, habit_name, user_name)) is Habit:
        questionary.print("New habit saved successfully!", style="bold fg:cyan")
    else:
        raise HabitSaveError


def __check_updated_successfully(db, habit_name: str, user_name: str, new_status: bool):
    """Function that checks if the active status has changed in database"""
    if get_habit_by_name(db, habit_name, user_name).is_active is new_status:
        questionary.print("Habit updated successfully!", style="bold fg:cyan")
    else:
        raise HabitUpdateError


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
