import matplotlib.patches as patches

def draw_bracket(ax, x, y_top, y_bottom, label, width=0.3, label_offset=0.1, fontsize=10):
    """
    Draw a straight bracket with a label on a horizontal bar chart.

    Parameters:
    - ax: matplotlib axis
    - x: horizontal position to place the bracket
    - y_top: y-position (top) of the bracket
    - y_bottom: y-position (bottom) of the bracket
    - label: text to display next to the bracket
    - width: how far the bracket sticks out
    - label_offset: horizontal distance from bracket to text
    - fontsize: size of the label
    """
    bracket = [
        [x, y_top],
        [x + width, y_top],
        [x + width, y_bottom],
        [x, y_bottom],
    ]
    bracket_line = patches.Polygon(bracket, closed=False, fill=False, color='black', linewidth=1.2)
    ax.add_patch(bracket_line)

    ax.text(x + width + label_offset, (y_top + y_bottom) / 2, label,
            va='center', ha='left', fontsize=fontsize)
