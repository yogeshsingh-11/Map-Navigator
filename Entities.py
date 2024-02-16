import math

from matplotlib.collections import LineCollection
import time
from FibHeap import FibonacciHeap
import matplotlib.pyplot as plt
from datetime import datetime
from PriorityQueue import PriorityQueue

WALK_SPEED = 5.0


class Node:
    def __init__(self, name: str, x: float, y: float, is_fake: bool):
        self.name = name
        self.x = x
        self.y = y
        self.roads = []
        self.is_fake = is_fake
        self.fib_node = None

    def add_road(self, road):
        self.roads.append(road)

    def add_fib_node(self, fib_node):
        self.fib_node = fib_node


class Road:
    def __init__(self, node1: Node, node2: Node, speed: float, is_fake: bool):
        self.node1 = node1
        self.node2 = node2
        self.speed = speed
        self.length = euclidean_distance(node1.x, node1.y, node2.x, node2.y)
        self.weight = self.length / speed
        self.is_fake = is_fake


class Graph:
    def __init__(self, map_path: str):
        self.nodes = []
        self.roads = []
        self._read_map(map_path)

    def _read_map(self, path: str):
        nodes = []
        roads = []
        try:
            with open(path, 'r') as file:
                nodes_count = 0
                for i, line in enumerate(file):
                    line = line.strip()
                    if i == 0:
                        nodes_count = int(line)
                        continue
                    elif i == nodes_count + 1:
                        continue
                    elif i <= nodes_count:
                        parts = line.split(' ')
                        name = parts[0]
                        x = float(parts[1])
                        y = float(parts[2])
                        nodes.append(Node(name, x, y, False))
                    elif i > nodes_count + 1:
                        parts = line.split(' ')
                        node1 = nodes[int(parts[0])]
                        node2 = nodes[int(parts[1])]
                        speed = float(parts[2])
                        road = Road(node1, node2, speed, False)
                        node1.add_road(road)
                        node2.add_road(road)
                        roads.append(road)

        except FileNotFoundError:
            print("File not found. Please provide a valid file path.")
        except Exception as e:
            print("An error occurred:", e)

        self.nodes = nodes
        self.roads = roads

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_road(self, road: Road):
        self.roads.append(road)


class Query:
    def __init__(self, id: int, src_x: float, src_y: float, dst_x: float, dst_y, r):
        self.id = id
        self.src_x = src_x
        self.src_y = src_y
        self.dst_x = dst_x
        self.dst_y = dst_y
        self.r = r
        self.file_name = None

    def set_file_name(self, file_name):
        self.file_name = file_name

    @staticmethod
    def read_queries(queries_path: str):
        queries = []
        try:
            with open(queries_path, 'r') as file:
                for i, line in enumerate(file):
                    line = line.strip()
                    if i == 0:
                        continue
                    parts = line.split(' ')
                    src_x = float(parts[0])
                    src_y = float(parts[1])
                    dst_x = float(parts[2])
                    dst_y = float(parts[3])
                    r = float(parts[4])
                    queries.append(Query(i, src_x, src_y, dst_x, dst_y, r))
        except FileNotFoundError:
            print("File not found. Please provide a valid file path.")
        except Exception as e:
            print("An error occurred:", e)

        return queries


