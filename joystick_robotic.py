import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPointF, QRectF, QLineF, QThread
from enum import Enum
import random

# Configuración para las direcciones de movimiento
class Direction(Enum):
    Left = 'left\n'
    Right = 'right\n'
    Forward = 'forward\n'
    Backward = 'backward\n'
    Stop = 'stop\n'

# Clase Joystick
class Joystick(QWidget):
    def __init__(self, parent=None):
        super(Joystick, self).__init__(parent)
        self.setFixedSize(200, 200)
        self.movingOffset = QPointF(0, 0)
        self.dragging = False
        self.__maxDistance = 70

        # Inicialización de la comunicación serial con manejo de excepciones
        try:
            # Detectar y listar puertos seriales disponibles
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                raise Exception("No serial ports found")
            # Usar un puerto /dev/tty específico (ajustar según sea necesario)
            self.serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        except Exception as e:
            self.serial = None  # Desactivar comunicación serial si hay un error
            self.show_error_message(str(e))

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Error de Conexión Serial")
        msg_box.setInformativeText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()

    def paintEvent(self, event):
        painter = QPainter(self)
        bounds = QRectF(-self.__maxDistance, -self.__maxDistance,
                        self.__maxDistance * 2, self.__maxDistance * 2).translated(self._center())
        painter.setBrush(QColor(200, 200, 200))
        painter.drawEllipse(bounds)
        painter.setBrush(QColor(100, 100, 100))
        painter.drawEllipse(self._centerEllipse())

    def _center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def _centerEllipse(self):
        if self.dragging:
            return QRectF(-20, -20, 40, 40).translated(self.movingOffset + self._center())
        return QRectF(-20, -20, 40, 40).translated(self._center())

    def _boundJoystick(self, point):
        limitLine = QLineF(self._center(), point)
        if limitLine.length() > self.__maxDistance:
            limitLine.setLength(self.__maxDistance)
        return limitLine.p2()

    def joystickDirection(self):
        if not self.dragging:
            return Direction.Stop
        normVector = QLineF(self._center(), self._center() + self.movingOffset)
        angle = normVector.angle()

        if angle <= 45 or angle > 315:
            return Direction.Right
        elif 45 < angle <= 135:
            return Direction.Backward
        elif 135 < angle <= 225:
            return Direction.Left
        elif 225 < angle <= 315:
            return Direction.Forward

    def send_command(self, direction):
        if self.serial:
            try:
                self.serial.write(direction.value.encode())
            except Exception as e:
                print(f"Error writing to serial port: {e}")

    def mousePressEvent(self, event):
        if self._centerEllipse().contains(event.pos()):
            self.dragging = True
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.movingOffset = QPointF(0, 0)
        self.update()
        self.send_command(Direction.Stop)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.movingOffset = self._boundJoystick(event.pos()) - self._center()
            direction = self.joystickDirection()
            if direction:
                self.send_command(direction)
            self.update()

    def move_backward_then_turn(self):
        # Enviar comando para retroceder
        self.send_command(Direction.Backward)
        QThread.msleep(1000)  # Retroceder por 1 segundo
        print("giro")
        # Girar a la derecha o izquierda aleatoriamente
        if random.choice([True, False]):
            self.send_command(Direction.Right)
        else:
            self.send_command(Direction.Left)
        QThread.msleep(4000)  # Girar por 1 segundo

        # Detener
        self.send_command(Direction.Stop)

    def keep(self):
        # Enviar comando para retroceder
        self.send_command(Direction.Backward)
        print("Adelante")
        QThread.msleep(1000)  # Retroceder por 1 segundo

# Inicialización de la aplicación PyQt
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Ventana del Joystick
    joystick_window = QMainWindow()
    joystick_window.setWindowTitle('Joystick Test')
    joystick_window.setGeometry(100, 100, 400, 300)
    joystick = Joystick()
    joystick_window.setCentralWidget(joystick)
    joystick_window.show()

    sys.exit(app.exec_())
