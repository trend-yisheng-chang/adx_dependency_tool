from .model.function import Function
from .model.table import Table
from .model.graph_node import GraphNode
from .node_type import NodeType
from .grouper import Grouper


class DependencyChecker():
    def __init__(self, tiles, queries, functions, tables):
        self._tiles = tiles
        self._queries = queries
        self._functions = functions
        self._function_names = [f.name for f in self._functions]
        self._tables = tables
        self._table_names = [t.name for t in self._tables]

    def _get_used_functions_in_dashboard(self):
        used_functions = set()

        def traverse(node):
            used_functions.update(node.used_functions)
            for f in node.used_functions:
                if isinstance(node, Function) and f == node.name:
                    continue
                traverse(self._functions[self._function_names.index(f)])

        for query in self._queries:
            traverse(query)

        return used_functions

    def _get_used_functions_in_page(self, page_id):
        used_functions = set()

        def traverse(node):
            used_functions.update(node.used_functions)
            for f in node.used_functions:
                if isinstance(node, Function) and f == node.name:
                    continue
                traverse(self._functions[self._function_names.index(f)])

        page_tiles = [t for t in self._tiles if t.page_id ==
                      page_id and t.linked_query_id]
        page_queries = [next(
            q for q in self._queries if t.linked_query_id == q.query_id) for t in page_tiles]
        for query in page_queries:
            traverse(query)

        return used_functions

    def _get_dependency(self, node, added_nodes=None):
        # node is either a query or a function.
        if not added_nodes:
            added_nodes = []
        edges = []

        def traverse(node):
            if not node.used_functions and not node.used_tables:
                return

            for f_name in node.used_functions:
                if isinstance(node, Function) and f_name == node.name:
                    continue

                f_instance = self._functions[self._function_names.index(
                    f_name)]

                start = get_start_node(node)

                end = get_end_node(f_instance)
                edge = (start, end)
                edges.append(edge)
                if edge[1].title == edges[0][0].title:
                    break
                traverse(f_instance)

            for t_name in node.used_tables:
                t_instance = self._tables[self._table_names.index(t_name)]
                start = get_start_node(node)
                end = get_end_node(t_instance)
                edge = (start, end)
                edges.append(edge)

        def get_start_node(node):
            if isinstance(node, Function):
                start = next(
                    (n for n in added_nodes if n.title == node.name and n.type == NodeType.FUNCTION), None)
                if not start:
                    start = GraphNode(
                        title=node.name, content=node.body, type=NodeType.FUNCTION)
                    added_nodes.append(start)
            else:
                start = next(
                    (n for n in added_nodes if n.title == 'Original Query'), None)
                if not start:
                    start = GraphNode(
                        title='Original Query', content=node.content, type=NodeType.QUERY)
                    added_nodes.append(start)
            return start

        def get_end_node(node):
            if isinstance(node, Function):
                end = next(
                    (n for n in added_nodes if n.title == node.name and n.type == NodeType.FUNCTION), None)
                if not end:
                    end = GraphNode(
                        title=node.name, content=node.body, type=NodeType.FUNCTION)
                    added_nodes.append(end)
            if isinstance(node, Table):
                end = next(
                    (n for n in added_nodes if n.title == node.name and n.type == NodeType.TABLE), None)
                if not end:
                    end = GraphNode(
                        title=node.name, content='', type=NodeType.TABLE)
                    added_nodes.append(end)
            return end

        traverse(node)
        return edges

    def check_dashboard(self):
        edges = []
        zero_out_degree_functions = []
        used_functions_in_dashboard = self._get_used_functions_in_dashboard()
        added_nodes = []
        for f in self._functions:
            if f.name not in used_functions_in_dashboard:
                continue
            e = self._get_dependency(f, added_nodes)
            if e:
                edges.extend(e)
                added_nodes.extend([node for edge in e for node in edge])
            else:
                zero_out_node = GraphNode(
                    title=f.name, content=f.body, type=NodeType.FUNCTION)
                zero_out_degree_functions.append(zero_out_node)
                added_nodes.append(zero_out_node)
        edges = list(set(edges))
        called_functions = list(
            set([node.title for edge in edges for node in edge]))
        dependency = {}
        for e in edges:
            if e[0].id not in dependency:
                dependency[e[0].id] = [e[1].id]
            else:
                dependency[e[0].id].append(e[1].id)
        for zodf in zero_out_degree_functions:
            if zodf.title not in called_functions:
                dependency[zodf.id] = []
        nodes = list(set([n for n in added_nodes]))
        node_groups = Grouper.group_by_tfidf([n.content for n in nodes])
        return dependency, nodes, node_groups

    def check_page(self, page_id):
        edges = []
        zero_out_degree_functions = []
        used_functions_in_page = self._get_used_functions_in_page(page_id)
        added_nodes = []
        for f in self._functions:
            if f.name not in used_functions_in_page:
                continue
            e = self._get_dependency(f, added_nodes)
            if e:
                edges.extend(e)
                added_nodes.extend([node for edge in e for node in edge])
            else:
                zero_out_node = GraphNode(
                    title=f.name, content=f.body, type=NodeType.FUNCTION)
                zero_out_degree_functions.append(zero_out_node)
                added_nodes.append(zero_out_node)
        edges = list(set(edges))
        called_functions = list(
            set([node.title for edge in edges for node in edge]))
        dependency = {}
        for e in edges:
            if e[0].id not in dependency:
                dependency[e[0].id] = [e[1].id]
            else:
                dependency[e[0].id].append(e[1].id)
        for zodf in zero_out_degree_functions:
            if zodf.title not in called_functions:
                dependency[zodf.id] = []
        nodes = list(set([n for n in added_nodes]))
        node_groups = Grouper.group_by_tfidf([n.content for n in nodes])
        return dependency, nodes, node_groups

    def check_tile(self, tile_id):
        tile = next((t for t in self._tiles if t.tile_id == tile_id), None)
        if not tile:
            raise Exception('Tile not found')
        if not tile.linked_query_id:
            return {}, []
        query = next(q for q in self._queries if q.query_id ==
                     tile.linked_query_id)
        edges = self._get_dependency(query)
        added_nodes = [node for e in edges for node in e]
        dependency = {}
        for e in edges:
            if e[0].id not in dependency:
                dependency[e[0].id] = [e[1].id]
            else:
                dependency[e[0].id].append(e[1].id)
        nodes = list(set([n for n in added_nodes]))
        node_groups = Grouper.group_by_tfidf([n.content for n in nodes])
        return dependency, nodes, node_groups
