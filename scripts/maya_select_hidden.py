"""
From a top parent node, select all childrens that are hidden and ask if teh user want to set them to visible again.

Origin: https://gist.github.com/MrLixm/c703eddbc8564e55f9f066fec0e8d6ab
Author: Liam Collod
Last Modified: 05/12/2021
HowTo:
- Select a top-group where all the hidden nodes inside need to be visible again.
- Run script.
Only select ONE object.
"""

import maya.cmds as cmds


def get_nodes_from_selection(include_hierarchy=True):
    """
    Args:
        include_hierarchy (bool): If True, the hierarchy for each node in the user selection will also be returned
    Returns:
        list of str: list of maya nodes by UUID, excluding shape nodes.
    """
    user_sel = cmds.ls(sl=True, long=True)
    if not user_sel:
        raise ValueError("Original selection is empty")

    if not include_hierarchy:
        return nodes_list_to_uuid(user_sel)

    output_node_list = []
    for user_node in user_sel:
        child_list = get_children_hierarchy(node=user_node)
        for child in child_list:
            if child not in output_node_list:
                # don't add if its a shape
                if "shape" not in cmds.nodeType(child, inherited=True):
                    output_node_list.append(child)
        if user_node not in output_node_list:
            if "shape" not in cmds.nodeType(user_node, inherited=True):
                output_node_list.append(user_node)

    return nodes_list_to_uuid(output_node_list)


def get_children_hierarchy(node):
    """ From a given node name return its hierarchy
     Credit: https://gist.github.com/BigRoy/eddac6a93ad4ff233e2757c6bbccf3da
    Args:
        node(str): long name of the node
    Returns:
        list
    """
    result = set()
    children = set(cmds.listRelatives(node, fullPath=True) or [])
    while children:
        # logger.debug("child: {}".format(children))
        result.update(children)
        children = set(cmds.listRelatives(children, fullPath=True) or []) - result

    return list(result)


def nodes_list_to_uuid(node_list):
    """ Convert a list of node name to a list of node UUID
    Args:
        node_list(list of str):
    Returns:
        list of str: list of UUID
    """
    uuid_list = []
    for node in node_list:
        uuid_list.extend(cmds.ls(node, uuid=True))
    return uuid_list


def set_visible(node_list):
    """
    Args:
        node_list(list of str):
    """

    for node in node_list:
        cmds.setAttr("{}.visibility".format(node), 1)

    print(
        "[HiddenNodes][set_visible] All nodes {} set"
        "to visible.".format(node_list)
        )
    return


def main():

    children_nodes = get_nodes_from_selection()
    hidden_nodes = list()

    for child_node in children_nodes:
        child_node = cmds.ls(child_node, long=True)[0]  # convert from UUID to long name
        if cmds.getAttr("{}.visibility".format(child_node)) == 0:
            hidden_nodes.append(child_node)

    cmds.select(hidden_nodes)
    # make sure the user see what selected before prompting the window under 
    cmds.refresh(force=True)  # doesn't work lol
    print(
        "[HiddenNodes][main] Found and selected"
        "{} hidden nodes : {}".format(len(hidden_nodes), hidden_nodes)
    )

    make_visible = cmds.confirmDialog(
        title='Make hidden visible ?',
        message="The script found {} hidden nodes,"
                "do you wish to make them visible ?".format(len(hidden_nodes)),
        button=['Yes','No'],
        defaultButton='Yes',
        cancelButton='No',
        dismissString='No'
    )

    if make_visible == "Yes":
        set_visible(hidden_nodes)
        
    print("[HiddenNodes][main] Finished")    
    return

# execute main function
main()