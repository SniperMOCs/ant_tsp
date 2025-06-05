import numpy as np
import time
from ant_colony_tsp import AntColonyTSP

def analyze_ants_impact(distances, parameters):
    """Анализ влияния количества муравьев на сходимость алгоритма"""
    base_ants = int(parameters['n_ants'])
    # Создаем 5 значений: -60%, -30%, базовое, +30%, +60% от базового
    n_ants_values = [
        max(5, int(base_ants * 0.4)),  # -60%
        max(5, int(base_ants * 0.7)),  # -30%
        base_ants,                      # базовое
        int(base_ants * 1.3),          # +30%
        int(base_ants * 1.6)           # +60%
    ]
    n_ants_values = sorted(list(set(n_ants_values)))  # Убираем дубликаты и сортируем
    
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    
    for n_ants in n_ants_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=n_ants,
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=parameters['alpha'],
            beta=parameters['beta'],
            delay=0
        )
        
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        aco.on_iteration = iteration_callback
        aco.solve()
        
        convergence_data.append(best_distances)
    
    return iterations, convergence_data, [f"Муравьев: {n}" for n in n_ants_values]

def analyze_decay_impact(distances, parameters):
    """Анализ влияния коэффициента испарения на сходимость алгоритма"""
    base_decay = parameters['decay']
    
    # Адаптивно определяем шаг изменения параметра
    if base_decay <= 0.3:
        # Если базовое значение близко к минимуму, сдвигаем диапазон вправо
        decay_values = [
            0.1,
            base_decay,
            min(0.9, base_decay + 0.2),
            min(0.9, base_decay + 0.4),
            min(0.9, base_decay + 0.6)
        ]
    elif base_decay >= 0.7:
        # Если базовое значение близко к максимуму, сдвигаем диапазон влево
        decay_values = [
            max(0.1, base_decay - 0.6),
            max(0.1, base_decay - 0.4),
            max(0.1, base_decay - 0.2),
            base_decay,
            0.9
        ]
    else:
        # Если базовое значение в середине диапазона, распределяем значения равномерно
        step = min(
            (0.9 - base_decay) / 2,  # шаг вверх
            (base_decay - 0.1) / 2    # шаг вниз
        )
        decay_values = [
            max(0.1, base_decay - 2*step),
            max(0.1, base_decay - step),
            base_decay,
            min(0.9, base_decay + step),
            min(0.9, base_decay + 2*step)
        ]
    
    decay_values = sorted(list(set(decay_values)))  # Убираем дубликаты и сортируем
    
    # Если после удаления дубликатов осталось меньше 5 значений,
    # добавляем промежуточные значения
    while len(decay_values) < 5:
        # Находим максимальный промежуток между соседними значениями
        max_gap = 0
        insert_pos = 0
        for i in range(len(decay_values) - 1):
            gap = decay_values[i + 1] - decay_values[i]
            if gap > max_gap:
                max_gap = gap
                insert_pos = i
        
        # Вставляем значение в середину максимального промежутка
        new_value = decay_values[insert_pos] + max_gap / 2
        decay_values.insert(insert_pos + 1, new_value)
    
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    
    for decay in decay_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=decay,
            alpha=parameters['alpha'],
            beta=parameters['beta'],
            delay=0
        )
        
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        aco.on_iteration = iteration_callback
        aco.solve()
        
        convergence_data.append(best_distances)
    
    return iterations, convergence_data, [f"Испарение: {d:.2f}" for d in decay_values]

def analyze_alpha_impact(distances, parameters):
    """Анализ влияния параметра alpha на сходимость алгоритма"""
    base_alpha = parameters['alpha']
    # Создаем 5 значений: -60%, -30%, базовое, +30%, +60% от базового
    alpha_values = [
        max(0.5, base_alpha * 0.4),  # -60%
        max(0.5, base_alpha * 0.7),  # -30%
        base_alpha,                   # базовое
        base_alpha * 1.3,            # +30%
        base_alpha * 1.6             # +60%
    ]
    alpha_values = sorted(list(set(alpha_values)))  # Убираем дубликаты и сортируем
    
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    
    for alpha in alpha_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=alpha,
            beta=parameters['beta'],
            delay=0
        )
        
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        aco.on_iteration = iteration_callback
        aco.solve()
        
        convergence_data.append(best_distances)
    
    return iterations, convergence_data, [f"Alpha: {a:.2f}" for a in alpha_values]

