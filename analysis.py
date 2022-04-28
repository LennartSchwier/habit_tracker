
def analyse_habits(task: str, **kwargs):
    active_habits = kwargs.get("active_habits")
    inactive_habits = kwargs.get("inactive_habits")
    period = kwargs.get("period", int)
    if task == "Show currently tracked habits.":
        return [
            f"{habit.name}. Period: {habit.period} days. Deadline: {habit.deadline}. Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}."
            for habit in active_habits]

    elif task == "Show paused habits.":
        print(inactive_habits)
        return [
            f"{habit.name}. Period: {habit.period} days. Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}."
            for habit in inactive_habits]

    elif task == "Show all habits with same period.":
        return [f"{habit.name}" for habit in active_habits if habit.period is period]

    elif task == "Show habit with longest streak.":
        longest_streaks = [habit.longest_streak for habit in active_habits]
        record_habits = [habit for habit in active_habits if habit.longest_streak is max(longest_streaks)]
        return [f"{habit.name} with {habit.longest_streak} times" for habit in record_habits]
