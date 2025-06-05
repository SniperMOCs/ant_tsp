import sys
import math
import random
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QPushButton, QVBoxLayout, QHBoxLayout,
                           QTextEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import (QPainter, QPen, QColor, QFont, 
                        QBrush, qRgb)
import numpy as np
from ant_colony_tsp import AntColonyTSP
from analytics_window import AnalyticsWindow

def read_distances(filename):
    distances = []
    with open(filename, 'r') as f:
        for line in f:
            row = [float(x) for x in line.strip().split()]
            distances.append(row)
    return distances

def read_parameters(filename):
    parameters = {}
    with open(filename, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            parameters[key] = float(value)
    return parameters

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.adj_list = {}

    def set_adj_list(self, adj_list):
        self.adj_list = adj_list
        self.nodes = list(adj_list.keys())
        self.edges = []
        for node in adj_list:
            for neighbor in adj_list[node]:
                if (node, neighbor) not in self.edges and (neighbor, node) not in self.edges:
                    self.edges.append((node, neighbor))

    def get_adj_list(self):
        return self.adj_list

class GraphWidget(QWidget, Graph):
    def __init__(self):
        QWidget.__init__(self)
        Graph.__init__(self)
        
        self.setMinimumSize(800, 400)
        self.setMaximumSize(16777215, 16777215)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        
        # Установка темного фона
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#0e1621"))
        self.setPalette(palette)

        # Инициализация переменных
        self.node_positions = {}
        self.pheromone_matrix = None
        self.current_paths = []
        self.current_iteration = 0
        self.best_path = None
        self.best_distance = float('inf')
        self.nodeColor = {}
        self.is_animating = False
        self.n_ants = 10  # Значение по умолчанию
        
        # Переменные для финальной анимации
        self.current_edge_index = 0
        self.edge_animation_step = 0
        self.total_animation_steps = 5
        self.edges_to_draw = []
        self.is_final_animation = False
        self.animation_completed = False  # Новый флаг для отслеживания завершенной анимации
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

    def reset(self):
        """Сброс всех результатов и состояний визуализации"""
        self.node_positions = {}
        self.pheromone_matrix = None
        self.current_paths = []
        self.current_iteration = 0
        self.best_path = None
        self.best_distance = float('inf')
        self.nodeColor = {}
        self.is_animating = False
        self.nodes = []
        self.edges = []
        self.adj_list = {}
        self.current_edge_index = 0
        self.edge_animation_step = 0
        self.edges_to_draw = []
        self.is_final_animation = False
        self.animation_completed = False
        self.update()

    def set_cities(self, distances, n_ants=10):
        # Сначала очищаем все предыдущие данные
        self.reset()
        
        # Сохраняем количество муравьев
        self.n_ants = n_ants
        
        # Создаем список смежности из матрицы расстояний
        adj_list = {}
        for i in range(len(distances)):
            adj_list[i] = []
            for j in range(len(distances[i])):
                if i != j and distances[i][j] > 0:
                    adj_list[i].append(j)
        
        # Устанавливаем список смежности
        self.set_adj_list(adj_list)
        
        # Устанавливаем цвета узлов
        for node in self.nodes:
            self.nodeColor[node] = 0
        self.colors = self.generateColors(0)
        
        # Рассчитываем позиции узлов
        self.node_positions = self.calculate_node_positions()
        
        # Инициализируем матрицу феромонов
        self.pheromone_matrix = np.ones((len(distances), len(distances)))
        
        self.update()

    def on_iteration(self, iteration, pheromone_state, paths, distances, current_best):
        """Обработчик события итерации алгоритма"""
        self.current_iteration = iteration
        self.pheromone_matrix = pheromone_state
        self.current_paths = paths
        
        # Сохраняем лучший путь и расстояние, но не отображаем их
        if current_best[1] < self.best_distance:
            self.best_path = current_best[0]
            self.best_distance = current_best[1]
        
        # Обновляем информацию об итерации
        if hasattr(self, 'parent') and self.parent():
            main_window = self.parent().parent()
            if hasattr(main_window, 'result_text'):
                text = f"Выполняется итерация: {iteration + 1}\n\n"
                text += f"Текущий лучший путь:\n{self.best_path + [self.best_path[0]]}\n"
                text += f"Длина пути: {self.best_distance:.2f}\n"
                text += f"Прошло времени: {time.time() - main_window.aco.start_time:.2f} сек."
                main_window.result_text.setText(text)
        
        self.update()
        QApplication.processEvents()

    def update_animation(self):
        """Обновление анимации"""
        if self.is_final_animation:
            if self.current_edge_index < len(self.edges_to_draw):
                if self.edge_animation_step < self.total_animation_steps:
                    self.edge_animation_step += 1
                else:
                    self.current_edge_index += 1
                    self.edge_animation_step = 0
            else:
                self.animation_timer.stop()
                self.is_final_animation = False
                self.animation_completed = True  # Устанавливаем флаг завершения анимации
            self.update()

    def show_final_result(self):
        """Отображение финального результата"""
        if self.best_path is not None:
            # Обновляем текст с финальным результатом
            if hasattr(self, 'parent') and self.parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'result_text'):
                    # Конвертируем значения в обычные Python числа
                    path_display = [int(x) for x in self.best_path] + [int(self.best_path[0])]
                    text = f"Найден оптимальный путь: {path_display}\n"
                    text += f"Длина пути: {float(self.best_distance):.2f}"
                    main_window.result_text.setText(text)
            
            # Подготовка к анимации
            self.is_final_animation = True
            self.current_edge_index = 0
            self.edge_animation_step = 0
            
            # Создаем список ребер для анимации
            path = [int(x) for x in self.best_path] + [int(self.best_path[0])]  # Замыкаем путь и конвертируем в обычные числа
            self.edges_to_draw = [(path[i], path[i+1]) for i in range(len(path)-1)]
            
            # Запускаем анимацию
            self.animation_timer.start(50)
            self.update()

    def paintEvent(self, event):
        if not self.node_positions:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Во время работы алгоритма рисуем феромонные следы
        if self.pheromone_matrix is not None and self.is_animating:
            max_pheromone = np.max(self.pheromone_matrix)
            min_pheromone = np.min(self.pheromone_matrix)
            pheromone_range = max_pheromone - min_pheromone

            # Рисуем феромонные следы
            for i in range(len(self.nodes)):
                for j in range(i + 1, len(self.nodes)):
                    start = self.node_positions[i]
                    end = self.node_positions[j]
                    
                    # Вычисляем среднее количество феромонов на пути
                    pheromone_amount = (self.pheromone_matrix[i][j] + self.pheromone_matrix[j][i]) / 2
                    
                    # Нормализуем значение феромонов для визуализации
                    normalized_pheromone = (pheromone_amount - min_pheromone) / (pheromone_range + 1e-10)
                    normalized_pheromone = math.pow(normalized_pheromone, 1.5)  # Усиливаем контраст
                    
                    # Настраиваем параметры отрисовки в зависимости от количества феромонов
                    thickness = 0.5 + 4 * normalized_pheromone  # Увеличили максимальную толщину
                    alpha = int(40 + 85 * normalized_pheromone)  # Настроили диапазон прозрачности
                    
                    # Используем градиент от темно-синего к ярко-синему
                    blue = int(100 + 155 * normalized_pheromone)  # от 100 до 255
                    color = QColor(120, 170, blue, alpha)
                    
                    painter.setPen(QPen(color, thickness))
                    painter.drawLine(start, end)

        # Рисуем финальную анимацию или завершенный путь
        if self.is_final_animation or self.animation_completed:
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            
            # Рисуем уже отрисованные ребра
            for i in range(self.current_edge_index):
                if i < len(self.edges_to_draw):
                    edge = self.edges_to_draw[i]
                    start = self.node_positions[edge[0]]
                    end = self.node_positions[edge[1]]
                    painter.drawLine(start, end)
            
            # Рисуем текущее анимируемое ребро или все ребра после завершения анимации
            if self.is_final_animation and self.current_edge_index < len(self.edges_to_draw):
                edge = self.edges_to_draw[self.current_edge_index]
                start = self.node_positions[edge[0]]
                end = self.node_positions[edge[1]]
                t = self.edge_animation_step / self.total_animation_steps
                current_pos = QPoint(
                    int(start.x() + t * (end.x() - start.x())),
                    int(start.y() + t * (end.y() - start.y()))
                )
                painter.drawLine(start, current_pos)
            elif self.animation_completed:  # Если анимация завершена, рисуем оставшиеся ребра
                for i in range(self.current_edge_index, len(self.edges_to_draw)):
                    edge = self.edges_to_draw[i]
                    start = self.node_positions[edge[0]]
                    end = self.node_positions[edge[1]]
                    painter.drawLine(start, end)

        # Рисуем узлы поверх всех линий
        nodesize = self.getNodeSize()
        font = QFont("Bahnschrift", nodesize)
        painter.setFont(font)

        for node in self.nodes:
            pos = self.node_positions[node]
            # Рисуем узел
            painter.setBrush(QBrush(self.colors[self.nodeColor[node]], Qt.BrushStyle.SolidPattern))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawEllipse(pos, nodesize, nodesize)
            
            # Рисуем номер узла
            text_rect = painter.boundingRect(
                pos.x() - nodesize//2, 
                pos.y() - nodesize//2,
                nodesize, nodesize,
                Qt.AlignmentFlag.AlignCenter,
                str(node)
            )
            painter.setPen(QPen(self.getFontColor(self.colors[self.nodeColor[node]]), 2))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(node))

    def calculate_node_positions(self):
        positions = {}
        radius = min(self.width(), self.height()) / 2.5
        center_x, center_y = self.width() / 2.0, self.height() / 2.0
        num_nodes = len(self.nodes)

        for i, node in enumerate(self.nodes):
            angle = 2 * math.pi * i / num_nodes
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[node] = QPoint(round(x), round(y))
        return positions

    def resizeEvent(self, event):
        self.node_positions = self.calculate_node_positions()
        self.update()

    def getNodeSize(self):
        if not self.nodes:
            return 30
        nodesize = max(20, min(60, int(300/len(self.nodes))))
        if not self.node_positions:
            return nodesize
        maxy = max(pos.y() for pos in self.node_positions.values())
        while nodesize > 10 and maxy + nodesize > self.height() - 5:
            nodesize -= 5
        return max(10, nodesize)

    def generateColors(self, n):
        colors = []
        if n <= 1:
            colors.append(qRgb(43,82,120))
        else:
            for i in range(n):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                if (r != 0 or g != 0 or b != 0) and (r != 255 or g != 255 or b != 255) and qRgb(r, g, b) not in colors:
                    colors.append(qRgb(r, g, b))
                else:
                    while (r == 0 and g == 0 and b == 0) or (r == 255 or g == 255 or b == 255) or qRgb(r, g, b) in colors:
                        r = random.randint(0, 255)
                        g = random.randint(0, 255)
                        b = random.randint(0, 255)
        return colors

    def getFontColor(self, nodecolor):
        rgb = QColor(nodecolor).getRgb()
        r, g, b = rgb[0], rgb[1], rgb[2]
        if 255 - r < 100 or 255 - g < 100 or 255 - b < 100:
            return Qt.GlobalColor.black
        return Qt.GlobalColor.white

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация решения задачи коммивояжера")
        self.setMinimumSize(800, 600)

        # Добавляем флаг для отслеживания состояния алгоритма
        self.is_running = False
        
        # Создаем окно аналитики
        self.analytics_window = None

        # Установка темного фона для главного окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0e1621;
            }
            QWidget {
                background-color: #0e1621;
                color: white;
                font-family: 'Bahnschrift Condensed';
                font-size: 16px;
            }
            QPushButton {
                background-color: #17212b;
                border: 1px solid #365069;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 120px;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1c2733;
            }
            QPushButton:disabled {
                background-color: #12191f;
                color: #516270;
                border: 1px solid #1e2c3a;
            }
            QTextEdit {
                background-color: #17212b;
                border: 1px solid #365069;
                border-radius: 5px;
                padding: 10px;
                color: white;
                font-size: 18px;
            }
        """)

        # Создание центрального виджета и главного layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)  # Добавляем отступы между элементами
        main_layout.setContentsMargins(10, 10, 10, 10)  # Добавляем отступы от краев

        # Создание контейнера для графа с горизонтальным layout для центрирования
        graph_container = QWidget()
        graph_container_layout = QHBoxLayout(graph_container)
        graph_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создание виджета для отрисовки графа
        self.graph_widget = GraphWidget()
        
        # Добавляем растягивающиеся спейсеры слева и справа от графа для центрирования
        graph_container_layout.addStretch()
        graph_container_layout.addWidget(self.graph_widget)
        graph_container_layout.addStretch()
        
        # Устанавливаем политику размера для контейнера графа
        graph_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # Устанавливаем политику размера для самого графа
        self.graph_widget.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )
        
        main_layout.addWidget(graph_container)

        # Создание текстового поля для вывода результатов
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(150)  # Увеличиваем минимальную высоту
        self.result_text.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding  # Меняем на Expanding для увеличения по вертикали
        )
        font = QFont("Bahnschrift Condensed", 18)
        self.result_text.setFont(font)
        main_layout.addWidget(self.result_text)

        # Создание контейнера для кнопок
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создание кнопок
        self.load_button = QPushButton("Прочитать файлы")
        self.animate_button = QPushButton("Начать анимацию")
        self.analytics_button = QPushButton("Графики")  # Новая кнопка
        self.animate_button.setEnabled(False)
        self.analytics_button.setEnabled(False)  # Изначально отключена

        # Установка шрифта для кнопок
        self.load_button.setFont(font)
        self.animate_button.setFont(font)
        self.analytics_button.setFont(font)
        
        # Установка фиксированной высоты для кнопок
        self.load_button.setFixedHeight(40)
        self.animate_button.setFixedHeight(40)
        self.analytics_button.setFixedHeight(40)

        # Добавление кнопок в layout
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.animate_button)
        button_layout.addWidget(self.analytics_button)
        
        # Устанавливаем политику размера для контейнера кнопок
        button_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        main_layout.addWidget(button_container)

        # Устанавливаем соотношение растяжения для элементов
        main_layout.setStretchFactor(graph_container, 2)  # Граф получает 2 части
        main_layout.setStretchFactor(self.result_text, 1)  # Текстовое поле получает 1 часть
        main_layout.setStretchFactor(button_container, 0)  # Кнопки не растягиваются

        # Подключение обработчиков событий
        self.load_button.clicked.connect(self.load_files)
        self.animate_button.clicked.connect(self.start_animation)
        self.analytics_button.clicked.connect(self.show_analytics)  # Новый обработчик

        # Инициализация переменных для данных
        self.distances = None
        self.parameters = None
        self.aco = None

    def show_analytics(self):
        """Показать окно аналитики"""
        # Скрываем главное окно перед созданием окна аналитики
        self.hide()
        QApplication.processEvents()  # Обрабатываем все отложенные события
        
        # Создаем новое окно аналитики каждый раз
        if self.analytics_window is not None:
            self.analytics_window.close()
        self.analytics_window = AnalyticsWindow(self)
        self.analytics_window.show()  # Показываем окно аналитики

    def load_files(self):
        try:
            # Читаем новые данные
            self.distances = read_distances('distances.txt')
            self.parameters = read_parameters('parameters.txt')
            
            # Если окно аналитики существует, закрываем его
            if self.analytics_window is not None:
                self.analytics_window.close()
                self.analytics_window = None
            
            # Формируем информацию о прочитанных данных
            info_text = "Файлы успешно прочитаны:\n\n"
            
            # Информация о матрице расстояний
            info_text += "Матрица расстояний: размер {}x{}\n".format(
                len(self.distances), 
                len(self.distances[0])
            )
            
            # Информация о параметрах алгоритма
            info_text += "\nПараметры алгоритма:\n"
            for param, value in self.parameters.items():
                if param == 'n_ants':
                    info_text += f"• Количество муравьев: {int(value)}\n"
                elif param == 'n_iterations':
                    info_text += f"• Количество итераций: {int(value)}\n"
                elif param == 'decay':
                    info_text += f"• Коэффициент испарения: {value}\n"
                elif param == 'alpha':
                    info_text += f"• Вес феромона (alpha): {value}\n"
                elif param == 'beta':
                    info_text += f"• Вес расстояния (beta): {value}\n"
            
            # Выводим информацию
            self.result_text.setText(info_text)
            
            # Настройка отображения графа с передачей количества муравьев
            self.graph_widget.set_cities(
                self.distances,
                n_ants=int(self.parameters['n_ants'])
            )
            
            # Активация кнопок
            self.animate_button.setEnabled(True)
            self.analytics_button.setEnabled(True)  # Активируем кнопку аналитики
            
        except Exception as e:
            self.result_text.setText(f"Ошибка при чтении файлов: {e}")

    def start_animation(self):
        # Если алгоритм уже запущен, останавливаем его
        if self.is_running:
            self.is_running = False
            self.animate_button.setText("Начать анимацию")
            self.load_button.setEnabled(True)
            self.graph_widget.is_animating = False
            return

        if self.distances is None or self.parameters is None:
            return

        # Отключаем кнопку загрузки и меняем текст кнопки анимации
        self.load_button.setEnabled(False)
        self.animate_button.setText("Остановить")
        self.is_running = True

        try:
            # Очищаем текстовое поле перед началом анимации
            self.result_text.clear()
            
            # Сбрасываем состояние предыдущей анимации
            self.graph_widget.animation_completed = False
            self.graph_widget.current_edge_index = 0
            self.graph_widget.edge_animation_step = 0
            self.graph_widget.edges_to_draw = []
            
            # Устанавливаем флаг анимации
            self.graph_widget.is_animating = True
            
            # Создание экземпляра ACO с функцией обратного вызова
            self.aco = AntColonyTSP(
                distances=self.distances,
                n_ants=int(self.parameters['n_ants']),
                n_iterations=int(self.parameters['n_iterations']),
                decay=self.parameters['decay'],
                alpha=self.parameters['alpha'],
                beta=self.parameters['beta'],
                on_iteration=self.graph_widget.on_iteration,
                delay=0.1  # Добавляем задержку
            )

            # Решение задачи
            best_path, best_distance, execution_time = self.aco.solve(stop_flag=lambda: not self.is_running)
            
            # Если алгоритм не был остановлен, показываем результат
            if self.is_running:
                # Завершаем анимацию и показываем финальный результат
                self.graph_widget.is_animating = False
                
                # Формируем информацию о найденном решении
                result_text = "Алгоритм завершил работу\n\n"
                result_text += f"Найден оптимальный путь:\n{best_path + [best_path[0]]}\n\n"
                result_text += f"Длина пути: {best_distance:.2f}\n"
                result_text += f"Время выполнения: {execution_time:.2f} сек."
                self.result_text.setText(result_text)
                
                # Запускаем анимацию отрисовки пути
                self.graph_widget.show_final_result()
            else:
                # Если алгоритм был остановлен, выводим текущий лучший результат
                self.graph_widget.is_animating = False
                if best_path is not None:
                    result_text = "Алгоритм остановлен пользователем\n\n"
                    result_text += f"Текущий лучший путь:\n{best_path + [best_path[0]]}\n\n"
                    result_text += f"Длина пути: {best_distance:.2f}\n"
                    result_text += f"Время до остановки: {execution_time:.2f} сек."
                    self.result_text.setText(result_text)
                    # Показываем анимацию текущего лучшего пути
                    self.graph_widget.show_final_result()
                else:
                    self.result_text.setText("Алгоритм остановлен пользователем (решение не найдено)")

        finally:
            # Возвращаем кнопки в исходное состояние
            self.is_running = False
            self.animate_button.setText("Начать анимацию")
            self.load_button.setEnabled(True)
            self.animate_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 