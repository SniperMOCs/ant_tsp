import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QStackedWidget,
                           QProgressDialog, QApplication)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from analytics_utils import (analyze_ants_impact, analyze_decay_impact,
                           analyze_alpha_impact, analyze_beta_impact,
                           analyze_parameters_comparison)

class AnalyticsWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Анализ алгоритма")
        self.setMinimumSize(1000, 600)
        
        # Сохраняем данные из основного окна
        self.distances = main_window.distances
        self.parameters = main_window.parameters
        
        # Создаем и показываем диалог загрузки
        self.progress_dialog = QProgressDialog("Подготовка данных для графиков...", None, 0, 100, self)
        self.progress_dialog.setWindowTitle("Загрузка")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # Остальной код инициализации будет выполнен после получения данных
        QApplication.processEvents()
        
        # Получаем данные для всех графиков
        self.collect_data()
        
        # Инициализируем интерфейс
        self.init_ui()

    def collect_data(self):
        """Сбор данных для всех графиков"""
        # Данные для графика количества муравьев
        self.progress_dialog.setLabelText("Анализ влияния количества муравьев (1/5)...")
        self.progress_dialog.setValue(0)
        QApplication.processEvents()
        self.ants_data = analyze_ants_impact(self.distances, self.parameters)
        
        # Данные для графика коэффициента испарения
        self.progress_dialog.setLabelText("Анализ влияния коэффициента испарения (2/5)...")
        self.progress_dialog.setValue(20)
        QApplication.processEvents()
        self.decay_data = analyze_decay_impact(self.distances, self.parameters)
        
        # Данные для графика alpha
        self.progress_dialog.setLabelText("Анализ влияния параметра alpha (3/5)...")
        self.progress_dialog.setValue(40)
        QApplication.processEvents()
        self.alpha_data = analyze_alpha_impact(self.distances, self.parameters)
        
        # Данные для графика beta
        self.progress_dialog.setLabelText("Анализ влияния параметра beta (4/5)...")
        self.progress_dialog.setValue(60)
        QApplication.processEvents()
        self.beta_data = analyze_beta_impact(self.distances, self.parameters)
        
        # Данные для графика сравнения параметров
        self.progress_dialog.setLabelText("Анализ сравнения параметров (5/5)...")
        self.progress_dialog.setValue(80)
        QApplication.processEvents()
        self.comparison_data = analyze_parameters_comparison(self.distances, self.parameters)
        
        self.progress_dialog.setValue(100)

    def init_ui(self):
        """Инициализация интерфейса после получения данных"""
        # Установка темного фона
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0e1621;
                color: white;
            }
            QPushButton {
                background-color: #17212b;
                border: 1px solid #365069;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 200px;
                color: white;
                font-family: 'Bahnschrift';
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1c2733;
            }
            QPushButton:checked {
                background-color: #2B5278;
            }
            #back_button {
                background-color: #2C3E50;
                min-width: 200px;
                font-size: 16px;
                padding: 10px;
                margin-top: 20px;
            }
            #back_button:hover {
                background-color: #34495E;
            }
        """)

        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создание главного вертикального layout
        main_layout = QVBoxLayout(central_widget)
        
        # Создание горизонтального layout для кнопок и графиков
        content_layout = QHBoxLayout()
        
        # Создание левой панели с кнопками
        button_panel = QWidget()
        button_layout = QVBoxLayout(button_panel)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Создание кнопок
        self.buttons = {
            'ants': QPushButton("Влияние количества\nмуравьев"),
            'decay': QPushButton("Влияние коэффициента\nиспарения"),
            'alpha': QPushButton("Влияние параметра\nalpha"),
            'beta': QPushButton("Влияние параметра\nbeta"),
            'comparison': QPushButton("Сравнение\nпараметров")
        }
        
        # Настройка кнопок
        for button in self.buttons.values():
            button.setCheckable(True)
            button_layout.addWidget(button)
        
        # Добавление растягивающегося пространства после кнопок
        button_layout.addStretch()
        
        # Создание стека для графиков
        self.plot_stack = QStackedWidget()
        
        # Создание виджетов с графиками
        self.create_plot_widgets()
        
        # Подключение сигналов кнопок
        self.buttons['ants'].clicked.connect(lambda: self.show_plot(0))
        self.buttons['decay'].clicked.connect(lambda: self.show_plot(1))
        self.buttons['alpha'].clicked.connect(lambda: self.show_plot(2))
        self.buttons['beta'].clicked.connect(lambda: self.show_plot(3))
        self.buttons['comparison'].clicked.connect(lambda: self.show_plot(4))
        
        # Добавление виджетов в горизонтальный layout
        content_layout.addWidget(button_panel, stretch=1)
        content_layout.addWidget(self.plot_stack, stretch=4)
        
        # Добавление горизонтального layout в главный вертикальный
        main_layout.addLayout(content_layout)
        
        # Создание кнопки возврата
        back_button = QPushButton("Вернуться к визуализации")
        back_button.setObjectName("back_button")
        back_button.clicked.connect(self.switch_to_main_window)
        
        # Создание контейнера для кнопки возврата с горизонтальным выравниванием по центру
        back_button_container = QHBoxLayout()
        back_button_container.addStretch()
        back_button_container.addWidget(back_button)
        back_button_container.addStretch()
        
        # Добавление контейнера с кнопкой возврата в главный layout
        main_layout.addLayout(back_button_container)
        
        # Показать первый график по умолчанию
        self.buttons['ants'].setChecked(True)
        self.show_plot(0)

    def create_plot_widgets(self):
        """Создание виджетов с графиками используя уже собранные данные"""
        self.create_ants_plot()
        self.create_decay_plot()
        self.create_alpha_plot()
        self.create_beta_plot()
        self.create_comparison_plot()

    def create_ants_plot(self):
        fig = Figure(facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Настройка цветов для светлой темы
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.title.set_color('black')
        
        # Используем собранные данные
        iterations, convergence_data, labels = self.ants_data
        
        # Задаем цвета для линий (больше цветов для безопасности)
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#2c3e50']
        
        # Строим график для каждого количества муравьев
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i % len(colors)], linewidth=2)
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сходимость алгоритма для разного количества муравьев')
        ax.grid(True, color='#cccccc', linestyle='--', alpha=0.7)
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='medium')
        
        self.plot_stack.addWidget(canvas)

    def create_decay_plot(self):
        fig = Figure(facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Настройка цветов для светлой темы
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.title.set_color('black')
        
        # Используем собранные данные
        iterations, convergence_data, labels = self.decay_data
        
        # Задаем цвета для линий (больше цветов для безопасности)
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#2c3e50']
        
        # Строим график для каждого значения коэффициента испарения
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i % len(colors)], linewidth=2)
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сходимость алгоритма для разных коэффициентов испарения')
        ax.grid(True, color='#cccccc', linestyle='--', alpha=0.7)
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='medium')
        
        self.plot_stack.addWidget(canvas)

    def create_alpha_plot(self):
        fig = Figure(facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Настройка цветов для светлой темы
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.title.set_color('black')
        
        # Используем собранные данные
        iterations, convergence_data, labels = self.alpha_data
        
        # Задаем цвета для линий (больше цветов для безопасности)
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#2c3e50']
        
        # Строим график для каждого значения alpha
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i % len(colors)], linewidth=2)
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сходимость алгоритма для разных значений alpha')
        ax.grid(True, color='#cccccc', linestyle='--', alpha=0.7)
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='medium')
        
        self.plot_stack.addWidget(canvas)

    def create_beta_plot(self):
        fig = Figure(facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Настройка цветов для светлой темы
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.title.set_color('black')
        
        # Используем собранные данные
        iterations, convergence_data, labels = self.beta_data
        
        # Задаем цвета для линий (больше цветов для безопасности)
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#2c3e50']
        
        # Строим график для каждого значения beta
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i % len(colors)], linewidth=2)
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сходимость алгоритма для разных значений beta')
        ax.grid(True, color='#cccccc', linestyle='--', alpha=0.7)
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='medium')
        
        self.plot_stack.addWidget(canvas)

    def create_comparison_plot(self):
        fig = Figure(facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Настройка цветов для светлой темы
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.xaxis.label.set_color('black')
        ax.yaxis.label.set_color('black')
        ax.title.set_color('black')
        
        # Используем собранные данные
        iterations, convergence_data, labels = self.comparison_data
        
        # Задаем цвета для линий (больше цветов для безопасности)
        colors = ['#2980b9', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#2c3e50']
        
        # Строим график для каждого набора параметров
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i % len(colors)], linewidth=2)
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сравнение разных параметров')
        ax.grid(True, color='#cccccc', linestyle='--', alpha=0.7)
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='medium')
        
        self.plot_stack.addWidget(canvas)

    def show_plot(self, index):
        # Снимаем выделение со всех кнопок
        for button in self.buttons.values():
            button.setChecked(False)
        
        # Устанавливаем выделение на нужную кнопку
        button_list = list(self.buttons.values())
        button_list[index].setChecked(True)
        
        # Показываем нужный график
        self.plot_stack.setCurrentIndex(index)

    def switch_to_main_window(self):
        self.hide()
        self.main_window.show()

    def closeEvent(self, event):
        self.main_window.show()
        event.accept() 