class Result:
    REASON_SUCCESS = 0
    REASON_START_NODE_NOT_FOUND = 1
    REASON_END_NODE_NOT_FOUND = 2
    REASON_START_END_NODES_NOT_FOUND = 3
    REASON_NO_PATH = 4

    def __init__(self, graph: Graph, query: Query, nodes: list, duration: float, reason: int):
        self.graph = graph
        self.query = query
        self.nodes = nodes
        self.duration = duration
        self.exec_time = None
        self.reason = reason

    def set_exec_time(self, exec_time: float):
        self.exec_time = exec_time

    def get_path_length(self):
        walking_length = 0
        vehicle_length = 0
        path_step = len(self.nodes)
        for i in range(path_step - 1):
            node = self.nodes[i]
            next_node = self.nodes[i + 1]
            for road in node.roads:
                if road.node1 == next_node or road.node2 == next_node:
                    if i == 0 or i == path_step - 2:
                        walking_length += road.length
                    else:
                        vehicle_length += road.length
                    break
        return walking_length, vehicle_length

    def __str__(self):
        if self.reason == self.REASON_START_END_NODES_NOT_FOUND:
            return (f'Query #{self.query.id}\n'
                    f'No solution for Query {self.query.id} because there is no starting and ending nodes close enough')
        elif self.reason == self.REASON_START_NODE_NOT_FOUND:
            return (f'Query #{self.query.id}\n'
                    f'No solution for Query {self.query.id} because there is no starting node close enough')
        elif self.reason == self.REASON_END_NODE_NOT_FOUND:
            return (f'Query #{self.query.id}\n'
                    f'No solution for Query {self.query.id} because there is no ending node close enough')
        elif self.reason == self.REASON_NO_PATH:
            return (f'Query #{self.query.id}\n'
                    f'No solution for Query {self.query.id} because there is no path between starting and ending nodes')
        else:
            nodes = [node.name for node in self.nodes]
            walking_length, vehicle_length = self.get_path_length()
            return (f'Query #{self.query.id}\n'
                    f'Path with the shortest time is: {nodes}\n'
                    f'Shortest time in hours from source to destination: {self.duration * 60} min\n'
                    f'Distance from source to destination: {walking_length + vehicle_length}\n'
                    f'       Walking distance from source to destination: {walking_length} km\n'
                    f'       Vehicle distance from source to destination: {vehicle_length} km\n'
                    f'Total execution time = {self.exec_time} s')

    def generate_map(self, saving_path: str, plot_all_nodes: bool):
        fig, ax = plt.subplots(figsize=(8, 8))

        if plot_all_nodes:
            # Plotting the points
            x = []
            y = []
            for node in self.graph.nodes:
                if node.is_fake:
                    continue
                x.append(node.x)
                y.append(node.y)
            ax.scatter(x, y)

            line_segments = []
            for road in self.graph.roads:
                if road.is_fake:
                    continue
                line_segments.append(((road.node1.x, road.node1.y), (road.node2.x, road.node2.y)))

            lc = LineCollection(line_segments, colors='grey', linestyles='--')
            ax.add_collection(lc)

        # Highlighting source and destination
        ax.scatter(self.query.src_x, self.query.src_y, color='orange', s=100, marker='*')
        ax.scatter(self.query.dst_x, self.query.dst_y, color='red', s=100, marker='*')

        # Plotting the road
        if self.nodes:
            ax.plot([self.nodes[0].x, self.nodes[1].x], [self.nodes[0].y, self.nodes[1].y], color='orange',
                    linestyle='--')
            ax.plot([self.nodes[-2].x, self.nodes[-1].x], [self.nodes[-2].y, self.nodes[-1].y], color='red',
                    linestyle='--')
            road_length = len(self.nodes)
            path_segment = []
            for i in range(1, road_length - 2):
                point1 = self.nodes[i]
                point2 = self.nodes[i + 1]
                path_segment.append(((point1.x, point1.y), (point2.x, point2.y)))
            plc = LineCollection(path_segment, colors='green', linestyles='-')
            ax.add_collection(plc)

        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        file_name = f'Query{self.query.id}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        self.query.set_file_name(file_name)
        plt.savefig(f'{saving_path}/{file_name}', dpi=300)
        plt.close()


