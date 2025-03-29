
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

class CustomTooltip:
    def __init__(self, ax):
        self.ax = ax
        self.annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15),
            textcoords="offset points", bbox=dict(boxstyle="round,pad=0.3", facecolor='black', edgecolor='white', alpha=1.0),
            arrowprops=dict(arrowstyle="->", color='white'),
            fontsize=10, color='white'
        )
        self.annotation.set_visible(False)

    def update(self, x, y, text, color):
        self.annotation.xy = (x, y)
        self.annotation.set_text(text)
        self.annotation.get_bbox_patch().set_edgecolor(color)
        self.annotation.set_color('white')  # Set text color to white
        self.annotation.set_visible(True)
        self.adjust_position()
        self.ax.figure.canvas.draw()

    def hide(self):
        self.annotation.set_visible(False)
        self.ax.figure.canvas.draw()

    def adjust_position(self):
        bbox = self.annotation.get_window_extent()
        canvas_width, canvas_height = self.ax.figure.canvas.get_width_height()
        tooltip_width, tooltip_height = bbox.width, bbox.height

        x_offset, y_offset = 15, 15
        x, y = self.annotation.xy

        if bbox.x0 < 0:
            x_offset = -bbox.x0 + 5
        elif bbox.x1 > canvas_width:
            x_offset = -(bbox.x1 - canvas_width + 5)

        if bbox.y0 < 0:
            y_offset = -bbox.y0 + 5
        elif bbox.y1 > canvas_height:
            y_offset = -(bbox.y1 - canvas_height + 5)

        self.annotation.set_position((x_offset, y_offset))


def create_plot():
    fig, ax = plt.subplots(figsize=(8.05, 5))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_xlabel('X-axis', color='white')
    ax.set_ylabel('Y-axis', color='white')
    ax.set_xlim([0, 8])
    ax.set_ylim([0, 8])
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(True, which='both', color='#444444', linestyle='--', linewidth=0.5)
    return fig, ax

