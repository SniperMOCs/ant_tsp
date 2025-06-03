import numpy as np
from typing import List, Tuple, Callable
import random
import time

class AntColonyTSP:
    def __init__(
        self,
        distances: List[List[float]],
        n_ants: int = 10,
        n_iterations: int = 100,
        decay: float = 0.1,
        alpha: float = 1.0,
        beta: float = 2.0,
        on_iteration: Callable = None,
        delay: float = 0.1  # Задержка между итерациями в секундах
    ):
        """
        Инициализация алгоритма муравьиной колонии для решения задачи коммивояжера
        
        Args:
            distances: матрица расстояний между городами
            n_ants: количество муравьев
            n_iterations: количество итераций
            decay: коэффициент испарения феромона
            alpha: важность феромона
            beta: важность расстояния
            on_iteration: функция обратного вызова для визуализации процесса
            delay: задержка между итерациями в секундах
        """
        self.distances = np.array(distances)
        self.n_cities = len(distances)
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.on_iteration = on_iteration
        self.delay = delay
        
        # Инициализация матрицы феромонов
        self.pheromone = np.ones((self.n_cities, self.n_cities))
        self.best_path = None
        self.best_distance = float('inf')

    def _calculate_probabilities(self, pheromone: np.ndarray, dist: np.ndarray, visited: List[int], current: int) -> np.ndarray:
        """Вычисление вероятностей перехода в следующий город"""
        pheromone = np.copy(pheromone[current])
        dist = np.copy(dist[current])
        
        # Установка вероятности 0 для посещенных городов
        for i in visited:
            pheromone[i] = 0
            
        # Вычисление вероятностей
        probabilities = (pheromone ** self.alpha) * ((1.0 / (dist + 1e-10)) ** self.beta)
        
        # Проверка на случай, если все вероятности равны 0
        sum_probabilities = np.sum(probabilities)
        if sum_probabilities == 0:
            # Если все вероятности равны 0, установим равные вероятности для непосещенных городов
            unvisited = [i for i in range(self.n_cities) if i not in visited]
            if unvisited:
                probabilities[unvisited] = 1
            
        # Нормализация вероятностей
        sum_probabilities = np.sum(probabilities)
        if sum_probabilities > 0:
            probabilities = probabilities / sum_probabilities
        
        return probabilities

    def _construct_solution(self) -> Tuple[List[int], float]:
        """Построение решения одним муравьем"""
        path = []
        visited = set()
        current_city = random.randint(0, self.n_cities - 1)
        path.append(current_city)
        visited.add(current_city)
        
        while len(visited) < self.n_cities:
            probabilities = self._calculate_probabilities(
                self.pheromone,
                self.distances,
                list(visited),
                current_city
            )
            
            # Выбор следующего города
            next_city = np.random.choice(range(self.n_cities), p=probabilities)
            path.append(next_city)
            visited.add(next_city)
            current_city = next_city
            
        # Вычисление общего расстояния
        total_distance = 0
        for i in range(len(path)):
            total_distance += self.distances[path[i]][path[(i + 1) % self.n_cities]]
            
        return path, total_distance

    def _update_pheromone(self, paths: List[List[int]], distances: List[float]):
        """Обновление феромонов на путях"""
        # Испарение феромона
        self.pheromone *= (1 - self.decay)
        
        # Добавление нового феромона
        for path, distance in zip(paths, distances):
            for i in range(len(path)):
                current_city = path[i]
                next_city = path[(i + 1) % self.n_cities]
                # Добавляем феромон пропорционально качеству решения
                pheromone_amount = 1.0 / distance
                self.pheromone[current_city][next_city] += pheromone_amount
                self.pheromone[next_city][current_city] += pheromone_amount

    def solve(self, stop_flag=None):
        """
        Решение задачи коммивояжера
        stop_flag: функция, возвращающая True, если нужно остановить алгоритм
        """
        best_path = None
        best_distance = float('inf')
        start_time = time.time()  # Начинаем замер времени
        
        for iteration in range(self.n_iterations):
            # Проверяем флаг остановки
            if stop_flag and stop_flag():
                break
                
            # Отправляем муравьев на поиск пути
            paths = []
            distances = []
            
            for ant in range(self.n_ants):
                path = self._construct_solution()[0]
                distance = self._construct_solution()[1]
                paths.append(path)
                distances.append(distance)
                
                # Обновляем лучший путь
                if distance < best_distance:
                    best_distance = distance
                    best_path = path.copy()
            
            # Обновляем феромоны
            self._update_pheromone(paths, distances)
            
            # Вызываем callback с текущим состоянием
            if self.on_iteration:
                self.on_iteration(
                    iteration,
                    self.pheromone.copy(),
                    paths,
                    distances,
                    (best_path, best_distance)
                )
            
            # Добавляем задержку если она указана
            if self.delay:
                time.sleep(self.delay)

        execution_time = time.time() - start_time  # Завершаем замер времени
        return best_path, best_distance, execution_time 