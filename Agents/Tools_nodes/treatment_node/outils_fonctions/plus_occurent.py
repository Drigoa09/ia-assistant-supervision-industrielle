from Agents.Tools_nodes.database_node.database_node import DataFrameRole

def plus_occurent(dataFrames, args):

    new_dataFrames = dataFrames

    for arg in args:
        frame = dataFrames[arg.numero_dataFrame].dataFrame[arg.cle_dataFrame].value_counts().to_frame()
        frame.columns = ["Occurences"]
        new_dataFrames.append(DataFrameRole(frame, dataFrames[arg.numero_dataFrame].role + " avec les occurences"))

    return new_dataFrames
