from datetime import datetime

fecha_original = "9/22/2026 7:33:05 AM"

fecha = datetime.strptime(fecha_original, "%m/%d/%Y %I:%M:%S %p")

print(fecha)

fecha_sql = fecha.strftime("%Y-%m-%d %H:%M:%S")

print(fecha_sql)


def convertir_fecha(fecha):

    if not fecha:
        return None

    fecha_datetime = datetime.strptime(fecha, "%m/%d/%Y %I:%M:%S %p")

    return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")

print()

print(f"\n\t------- {convertir_fecha(fecha_original)}")