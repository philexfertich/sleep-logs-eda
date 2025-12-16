import calendar
import numpy as np

def get_quartile(table, quartile_name, column):
        summary = table[column].describe()
        return summary[quartile_name].astype(np.int64)


def weekdays_boxplot(ax, week_days):
    # Define edges of the graph using `get_quartile` 
    # and assign 25% and 75% of the summary to 
    # `lowest` and `highest` respectively.

    COL = 'Duration'
    lowest = get_quartile(week_days, '25%', COL)
    highest = get_quartile(week_days, '75%', COL) + 2
    del COL

    # Decorate axes
    ax.set_yticks(
        np.arange(lowest, highest), 
        labels=[
            f"{td.astype('timedelta64[h]').astype(int)} h"
            for td in np.arange(
                np.timedelta64(lowest, 'h'), 
                np.timedelta64(highest, 'h')
            )
        ]
    )
    ax.set_xticks(
        np.arange(1, 8),
        labels=[s[:3] for s in calendar.day_name]
    )
    ax.set_title("Time deltas by day of the week")
    ax.get_figure().suptitle('')
    ax.set_ylabel("Time")
    ax.set_xlabel("Week day")
    return ax