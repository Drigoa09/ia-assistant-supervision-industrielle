from Agents.Tools_nodes.database_node.database_node import DataFrameRole

def n_premiers(dataFrames, args):

    new_dataFrames = dataFrames

    dataFrame = dataFrames[args[0].numero_dataFrame].dataFrame

    new_dataFrames.append(DataFrameRole(dataFrame.head(int(args[1])), dataFrames[args[0].numero_dataFrame].role + " contenant les " + str(args[1]) + " premiers éléments"))

    return new_dataFrames
