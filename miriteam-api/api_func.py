import load
from xlrd.xldate import xldate_as_datetime

def get_quantity_of_calls(filepath: str) -> int:
    return len(load.load(filepath))


def get_workload_chart(filepath: str) -> dict:
    rv = dict()
    for call in load.load(filepath):
        date = call["date"]

        rv.setdefault(date, 0)
        rv[date] += 1

    return rv


def get_average_time_all(filepath: str) -> float:
    counter, summary = 0.0, 0.0
    for call in load.load(filepath):
        try:
            summary += 86400.0 * float(call["arrival"] - call["accepted"])
            counter += 1.0
        except:
            pass
    return summary / counter


def get_average_time_by_days(filepath: str) -> dict:
    rv = dict()
    for call in load.load(filepath):
        date = call["date"]

        rv.setdefault(date, (0.0, 0.0))
        try:
            rv[date] = (rv[date][0] + 86400.0 * float(call["arrival"] - call["accepted"]), rv[date][1] + 1.0)
        except:
            pass

    for date, time_counter in rv.items():
        rv[date] = abs(time_counter[0] / time_counter[1])

    return rv


def get_quantity_of_lateness(filepath: str) -> dict:
    rv = {"all": 0}
    for call in load.load(filepath):
        date = call["date"]
        try:
            time_in_road = 86400.0 * float(call["arrival"] - call["accepted"])
        except:
            pass

        if call["type"] == 1:
            if time_in_road <= 20 * 60:
                continue
        else:
            if time_in_road <= 2 * 60 * 60:
                continue

        rv["all"] += 1

        rv.setdefault(date, 0)
        rv[date] += 1

    return rv


if __name__ == "__main__":
    print(get_workload_chart('Big Data для оптимизации работы скорой помощи\Журнал активных вызовов 2020\Журнал активных вызовов 01-2020.xls'))