"""
Analyses the stored habits of the current user and returns them in a list.

Functions:
    analyse_habits() -> list
"""
def analyse_habits(choice: str, **kwargs) -> list:
    """
    Receives stored habits, performs different analysis task on them and returns the result as a list.

    Parameters:
        choice (str): The chosen analysis task
        kwargs: Filter active, inactive or completed habits from all stored habits

    Returns:
        (list): The result of the analysis
    """
    active_habits = kwargs.get("active_habits")
    inactive_habits = kwargs.get("inactive_habits")
    completed_tasks = kwargs.get("completed_tasks")
    period = kwargs.get("period", int)
    if choice == "Currently tracked habits.":
        return [
            f"""{habit.name}:
            Created: {habit.created}. Period: {habit.period} days. Deadline: {habit.deadline}. 
            Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}.
            ------------------------------------------"""
            for habit in active_habits]

    elif choice == "Paused habits.":
        print(inactive_habits)
        return [
            f"""{habit.name}: 
            Period: {habit.period} days. 
            Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}.
            ------------------------------------------"""
            for habit in inactive_habits]

    elif choice == "All habits with same period.":
        return [f"{habit.name}" for habit in active_habits if habit.period is period]

    elif choice == "Habit with longest streak.":
        longest_streaks = [habit.longest_streak for habit in active_habits]
        record_habits = [habit for habit in active_habits if habit.longest_streak is max(longest_streaks)]
        return [f"{habit.name} with {habit.longest_streak} times" for habit in record_habits]

    elif choice == "Completed tasks.":
        return [f"{completed_tasks.index(task) + 1}. Task. Completed on: {task.created}" for task in completed_tasks]
