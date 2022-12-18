import json  # parse the data
import time  # delay
from datetime import datetime  # compare how long its been

import dearpygui.dearpygui as dpg  # create OS gui window
import pandas as pd  # graph the data
import requests  # make the api request
from playsound import playsound  # play sound duhh


def request():
    """Requests from the DMV api.
    Gets TypeId and ZipCode from gui.
    Returns a list of all locations
    that are availible right now.
    """
    var_zipcode = dpg.get_value('var_zipcode')
    var_typeid = dpg.get_value('var_typeid')
    if var_typeid == 'Apply for first time Texas DL/Permit':
        var_typeid = 71
    elif var_typeid == 'Change, replace or renew Texas DL/Permit':
        var_typeid = 81
    elif var_typeid == 'Class C Road Skills Test':
        var_typeid = 21
    elif var_typeid == 'Apply for first time Texas ID':
        var_typeid = 72
    errored = True
    while errored:
        try:
            locations = requests.post(
                url='https://publicapi.txdpsscheduler.com/api/AvailableLocation',
                data=json.dumps({
                    'TypeId': var_typeid,
                    'ZipCode': f'{var_zipcode}',
                    'CityName': '',
                    'PreferredDay': 0
                }),
                headers={'Origin': 'https://public.txdpsscheduler.com'}, timeout=30)
            errored = False
            print(f"Errored {errored}")
            return json.loads(locations.content.decode('utf-8'))
        except Exception as f:
            print(f"Errored {errored} {f}")
            print_console(False, "Error Connecting to API")
            time.sleep(5)


def parse(locations: list):
    """Parses the reqest.
    Takes in the locations and tdratio.
    Returns the lists: name,
    distance, date, days, and score.
    """
    var_tdratio = dpg.get_value('var_tdratio')
    name, distance, date, days, score, = [], [], [], [], []
    for location in locations:
        name.append(location['Name'])
        distance.append(location['Distance'])
        date.append(location['NextAvailableDate'])
        delta = datetime(
            int(location['NextAvailableDateYear']),
            int(location['NextAvailableDateMonth']),
            int(location['NextAvailableDateDay'])) - datetime.now()
        days.append(delta.days)
        score.append(
            int(100 -
                (delta.days + var_tdratio * int(location['Distance'])) / 2))
    return name, distance, date, days, score


def graph(name: list, distance: list, date: list, days: list, score: list, counter: int):
    """Graphs the locations on pandas.
    Takes in the name, distance, date, score, and counter.
    Returns the sorted pandas dataframe.
    """
    data = {
        'Name': name,
        'Distance': distance,
        'Date': date,
        'Days': days,
        'Score': score
    }
    for i in range(len(days)):
        dpg.set_item_label(f'location{i}', name[i])
        graph_data = dpg.get_value(f'location{i}')
        graph_data[0].append(counter)
        graph_data[1].append(days[i])
        dpg.set_value(f'location{i}', graph_data)
        dpg.set_axis_limits('y_axis', -10.0, 200.0)
        dpg.set_axis_limits('x_axis', graph_data[0][0] - 1,
                            graph_data[0][-1]*1.01)
        # dpg.set_axis_limits_auto("x_axis")
    dataframe = pd.DataFrame(data)
    dataframe = dataframe.sort_values(by=['Score'], ascending=False)
    return dataframe


def update(counter, current_score):
    """Calls and checks for changes.
    Takes in the counter and current_score.
    Prints if there has been a change and
    returns the latest score list.
    """
    name, distance, date, days, score = parse(request())
    if current_score == score:
        print_console(
            False,
            f'#{str(counter).zfill(6)} | SAME | Best Score: {max(score)} \r')
        graph(name, distance, date, days, score, counter)
        counter += 1
        return counter, score
    else:
        print_console(True, f'{str(graph(name, distance, date, days, score, counter))}\n\n')
        play_sound()
        return counter, score


def play_sound():
    """Plays the alert sound.
    Loops if the option is on.
    """
    if dpg.get_value('var_sound'):
        dpg.configure_item('update', show=True)
        while not dpg.get_value('var_acknowledged'):
            playsound('sms-alert-4-daniel_simon.mp3')
        dpg.configure_item('update', show=False)
        dpg.set_value('var_acknowledged', False)
    else:
        playsound('sms-alert-4-daniel_simon.mp3')


def setup_gui():
    """Creates, styles, and sets up the gui.
    Font, theme, items, and values are created.
    """
    dpg.create_context()
    dpg.create_viewport(title='DMVscanner', width=1025, height=920)
    dpg.setup_dearpygui()
    dpg.add_font_registry(tag='font reg')
    SourceSans = dpg.add_font('SourceSansPro-Regular.ttf',
                              20,
                              parent='font reg')
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 2)
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 12, 12)
    dpg.bind_font(SourceSans)
    dpg.bind_theme(global_theme)
    with dpg.item_handler_registry(tag='widget handler'):
        dpg.add_item_visible_handler(callback=lambda: print_console())
    with dpg.value_registry():
        dpg.add_string_value(
            tag='var_typeid',
            default_value='Apply for first time Texas DL/Permit')
        dpg.add_bool_value(tag='var_paused', default_value=True)
        dpg.add_int_value(tag='var_zipcode', default_value=76036)
        dpg.add_float_value(tag='var_tdratio', default_value=1.5)
        dpg.add_string_value(tag='var_console', default_value='')
        dpg.add_int_value(tag='var_sleep', default_value=1)
        dpg.add_bool_value(tag='var_sound', default_value=False)
        dpg.add_bool_value(tag='var_acknowledged', default_value=False)
    with dpg.window(label='Update!',
                    pos=(200, 200),
                    show=False,
                    tag='update',
                    width=200,
                    height=50):
        dpg.add_checkbox(label='Dismiss', source='var_acknowledged')


