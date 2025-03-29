# activity.py

import pandas as pd
import matplotlib.pyplot as plt

def plot_activity_levels(cow_id, compare_with_cow_id=None, file_path=None):
    data = pd.read_csv(file_path, encoding='utf-8')
    print("Columns in the dataset:", data.columns)

    columns_to_extract = ['Unnamed: 0', str(cow_id), 'Group mean']
    if compare_with_cow_id:
        columns_to_extract.append(str(compare_with_cow_id))
    
    cow_data = data[columns_to_extract].copy()
    cow_data.columns = ['Date', 'Activity Level', 'Entire Cow Herd Activity Level'] + ([f'Cow {compare_with_cow_id} Activity Level'] if compare_with_cow_id else [])

    cow_data['Date'] = pd.to_datetime(cow_data['Date'])
    cow_data['Week Number'] = ((cow_data['Date'] - cow_data['Date'].min()).dt.days // 7) + 1

    return cow_data

def create_activity_plot(cow_data, cow_id):
    fig, ax = plt.subplots(figsize=(12, 6))
    cow_line, = ax.plot(cow_data['Date'], cow_data['Activity Level'], linestyle='-', label=f'Cow {cow_id} Activity Level', color='blue')
    group_line, = ax.plot(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], linestyle='-', label='Entire Cow Herd Activity Level', color='red')

    cow_marker = ax.scatter(cow_data['Date'], cow_data['Activity Level'], color='blue', s=50, label=f'Cow {cow_id} Activity Level')
    group_marker = ax.scatter(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], color='red', s=50, label='Entire Cow Herd Activity Level')

    ax.set_title(f'Activity Levels of Cow ID {cow_id} vs Entire Cow Herd Activity Level')
    ax.set_xlabel('Date')
    ax.set_ylabel('Activity Level')
    ax.grid(True, color='gray')

    week_numbers = cow_data['Week Number'].unique()
    week_labels = [f'Week {int(week)}' for week in week_numbers]
    week_dates = cow_data['Date'].iloc[::7]
    ax.set_xticks(week_dates)
    ax.set_xticklabels(week_labels, rotation=45)

    handles, labels = ax.get_legend_handles_labels()
    handles = [handles[0], handles[1]]
    labels = [labels[0], labels[1]]
    ax.legend(handles, labels)

    plt.tight_layout()

    fig.canvas.mpl_connect("motion_notify_event", lambda event: on_hover(event, cow_data, cow_marker, group_marker, ax))

    # Enable zoom functionality
    fig.canvas.mpl_connect('scroll_event', lambda event: zoom(event, ax))

    return fig, ax

def create_comparison_plot(cow_data, cow_id, compare_with_cow_id):
    fig, ax = plt.subplots(figsize=(12, 6))
    cow_line, = ax.plot(cow_data['Date'], cow_data['Activity Level'], linestyle='-', label=f'Cow {cow_id} Activity Level', color='blue')
    compare_line, = ax.plot(cow_data['Date'], cow_data[f'Cow {compare_with_cow_id} Activity Level'], linestyle='-', label=f'Cow {compare_with_cow_id} Activity Level', color='lime')
    group_line, = ax.plot(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], linestyle='-', label='Entire Cow Herd Activity Level', color='red')

    cow_marker = ax.scatter(cow_data['Date'], cow_data['Activity Level'], color='blue', s=50, label=f'Cow {cow_id} Activity Level')
    compare_marker = ax.scatter(cow_data['Date'], cow_data[f'Cow {compare_with_cow_id} Activity Level'], color='lime', s=50, label=f'Cow {compare_with_cow_id} Activity Level')
    group_marker = ax.scatter(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], color='red', s=50, label='Entire Cow Herd Activity Level')

    ax.set_title(f'Activity Levels of Cow ID {cow_id} vs Entire Cow Herd Activity Level vs Cow ID {compare_with_cow_id}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Activity Level')
    ax.grid(True, color='gray')

    week_numbers = cow_data['Week Number'].unique()
    week_labels = [f'Week {int(week)}' for week in week_numbers]
    week_dates = cow_data['Date'].iloc[::7]
    ax.set_xticks(week_dates)
    ax.set_xticklabels(week_labels, rotation=45)

    handles, labels = ax.get_legend_handles_labels()
    handles = [handles[0], handles[1], handles[2]]
    labels = [labels[0], labels[1], labels[2]]
    ax.legend(handles, labels)

    plt.tight_layout()

    fig.canvas.mpl_connect("motion_notify_event", lambda event: on_hover(event, cow_data, cow_marker, group_marker, compare_marker, ax))

    # Enable zoom functionality
    fig.canvas.mpl_connect('scroll_event', lambda event: zoom(event, ax))

    return fig, ax

def on_hover(event, cow_data, *markers, ax):
    for annotation in ax.texts:
        annotation.set_visible(False)
    if event.inaxes == ax:
        for marker in markers:
            cont, ind = marker.contains(event)
            if cont:
                update_annotation(ax, event, cow_data, marker, ind)
                break
    event.canvas.draw_idle()

def update_annotation(ax, event, cow_data, marker, ind):
    for i in ind["ind"]:
        x, y = marker.get_offsets()[i]
        annotation = ax.annotate(
            f"Cow ID: {cow_data.columns[1]}\nDate: {pd.to_datetime(x).strftime('%Y-%m-%d')}\nActivity: {y:.2f}",
            xy=(x, y), xycoords='data',
            xytext=(10, 10), textcoords='offset points',
            bbox=dict(boxstyle="round,pad=0.3", edgecolor=marker.get_facecolor()[0], facecolor='black'),
            arrowprops=dict(arrowstyle='-|>', color='white', connectionstyle='arc3,rad=0')
        )
        adjust_annotation(annotation, event)

def adjust_annotation(annotation, event):
    window_width, window_height = plt.gcf().get_size_inches() * plt.gcf().dpi
    x, y = event.x, event.y
    width, height = annotation.get_bbox_patch().get_window_extent().width, annotation.get_bbox_patch().get_window_extent().height
    if x + width > window_width:
        annotation.xytext = (-10-width, 10)
    if y + height > window_height:
        annotation.xytext = (-10-width, -10-height)

def zoom(event, ax):
    base_scale = 1.5
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    xdata = event.xdata
    ydata = event.ydata
    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        scale_factor = 1
        print(event.button)
    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
    ax.set_ylim([ydata - new_height * (1 - rely)])
    ax.figure.canvas.draw()
