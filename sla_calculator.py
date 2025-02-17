from datetime import datetime, timedelta, date, time

from models import BusinessHour, HolidayMaster

day_to_index = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}


def timedelta_to_time(timedelta_obj):
    total_seconds = timedelta_obj.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return time(hour=hours, minute=minutes)


def get_business_hour(customer_id):

    query = """
    SELECT day, starting_time, ending_time, weekly_holiday
    FROM business_hour
    WHERE customer_id = %s
    ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
    """
    rows = BusinessHour.query.filter_by(customer_id=customer_id).order_by(BusinessHour.day).all()
    print("business hours rows: ", rows)

    business_hours = {}

    for row in rows:
        day, starting_time, ending_time, weekly_holiday = row.day, row.starting_time, row.ending_time, row.weekly_holiday
        day_index = day_to_index[day]

        if weekly_holiday == 1:
            business_hours[day_index] = None
        else:
            business_hours[day_index] = {
                "from": timedelta_to_time(starting_time),
                "to": timedelta_to_time(ending_time)
            }

    return business_hours


def get_holiday_master(customer_id):

    query = """
    SELECT day 
    FROM holiday_master
    WHERE customer_id = %s
    """

    rows = HolidayMaster.query.filter_by(customer_id=customer_id).all()

    # holidays = [day[0] for day in rows]
    holidays = [holiday.day for holiday in rows]

    return holidays


def calculate_sla(customer_id, start_time, sla_minutes, business_hr_bypass, holiday_hour_bypass):
    business_hours_template = {
        0: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Monday
        1: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Tuesday
        2: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Wednesday
        3: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Thursday
        4: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Friday
        5: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Saturday
        6: {"from": time(hour=0, minute=0), "to": time(hour=23, minute=59)},  # Sunday
    }

    if holiday_hour_bypass == 'N':
        holidays = get_holiday_master(customer_id)
    else:
        holidays = []

    if business_hr_bypass == 'N':
        business_hours = get_business_hour(customer_id)
        if bool(business_hours) == False:
            business_hours = business_hours_template
    else:
        business_hours = business_hours_template

    def is_in_open_hours(dt) -> bool:
        day_hours = business_hours.get(dt.weekday())
        if day_hours is None:
            return False

        return dt.date() not in holidays and \
            day_hours["from"] <= dt.time() < day_hours["to"]

    def get_next_open_datetime(dt) -> datetime:
        while True:
            dt = dt + timedelta(minutes=1)
            if is_in_open_hours(dt):
                dt = datetime.combine(dt.date(), business_hours[dt.weekday()]["from"])
                return dt

    def add_hours(dt, minutes: int) -> datetime:

        while minutes > 0:
            if is_in_open_hours(dt):
                dt = dt + timedelta(minutes=1)
                minutes -= 1
            else:
                dt = get_next_open_datetime(dt)
        return dt

    result = add_hours(start_time, sla_minutes)
    return result







