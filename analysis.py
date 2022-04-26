from db_logic import get_all_habits


def analyse_habits(db, task: str, **kwargs):
    period = kwargs.get("period", int)
    all_habits = get_all_habits(db)
    if all_habits:
        if task == "Show currently tracked habits.":
            return [
                f"{habit.name}. Period: {habit.period} days. Deadline: {habit.deadline}. Current streak: {habit.current_streak}. Longest streak: {habit.longest_streak}."
                for habit in all_habits]

        if task == "Show all habits with same period.":
            return [f"{habit.name}" for habit in all_habits if habit.period is period]

        if task == "Show habit with longest streak.":
            longest_streaks = [habit.longest_streak for habit in all_habits]
            record_habits = [habit for habit in all_habits if habit.longest_streak is max(longest_streaks)]
            return [f"{habit.name} with {habit.longest_streak} times" for habit in record_habits]