def create_settings_gui():
    """Create window: Settings.
    Can pause and change settings
    of the update_loop() before its called.
    """
    with dpg.window(tag='Settings',
                    label='Settings',
                    min_size=(400, 200),
                    pos=(600, 10)):
        dpg.add_checkbox(label='Paused',
                         source='var_paused',
                         callback=update_loop)
        dpg.add_text(default_value='What appointment type:')
        dpg.add_radio_button(items=[
            'Apply for first time Texas DL/Permit',
            'Change, replace or renew Texas DL/Permit',
            'Class C Road Skills Test',
            'Apply for first time Texas ID'
        ],
                             indent=20,
                             source='var_typeid')
        dpg.add_input_int(label='ZIP Code',
                          source='var_zipcode',
                          step=0,
                          width=100,
                          tag='zipcode')
        with dpg.tooltip('zipcode'):
            dpg.add_text('Texas 5 digit ZIP code')
        dpg.add_slider_float(label='Time/Distance ratio',
                             min_value=0.0,
                             max_value=3.0,
                             default_value=1.5,
                             width=200,
                             tag='tdratio',
                             source='var_tdratio')
        with dpg.tooltip('tdratio'):
            dpg.add_text('days per mile')
        dpg.add_input_int(label='Sleep Time',
                          source='var_sleep',
                          width=85,
                          tag='sleep')
        with dpg.tooltip('sleep'):
            dpg.add_text('How many seconds between each scan')
        dpg.add_checkbox(label='Loop Sound', source='var_sound', tag='sound')
        with dpg.tooltip('sound'):
            dpg.add_text('Loop the sound until acknowledged')


def create_console_gui():
    """Adds window: Console.
    The console gets updated by
    print_console().
    Has two boxes to highlight.
    """
    with dpg.window(tag='Console'):
        dpg.add_text(source='var_console', tag='console')
        with dpg.draw_layer(tag='box', show=False):
            dpg.draw_rectangle(pmin=(-5, 701),
                               pmax=(550, 726),
                               fill=(0, 102, 255, 50),
                               rounding=8)
            dpg.draw_rectangle(pmin=(490, 683),
                               pmax=(545, 805),
                               fill=(0, 102, 255, 50),
                               rounding=8)
    RobotoMono = dpg.add_font('RobotoMono-VariableFont_wght.ttf',
                              20,
                              parent='font reg')
    dpg.bind_item_font('console', RobotoMono)
    dpg.bind_item_handler_registry('console', 'widget handler')


def create_graph_gui():
    """Add a window: Graph.
    The graph has 5 lines.
    """
    with dpg.window(tag='Graph',
                    label='Graph',
                    min_size=(400, 200),
                    pos=(600, 335)):
        with dpg.plot(height=500, width=-1):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis,
                              tag='x_axis',
                              label='Runtime',
                              no_gridlines=True)
            with dpg.plot_axis(dpg.mvYAxis,
                               tag='y_axis',
                               label='Days',
                               no_gridlines=False):
                for i in range(5):
                    dpg.add_stair_series([], [], tag=f'location{i}')


def open_gui():
    """Runs and opens the gui.
    Makes console the primary.
    """
    dpg.show_viewport()
    dpg.set_primary_window('Console', True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def print_console(change=False, addon=''):
    """Adds text to the GUI console.
    Takes in change and addon.
    If there is no data change it
    overwrites the previous line.
    """
    if change:
        if dpg.get_value('var_console').count('\n') > 40:
            var_console = dpg.get_value('var_console').split('\n', 8)[8]
            dpg.configure_item('box', show=True)
        else:
            var_console = dpg.get_value('var_console')
        dpg.set_value('var_console', f"""{var_console}\n{str(addon)}""")
        return addon
    elif not change:
        var_console = dpg.get_value('var_console')
        cut = var_console[:var_console.rfind('\n')]
        dpg.set_value('var_console', f"""{cut}\n{str(addon)}""")
        return addon


def update_loop():
    """Loops the update function.
    Skips if var_paused is true.
    Sleeps for var_sleep seconds
    """
    try:
        counter
    except NameError:
        counter = 0
        current_score = []
    while not dpg.get_value('var_paused'):
        counter, current_score = update(counter, current_score)
        time.sleep(dpg.get_value('var_sleep'))


if __name__ == '__main__':
    start_time = datetime.now()
    setup_gui()
    create_settings_gui()
    create_console_gui()
    create_graph_gui()
    open_gui()
