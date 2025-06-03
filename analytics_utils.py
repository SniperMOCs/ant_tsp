import numpy as np
import time
from ant_colony_tsp import AntColonyTSP

def analyze_ants_impact(distances, parameters):
    """Анализ влияния количества муравьев на время выполнения"""
    n_ants_values = list(range(5, 31, 5))  # От 5 до 30 с шагом 5
    time_results = []
    
    for n_ants in n_ants_values:
        # Создаем экземпляр ACO с текущим количеством муравьев
        aco = AntColonyTSP(
            distances=distances,
            n_ants=n_ants,
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=parameters['alpha'],
            beta=parameters['beta'],
            delay=0  # Отключаем задержку для ускорения анализа
        )
        
        # Запускаем алгоритм и получаем время выполнения
        _, _, execution_time = aco.solve()
        time_results.append(execution_time)
    
    return n_ants_values, time_results

def analyze_decay_impact(distances, parameters):
    """Анализ влияния коэффициента испарения на время выполнения"""
    decay_values = np.linspace(0.1, 0.9, 9)  # От 0.1 до 0.9 с шагом 0.1
    time_results = []
    
    for decay in decay_values:
        # Создаем экземпляр ACO с текущим коэффициентом испарения
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=decay,
            alpha=parameters['alpha'],
            beta=parameters['beta'],
            delay=0
        )
        
        # Запускаем алгоритм и получаем время выполнения
        _, _, execution_time = aco.solve()
        time_results.append(execution_time)
    
    return decay_values, time_results

def analyze_alpha_beta_impact(distances, parameters):
    """Анализ влияния параметров alpha и beta на качество решения"""
    param_values = np.linspace(0.5, 3.0, 6)  # От 0.5 до 3.0 с шагом 0.5
    alpha_results = []
    beta_results = []
    
    # Анализ влияния alpha
    for alpha in param_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=alpha,
            beta=parameters['beta'],
            delay=0
        )
        best_path, best_distance, _ = aco.solve()  # Игнорируем время выполнения
        alpha_results.append(best_distance)
    
    # Анализ влияния beta
    for beta in param_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=parameters['alpha'],
            beta=beta,
            delay=0
        )
        best_path, best_distance, _ = aco.solve()  # Игнорируем время выполнения
        beta_results.append(best_distance)
    
    return param_values, param_values, alpha_results, beta_results

def analyze_convergence(distances, parameters):
    """Анализ сходимости алгоритма с разными параметрами"""
    # Определяем наборы параметров для сравнения
    parameter_sets = [
        {
            'n_ants': 5,
            'decay': 0.1,
            'alpha': 1,
            'beta': 2,
            'label': 'Муравьи=5, Испарение=0.1, α=1, β=2'
        },
        {
            'n_ants': 10,
            'decay': 0.1,
            'alpha': 1,
            'beta': 2,
            'label': 'Муравьи=10, Испарение=0.1, α=1, β=2'
        },
        {
            'n_ants': 10,
            'decay': 0.2,
            'alpha': 1,
            'beta': 2,
            'label': 'Муравьи=10, Испарение=0.2, α=1, β=2'
        },
        {
            'n_ants': 10,
            'decay': 0.1,
            'alpha': 2,
            'beta': 1,
            'label': 'Муравьи=10, Испарение=0.1, α=2, β=1'
        }
    ]
    
    # Создаем списки для хранения результатов
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    labels = []
    
    # Для каждого набора параметров
    for params in parameter_sets:
        # Создаем экземпляр ACO с текущими параметрами
        aco = AntColonyTSP(
            distances=distances,
            n_ants=params['n_ants'],
            n_iterations=int(parameters['n_iterations']),
            decay=params['decay'],
            alpha=params['alpha'],
            beta=params['beta'],
            delay=0
        )
        
        # Отслеживаем лучшее расстояние на каждой итерации
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        # Запускаем алгоритм с callback-функцией
        aco.on_iteration = iteration_callback
        aco.solve()
        
        # Сохраняем результаты
        convergence_data.append(best_distances)
        labels.append(params['label'])
    
    return iterations, convergence_data, labels 