def analyze_beta_impact(distances, parameters):
    """Анализ влияния параметра beta на сходимость алгоритма"""
    base_beta = parameters['beta']
    # Создаем 5 значений: -60%, -30%, базовое, +30%, +60% от базового
    beta_values = [
        max(0.5, base_beta * 0.4),  # -60%
        max(0.5, base_beta * 0.7),  # -30%
        base_beta,                   # базовое
        base_beta * 1.3,            # +30%
        base_beta * 1.6             # +60%
    ]
    beta_values = sorted(list(set(beta_values)))  # Убираем дубликаты и сортируем
    
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    
    for beta in beta_values:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=int(parameters['n_ants']),
            n_iterations=int(parameters['n_iterations']),
            decay=parameters['decay'],
            alpha=parameters['alpha'],
            beta=beta,
            delay=0
        )
        
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        aco.on_iteration = iteration_callback
        aco.solve()
        
        convergence_data.append(best_distances)
    
    return iterations, convergence_data, [f"Beta: {b:.2f}" for b in beta_values]

def analyze_parameters_comparison(distances, parameters):
    """Анализ сходимости алгоритма с разными параметрами"""
    # Определяем наборы параметров для сравнения
    base_ants = int(parameters['n_ants'])
    base_decay = parameters['decay']
    base_alpha = parameters['alpha']
    base_beta = parameters['beta']
    
    parameter_sets = [
        {
            'n_ants': base_ants,
            'decay': base_decay,
            'alpha': base_alpha,
            'beta': base_beta,
            'label': f'Муравьи={base_ants}, Испарение={base_decay:.2f}, α={base_alpha:.2f}, β={base_beta:.2f}'
        },
        {
            'n_ants': max(5, int(base_ants * 0.4)),  # -60% муравьев
            'decay': base_decay,
            'alpha': base_alpha,
            'beta': base_beta,
            'label': f'Муравьи={max(5, int(base_ants * 0.4))}, Испарение={base_decay:.2f}, α={base_alpha:.2f}, β={base_beta:.2f}'
        },
        {
            'n_ants': base_ants,
            'decay': min(0.9, base_decay + 0.3),  # +0.3 к испарению
            'alpha': base_alpha,
            'beta': base_beta,
            'label': f'Муравьи={base_ants}, Испарение={min(0.9, base_decay + 0.3):.2f}, α={base_alpha:.2f}, β={base_beta:.2f}'
        },
        {
            'n_ants': base_ants,
            'decay': max(0.1, base_decay - 0.3),  # -0.3 к испарению
            'alpha': base_alpha,
            'beta': base_beta,
            'label': f'Муравьи={base_ants}, Испарение={max(0.1, base_decay - 0.3):.2f}, α={base_alpha:.2f}, β={base_beta:.2f}'
        },
        {
            'n_ants': base_ants,
            'decay': base_decay,
            'alpha': base_alpha * 1.6,  # +60% к alpha
            'beta': base_beta,
            'label': f'Муравьи={base_ants}, Испарение={base_decay:.2f}, α={base_alpha * 1.6:.2f}, β={base_beta:.2f}'
        },
        {
            'n_ants': base_ants,
            'decay': base_decay,
            'alpha': base_alpha,
            'beta': base_beta * 1.6,  # +60% к beta
            'label': f'Муравьи={base_ants}, Испарение={base_decay:.2f}, α={base_alpha:.2f}, β={base_beta * 1.6:.2f}'
        }
    ]
    
    iterations = list(range(int(parameters['n_iterations'])))
    convergence_data = []
    labels = []
    
    for params in parameter_sets:
        aco = AntColonyTSP(
            distances=distances,
            n_ants=params['n_ants'],
            n_iterations=int(parameters['n_iterations']),
            decay=params['decay'],
            alpha=params['alpha'],
            beta=params['beta'],
            delay=0
        )
        
        best_distances = []
        current_best = float('inf')
        
        def iteration_callback(iteration, pheromone, paths, distances, current_best_info):
            nonlocal current_best
            if current_best_info[1] < current_best:
                current_best = current_best_info[1]
            best_distances.append(current_best)
        
        aco.on_iteration = iteration_callback
        aco.solve()
        
        convergence_data.append(best_distances)
        labels.append(params['label'])
    
    return iterations, convergence_data, labels 