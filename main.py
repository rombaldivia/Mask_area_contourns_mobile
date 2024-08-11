import sys
import cvx  2
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QSlider, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QColor, QPixmap, QImage
from joystick_robotic import Joystick, Direction

class SliderSignals(QObject):
    new_hsv = pyqtSignal(tuple)

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    change_original_pixmap_signal = pyqtSignal(QImage)
    update_area_signal = pyqtSignal(float)

    def __init__(self, hsv_signal, joystick):
        super().__init__()
        self.hsv_signal = hsv_signal
        self.joystick = joystick
        self.current_hsv = (0, 0, 0)  # Valores iniciales
        self.pixels_per_cm = 10  # Asume una escala de 10 píxeles por centímetro
        self.automatic_mode = False  # Modo automático inicial
        hsv_signal.connect(self.update_hsv)

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Cannot open webcam")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (640, 480)) #PP
            frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75,sigmaSpace=75)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_bound = np.array([self.current_hsv[0] - 20, self.current_hsv[1] - 40, self.current_hsv[2] - 40]) 
            upper_bound = np.array([self.current_hsv[0] + 20, self.current_hsv[1] + 40, self.current_hsv[2] + 40])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)   
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
            mask = cv2.erode(mask, kernel, iterations=1)
            # Convertir el frame de la cámara a HSV
            #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            #lower_bound = np.array([self.current_hsv[0] - 10, self.current_hsv[1] - 40, self.current_hsv[2] - 40])
            #upper_bound = np.array([self.current_hsv[0] + 10, self.current_hsv[1] + 40, self.current_hsv[2] + 40])
            #mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # Encontrar contornos en la máscara
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            max_area = 0
            max_contour = None

            # Encontrar el contorno con el área más grande
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    max_area = area
                    max_contour = contour

            total_area_cm2 = 0
            if max_contour is not None and max_area > 500:  # Ajustar este valor según sea necesario
                x, y, w, h = cv2.boundingRect(max_contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                total_area_cm2 = (w / self.pixels_per_cm) * (h / self.pixels_per_cm)
                cv2.putText(frame, f'Area: {total_area_cm2:.2f} cm²', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if self.automatic_mode:
                    # Si el área supera el umbral, retroceder y girar
                    if total_area_cm2 > 1500:  # Ajusta este umbral según sea necesario
                        self.joystick.move_backward_then_turn()
                    else:
                        self.joystick.send_command(Direction.Forward)

            # Emitir el área total en cm²
            self.update_area_signal.emit(total_area_cm2)

            # Emitir la imagen original con los cuadros delimitadores
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            self.change_original_pixmap_signal.emit(convert_to_Qt_format)

            # Convertir la máscara a un formato de imagen adecuado para mostrar en QLabel
            mask_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            h, w, ch = mask_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(mask_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.change_pixmap_signal.emit(convert_to_Qt_format)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def update_hsv(self, hsv):
        self.current_hsv = hsv

    def toggle_automatic_mode(self):
        self.automatic_mode = not self.automatic_mode

class MaskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mask Display")
        self.setGeometry(100, 100, 650, 490)
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)
        self.setCentralWidget(self.label)

    def setMaskImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Display")
        self.setGeometry(800, 100, 650, 490)
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)
        self.setCentralWidget(self.label)

    def setCameraImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

class ColorSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = SliderSignals()
        self.joystick = Joystick()
        self.mask_window = MaskWindow()
        self.mask_window.show()
        self.camera_window = CameraWindow()
        self.camera_window.show()
        self.initUI()
        self.video_thread = VideoThread(self.signals.new_hsv, self.joystick)
        self.video_thread.change_pixmap_signal.connect(self.mask_window.setMaskImage)
        self.video_thread.change_original_pixmap_signal.connect(self.camera_window.setCameraImage)
        self.video_thread.update_area_signal.connect(self.update_area_display)
        self.video_thread.start()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('HSV Control Panel')

        # Crear el layout principal horizontal
        main_layout = QHBoxLayout()

        # Crear el layout vertical para los sliders y etiquetas
        sliders_layout = QVBoxLayout()

        # Crear y agregar sliders
        self.slider_h = self.create_slider(0, 360, "Hue")
        self.slider_s = self.create_slider(0, 255, "Saturation")
        self.slider_v = self.create_slider(0, 255, "Value")

        sliders_layout.addLayout(self.slider_h)
        sliders_layout.addLayout(self.slider_s)
        sliders_layout.addLayout(self.slider_v)

        # Color display label
        self.color_display = QLabel()
        self.color_display.setFixedSize(100, 100)
        sliders_layout.addWidget(self.color_display)
        self.update_color_display(0, 0, 0)  # Initialize display with black

        # Area display label
        self.area_display = QLabel("Area: 0 cm²")
        sliders_layout.addWidget(self.area_display)

        # Botón para alternar entre modos automático y manual
        self.mode_button = QPushButton("Switch to Automatic Mode")
        self.mode_button.setCheckable(True)
        self.mode_button.clicked.connect(self.toggle_mode)
        sliders_layout.addWidget(self.mode_button)

        # Añadir el layout de sliders al layout principal
        main_layout.addLayout(sliders_layout)

        # Crear e integrar el joystick en la interfaz
        main_layout.addWidget(self.joystick)

        # Crear un widget central y establecer el layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_slider(self, min_val, max_val, label_text):
        vbox = QVBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(0)
        label = QLabel(f"{label_text}: {slider.value()}")
        slider.valueChanged.connect(lambda value, lbl=label: lbl.setText(f"{label_text}: {value}"))
        slider.valueChanged.connect(self.update_values)

        vbox.addWidget(label)
        vbox.addWidget(slider)

        return vbox

    def update_values(self):
        h = self.slider_h.itemAt(1).widget().value() // 2
        s = self.slider_s.itemAt(1).widget().value()
        v = self.slider_v.itemAt(1).widget().value()
        self.update_color_display(h, s, v)
        self.signals.new_hsv.emit((h, s, v))

    def update_color_display(self, h, s, v):
        h = h * 2  # Ajustar hue de vuelta a 360 grados para visualización correcta
        color = QColor.fromHsv(h, s, v)
        pixmap = QPixmap(100, 100)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)

    def update_area_display(self, area):
        try:
            if self.area_display:  # Asegurarse de que el QLabel aún existe
                self.area_display.setText(f"Area: {area:.2f} cm²")
        except RuntimeError as e:
            print(f"Error updating area display: {e}")

    def toggle_mode(self):
        if self.mode_button.isChecked():
            self.mode_button.setText("Switch to Manual Mode")
            self.video_thread.toggle_automatic_mode()
        else:
            self.mode_button.setText("Switch to Automatic Mode")
            self.video_thread.toggle_automatic_mode()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorSelector()
    ex.show()
    sys.exit(app.exec_())
