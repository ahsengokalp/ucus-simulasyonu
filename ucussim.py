import folium
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QPushButton, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer
import os

class MapApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Uçuş Simülasyonu")
        self.setGeometry(100, 100, 800, 600)

        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        
        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)

        
        self.map_view = QWebEngineView()
        layout.addWidget(self.map_view)

        
        self.start_lat_input = QLineEdit()
        self.start_lat_input.setPlaceholderText("Başlangıç Enlemi")
        layout.addWidget(self.start_lat_input)

        self.start_lon_input = QLineEdit()
        self.start_lon_input.setPlaceholderText("Başlangıç Boylamı")
        layout.addWidget(self.start_lon_input)

        
        self.end_lat_input = QLineEdit()
        self.end_lat_input.setPlaceholderText("Bitiş Enlemi")
        layout.addWidget(self.end_lat_input)

        self.end_lon_input = QLineEdit()
        self.end_lon_input.setPlaceholderText("Bitiş Boylamı")
        layout.addWidget(self.end_lon_input)

        
        self.draw_route_button = QPushButton("Rota Çiz")
        self.draw_route_button.clicked.connect(self.draw_route)
        layout.addWidget(self.draw_route_button)

        self.start_simulation_button = QPushButton("Simülasyonu Başlat")
        self.start_simulation_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_simulation_button)

        
        self.map = folium.Map(location=[41.0082, 28.9784], zoom_start=12)
        self.update_map()

        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.current_position = None
        self.route_coordinates = []
        self.step_index = 0

        
        self.velocity = []
        self.acceleration = []
        self.load_simulation_data()

    def load_simulation_data(self):
        """Hız ve ivme verilerini CSV dosyasından yükle"""
        data = pd.read_csv("hiz_ivme.csv")  
        self.acceleration = data['ivme'].values
        self.velocity = data['hiz'].values

    def update_map(self):
        """HTML Haritasını Güncelle"""
        self.map.save("map.html")
        self.map_view.setHtml(open("map.html", "r", encoding="utf-8").read())

    def draw_route(self):
        """Başlangıç ve Bitiş Noktaları Arasında Rota Çiz"""
        try:
            start_lat = float(self.start_lat_input.text())
            start_lon = float(self.start_lon_input.text())
            end_lat = float(self.end_lat_input.text())
            end_lon = float(self.end_lon_input.text())

            
            self.route_coordinates = np.linspace(
                [start_lat, start_lon], [end_lat, end_lon], num=50
            ).tolist()
            self.current_position = self.route_coordinates[0]

            
            folium.PolyLine(
                locations=self.route_coordinates,
                color="blue",
                weight=5
            ).add_to(self.map)

            
            folium.Marker(location=[start_lat, start_lon], popup="Başlangıç").add_to(self.map)
            folium.Marker(location=[end_lat, end_lon], popup="Bitiş").add_to(self.map)

            self.update_map()
            print("Rota oluşturuldu!")
        except ValueError:
            print("Geçerli koordinatlar girin!")

    def start_simulation(self):
        """Simülasyonu Başlat"""
        if not self.route_coordinates:
            print("Önce bir rota oluşturun!")
            return

        self.step_index = 0
        self.timer.start(500)  

    def update_simulation(self):
        """Simülasyonu Adım Adım Güncelle"""
        if self.step_index >= len(self.route_coordinates):
            self.timer.stop()
            print("Simülasyon tamamlandı!")
            return

        
        if self.step_index < len(self.velocity):
            time = self.velocity[self.step_index] / self.acceleration[self.step_index]
        else:
            time=1  

        self.current_position = self.route_coordinates[self.step_index]
        self.step_index += 1
        self.map = folium.Map(location=self.current_position, zoom_start=12)
        folium.PolyLine(
            locations=self.route_coordinates,
            color="blue",
            weight=5
        ).add_to(self.map)

       
        icon_path = "plane.png"
        if os.path.exists(icon_path):
            icon = folium.CustomIcon(icon_path, icon_size=(30, 30))
            folium.Marker(location=self.current_position, icon=icon).add_to(self.map)

        self.update_map()
        print(f"Uçak hareket ediyor: {self.current_position}")


if __name__ == "__main__":
    app = QApplication([])
    window = MapApplication()
    window.show()
    app.exec_()
