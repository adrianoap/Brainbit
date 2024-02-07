import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QComboBox, QPushButton, QMessageBox, QHBoxLayout, QRadioButton, QButtonGroup
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QTranslator

# Establece la configuración regional a español (cambia 'es' según tu configuración)
os.environ["LANG"] = "es_ES.UTF-8"

# Importa Matplotlib después de configurar la configuración regional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from qtawesome import icon

class EEGWaveletAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Analizador de Ondas EEG - Transformada de Fourier')
        self.setWindowIcon(icon('fa.signal'))
        self.setGeometry(100, 100, 800, 600)

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Contenedor principal
        main_layout = QVBoxLayout()

        # Contenedor de botones
        button_container = QHBoxLayout()

        # Botón de carga
        self.load_button = QPushButton(icon('fa.file'), ' Cargar Archivo CSV', self)
        self.load_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_button.clicked.connect(self.load_csv)
        self.load_button.setStyleSheet("background-color: #4CAF50; color: black; font-weight: bold;")  # Cambios aquí
        self.load_button.setToolTip("Haz clic para cargar un archivo CSV")  # Agregado el tooltip
        button_container.addWidget(self.load_button)

        # Grupo de botones de tipo de gráfico
        self.chart_type_group = QButtonGroup(self)
        self.amplitude_button = QRadioButton("Amplitud vs Frecuencia", self)
        self.voltage_button = QRadioButton("Voltaje vs Tiempo", self)
        self.chart_type_group.addButton(self.amplitude_button)
        self.chart_type_group.addButton(self.voltage_button)
        self.chart_type_group.setExclusive(True)

        # Aplicar estilos a los radio buttons
        self.amplitude_button.setStyleSheet("color: black; font-weight: bold;")  # Ajusta según tus preferencias
        self.voltage_button.setStyleSheet("color: black; font-weight: bold;")  # Ajusta según tus preferencias

        button_container.addWidget(self.amplitude_button)
        button_container.addWidget(self.voltage_button)

        # Botón de ayuda
        self.help_button = QPushButton(icon('fa.question-circle'), ' Ayuda', self)
        self.help_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_button.clicked.connect(self.show_help)
        self.help_button.setStyleSheet("background-color: #3498db; color: black; font-weight: bold;")  # Cambios aquí
        self.help_button.setToolTip("Haz clic para obtener ayuda")  # Agregado el tooltip
        button_container.addWidget(self.help_button)

        main_layout.addLayout(button_container)

        # Selector de columna
        self.chart_selector = QComboBox(self)
        self.chart_selector.setStyleSheet("background-color: #ecf0f1; color: black; font-weight: bold;")  # Añadir estilos aquí
        self.chart_selector.setEditText("Seleccione una columna")
        self.chart_selector.setToolTip("Selecciona la columna para visualizar en el gráfico")  # Agregar tooltip
        main_layout.addWidget(self.chart_selector)

        # Configuración de la figura de Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Cambia los tooltips de la barra de herramientas a español
        self.toolbar.actions()[0].setToolTip("Inicio")
        self.toolbar.actions()[1].setToolTip("Atrás")
        self.toolbar.actions()[2].setToolTip("Adelante")
        self.toolbar.actions()[4].setToolTip("Mover")
        self.toolbar.actions()[5].setToolTip("Agrandar")
        self.toolbar.actions()[6].setToolTip("Configurar Subplots")
        self.toolbar.actions()[7].setToolTip("Personalizar ejes, curva e imagen")
        self.toolbar.actions()[9].setToolTip("Guardar")

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        # Configuración de la traducción para Matplotlib
        translator = QTranslator()
        translator.load("es", "translations")
        QApplication.installTranslator(translator)

        # Establecer el diseño principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.df = None
        self.selected_column = None

        # Configuración de botones y señales
        self.amplitude_button.setChecked(False)
        self.voltage_button.setChecked(False)
        self.amplitude_button.setEnabled(False)
        self.voltage_button.setEnabled(False)
        self.chart_selector.setEnabled(False)
        self.chart_type_group.buttonClicked.connect(self.plot_chart)
        self.chart_selector.currentIndexChanged.connect(self.plot_chart)

    def load_csv(self):
        try:
            file_dialog = QFileDialog.getOpenFileName(self, 'Seleccionar archivo CSV', filter="Archivos CSV (*.csv)")
            file_path = file_dialog[0]

            if file_path:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)

                    # Convertir los nombres de las columnas a minúsculas y eliminar espacios en blanco
                    self.df.columns = self.df.columns.str.lower().str.strip()

                    required_columns = ["time", "alpha1", "alpha2", "beta1", "beta2"]
                    if all(col in self.df.columns for col in required_columns):
                        self.chart_selector.setEnabled(True)
                        self.chart_selector.clear()

                        # Conservar los nombres con la primera letra en mayúscula en el ComboBox
                        columns = ["Alpha1", "Alpha2", "Beta1", "Beta2"]
                        self.chart_selector.addItems([col.capitalize() for col in columns])

                        self.amplitude_button.setChecked(False)
                        self.voltage_button.setChecked(False)
                        self.amplitude_button.setEnabled(True)
                        self.voltage_button.setEnabled(True)
                        self.figure.clear()  # Limpiar la figura al cargar un nuevo CSV
                        self.canvas.draw()
                        self.chart_selector.setEditText("Seleccione una columna")  # Restaurar el texto "Seleccione una columna"
                    else:
                        raise Exception("Elija un archivo con las columnas necesarias y extensión .csv.")

                else:
                    raise Exception("El archivo seleccionado no es un archivo CSV.")

            else:
                pass
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
            self.chart_selector.setEnabled(False)
            self.amplitude_button.setEnabled(False)
            self.voltage_button.setEnabled(False)
            self.figure.clear()  # Limpiar la figura al cargar un nuevo CSV
            self.canvas.draw()
            self.chart_selector.setEditText("Seleccione una columna")  # Restaurar el texto "Seleccione una columna"

    def plot_chart(self):
        if self.df is not None:
            self.selected_column = self.chart_selector.currentText().lower()
            if self.selected_column and self.selected_column != "Seleccione una columna":
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                tiempo = self.df['time']

                try:
                    if self.amplitude_button.isChecked():
                        eeg_data = pd.to_numeric(self.df[self.selected_column])
                        eeg_fft = np.fft.fft(eeg_data)
                        frecuencia = np.fft.fftfreq(len(eeg_data), d=1/len(tiempo))
                        ax.plot(frecuencia, np.abs(eeg_fft), label=self.selected_column.upper(), color='#3498db')
                        ax.set(xlabel='Frecuencia (Hz)', ylabel='Amplitud', title='Amplitud vs Frecuencia')
                        ax.legend()
                        ax.set_xlim([8, 30])  # Ajustar límites del eje x
                    elif self.voltage_button.isChecked():
                        if self.selected_column in self.df.columns:  
                            voltage_data = pd.to_numeric(self.df[self.selected_column])
                            ax.plot(tiempo, voltage_data, label=self.selected_column.upper(), color='#2ecc71')
                            ax.set(xlabel='Tiempo (s)', ylabel='Voltaje (uV)', title='Voltaje vs Tiempo')
                            ax.legend()
                            ax.set_xlim([8, 30])  
                        else:
                            raise ValueError(f"La columna '{self.selected_column}' no está presente en el DataFrame.")
                except ValueError as e:
                    QMessageBox.critical(self, 'Error', f"Error al procesar las columnas: {str(e)}")

                self.canvas.draw()

    def show_help(self):
        QMessageBox.information(self, 'Ayuda', "Bienvenido al Analizador de Ondas EEG - Transformada de Fourier.\n\n"
            "Pasos para usar la aplicación:\n"
            "1. Haga clic en 'Cargar Archivo CSV' para cargar un archivo CSV.\n"
            "2. Seleccione 'Amplitud vs Frecuencia' o 'Voltaje vs Tiempo' con los radio buttons.\n"
            "3. Seleccione la columna deseada en el menú desplegable.\n"
            "4. Explore las ondas EEG en el gráfico.\n"
            "5. Formato requerido del archivo CSV:\n"
            "El archivo CSV debe contener las siguientes columnas:\n"
            "\t1. 'time' - Tiempo en segundos.\n"
            "\t2. 'Alpha1' - Datos de la columna Alpha1.\n"
            "\t3. 'Alpha2' - Datos de la columna Alpha2.\n"
            "\t4. 'Beta1' - Datos de la columna Beta1.\n"
            "\t5. 'Beta2' - Datos de la columna Beta2.\n\n"
            "¡Disfrute de la aplicación!")

def run_app():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Establecer el estilo de la aplicación (puedes cambiarlo según tus preferencias)
    window = EEGWaveletAnalyzer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
