DROP DATABASE IF EXISTS bd_navio;
CREATE DATABASE IF NOT EXISTS bd_navio;
Use bd_navio;


-- TABLAS Sin FORANEAS
CREATE TABLE TRIPULANTE (
id_tripulante INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
legajo VARCHAR(20) UNIQUE NOT NULL,
dni VARCHAR(20) UNIQUE NOT NULL,
direccion VARCHAR(100),
fecha_nacimiento DATE,
nacionalidad VARCHAR(50),
genero VARCHAR(20)
) ENGINE=InnoDB;


CREATE TABLE ESTADO_CAMAROTE (
id_estado_camarote INT AUTO_INCREMENT PRIMARY KEY,
descripcion varchar(500)
) ENGINE=InnoDB;

CREATE TABLE ROL (
id_rol INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(50),
descripcion varchar(50)
) ENGINE=InnoDB;


CREATE TABLE TIPO_DE_NAVIO (
id_tipo_navio INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(50),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE TIPO_CAMAROTE (
id_tipo_camarote INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(45),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE ESTADO_PASAJERO (
id_estado_pasajero INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(50),
descripcion varchar(500)

) ENGINE=InnoDB;


CREATE TABLE ESTADO_RESERVA (
id_estado_reserva INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE METODO_PAGO (
id_metodo_pago INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE ESTADO_PAGO (
id_estado_pago INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE TIPO_ITINERARIO (
id_tipo_itinerario INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500)
) ENGINE=InnoDB;


CREATE TABLE UBICACION_PUERTO (
id_ubicacion_puerto INT AUTO_INCREMENT PRIMARY KEY,
numero_muelle INT
) ENGINE=InnoDB;


CREATE TABLE ACTIVIDAD_POSIBLE (
id_actividad_posible INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500)
) ENGINE=InnoDB;




##Tablas con foraneasE
CREATE TABLE USUARIO (
id_usuario INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL,
email VARCHAR(100) NOT NULL,
contrasenia VARCHAR(255) NOT NULL,

id_rol INT ,
constraint fk_id_rol
foreign key (id_rol)
references ROL(id_rol)
) ENGINE=InnoDB;

CREATE TABLE CLIENTE (
id_cliente INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
apellido VARCHAR(50) NOT NULL,
dni VARCHAR(20) UNIQUE NOT NULL,
direccion VARCHAR(100),
fecha_nacimiento DATE,
nacionalidad VARCHAR(50),
genero VARCHAR(20),

id_usuario INT,
CONSTRAINT fk_usuario
FOREIGN KEY (id_usuario)
REFERENCES USUARIO(id_usuario)
) ENGINE=InnoDB;


CREATE TABLE NAVIO (
codigo_de_navio INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(100) NOT NULL,
altura FLOAT,
eslora FLOAT,
manga FLOAT,
desplazamiento FLOAT,
autonomia_de_viaje INT,
cantidad_maxima_de_pasajeros INT,
cantidad_de_motores INT,
imagen VARCHAR(255),

id_tipo_navio INT,
CONSTRAINT fk_tipo_navio
FOREIGN KEY (id_tipo_navio)
REFERENCES TIPO_DE_NAVIO(id_tipo_navio)
) ENGINE=InnoDB;


CREATE TABLE CUBIERTA (
numero_de_cubierta INT AUTO_INCREMENT PRIMARY KEY,
descripcion VARCHAR(500),
encargado VARCHAR(50),
codigo_de_navio INT,
CONSTRAINT fk_navio
FOREIGN KEY (codigo_de_navio)
REFERENCES NAVIO(codigo_de_navio)

) ENGINE=InnoDB;



CREATE TABLE CAMAROTE (
id_camarote INT AUTO_INCREMENT PRIMARY KEY,
numero_de_camarote INT,
imagen varchar(255),

numero_de_cubierta INT,
CONSTRAINT id_numero_de_cubierta
FOREIGN KEY (numero_de_cubierta)
REFERENCES CUBIERTA(numero_de_cubierta),

id_estado_camarote INT,
CONSTRAINT fk_estado_camarote
FOREIGN KEY (id_estado_camarote)
REFERENCES ESTADO_CAMAROTE (id_estado_camarote),

id_tipo_camarote INT,
CONSTRAINT fk_tipo_camarote
FOREIGN KEY (id_tipo_camarote)
REFERENCES TIPO_CAMAROTE (id_tipo_camarote)

) ENGINE=InnoDB;


CREATE TABLE ITINERARIO (
id_itinerario INT AUTO_INCREMENT PRIMARY KEY,
id_tipo_itinerario INT,
CONSTRAINT fk_tipo_itinerario
FOREIGN KEY (id_tipo_itinerario)
REFERENCES TIPO_ITINERARIO(id_tipo_itinerario)

) ENGINE=InnoDB;


CREATE TABLE ORDEN (
id_orden INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),
descripcion varchar(500),

id_itinerario INT,
CONSTRAINT fk_itinerario
FOREIGN KEY (id_itinerario)
REFERENCES ITINERARIO(id_itinerario)
) ENGINE=InnoDB;

CREATE TABLE PUERTO (
id_puerto INT AUTO_INCREMENT PRIMARY KEY,
nombre varchar(25),

id_orden INT,
CONSTRAINT fk_orden_
FOREIGN KEY (id_orden)
REFERENCES ORDEN(id_orden)
#FK A ORDEN
) ENGINE=InnoDB;

CREATE TABLE PUERTO_ACTIVIDAD (
id_puerto_actividad INT AUTO_INCREMENT PRIMARY KEY,

id_puerto INT,
CONSTRAINT fk_puerto
FOREIGN KEY (id_puerto)
REFERENCES PUERTO(id_puerto),

id_actividad_posible INT,
CONSTRAINT fk_actividad
FOREIGN KEY (id_actividad_posible)
REFERENCES ACTIVIDAD_POSIBLE(id_actividad_posible)


) ENGINE=InnoDB;


CREATE TABLE VIAJE (
id_viaje INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(100) NOT NULL,
descripcion varchar(500),
fecha_de_salida DATE,
fecha_fin DATE,
hora_salida TIME,
hora_llegada TIME,
lugar_destino VARCHAR(100),
fecha_actual DATE,
imagen VARCHAR(255)
) ENGINE=InnoDB;


CREATE TABLE VIAJEXNAVIO (
id_viaje_navio INT AUTO_INCREMENT PRIMARY KEY,

codigo_de_navio INT,
CONSTRAINT fk__navio
FOREIGN KEY (codigo_de_navio)
REFERENCES NAVIO(codigo_de_navio),

id_viaje INT,
CONSTRAINT fk_viaje
FOREIGN KEY (id_viaje)
REFERENCES VIAJE(id_viaje)


) ENGINE=InnoDB;


CREATE TABLE ASIGNACION_TRIPULANTE_VIAJE (
id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
fecha_inicio DATE,
fecha_fin DATE,

id_tripulante INT,
CONSTRAINT fk___tripulante
FOREIGN KEY (id_tripulante)
REFERENCES TRIPULANTE(id_tripulante),

id_viaje_navio INT,
CONSTRAINT fk_viaje_navio
FOREIGN KEY (id_viaje_navio)
REFERENCES VIAJEXNAVIO(id_viaje_navio)
) ENGINE=InnoDB;


CREATE TABLE RESERVA (
id_reserva INT AUTO_INCREMENT PRIMARY KEY,
descripcion varchar(500),
created_at DATE,
updated_at DATE,


id_viaje_navio INT,
CONSTRAINT fk__viaje_navio
FOREIGN KEY (id_viaje_navio)
REFERENCES VIAJEXNAVIO(id_viaje_navio),

id_estado_reserva INT,
CONSTRAINT fk_estado_reserva
FOREIGN KEY (id_estado_reserva)
REFERENCES ESTADO_RESERVA(id_estado_reserva),

id_cliente INT,
CONSTRAINT fk_cliente
FOREIGN KEY (id_cliente)
REFERENCES CLIENTE(id_cliente)
#FORANEA A ID_VIAJE_NAVIO, ID_ESTADO_RESERVA, ID_CLIENTE
) ENGINE=InnoDB;

CREATE TABLE PASAJERO (
id_pasajero INT AUTO_INCREMENT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
apellido VARCHAR(50) NOT NULL,
fecha_inicio DATE,
fecha_fin DATE,

id_reserva INT,
CONSTRAINT fk_reserva
FOREIGN KEY (id_reserva)
REFERENCES RESERVA(id_reserva),

id_estado_pasajero INT,
CONSTRAINT fk_Estado_pasajero
FOREIGN KEY (id_estado_pasajero)
REFERENCES ESTADO_PASAJERO(id_estado_pasajero)
) ENGINE=InnoDB;



CREATE TABLE OCUPACION_CAMAROTE (
id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
fecha_inicio DATETIME,
fecha_fin DATETIME,

id_camarote INT,
CONSTRAINT fk_camarote
FOREIGN KEY (id_camarote)
REFERENCES CAMAROTE(id_camarote),

id_tripulante INT,
CONSTRAINT fk__tripulante
FOREIGN KEY (id_tripulante)
REFERENCES TRIPULANTE(id_tripulante),

id_pasajero INT,
CONSTRAINT fk__pasajero
FOREIGN KEY (id_pasajero)
REFERENCES PASAJERO(id_pasajero),

id_viaje_navio INT,
CONSTRAINT fk___viaje_navio
FOREIGN KEY (id_viaje_navio)
REFERENCES VIAJEXNAVIO(id_viaje_navio)


#FORANEA ID_cAMAROTE, ID_TRIPULANTE, ID_PASAJERO, ID_VIAJE_NAVIO
) ENGINE=InnoDB;


CREATE TABLE PAGO (
id_pago INT AUTO_INCREMENT PRIMARY KEY,
fecha_pago DATE NOT NULL,
monto FLOAT NOT NULL,
created_at DATE,
updated_at DATE,


id_reserva INT,
CONSTRAINT fk__reserva
FOREIGN KEY (id_reserva)
REFERENCES RESERVA(id_reserva),


id_metodo_pago INT,
CONSTRAINT fk_metodo_pago
FOREIGN KEY (id_metodo_pago)
REFERENCES METODO_PAGO(id_metodo_pago),

id_estado_pago INT,
CONSTRAINT fk_estado_pago
FOREIGN KEY (id_estado_pago)
REFERENCES ESTADO_PAGO(id_estado_pago)

#FORANEA ID_RESERVA, ID_METODO_PAGO, ID_eSTADO_PAGO
) ENGINE=InnoDB;


CREATE TABLE HISTORIAL_RESERVA (
id_historial_reserva INT AUTO_INCREMENT PRIMARY KEY,
fecha_cambio DATE,
cambio_realizado VARCHAR(100),


id_reserva INT,
CONSTRAINT fk___reserva
FOREIGN KEY (id_reserva)
REFERENCES RESERVA(id_reserva)
#FORANEA ID_rESERVA
) ENGINE=InnoDB;



CREATE TABLE HISTORIAL_PAGO (
id_historial_pago INT AUTO_INCREMENT PRIMARY KEY,
fecha_cambio DATE NOT NULL,
cambio_realizado VARCHAR(255) NOT NULL,

id_pago INT,
CONSTRAINT fk_pago
FOREIGN KEY (id_pago)
REFERENCES PAGO(id_pago),


id_estado_pago INT,
CONSTRAINT fk__estado_pago
FOREIGN KEY (id_estado_pago)
REFERENCES ESTADO_PAGO(id_estado_pago),

id_usuario INT,
CONSTRAINT fk__usuario
FOREIGN KEY (id_usuario)
REFERENCES USUARIO(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE ITINERARIO_VIAJE (
id_itinerario_viaje INT AUTO_INCREMENT PRIMARY KEY,
id_viaje INT,
CONSTRAINT fk___viaje
FOREIGN KEY (id_viaje)
REFERENCES VIAJE(id_viaje),


id_itinerario INT,
CONSTRAINT fk___itinerario
FOREIGN KEY (id_itinerario)
REFERENCES ITINERARIO(id_itinerario)
#FORANEA  DE ID_VIAJE Y ID_ITINERARIO
) ENGINE=InnoDB;