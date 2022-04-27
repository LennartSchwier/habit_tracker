from db_logic import get_all_habits


def analyse_habits(db, task: str, user_name: str, **kwargs):
    period = kwargs.get("period", int)
    all_active_habits = get_all_habits(db, user_name, True)
    all_paused_habits = get_all_habits(db, user_name, False)
    if all_active_habits:
        if task == "Show currently tracked habits.":
            return [
                f"{habit.name}. Period: {habit.period} days. Deadline: {habit.deadline}. Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}."
                for habit in all_active_habits]

        if task == "Show all habits with same period.":
            return [f"{habit.name}" for habit in all_active_habits if habit.period is period]

        if task == "Show habit with longest streak.":
            longest_streaks = [habit.longest_streak for habit in all_active_habits]
            record_habits = [habit for habit in all_active_habits if habit.longest_streak is max(longest_streaks)]
            return [f"{habit.name} with {habit.longest_streak} times" for habit in record_habits]
