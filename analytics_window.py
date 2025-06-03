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
                           analyze_alpha_beta_impact, analyze_convergence)

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
        self.progress_dialog.setLabelText("Анализ влияния количества муравьев (1/4)...")
        self.progress_dialog.setValue(0)
        QApplication.processEvents()
        self.ants_data = analyze_ants_impact(self.distances, self.parameters)
        
        # Данные для графика коэффициента испарения
        self.progress_dialog.setLabelText("Анализ влияния коэффициента испарения (2/4)...")
        self.progress_dialog.setValue(25)
        QApplication.processEvents()
        self.decay_data = analyze_decay_impact(self.distances, self.parameters)
        
        # Данные для графика alpha и beta
        self.progress_dialog.setLabelText("Анализ влияния параметров alpha и beta (3/4)...")
        self.progress_dialog.setValue(50)
        QApplication.processEvents()
        self.alpha_beta_data = analyze_alpha_beta_impact(self.distances, self.parameters)
        
        # Данные для графика сходимости
        self.progress_dialog.setLabelText("Анализ сходимости алгоритма (4/4)...")
        self.progress_dialog.setValue(75)
        QApplication.processEvents()
        self.convergence_data = analyze_convergence(self.distances, self.parameters)
        
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
            'ants': QPushButton("Влияние количества муравьев"),
            'decay': QPushButton("Влияние коэффициента\nиспарения"),
            'alpha_beta': QPushButton("Влияние alpha и beta"),
            'convergence': QPushButton("Сравнение параметров")
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
        self.buttons['alpha_beta'].clicked.connect(lambda: self.show_plot(2))
        self.buttons['convergence'].clicked.connect(lambda: self.show_plot(3))
        
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
        self.create_alpha_beta_plot()
        self.create_convergence_plot()

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
        n_ants_values, time_results = self.ants_data
        
        ax.plot(n_ants_values, time_results, 'o-', color='#2980b9')
        ax.set_xlabel('Количество муравьев')
        ax.set_ylabel('Время выполнения (сек)')
        ax.set_title('Зависимость времени выполнения от количества муравьев')
        ax.grid(True, color='#cccccc')
        
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
        decay_values, time_results = self.decay_data
        
        ax.plot(decay_values, time_results, 'o-', color='#27ae60')
        ax.set_xlabel('Коэффициент испарения')
        ax.set_ylabel('Время выполнения (сек)')
        ax.set_title('Зависимость времени выполнения от коэффициента испарения')
        ax.grid(True, color='#cccccc')
        
        self.plot_stack.addWidget(canvas)

    def create_alpha_beta_plot(self):
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
        alpha_values, beta_values, alpha_results, beta_results = self.alpha_beta_data
        
        ax.plot(alpha_values, alpha_results, 'o-', label='Alpha', color='#c0392b')
        ax.plot(beta_values, beta_results, 'o-', label='Beta', color='#f39c12')
        ax.set_xlabel('Значение параметра')
        ax.set_ylabel('Длина лучшего пути')
        ax.set_title('Влияние параметров alpha и beta на качество решения')
        ax.legend()
        ax.grid(True, color='#cccccc')
        
        self.plot_stack.addWidget(canvas)

    def create_convergence_plot(self):
        """Создание графика сходимости алгоритма"""
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
        iterations, convergence_data, labels = self.convergence_data
        
        # Задаем цвета для линий
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        # Строим график для каждого набора параметров
        for i, (data, label) in enumerate(zip(convergence_data, labels)):
            ax.plot(iterations, data, '-', label=label, color=colors[i])
        
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Длина пути')
        ax.set_title('Сравнение разных параметров')
        ax.grid(True, color='#cccccc')
        ax.legend()
        
        # Настраиваем легенду
        ax.legend(loc='upper right', fontsize='small')
        
        self.plot_stack.addWidget(canvas)

    def show_plot(self, index):
        # Снимаем выделение со всех кнопок
        for button in self.buttons.values():
            button.setChecked(False)
        
        # Выделяем нужную кнопку
        button = list(self.buttons.values())[index]
        button.setChecked(True)
        
        # Показываем нужный график
        self.plot_stack.setCurrentIndex(index)

    def switch_to_main_window(self):
        self.hide()  # Скрываем окно аналитики
        self.main_window.show()  # Показываем главное окно

    def closeEvent(self, event):
        """Переопределяем событие закрытия окна"""
        self.switch_to_main_window()
        event.ignore()  # Игнорируем закрытие окна 