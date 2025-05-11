import copy
from collections import deque
from typing import List, Tuple
from pacman.data_core.enums import GhostStateEnum
from pacmania.config import *
import heapq


class PacManIA:
    def __init__(self, main_scene):
        self.main_scene = main_scene
        self.bool = False
        self.recent_positions = deque(maxlen=4)

    def get_map(self):
        return self.main_scene.get_loader().collision_map

    def get_slow_zone(self):
        return self.main_scene.get_loader().slow_ghost_rect

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
        pos = self.main_scene.get_pacman().get_cell() #mettre un malus pour un retour en areiere
        if pos not in self.recent_positions:
            self.recent_positions.append(pos)
        return pos

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
        pos_pac = self.get_pacman_pos()
        res = self.alpha_beta(pos_pac, self.get_ghosts_positions(), self.get_seeds_positions(), SEARCH_DEPTH, 0, float('-inf'), float('inf'),[])
        return res[1][0]

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

    @staticmethod
    def apply_direction(pos : Tuple[int, int], direction):
        x, y = pos
        if direction == "up":
            y -= 1
        if direction == "down":
            y += 1
        if direction == "left":
            x -= 1
        if direction == "right":
            x += 1
        if x == 0:
            x = 27
        if x == 28:
            x = 1
        return x, y

    @staticmethod
    def manhattan_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def in_slow_zone(self, pos : Tuple[int, int]):
        tunnel = self.get_slow_zone()
        for i in range(len(tunnel)):
            if tunnel[i][0] <= pos[0] <= tunnel[i][2] and tunnel[i][1] <= pos[1] <= tunnel[i][3]:
                return True
        return False


    def dijkstra2(self,start, goal, collision_map):
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
            for direction in directions:
                new_x, new_y = self.apply_direction((x, y), direction)
                # Vérification des limites
                if not (0 <= new_x < cols and 0 <= new_y < rows):
                    continue
                # Vérification de la collision
                if collision_map[y][x]  & direction_flags[direction] == 0: #regler le probleme du bridge teleportation
                    continue
                new_pos = (new_x, new_y)
                new_cost = cost + 1
                if new_pos not in g_costs or new_cost < g_costs[new_pos]:
                    g_costs[new_pos] = new_cost
                    came_from[new_pos] = current
                    heapq.heappush(open_set, (new_cost, new_pos))
        # Aucun chemin trouvé
        return float('inf'), []


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

            for direction in directions:
                new_x, new_y = self.apply_direction((x, y), direction)

                # === Gérer les téléportations ===
                if new_x == -1:  # Sortie à gauche -> téléportation droite
                    new_x = cols - 1
                elif new_x == cols:  # Sortie à droite -> téléportation gauche
                    new_x = 0

                # Vérification des limites verticales
                if not (0 <= new_y < rows):
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

    @staticmethod
    def sort_directions(ghost, directions):
        orientation_x, orientation_y = ghost.get_direction()
        new_directions = copy.deepcopy(directions)
        if orientation_x == 1:
            if "left" in new_directions:
                new_directions.remove("left")
        if orientation_x == -1:
            if "right" in new_directions:
                new_directions.remove("right")
        if orientation_y == 1:
            if "up" in new_directions:
                new_directions.remove("up")
        if orientation_y == -1:
            if "down" in new_directions:
                new_directions.remove("down")
        return new_directions

    @staticmethod
    def get_nearby_seeds(pacman_pos, seeds_pos, radius=2):
        px, py = pacman_pos
        nearby_seeds = [(x, y) for x, y in seeds_pos
                        if px - radius <= x <= px + radius and py - radius <= y <= py + radius]
        return nearby_seeds

    def evaluation(self, pacman_pos: Tuple[int, int], ghost_pos: List[Tuple[int, int]], seeds_pos: List[Tuple[int, int]]):
        map_data = self.get_map()

        #partie pour les seeds proches : dijkstra sinon manhattan
        if seeds_pos:
            dijkstra_seed = self.get_nearby_seeds(pacman_pos, seeds_pos)
            if dijkstra_seed:
                closest_seed_dist = min(self.dijkstra(pacman_pos, seed, map_data)[0] for seed in dijkstra_seed)
            else:
                closest_seed_dist = min(self.manhattan_distance(pacman_pos, seed) for seed in seeds_pos)
            seed_score = SEED_WEIGHT / (closest_seed_dist + 1)
        else:
            seed_score = 0

        # Partie pour les fantômes
        ghost_score = 0
        ghosts = self.get_ghosts()
        for i in range(len(ghost_pos)):
            dist = self.dijkstra(pacman_pos, ghost_pos[i], map_data)[0]
            if ghosts[i].get_state() == GhostStateEnum.FRIGHTENED :
                if dist <= 2:
                    ghost_score += GHOST_FRIGHTENED_WEIGHT
                else :
                    ghost_score += GHOST_FRIGHTENED_WEIGHT / (dist + 1)
            else:
                if dist <= 2:  # Danger immédiat
                    ghost_score -= GHOST_AVOIDANCE_WEIGHT
                else:
                    ghost_score -= GHOST_AVOIDANCE_WEIGHT / (dist + 1)



        total_score = seed_score + ghost_score
        return total_score

    def alpha_beta(self, pacman_pos, ghost_pos, seeds_pos, depth, agent_index, alpha, beta, deplacements):
        num_agents = 5

        #quand on est a une feuille de notre arbre on evalue cette situation
        if depth == 0:
            return self.evaluation(pacman_pos, ghost_pos, seeds_pos), deplacements #on return déplacement pour avoir le meilleur deplacement de pacMan

        #on passe sur chaque agent et on decremente la profondeur seulement si on les a tous vu une fois
        next_agent = (agent_index + 1) % num_agents
        next_depth = depth - 1 if next_agent == 0 else depth

        if agent_index == 0:  # Pac-Man (Max)
            # on regarde les directions dans lesquelles il peut se rendre
            legal_actions = self.get_authorised_directions(pacman_pos)
            legal_actions.sort(key=lambda x: self.apply_direction(pacman_pos, x) in self.recent_positions)

            value = float('-inf')
            best_path = []
            for action in legal_actions:
                # On applique la direction à sa position
                successor = self.apply_direction(pacman_pos, action)
                new_deplacement = deplacements + [action] #mise à jour de la liste de ses déplacements

                score, path = self.alpha_beta(successor, copy.deepcopy(ghost_pos), seeds_pos, next_depth, next_agent, alpha, beta, new_deplacement)

                #regle les oscillations
                old_position = self.apply_direction(pacman_pos, action)
                if old_position in self.recent_positions:
                    score -= OSCILLATION_WEIGHT

                if score > value: # On vient de trouver un meilleur score par ce chemin
                    value = score
                    best_path = path # on retient ce chemin
                alpha = max(alpha, value)
                if beta <= alpha: # on coupe car on a forcément un chemin nous garantississant alpha
                    break
            return value, best_path

        else:  # Fantômes (Min)
            # On recupere les directions authorisé du fantome traité.
            legal_actions = self.get_authorised_directions(ghost_pos[agent_index-1])
            value = float('+inf')
            ghosts = self.get_ghosts()
            # Un fantôme ne peut pas rebrousser chemin donc on enleve l'opposé de sa direction actuelle.
            directions = self.sort_directions(ghosts[agent_index-1], legal_actions)

            for action in directions:
                successor = self.apply_direction(ghost_pos[agent_index-1], action)
                ghost_successor = copy.deepcopy(ghost_pos)
                ghost_successor[agent_index-1] = successor

                # Si un fantome n'est pas encore sortie de son enclôt on ne calcule rien sur lui et on passe au suivant
                while next_agent !=0 and ghosts[next_agent-1].get_state() == GhostStateEnum.INDOOR:
                    next_agent = (next_agent + 1) % num_agents
                    if next_agent == 0:
                        next_depth = next_depth -1

                map_data = self.get_map()
                # Si un fantôme est à plus de 2 * deeph de distance (dijkstra) alors on l'ignore
                while next_agent != 0 and self.dijkstra(pacman_pos, ghost_pos[next_agent-1], map_data)[0] > 2 * depth:
                    next_agent = (next_agent + 1) % num_agents
                    if next_agent == 0:
                        next_depth = next_depth - 1

                score, path = self.alpha_beta(pacman_pos, ghost_successor, seeds_pos, next_depth, next_agent, alpha, beta, deplacements)
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value, deplacements
