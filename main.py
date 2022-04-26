import questionary
from db_logic import connect_to_db, add_habit, remove_habit, \
    update_habit_streaks, get_habit_by_name, get_all_habits
from analysis import analyse_habits
from custom_exceptions import HabitSaveError, HabitDeletionError
from habit import Habit
from datetime import datetime, timedelta

feedback_style = "bold fg:cyan"
custom_style = questionary.Style([
    ("qmark", "red bold"),
    ("question", "white bold"),
    ("pointer", "red bold")])

stop = False
enter = False


def cli():
    db = connect_to_db()  # ":memory:"
    questionary.print("Hello! 🤖", style=feedback_style)
    global stop
    while not stop:
        global enter
        enter = questionary.confirm("Shall we start?", style=custom_style, auto_enter=False).ask()
        while enter:
            choice = __show_home_screen(db)
            if choice == "Add a new habit":
                __add_a_new_habit(db)
            elif choice == "Complete a task":
                __complete_a_task(db)
            elif choice == "Remove a habit":
                __remove_habit(db)
            elif choice == "Analyse my habits":
                __analyse_all_my_habits(db)
            elif choice == "Exit program":
                __exit_program()
        else:
            stop = True


def __show_home_screen(db):
    """Function that shows all stored habits and possible actions to user. It returns user's choice as :var choice"""
    if __create_list_of_habits_properties(db):
        questionary.print(
            "Alright, let's go..! 🦾\nThese are your currently tracked habits:", style=feedback_style
        )
        for habit in __create_list_of_habits_properties(db):
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


def __add_a_new_habit(db):
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
        add_habit(db, new_habit)
        __check_saved_successfully(db, new_habit.name)
    else:
        questionary.print("Changes have been discarded.", style=feedback_style)


def __complete_a_task(db):
    habit_to_update = questionary.select("Select a habit you want to complete a task for:",
                                         choices=[habit[0] for habit in __create_list_of_habits_properties(db)]).ask()
    update = questionary.confirm(
        f"Complete task for {habit_to_update}?", style=custom_style, auto_enter=False
    ).ask()
    if update:
        update_habit_streaks(db, habit_to_update)
    else:
        questionary.print("Habit has not been updated", style=feedback_style)


def __remove_habit(db):
    """Function that removes a habit after user confirmation and gives feedback from database"""
    old_habit = questionary.select("Select a habit you want to remove:",
                                   choices=[habit[0] for habit in __create_list_of_habits_properties(db)]).ask()
    delete = questionary.confirm(f"Delete {old_habit}?", style=custom_style, auto_enter=False).ask()
    if delete:
        remove_habit(db, old_habit)
        __check_deleted_successfully(db, old_habit)
    else:
        questionary.print("Habit has not been deleted.", style=feedback_style)


def __analyse_all_my_habits(db):
    in_analysis = True
    while in_analysis:
        task = questionary.select("What would you like to see?", style=custom_style,
                                  choices=["Show currently tracked habits.",
                                           "Show all habits with same period.",
                                           "Show habit with longest streak.",
                                           "Return to home screen."]
                                  ).ask()
        if task == "Show currently tracked habits.":
            __print_result(analyse_habits(db, task))
        elif task == "Show all habits with same period.":
            period = questionary.text("Enter period:",
                                      validate=lambda number: True if number.isnumeric()
                                      else "Please enter a natural number!",
                                      style=custom_style
                                      ).ask()
            output = analyse_habits(db, task, period=int(period))
            if output:
                __print_result(output)
            else:
                questionary.print(f"You are not tracking any habits with a period of {period} days.",
                                  style=feedback_style
                                  )
        elif task == "Show habit with longest streak.":
            __print_result(analyse_habits(db, task))
        else:
            in_analysis = False


def __exit_program():
    """Function that terminates the program after asking for user confirmation"""
    if questionary.confirm("Are you sure you want to exit?", style=custom_style, auto_enter=False).ask():
        questionary.print("Bye Bye! 🦄", style=feedback_style)
        global enter
        enter = False


def __create_list_of_habits_properties(db):
    """Function that creates a list of names of all habits stored in the given database"""
    all_habits = get_all_habits(db)
    if len(all_habits) != 0:
        return [[habit.name, habit.deadline, habit.current_streak, habit.longest_streak] for habit in all_habits]


def __check_saved_successfully(db, name: str):
    """Function that checks if the item is saved in database"""
    if type(get_habit_by_name(db, name)) is Habit:
        questionary.print("New habit saved successfully!", style="bold fg:cyan")
    else:
        raise HabitSaveError


def __check_deleted_successfully(db, name: str):
    """Function that checks if the item is deleted from database"""
    if get_habit_by_name(db, name) is None:
        questionary.print("Habit deleted successfully!", style="bold fg:cyan")
    else:
        raise HabitDeletionError


def __print_result(result):
    """Function that prints output from the analysis module"""
    for habit in result:
        questionary.print(habit, style=feedback_style)


if __name__ == "__main__":
    cli()
