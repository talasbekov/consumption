from datetime import timedelta, datetime

# Define the number of days in each month as a list
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def convert_days(days):
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    years = days // 365
    months = 0
    remaining_days = days % 365

    # Adjust for leap years
    for year in range(years):
        if is_leap_year(year + 1):
            remaining_days -= 1

    # Calculate the months and remaining days
    for i, days_in_current_month in enumerate(days_in_month):
        if remaining_days >= days_in_current_month:
            months += 1
            remaining_days -= days_in_current_month
        else:
            break

    return years, months, remaining_days


def get_iso_weekdays_between_dates(start_date, end_date, target_iso_weekday):
    # Convert the start_date and end_date to datetime objects
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())

    current_date = start_datetime + timedelta(
        days=(target_iso_weekday - start_datetime.isoweekday() + 7) % 7
    )

    iso_weekdays = []

    while current_date <= end_datetime:
        iso_weekdays.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=7)

    return iso_weekdays


def get_last_date_of_month(year, month):
    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)

    return last_date.strftime("%Y-%m-%d")
