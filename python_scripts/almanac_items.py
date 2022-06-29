#almanac_items.py
import pandas as pd
# import numpy as np
from astroplan import Observer, Target, FixedTarget
# from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
import astropy.units as u
from astropy.time import Time, TimeDelta, TimeDatetime
import matplotlib.pyplot as plt
# import datetime
from datetime import datetime, date, timedelta, time
# from pymeeus import Epoch, Mercury, Mars, Venus, Jupiter, Saturn

# Moon Illumination Chart

def moon_illumination_chart():
    """Return moon illumination chart as PNG for three months starting a week ago"""
    observer = Observer(longitude=-122.45 * u.deg, latitude=37.73 * u.deg,
                        elevation=150 * u.m, name='2Los', timezone='America/Los_Angeles')
    week_ago = (date.today() - timedelta(days=7))
    eleven_weeks_from_now = (date.today() + timedelta(days=83))
    start = datetime.strftime(week_ago, '%Y-%m-%d')
    end = datetime.strftime(eleven_weeks_from_now, '%Y-%m-%d')
    idx = pd.date_range(start=start, end=end, freq="D", tz='America/Los_Angeles') # '2022-09-01'

    sun_and_moon_df = pd.DataFrame(index=idx)

    sun_and_moon_df['MOON ILLUMINATION'] = observer.moon_illumination(Time(sun_and_moon_df.index))
    sun_and_moon_df.index.name = 'DATE'

    fig=plt.figure()
    ax=fig.add_subplot()
    sun_and_moon_df.plot(kind='line', y='MOON ILLUMINATION', linewidth=3, color='b', ax=ax, legend=None)
    plt.xlabel('', fontsize=14)
    plt.title('Moon Illumination', fontsize=20)
    fig.savefig('/Users/paulclanon/Documents/Python_Scripts/PycharmProjects/paulclanon_com/static/img/moon_illumination.png',
                bbox_inches='tight', dpi=300)

if __name__ == '__main__':
    moon_illumination_chart()
    print('Running almanac_items.py as main.')



