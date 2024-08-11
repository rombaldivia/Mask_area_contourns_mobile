// Definición de los pines del motor
const int mot1r = D1;
const int mot1l = D2;
const int mot2r = D3;
const int mot2l = D4;

void setup() {
  // Configuración de los pines
  pinMode(mot1r, OUTPUT);
  pinMode(mot1l, OUTPUT);
  pinMode(mot2r, OUTPUT);
  pinMode(mot2l, OUTPUT);

  // Inicialización de la comunicación serial
  Serial.begin(115200);
}

void loop() {
  // Verificar si hay datos disponibles en la entrada serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Elimina espacios en blanco al inicio y al final de la cadena

    // Activar funciones del motor según el comando recibido
    if (command == "stop") {
        STOPMOTOR(mot1r, mot1l);
        STOPMOTOR(mot2r, mot2l);
        Serial.println("Motores detenidos");
    } else if (command == "left") {
        LEFTTURN(mot1r, mot1l, mot2r, mot2l);
        Serial.println("Girando a la izquierda");
    } else if (command == "right") {
        RIGHTTURN(mot1r, mot1l, mot2r, mot2l);
        Serial.println("Girando a la derecha");
    } else if (command == "forward") {
        FORWARDMOTOR(mot1r, mot1l, mot2r, mot2l);
        Serial.println("Motores hacia adelante");
    } else if (command == "backward") {
        BACKWARDMOTOR(mot1r, mot1l, mot2r, mot2l);
        Serial.println("Motores hacia atrás");
    } else {
        Serial.println("Comando no reconocido");
    }
  }
}

void STOPMOTOR(int _in1, int _in2) {
  digitalWrite(_in1, HIGH);
  digitalWrite(_in2, HIGH);
}

void CCWMOTOR(int _in1, int _in2) {
  digitalWrite(_in1, HIGH);
  digitalWrite(_in2, LOW);
}

void CWMOTOR(int _in1, int _in2) {
  digitalWrite(_in1, LOW);
  digitalWrite(_in2, HIGH);
}

void FORWARDMOTOR(int _in1r, int _in1l, int _in2r, int _in2l) {
  digitalWrite(_in1r, LOW);
  digitalWrite(_in1l, HIGH);
  digitalWrite(_in2r, LOW);
  digitalWrite(_in2l, HIGH);
}

void BACKWARDMOTOR(int _in1r, int _in1l, int _in2r, int _in2l) {
  digitalWrite(_in1r, HIGH);
  digitalWrite(_in1l, LOW);
  digitalWrite(_in2r, HIGH);
  digitalWrite(_in2l, LOW);
}

void LEFTTURN(int _in1r, int _in1l, int _in2r, int _in2l) {
  digitalWrite(_in1r, HIGH); // Motor izquierdo gira en sentido antihorario
  digitalWrite(_in1l, LOW);
  digitalWrite(_in2r, LOW); // Motor derecho gira en sentido horario
  digitalWrite(_in2l, HIGH);
}

void RIGHTTURN(int _in1r, int _in1l, int _in2r, int _in2l) {
  digitalWrite(_in1r, LOW); // Motor izquierdo gira en sentido horario
  digitalWrite(_in1l, HIGH);
  digitalWrite(_in2r, HIGH); // Motor derecho gira en sentido antihorario
  digitalWrite(_in2l, LOW);
}