class Navigator:
    def __init__(self, map_file_path: str):
        self.map_file_path = map_file_path

    def navigate(self, query: Query, need_generate_map=False, saving_map_path=None, plot_all_nodes=True):
        graph = Graph(self.map_file_path)
        result = self._process_query(graph, query)
        if need_generate_map:
            result.generate_map(saving_map_path, plot_all_nodes)
        return result

    def _process_query(self, graph: Graph, query: Query):
        start_tic = time.time()
        src_candidates, dst_candidates = self._find_candidate_intersections(graph, query)
        if not src_candidates or not dst_candidates:
            if not src_candidates and not dst_candidates:
                reason = Result.REASON_START_END_NODES_NOT_FOUND
            elif not src_candidates:
                reason = Result.REASON_START_NODE_NOT_FOUND
            else:
                reason = Result.REASON_END_NODE_NOT_FOUND

            result = Result(graph, query, [], 0, reason)
            end_tick = time.time()
            result.set_exec_time(end_tick - start_tic)
            return result
        src = self._add_node(graph, 'S', query.src_x, query.src_y, src_candidates)
        dst = self._add_node(graph, 'E', query.dst_x, query.dst_y, dst_candidates)
        path, total_time = self._dijkstra(graph, src, dst)
        reason = Result.REASON_SUCCESS if path else Result.REASON_NO_PATH
        result = Result(graph, query, path, total_time, reason)
        end_tic = time.time()
        result.set_exec_time(end_tic - start_tic)
        return result

    @staticmethod
    def _add_node(graph: Graph, name: str, x: float, y: float, candidates: list):
        node = Node(name, x, y, True)
        for candidate in candidates:
            road = Road(node, candidate, WALK_SPEED, True)
            graph.add_road(road)
            node.add_road(road)
            candidate.add_road(road)

        graph.add_node(node)
        return node

    @staticmethod
    def _find_candidate_intersections(graph: Graph, query: Query):
        src_candidates = []
        dst_candidates = []
        for node in graph.nodes:
            dist = euclidean_distance(node.x, node.y, query.src_x, query.src_y)
            if dist <= query.r:
                src_candidates.append(node)

            dist = euclidean_distance(node.x, node.y, query.dst_x, query.dst_y)
            if dist <= query.r:
                dst_candidates.append(node)

        return src_candidates, dst_candidates

    @staticmethod
    def _dijkstra(graph: Graph, start_node: Node, end_node: Node):
        distance = {node: float('inf') for node in graph.nodes}
        distance[start_node] = 0
        previous = {node: None for node in graph.nodes}

        fib_heap = FibonacciHeap()
        for node in graph.nodes:
            if node == start_node:
                node.add_fib_node(fib_heap.insert(0, node))
            else:
                node.add_fib_node(fib_heap.insert(math.inf, node))

        while fib_heap.total_nodes != 0:
            current_node = fib_heap.extract_min().value

            if current_node == end_node:
                path = []
                while previous[current_node]:
                    path.append(current_node)
                    current_node = previous[current_node]
                if len(path) != 0:
                    path.append(start_node)
                return list(reversed(path)), distance[end_node]

            for road in current_node.roads:
                neighbor = road.node1 if road.node2 == current_node else road.node2
                alt_distance = distance[current_node] + road.weight
                if alt_distance < distance[neighbor]:
                    distance[neighbor] = alt_distance
                    previous[neighbor] = current_node
                    fib_heap.decrease_key(neighbor.fib_node, alt_distance)

        return [], None

    def evaluate(self, query: Query, use_fake_nodes: bool, use_fib: bool):
        graph = Graph(self.map_file_path)
        start_tic = time.time()
        src_candidates, dst_candidates = self._find_candidate_intersections(graph, query)
        if not src_candidates or not dst_candidates:
            if not src_candidates and not dst_candidates:
                reason = Result.REASON_START_END_NODES_NOT_FOUND
            elif not src_candidates:
                reason = Result.REASON_START_NODE_NOT_FOUND
            else:
                reason = Result.REASON_END_NODE_NOT_FOUND

            result = Result(graph, query, [], 0, reason)
            end_tick = time.time()
            result.set_exec_time(end_tick - start_tic)
            return result

        if use_fake_nodes:
            src = self._add_node(graph, 'S', query.src_x, query.src_y, src_candidates)
            dst = self._add_node(graph, 'E', query.dst_x, query.dst_y, dst_candidates)
            if use_fib:
                path, total_time = self._dijkstra(graph, src, dst)
            else:
                path, total_time = self._naive_dijkstra(graph, src, dst)
            reason = Result.REASON_SUCCESS if path else Result.REASON_NO_PATH
            result = Result(graph, query, path, total_time, reason)
            end_tic = time.time()
            result.set_exec_time(end_tic - start_tic)
            return result

        best_result = Result(graph, query, [], math.inf, Result.REASON_NO_PATH)
        for src in src_candidates:
            for dst in dst_candidates:
                if use_fib:
                    path, total_time = self._dijkstra(graph, src, dst)
                else:
                    path, total_time = self._naive_dijkstra(graph, src, dst)

                if path:
                    total_time += euclidean_distance(query.src_x, query.src_y, src.x, src.y) / WALK_SPEED
                    total_time += euclidean_distance(query.dst_x, query.dst_y, dst.x, dst.y) / WALK_SPEED

                    if total_time < best_result.duration:
                        best_result = Result(graph, query, path, total_time, Result.REASON_SUCCESS)

        end_tic = time.time()
        best_result.set_exec_time(end_tic - start_tic)

        return best_result

    def _naive_dijkstra(self, graph: Graph, start_node: Node, end_node: Node):
        distance = {node: float('inf') for node in graph.nodes}
        distance[start_node] = 0
        previous = {node: None for node in graph.nodes}
        pq = PriorityQueue()
        for node in graph.nodes:
            if node == start_node:
                pq.insert(0, node)
            else:
                pq.insert(math.inf, node)

        while not pq.is_empty():
            d, current_node = pq.extract_min()

            if current_node == end_node:
                path = []
                while previous[current_node]:
                    path.append(current_node)
                    current_node = previous[current_node]
                if len(path) != 0:
                    path.append(start_node)
                return list(reversed(path)), distance[end_node]

            for i, road in enumerate(current_node.roads):
                neighbor = road.node1 if road.node2 == current_node else road.node2
                alt_distance = distance[current_node] + road.weight
                if alt_distance < distance[neighbor]:
                    distance[neighbor] = alt_distance
                    previous[neighbor] = current_node
                    pq.decrease_key(alt_distance, neighbor)

        return [], None


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt(pow(x1 - x2, 2) + pow(y2 - y1, 2))
