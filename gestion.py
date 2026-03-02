from inventario.bd import db
from inventario.productos import Cita, Servicio

class GestionMedica:
    def agendar_cita(self, paciente, fecha, hora):
        nueva_cita = Cita(paciente=paciente, fecha=fecha, hora=hora) [cite: 383, 384, 385]
        db.session.add(nueva_cita)
        db.session.commit() [cite: 405]
        return nueva_cita.id [cite: 476]

    def obtener_citas(self):
        return Cita.query.all() [cite: 479]

    def actualizar_cita(self, id_cita, nueva_fecha):
        cita = Cita.query.get(id_cita) [cite: 480]
        if cita:
            cita.fecha = nueva_fecha [cite: 482]
            db.session.commit()