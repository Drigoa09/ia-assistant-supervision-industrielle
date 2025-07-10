from Tools_nodes.database_node.database_node import DataFrameRole

def plus_occurent(dataFrames, args):

    new_dataFrames = dataFrames

    for arg in args:
        frame = dataFrames[arg.numero_dataFrame].dataFrame[arg.cle_dataFrame].value_counts().to_frame()
        frame.columns = ["Occurences"]
        new_dataFrames.append(DataFrameRole(frame, f"Occurences avec cette information : {arg.cle_dataFrame}"))

    return new_dataFrames
