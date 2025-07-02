from matplotlib import animation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import matplotlib.text as txt

fig, ax = plt.subplots(figsize=(4, 2.5))
circle = mpatches.Circle((0.5, 0.5), 0.25, ec="none")
ax.add_artist(circle)
clipped_circle = mpatches.Circle((1, 0.5), 0.125, ec="none", facecolor='C1')
ax.add_artist(clipped_circle)
text = txt.Text(0.5, 0.5, 'Cool', wrap=True)
text.set_backgroundcolor("1")
ax.add_artist(text)

rectangle = mpatches.Rectangle((0.5, 0.5), 0.1, 0.1)

ax.add_artist(rectangle)

ax.set_aspect(1)


def update(frame):
    # for each frame, update the data stored on each artist.
    rectangle.set_y(0.5 + 0.1 * frame)

    return ax


ani = animation.FuncAnimation(fig=fig, func=update, frames=40, interval=30)
plt.show()
