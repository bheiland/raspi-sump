'''Graph sump pit activity.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
try:
    import ConfigParser as configparser # Python2
except ImportError:
    import configparser # Python3

config = configparser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')
configs = {'unit': config.get('pit', 'unit'),
           'pit_depth':config.getint('pit', 'pit_depth'),
           'critical_water_level':config.getint('pit', 'critical_water_level'),
           'graph_top':config.getint('pit','graph_top'),
           'show_pit_depth':config.getint('graphics','show_pit_depth'),
           'show_graph_top':config.getint('graphics','show_graph_top'),
           'show_pit_bottom':config.getint('graphics','show_pit_bottom'),
           'show_float_off':config.getint('graphics','show_float_off'),
           'show_float_on':config.getint('graphics','show_float_on'),
           'show_legend':config.getint('graphics','show_legend'),
           'float_on_height':config.getfloat('graphics','float_on_height'),
           'float_off_height':config.getfloat('graphics','float_off_height')
           }

MPL_VERSION = int(mpl.__version__.split(".")[0]) # Matplotlib major version

if MPL_VERSION > 1:
    rcParams['date.autoformatter.hour'] = '%H:%M:%S' # Matplotlib 2.0 changed time formatting
    
def bytesdate2str(fmt, encoding='utf-8'):
    '''Convert strpdate2num from bytes to string as required in Python3.

    This is a workaround as described in the following tread;
    https://github.com/matplotlib/matplotlib/issues/4126/

    Credit to github user cimarronm for this workaround.
    '''

    strconverter = mdates.strpdate2num(fmt)

    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)
    return bytesconverter


def graph(csv_file, filename, bytes2str):
    '''Create a line graph from a two column csv file.'''
    critical_water_level = configs['critical_water_level']
    pit_depth = configs['pit_depth']
    graph_top = configs['graph_top']
    show_pit_depth = configs['show_pit_depth']
    show_graph_top = configs['show_graph_top']
    show_pit_bottom = configs['show_pit_bottom']
    show_float_off = configs['show_float_off']
    show_float_on = configs['show_float_on']
    float_on_height = configs['float_on_height']
    float_off_height = configs['float_off_height']
    show_legend = configs['show_legend']
    unit = configs['unit']
    date, value = np.loadtxt(csv_file, delimiter=',', unpack=True,
                             converters={0: bytes2str}
                             )
    fig = plt.figure(figsize=(10, 2.5))
    
    # axisbg is deprecated in matplotlib 2.x. Maintain 1.x compatibility
    if MPL_VERSION > 1:
        fig.add_subplot(111, facecolor='white', frameon=False)
    else:
        fig.add_subplot(111,axisbg='white', frameon=False)
    
    rcParams.update({'font.size': 9})

    plt.plot_date(x=date, y=value, ls='solid', linewidth=2, color='#FB921D',
                  fmt=':'
                  )
    title = "Sump Pit Water Level {}".format(time.strftime('%Y-%m-%d %H:%M'))
    title_set = plt.title(title)
    title_set.set_y(1.09)
    plt.subplots_adjust(top=0.86)
    ax = plt.subplots()
    #rcParams['font.size'] = 6
    plt.axhline(y=critical_water_level, color = 'red', label = 'Alarm Critical Level')
    if show_graph_top:
        plt.axhline(y=graph_top,label = 'Graph Top')
    if show_pit_bottom:
        plt.axhline(y = 0.1, label = 'Pit Bottom')
    if show_pit_depth:
        plt.axhline(y = pit_depth, label = 'Pit Depth')
    if show_float_on:
        plt.axhline(y = float_on_height,color ='brown', linestyle='dashed', label = 'Float switch on height')
        #plt.text(0.35,0.5,'Close M!', dict(size=30))
    if show_float_off:
        plt.axhline(y = float_off_height, color = 'green',linestyle ='dashed', label = 'Float Switch Off Height')
    if show_legend:
        plt.legend()
    if unit == 'imperial':
        plt.ylabel('inches')
    if unit == 'metric':
        plt.ylabel('centimeters')
    #rcParams['font.size'] = 9
    plt.xlabel('Time of Day')
    plt.xticks(rotation=30)
    plt.grid(True, color='#ECE5DE', linestyle='solid')
    plt.tick_params(axis='x', bottom='off', top='off')
    plt.tick_params(axis='y', left='off', right='off')
    plt.savefig(filename, dpi=72)
