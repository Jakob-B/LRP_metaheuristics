
from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution import Solution
import metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution as ObjSolution
Solution = ObjSolution.Solution
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassSwarm import Swarm
import metaheuristik.marinakis.code2.LRPClassObjects.ClassSwarm as ObjSwarm
Swarm = ObjSwarm.Swarm
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance
import metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance as ObjInstance
LRPinstance = ObjInstance.LRPinstance

class SwarmNetwork:
    def __init__(self, swarm: Swarm, iteration: int):
        self.swarm: Swarm = swarm
        self.instance: LRPinstance = swarm.instance
        self.iteration = iteration
        self.pos = self.__posDict__()
        self.edges = None
        self.edgesProceed = None
        self.edgeLabelsProceed: Dict = None
        self.edgesReturn = None
        self.edgeLabelsReturn: Dict = None
        self.edgeLabels: Dict = None
        self.edgeStyles: List = None
        self.edgeConnectionStyles: List = None


    def __posDict__(self):
        """
        create a Positon Ditionary: {"Node":[xCoord, yCoord]}
        """
        coord = self.instance.coordinates
        nodes = self.instance.customers+self.instance.facilities
        pos = {}
        for n in nodes:
            pos.update({n: coord[nodes.index(n)+1]}) # Offset of 1, as coordinate List in instances uses a placeholder for the first entry of [0,0]. We want to skip this one.
        return pos

    def __getAllParticleSwarmEdges__(self):
        """
        returns a Dict containing the used edges and occurences: {[node1,node2]: occurences}
        for all current solutions of the swarm
        """
        edgeOccur = {}
        for p in self.swarm.particles:
            for t in p.curSol.tours:
                edges = self.__getEdges__(t.fullTrip)
                for e in edges:
                    if e in edgeOccur.keys():
                        occur = edgeOccur[e] + 1
                        edgeOccur[e] = occur
                    else:
                        edgeOccur.update({e:1}) 
        return edgeOccur    

    def __getBestSolutionSwarmEdges__(self):
        """
        returns a Dict containing the used edges and occurences: {[node1,node2]: occurences}
        only for the best solution of the swarm
        """
        edgeOccur = {}
        s = self.swarm.gBestSol
        for t in s.tours:
            edges = self.__getEdges__(t.fullTrip)
            for e in edges:
                if e in edgeOccur.keys():
                    occur = edgeOccur[e] + 1
                    edgeOccur[e] = occur
                else:
                    edgeOccur.update({e:1}) 
        return edgeOccur    

    def __getEdges__(self, fullTrip: List):
        edges = list()
        if len(fullTrip)>1:
            for nIndex in range(1,len(fullTrip)):
                n1 = fullTrip[nIndex-1]
                n2 = fullTrip[nIndex]
                edges.append((n1,n2))
        # add facilities self edges to ensure that facility appears on Graph
        for f in self.instance.facilities:
            edges.append((f,f))
        return edges

    def __drawGraph__(self, variant = "standard", fileName: str = "Fig", save = False, show = False):
        """
        Draw a Graph using networkx library. 

        @parameter variant: Defines if the simple route "standard" is drawn or if the strategy "strategy" (including the return and proceeding decisions) is drawn.
        @parameter fileName: Name/Path of file when figure is saved.
        @parameter save: If Figure should be saved, using the FileName.
        @parameter show: If Figure should be displayed.
        """
        plt.figure(figsize=(20,20))
        G = nx.DiGraph()
       
        
        G.add_edges_from(self.edges)
        
        # Color the facility nodes in orange and the customer nodes in blue
        color_map = {}
        for f in self.instance.facilities:
            color_map.update({f:"#FF9130"})
        color_values = [color_map.get(node,"#309FFF") for node in G.nodes()]
        # Draw the nodes and annotate them with the node number.
        nx.draw_networkx_nodes(G, self.pos, cmap=plt.get_cmap('jet'), 
                        node_color = color_values, node_size = 500)
        nx.draw_networkx_labels(G, self.pos)

        if variant == "standard":
            # Draw the simple route
            nx.draw_networkx_edges(G, self.pos, edgelist=self.edges, edge_color='black', arrows=True, 
                                style=self.edgeStyles)
        else:
            # Proceed Edges                        
            nx.draw_networkx_edges(G, self.pos, edgelist=self.edgesProceed, edge_color='black', arrows=True, 
                                    style= "solid", connectionstyle="arc3", arrowsize=30)
            self.__my_draw_networkx_edge_labels__(G,self.pos,edge_labels=self.edgeLabelsProceed)                            
            # Return Edges
            nx.draw_networkx_edges(G, self.pos, edgelist=self.edgesReturn, edge_color='black', arrows=True, 
                                    style=":", connectionstyle="arc3,rad=0.2", arrowsize=30)
            self.__my_draw_networkx_edge_labels__(G,self.pos,edge_labels=self.edgeLabelsReturn, rad=0.2)                                                            
            #nx.draw_networkx_edge_labels(G=G, pos=self.pos,edge_labels=self.edgeLabels, label_pos=0.25)
        if show:
            plt.show(block=False)
            plt.pause(120)
        if save:
            plt.savefig(fileName, bbox_inches="tight", pad_inches=0)
        
        #plt.close()
        #return plt

    def __getStrategyEdges__(self, sol: Solution):
        edges = list()
        edgesReturn = list()
        edgeLabelsReturn = dict()
        edgesProceed = list()
        edgeLabelsProceed = dict()
        edgeLabels = dict()
        edgeStyles = list()
        edgeConnectionStyles = list()
        for t in sol.tours:
            if len(t.fullTrip)>0:
                facility = t.facility
                t.refineStrategies()
                strat: dict = t.compactStrategy
                nodes = list(strat)
                # excluding last node
                for nIndex in range(len(nodes)):
                    n1 = nodes[nIndex]
                    # next node for last node is facility (strategy attribute of tour does not hold the facility as last node, instead the last customer of this tour.)
                    if nIndex == len(nodes)-1:
                        n2 = facility    
                    else:
                        n2 = nodes[nIndex+1]
                    strat1: dict = strat[n1]
                    for remainingCap in strat1.keys():
                        action = strat1[remainingCap]
                        if action[0] == "proceed":
                            edges.append((n1,n2))
                            edgesProceed.append((n1,n2))
                            edgeStyles.append("solid")
                            edgeConnectionStyles.append("arc3")
                            if (n1,n2) in edgeLabels:
                                label = str(edgeLabels[(n1,n2)]) #+ ", " + str(remainingCap)
                                cap = int(label.split(">= ")[1])
                                if remainingCap < cap:
                                    cap = remainingCap
                            else:
                                cap = remainingCap
                            label = "p : >= " + str(cap)
                            edgeLabels.update({(n1,n2): label})
                            edgeLabelsProceed.update({(n1,n2): label})
                        elif action[0] == "refill":
                            edges.append((n1,facility))
                            edgesReturn.append((n1,facility))
                            edgeStyles.append("dashed")
                            edgeConnectionStyles.append("arc3,rad=0.2")
                            if (n1,facility) in edgeLabels:
                                label = str(edgeLabels[(n1,facility)])
                                cap = int(label.split("<= ")[1])
                                if remainingCap > cap:
                                    cap = remainingCap
                            else:
                                cap = remainingCap
                            label = "r : <= " + str(cap)
                            edgeLabels.update({(n1,facility): label})
                            edgeLabelsReturn.update({(n1,facility): label})
                            #edgeLabels.update({(n1,facility):str(remainingCap) + ": r"})
                            edges.append((facility,n2))
                            edgesReturn.append((facility,n2))
                            edgeStyles.append("dashed")
                            edgeConnectionStyles.append("arc3,rad=0.2")
                            edgeLabels.update({(facility,n2): "Refilled: "+str(self.instance.totalVehicleCap)})
                            edgeLabelsReturn.update({(facility,n2):"Refilled: "+str(self.instance.totalVehicleCap)})
        self.edgeLabels = edgeLabels
        self.edges = edges
        self.edgeStyles = edgeStyles
        self.edgeConnectionStyles = edgeConnectionStyles        
        self.edgesProceed = edgesProceed
        self.edgesReturn = edgesReturn
        self.edgeLabelsProceed = edgeLabelsProceed
        self.edgeLabelsReturn = edgeLabelsReturn

        return 0

    def drawAllParticles(self, show = False):
        self.edges = self.__getAllParticleSwarmEdges__()
        return self.__drawGraph__(show=show)

    def drawBestSolution(self, save = False, fileName = "Fig", show = False):
        self.edges = self.__getBestSolutionSwarmEdges__()
        return self.__drawGraph__(save=save, fileName=fileName, show=show)

    def drawBestStrategy(self, save = False, fileName = "Fig", show = False):
        self.__getStrategyEdges__(self.swarm.gBestSol)
        #self.edges = self.__getBestSolutionSwarmEdges__()
        return self.__drawGraph__(variant="strategy", save=save, fileName=fileName, show=show)


    def __my_draw_networkx_edge_labels__(
        self,
        G,
        pos,
        edge_labels=None,
        label_pos=0.5,
        font_size=10,
        font_color="k",
        font_family="sans-serif",
        font_weight="normal",
        alpha=None,
        bbox=None,
        horizontalalignment="center",
        verticalalignment="center",
        ax=None,
        rotate=True,
        clip_on=True,
        rad=0
    ):
    # COPIED FROM @kcoskun, Stackoverflow https://stackoverflow.com/a/70245742
        """Draw edge labels.

        Parameters
        ----------
        G : graph
            A networkx graph

        pos : dictionary
            A dictionary with nodes as keys and positions as values.
            Positions should be sequences of length 2.

        edge_labels : dictionary (default={})
            Edge labels in a dictionary of labels keyed by edge two-tuple.
            Only labels for the keys in the dictionary are drawn.

        label_pos : float (default=0.5)
            Position of edge label along edge (0=head, 0.5=center, 1=tail)

        font_size : int (default=10)
            Font size for text labels

        font_color : string (default='k' black)
            Font color string

        font_weight : string (default='normal')
            Font weight

        font_family : string (default='sans-serif')
            Font family

        alpha : float or None (default=None)
            The text transparency

        bbox : Matplotlib bbox, optional
            Specify text box properties (e.g. shape, color etc.) for edge labels.
            Default is {boxstyle='round', ec=(1.0, 1.0, 1.0), fc=(1.0, 1.0, 1.0)}.

        horizontalalignment : string (default='center')
            Horizontal alignment {'center', 'right', 'left'}

        verticalalignment : string (default='center')
            Vertical alignment {'center', 'top', 'bottom', 'baseline', 'center_baseline'}

        ax : Matplotlib Axes object, optional
            Draw the graph in the specified Matplotlib axes.

        rotate : bool (deafult=True)
            Rotate edge labels to lie parallel to edges

        clip_on : bool (default=True)
            Turn on clipping of edge labels at axis boundaries

        Returns
        -------
        dict
            `dict` of labels keyed by edge

        Examples
        --------
        >>> G = nx.dodecahedral_graph()
        >>> edge_labels = nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G))

        Also see the NetworkX drawing examples at
        https://networkx.org/documentation/latest/auto_examples/index.html

        See Also
        --------
        draw
        draw_networkx
        draw_networkx_nodes
        draw_networkx_edges
        draw_networkx_labels
        """
        import matplotlib.pyplot as plt
        import numpy as np

        if ax is None:
            ax = plt.gca()
        if edge_labels is None:
            labels = {(u, v): d for u, v, d in G.edges(data=True)}
        else:
            labels = edge_labels
        text_items = {}
        for (n1, n2), label in labels.items():
            (x1, y1) = pos[n1]
            (x2, y2) = pos[n2]
            (x, y) = (
                x1 * label_pos + x2 * (1.0 - label_pos),
                y1 * label_pos + y2 * (1.0 - label_pos),
            )
            pos_1 = ax.transData.transform(np.array(pos[n1]))
            pos_2 = ax.transData.transform(np.array(pos[n2]))
            linear_mid = 0.5*pos_1 + 0.5*pos_2
            d_pos = pos_2 - pos_1
            rotation_matrix = np.array([(0,1), (-1,0)])
            ctrl_1 = linear_mid + rad*rotation_matrix@d_pos
            ctrl_mid_1 = 0.5*pos_1 + 0.5*ctrl_1
            ctrl_mid_2 = 0.5*pos_2 + 0.5*ctrl_1
            bezier_mid = 0.5*ctrl_mid_1 + 0.5*ctrl_mid_2
            (x, y) = ax.transData.inverted().transform(bezier_mid)

            if rotate:
                # in degrees
                angle = np.arctan2(y2 - y1, x2 - x1) / (2.0 * np.pi) * 360
                # make label orientation "right-side-up"
                if angle > 90:
                    angle -= 180
                if angle < -90:
                    angle += 180
                # transform data coordinate angle to screen coordinate angle
                xy = np.array((x, y))
                trans_angle = ax.transData.transform_angles(
                    np.array((angle,)), xy.reshape((1, 2))
                )[0]
            else:
                trans_angle = 0.0
            # use default box of white with white border
            if bbox is None:
                bbox = dict(boxstyle="round", ec=(1.0, 1.0, 1.0), fc=(1.0, 1.0, 1.0))
            if not isinstance(label, str):
                label = str(label)  # this makes "1" and 1 labeled the same

            t = ax.text(
                x,
                y,
                label,
                size=font_size,
                color=font_color,
                family=font_family,
                weight=font_weight,
                alpha=alpha,
                horizontalalignment=horizontalalignment,
                verticalalignment=verticalalignment,
                rotation=trans_angle,
                transform=ax.transData,
                bbox=bbox,
                zorder=1,
                clip_on=clip_on,
            )
            text_items[(n1, n2)] = t

        ax.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )

        return text_items