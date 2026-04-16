from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ======================
# MANTENEDORES
# ======================

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

# ======================
# USUARIOS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    rol = db.Column(db.String(20))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))

# ======================
# TRABAJADORES
# ======================

class Trabajador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'))

# ======================
# TURNOS
# ======================

class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    tipo_jornada = db.Column(db.String(50))
    colacion = db.Column(db.String(50))

class TurnoDetalle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id'))
    dia = db.Column(db.String(20))
    hora_inicio = db.Column(db.String(10))
    hora_fin = db.Column(db.String(10))

# ======================
# ASIGNACIONES
# ======================

class Asignacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer)
    turno_id = db.Column(db.Integer)
    fecha = db.Column(db.String(20))

# ======================
# SOLICITUDES
# ======================

class Solicitud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    turno_id = db.Column(db.Integer)
    fecha_inicio = db.Column(db.String(20))
    fecha_fin = db.Column(db.String(20))
    estado = db.Column(db.String(20))