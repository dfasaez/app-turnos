from flask import Flask, render_template, request, redirect, session, flash, send_file
from models import db, User, Turno, Trabajador, Asignacion, TurnoDetalle, Area, Cargo
import pandas as pd

app = Flask(__name__)
app.secret_key = "clave_segura_empresa"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

# =========================
# SEGURIDAD
# =========================
def login_required():
    return "user_id" in session

def es_admin():
    return session.get("rol") == "admin"

def es_jefe():
    return session.get("rol") == "jefatura"

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and user.password == request.form["password"]:
            session["user_id"] = user.id
            session["rol"] = user.rol
            flash("Ingreso exitoso", "success")
            return redirect("/dashboard")
        else:
            flash("Credenciales incorrectas", "error")

    return render_template("login.html")

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/")
    return render_template("dashboard.html")

# =========================
# ADMIN
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if not es_admin():
        return redirect("/dashboard")

    if request.method == "POST":
        db.session.add(User(
            nombre=request.form["nombre"],
            email=request.form["email"],
            password=request.form["password"],
            rol=request.form["rol"],
            area_id=request.form.get("area")
        ))
        db.session.commit()
        flash("Usuario creado", "success")

    return render_template("admin.html",
                           usuarios=User.query.all(),
                           trabajadores=Trabajador.query.all(),
                           areas=Area.query.all(),
                           cargos=Cargo.query.all())

# =========================
# CREAR TRABAJADOR
# =========================
@app.route("/crear_trabajador", methods=["POST"])
def crear_trabajador():

    db.session.add(Trabajador(
        nombre=request.form["nombre"],
        area_id=request.form["area"],
        cargo_id=request.form["cargo"]
    ))

    db.session.commit()
    flash("Trabajador creado", "success")

    return redirect("/admin")

# =========================
# ELIMINAR TRABAJADOR
# =========================
@app.route("/eliminar_trabajador/<int:id>")
def eliminar_trabajador():

    db.session.delete(Trabajador.query.get(id))
    db.session.commit()

    flash("Trabajador eliminado", "success")
    return redirect("/admin")

# =========================
# ASIGNAR TURNO (VALIDADO)
# =========================
@app.route("/asignar_turno", methods=["GET", "POST"])
def asignar_turno():

    if not login_required():
        return redirect("/")

    usuario = User.query.get(session["user_id"])

    if request.method == "POST":

        trabajador_id = request.form["trabajador"]
        fecha = request.form["fecha"]

        # 🔴 VALIDACIÓN DUPLICADO
        existe = Asignacion.query.filter_by(
            trabajador_id=trabajador_id,
            fecha=fecha
        ).first()

        if existe:
            flash("Ya existe un turno asignado ese día", "error")
            return redirect("/asignar_turno")

        # 🔴 VALIDACIÓN AREA
        trabajador = Trabajador.query.get(trabajador_id)

        if usuario.rol == "jefatura" and trabajador.area_id != usuario.area_id:
            flash("No puedes asignar fuera de tu área", "error")
            return redirect("/asignar_turno")

        db.session.add(Asignacion(
            trabajador_id=trabajador_id,
            turno_id=request.form["turno"],
            fecha=fecha
        ))

        db.session.commit()

        flash("Turno asignado correctamente", "success")
        return redirect("/dashboard")

    if usuario.rol == "jefatura":
        trabajadores = Trabajador.query.filter_by(area_id=usuario.area_id).all()
    else:
        trabajadores = Trabajador.query.all()

    return render_template("asignar_turno.html",
                           trabajadores=trabajadores,
                           turnos=Turno.query.all())

# =========================
# CALENDARIO
# =========================
@app.route("/calendario")
def calendario():

    if not login_required():
        return redirect("/")

    usuario = User.query.get(session["user_id"])

    if usuario.rol == "jefatura":
        trabajadores = Trabajador.query.filter_by(area_id=usuario.area_id).all()
    else:
        trabajadores = Trabajador.query.all()

    asignaciones = Asignacion.query.all()
    detalles = TurnoDetalle.query.all()

    calendario = {}

    for t in trabajadores:
        calendario[t.id] = {
            "nombre": t.nombre,
            "dias": {"lunes":"","martes":"","miercoles":"","jueves":"","viernes":"","sabado":"","domingo":""}
        }

    for a in asignaciones:
        if a.trabajador_id not in calendario:
            continue

        for d in [d for d in detalles if d.turno_id == a.turno_id]:
            calendario[a.trabajador_id]["dias"][d.dia] = f"{d.hora_inicio}-{d.hora_fin}"

    return render_template("calendario.html", calendario=calendario)

# =========================
# EXPORTAR EXCEL
# =========================
@app.route("/exportar_excel")
def exportar_excel():

    data = []

    for a in Asignacion.query.all():
        trabajador = Trabajador.query.get(a.trabajador_id)

        for d in TurnoDetalle.query.filter_by(turno_id=a.turno_id):
            data.append({
                "Trabajador": trabajador.nombre,
                "Día": d.dia,
                "Horario": f"{d.hora_inicio}-{d.hora_fin}"
            })

    df = pd.DataFrame(data)
    df.to_excel("turnos.xlsx", index=False)

    return send_file("turnos.xlsx", as_attachment=True)

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)