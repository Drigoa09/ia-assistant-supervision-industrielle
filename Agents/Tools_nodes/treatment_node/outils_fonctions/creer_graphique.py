from matplotlib.figure import Figure

def creer_graphique(dataFrames, args):
    fig = Figure()
    ax = fig.add_subplot(111)
    x = dataFrames[args[0].numero_dataFrame].dataFrame[args[0].cle_dataFrame]
    y = dataFrames[args[1].numero_dataFrame].dataFrame[args[1].cle_dataFrame]
    ax.plot(x,y)
    ax.set_xlabel(args[0].cle_dataFrame)
    ax.set_ylabel(args[1].cle_dataFrame)
    ax.set_title("Graphique de " + args[1].cle_dataFrame + " en fonction de " + args[0].cle_dataFrame)

    return fig

