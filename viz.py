import math
import calendar

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt


def get_bounds(df, c, l, h):
    return tuple(df.loc[[l, h], c])


def round_f(n, decimals, agg):
    if decimals < 0:
        raise ZeroDivisionError()

    factor = 10**decimals

    if agg == 'floor':
        return math.floor(n * factor) / factor
    elif agg == 'ceil':
        return math.ceil(n * factor) / factor
    else:
        raise ValueError("Aggregate function must be only ceil or floor.")


def theme_sleeptime_plt(ax, df):
    border = lambda v, c, agg: math.floor(round_f(df[c].min(), 1, agg) * 24) / 24 
    
    start = border(df, 'Sleep Time', 'floor')
    end = border(df, 'Wake Time', 'ceil')
    ticks = np.linspace(start, end, 6)
    labels = (
        pd.to_datetime("1900-01-01") + 
        pd.to_timedelta(ticks * 24 % 24, 'h')
    ).strftime("%I:%M %p")
    
    ax.set_yticks(ticks, labels)
    ax.set_title("Sleep Time of the year")
    plt.fill_between(df.index, df['Sleep Time'], df['Wake Time'], alpha=0.3)
    
    return ax


def theme_durations_barplt(ax, df):
    start, end = get_bounds(df.describe(), 'Duration', 'min', 'max')

    ticks = np.linspace(
        round_f(start, 0, 'floor'), 
        round_f(end, 0, 'ceil'), 
        5
    )
    
    ax.set_ylim(ticks.min(), ticks.max())
    
    ax.set_yticks(ticks)
    ax.set_xticks(np.arange(df.shape[0]), df.index.strftime("%y-%m-%d"))
    ax.get_figure().suptitle('')
    ax.tick_params('x', rotation=45)

    return ax


def theme_weekdays_boxplt(ax, df):
    start, end = get_bounds(df.describe(), 'Duration', '25%', '75%')

    ticks = np.linspace(
        round_f(start, 0, 'floor'), 
        round_f(end, 0, 'ceil'), 
        5
    )
    
    ax.set_yticks(ticks)
    weekdays = [s[:3] for s in calendar.day_name]
    ax.set_xticks(
        np.arange(len(weekdays)) + 1,
        labels=weekdays
    )
    ax.get_figure().suptitle('')
    
    return ax