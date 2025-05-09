import copy
from typing import List, Tuple
from pacman.data_core.enums import GhostStateEnum
from pacmania.config import *
import heapq


class PacManIA:
    def __init__(self, main_scene):
        self.main_scene = main_scene
        self.bool = False

    def get_map(self):
        return self.main_scene.get_loader().collision_map

    def get_ghosts(self):
        return self.main_scene.get_ghosts()

    def get_ghosts_positions(self)-> List[Tuple[int, int]]:
        pos = []
        for ghost in self.get_ghosts():
            pos.append(ghost.get_cell())
        return pos

    def get_pacman(self):
        return self.main_scene.get_pacman()

    def get_pacman_pos(self):
        return self.main_scene.get_pacman().get_cell()

    def get_seeds(self):
        return self.main_scene.get_seeds().get_seeds()

    def get_seeds_positions(self)-> List[Tuple[int, int]]:
        pos = []
        seeds = self.get_seeds()
        for y in range(len(seeds)):
            for x in range(len(seeds[y])):
                if seeds[y][x]:
                    pos.append((x, y))
        return pos

    def get_direction(self):
        res = self.alpha_beta(self.get_pacman_pos(), self.get_ghosts_positions(), self.get_seeds_positions(),2, 0, float('-inf'), float('inf'),[])
        return res[1][0]

    def print_seed(self):
        if self.bool:
            return
        self.bool = True
        seed = self.get_seeds()
        for y in seed:
            for x in y:
                if x :
                    print("+", end="")
                else:
                    print("-", end="")
            print("")

    def get_authorised_directions(self, pos : Tuple[int, int]):
        res = []
        collision_map = self.get_map()
        collision_value = collision_map[pos[1]][pos[0]]
        if collision_value & 0b0001:
            res.append("right")
        if collision_value & 0b0010:
            res.append("down")
        if collision_value & 0b0100:
            res.append("left")
        if collision_value & 0b1000:
            res.append("up")
        return res

    def apply_direction(self, pos : Tuple[int, int], direction):
        if direction == "up":
            return pos[0], pos[1] - 1
        if direction == "down":
            return pos[0], pos[1] + 1
        if direction == "left":
            return pos[0] - 1, pos[1]
        if direction == "right":
            return pos[0] + 1, pos[1]

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def dijkstra(self, start, goal, collision_map):
        rows, cols = len(collision_map), len(collision_map[0])

        # Directions autorisées
        directions = {
            "right": (1, 0),
            "down": (0, 1),
            "left": (-1, 0),
            "up": (0, -1),
        }

        direction_flags = {
            "right": 0b0001,
            "down": 0b0010,
            "left": 0b0100,
            "up": 0b1000,
        }

        # File de priorité (coût, position)
        open_set = []
        heapq.heappush(open_set, (0, start))

        # Coût pour arriver à chaque nœud
        g_costs = {start: 0}

        # Pour reconstruire le chemin
        came_from = {}

        while open_set:
            cost, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruction du chemin
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return len(path), path

            x, y = current

            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy

                # Vérification des limites
                if not (0 <= new_x < cols and 0 <= new_y < rows):
                    continue

                # Vérification de la collision
                if collision_map[y][x] & direction_flags[direction] == 0:
                    continue

                new_pos = (new_x, new_y)
                new_cost = cost + 1

                if new_pos not in g_costs or new_cost < g_costs[new_pos]:
                    g_costs[new_pos] = new_cost
                    came_from[new_pos] = current
                    heapq.heappush(open_set, (new_cost, new_pos))

        # Aucun chemin trouvé
        return float('inf'), []

    def evaluation(self, pacman_pos: Tuple[int, int], ghost_pos: List[Tuple[int, int]], seeds_pos: List[Tuple[int, int]]):

        if seeds_pos:
            closest_seed_dist = min(self.manhattan_distance(pacman_pos, seed) for seed in seeds_pos)
            seed_score = SEED_WEIGHT / (closest_seed_dist + 1)
        else:
            seed_score = 0

        ghost_score = 0
        for ghost in ghost_pos:
            dist = self.dijkstra(pacman_pos, ghost, self.get_map())[0]
            if dist <= 2:  # Danger immédiat
                ghost_score -= GHOST_AVOIDANCE_WEIGHT
            else:
                ghost_score -= GHOST_AVOIDANCE_WEIGHT / (dist + 1)

        total_score = seed_score + ghost_score
        return total_score



    def alpha_beta(self, pacman_pos, ghost_pos, seeds_pos, depth, agent_index, alpha, beta, deplacements):
        num_agents = 5

        if depth == 0:
            return self.evaluation(pacman_pos, ghost_pos, seeds_pos), deplacements

        next_agent = (agent_index + 1) % num_agents
        next_depth = depth - 1 if next_agent == 0 else depth

        if agent_index == 0:  # Pac-Man (Max)
            legal_actions = self.get_authorised_directions(pacman_pos)
            value = float('-inf')
            best_path = []
            for action in legal_actions:
                successor = self.apply_direction(pacman_pos, action)
                new_deplacement = deplacements + [action]
                score, path = self.alpha_beta(successor, copy.deepcopy(ghost_pos), seeds_pos, next_depth, next_agent, alpha, beta, new_deplacement)
                if score > value:
                    value = score
                    best_path = path
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value, best_path

        else:  # Fantômes (Min)
            legal_actions = self.get_authorised_directions(ghost_pos[agent_index-1])
            value = float('+inf')
            for action in legal_actions:
                successor = self.apply_direction(ghost_pos[agent_index-1], action)
                ghost_successor = copy.deepcopy(ghost_pos)
                ghost_successor[agent_index-1] = successor
                ghosts = self.get_ghosts()
                while next_agent !=0 and ghosts[next_agent-1].get_state() == GhostStateEnum.INDOOR:
                    next_agent = (next_agent + 1) % num_agents
                    if next_agent == 0:
                        next_depth = next_depth -1

                score, path = self.alpha_beta(pacman_pos, ghost_successor, seeds_pos, next_depth, next_agent, alpha, beta, deplacements)
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value, deplacements
