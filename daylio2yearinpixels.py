""" Convert a Daylio export CSV to the format needed for Year in Pixels. """

import sys
import calendar

from datetime import datetime


def read_daylio(filename):
    """
    Read the daylio exported data.

    Parameters
    ----------
    filename : str
        The Daylio CSV file path.

    Returns
    -------
    daylio : tuple
        Tuple of the dates (as datetime objects) and the recorded moods
        (as a list of numbers as strings).

    """

    # Parse the Daylio output.
    columns = ['full_date', 'date', 'day', 'time', 'mood', 'activities', 'note']
    mood = {c: [] for c in columns}
    with open(filename, 'r') as f:
        next(f)  # skip header
        lines = f.readlines()
        prev_date = None
        for line in lines:
            line = line.strip().split(',')
            # if mood['full_date'] != prev_date:
            mood['full_date'].append(line[0])
            mood['date'].append(line[1])
            mood['day'].append(line[2])
            mood['time'].append(line[3])
            mood['mood'].append(line[4])
            mood['activities'].append(line[5])
            mood['note'].append(line[6])
            # prev_date = mood['full_date']


    # Convert the dates to datetime objects.
    dates = [datetime.strptime(i, r'%Y-%m-%d') for i in mood['full_date']]

    # Convert mood to a numeric value (higher = better).
    convert = {'amazing ': '5',
               'happy': '4',
               'average': '3',
               'sad ': '2',
               'horrible': '1'}
    for entry in convert:
        for count, m in enumerate(mood['mood']):
            if m == entry:
                mood['mood'][count] = convert[entry]

    return (dates, mood['mood'])


def write_year_in_pixels(daylio, output, year=None):
    """
    Take the output of read_daylio() and export it to the format expected by
    Year in Pixels.

    Parameters
    ----------
    daylio : tuple
        Tuple of dates (as datetime objects) and the recorded Daylio moods as
        numbers (low = bad, high = good).
    output : str
        File name to which to save the output.
    year : int, optional
        The year we're extracting from the Daylio output. If omitted, uses the
        year from the first entry in daylio.

    """

    # Year in Pixels wants the data shaped as a single line of digits, where
    # zero represents no data. Should be easy enough.

    if not year:
        year = daylio[0][0].year

    # Year in Pixels doesn't support leap days.
    yip = ['0'] * 365

    for (day, felt) in zip(daylio[0], daylio[1]):
        if day.year == year:
            # Year in Pixels doesn't support leap days, so drop them here.
            if calendar.isleap(year) and day.month == 2 and day.day == 29:
                print('Skipping leap day.')
                pass

            # 1st of January needs to be 0, not 1
            dayofyear = int(day.strftime('%j')) - 1

            # We have to remove a day from the index to account for Life in
            # Pixels not supporting leap years, but only in leap years and
            # only after the 29th February (the 60th day of the year).
            if calendar.isleap(year) and dayofyear > 60:
                dayofyear -= 1

            yip[dayofyear] = felt

    with open(output, 'wt') as f:
        f.write(''.join(yip))


if __name__ == '__main__':

    daylio = read_daylio(sys.argv[2])
    write_year_in_pixels(daylio, sys.argv[3], year=int(sys.argv[1]))