def update_plot(ax, cow_data, cow_id, data_type, annotations):
    ax.clear()
    ax.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_xlabel('Date', color='white')
    ax.set_ylabel('Activity Level' if data_type == 'activity' else 'Temperature', color='white')
    ax.grid(True, which='both', color='#444444', linestyle='--', linewidth=0.5)

    if data_type == 'activity':
        line1, = ax.plot(cow_data['Date'], cow_data['Activity Level'], linestyle='-', color='#008B8B', linewidth=1.0, label='Cow Activity Level')
        scatter1 = ax.scatter(cow_data['Date'], cow_data['Activity Level'], color='#00CED1', s=10)
        line2, = ax.plot(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], linestyle='-', color='darkred', linewidth=1.0, label='Entire Cow Herd Activity Level')
        scatter2 = ax.scatter(cow_data['Date'], cow_data['Entire Cow Herd Activity Level'], color='red', s=10)
    else:
        line1, = ax.plot(cow_data['Date'], cow_data['Temperature'], linestyle='-', color='#008B8B', linewidth=1.0, label='Cow Temperature Level')
        scatter1 = ax.scatter(cow_data['Date'], cow_data['Temperature'], color='#00CED1', s=10)
        line2, = ax.plot(cow_data['Date'], cow_data['Group Mean'], linestyle='-', color='darkred', linewidth=1.0, label='Entire Cow Herd Temperature Level')
        scatter2 = ax.scatter(cow_data['Date'], cow_data['Group Mean'], color='red', s=10)

    title = f'{data_type.capitalize()} Data: Cow ID {cow_id} (cyan) vs Entire Cow Herd (red)'
    ax.set_title(title, fontsize=12, color='white', pad=20)

    week_numbers = cow_data['Week Number'].unique()
    week_labels = [f'Week {int(week)}' for week in week_numbers]
    week_dates = cow_data['Date'].iloc[::7]
    ax.set_xticks(week_dates)
    ax.set_xticklabels(week_labels, rotation=45)

    tooltip = CustomTooltip(ax)

    def on_hover(event):
        if event.inaxes == ax:
            for line, data, label, color in [
                (line1, cow_data['Activity Level'], cow_id, '#00CED1') if data_type == 'activity' else (line1, cow_data['Temperature'], cow_id, '#00CED1'),
                (line2, cow_data['Entire Cow Herd Activity Level'], "Entire Cow Herd", 'red') if data_type == 'activity' else (line2, cow_data['Group Mean'], "Entire Cow Herd", 'red')
            ]:
                cont, ind = line.contains(event)
                if cont:
                    index = ind['ind'][0]
                    x = date2num(cow_data['Date'].iloc[index])
                    y = data.iloc[index]
                    text = f'Cow ID: {label}\nDate: {cow_data["Date"].iloc[index].strftime("%Y-%m-%d")}\n{data_type.capitalize()}: {y:.2f}'
                    tooltip.update(x, y, text, color)
                    break
            else:
                tooltip.hide()
        else:
            tooltip.hide()

    def on_double_click(event):
        if event.inaxes == ax:
            for line, data, label in [
                (line1, cow_data['Activity Level'], cow_id) if data_type == 'activity' else (line1, cow_data['Temperature'], cow_id),
                (line2, cow_data['Entire Cow Herd Activity Level'], "Entire Cow Herd") if data_type == 'activity' else (line2, cow_data['Group Mean'], "Entire Cow Herd")
            ]:
                cont, ind = line.contains(event)
                if cont:
                    # Capture the current plot data and title
                    title = f'{data_type.capitalize()} Data: Cow ID {cow_id} (cyan) vs Entire Cow Herd (red)'
                    # Create a new plot window with the current plot data
                    open_new_window(cow_data, data, title, data_type)
                    break
    ax.figure.canvas.mpl_connect("motion_notify_event", on_hover)
    ax.figure.canvas.mpl_connect("button_press_event", on_double_click)
    annotations.append(tooltip)

def open_new_window(data, plot_data, title, data_type):
    new_fig, new_ax = plt.subplots(figsize=(8, 5))
    new_ax.set_facecolor('black')
    new_ax.spines['bottom'].set_color('white')
    new_ax.spines['top'].set_color('white')
    new_ax.spines['right'].set_color('white')
    new_ax.spines['left'].set_color('white')
    new_ax.tick_params(axis='x', colors='white')
    new_ax.tick_params(axis='y', colors='white')
    new_ax.set_xlabel('Date', color='white')
    new_ax.set_ylabel('Activity Level' if data_type == 'activity' else 'Temperature', color='white')
    new_ax.grid(True, which='both', color='#444444', linestyle='--', linewidth=0.5)
    new_ax.set_title(title, fontsize=12, color='white', pad=20)

    if data_type == 'activity':
        new_ax.plot(data['Date'], data['Activity Level'], linestyle='-', color='#008B8B', linewidth=1.0, label='Cow Activity Level')
        new_ax.scatter(data['Date'], data['Activity Level'], color='#00CED1', s=10)
        new_ax.plot(data['Date'], data['Entire Cow Herd Activity Level'], linestyle='-', color='darkred', linewidth=1.0, label='Entire Cow Herd Activity Level')
        new_ax.scatter(data['Date'], data['Entire Cow Herd Activity Level'], color='red', s=10)
    else:
        new_ax.plot(data['Date'], data['Temperature'], linestyle='-', color='#008B8B', linewidth=1.0, label='Cow Temperature Level')
        new_ax.scatter(data['Date'], data['Temperature'], color='#00CED1', s=10)
        new_ax.plot(data['Date'], data['Group Mean'], linestyle='-', color='darkred', linewidth=1.0, label='Entire Cow Herd Temperature Level')
        new_ax.scatter(data['Date'], data['Group Mean'], color='red', s=10)

    new_fig.canvas.set_window_title(title)
    plt.show()