from datetime import datetime, time


def reporte_productividad(datos):
    # Convertimos a lista para poder medirla y extraer los encabezados
    lista_filas = list(datos)
    
    if not lista_filas:
        print("La consulta está vacía.")
        return []

    # Diccionario temporal para encontrar cuáles cumplen las condiciones
    resumen = {}

    for fila in lista_filas:
        ulid = fila["load_number"]
        from_loc = fila["from_location"]
        to_loc = fila["to_location"]

        # Condición: Omitir si ambos están vacíos
        if not from_loc and not to_loc:
            continue

        if ulid not in resumen:
            resumen[ulid] = {"primer_from": None, "ultimo_to": None}

        # Guardar fila completa del primer FROM
        if from_loc and resumen[ulid]["primer_from"] is None:
            resumen[ulid]["primer_from"] = fila

        # Guardar fila completa del último TO
        if to_loc:
            resumen[ulid]["ultimo_to"] = fila

    # --- ESTA ES LA PARTE QUE MODIFICAMOS ---
    # Aquí creamos una lista plana, exactamente con la misma estructura que 'datos'
    tabla_completa_filtrada = []

    for ulid, info in resumen.items():
        # Validamos que el load_number tenga tanto un FROM como un TO válido
        if info["primer_from"] is not None and info["ultimo_to"] is not None:
            # Añadimos las filas completas directamente a la lista
            tabla_completa_filtrada.append(info["primer_from"])
            tabla_completa_filtrada.append(info["ultimo_to"])

    # Retorna una lista de objetos sqlite3.Row, sin agrupaciones, limpia y plana
    return tabla_completa_filtrada


def resumen_productividad_por_usuario(datos):
    lista_filas = list(datos)
    
    if not lista_filas:
        print("La consulta está vacía.")
        return []

    # Estructura del reporte: {(fecha, user_id, turno): {loads: set(), from_locs: {}, to_locs: {}}}
    reporte = {}

    for fila in lista_filas:
        # Acceso correcto para objetos sqlite3.Row usando corchetes []
        try:
            user_id = fila["user_id"]
            ulid = fila["load_number"]
            from_loc = fila["from_location"]
            to_loc = fila["to_location"]
            fecha_act = fila["last_Updated_Date"]
        except IndexError:
            # Por si alguna columna no existe en la consulta SQL
            continue

        # Ignorar registros sin datos clave para el reporte
        if not user_id or not fecha_act:
            continue

        # 1. Parsear la fecha y hora considerando formato de 12 horas (AM/PM)
        if isinstance(fecha_act, str):
            try:
                dt = datetime.strptime(fecha_act.strip(), "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue
        elif isinstance(fecha_act, datetime):
            dt = fecha_act
        else:
            continue

        # 2. Determinar el turno de 8 horas y ajustar la fecha si cruza la medianoche
        # Turno 1: 07:00:00 a 14:59:59
        # Turno 2: 15:00:00 a 22:59:59
        # Turno 3: 23:00:00 a 06:59:59 (del día siguiente)
        hora = dt.time()
        
        if time(7, 0) <= hora < time(15, 0):
            turno = "07:00 - 15:00"
            fecha_str = dt.strftime("%Y-%m-%d")
        elif time(15, 0) <= hora < time(23, 0):
            turno = "15:00 - 23:00"
            fecha_str = dt.strftime("%Y-%m-%d")
        else:
            turno = "23:00 - 07:00"
            # Si el Turno 3 ocurre entre las 00:00 y las 06:59, pertenece al "día laboral" de ayer
            if hora < time(7, 0):
                from datetime import timedelta
                fecha_str = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                fecha_str = dt.strftime("%Y-%m-%d")

        # 3. Inicializar la clave única en el diccionario
        clave = (fecha_str, user_id, turno)
        if clave not in reporte:
            reporte[clave] = {
                "loads_unicos": set(),
                "origenes": {},
                "destinos": {}
            }

        # 4. Acumular las métricas
        if ulid:
            reporte[clave]["loads_unicos"].add(ulid)
        
        if from_loc:
            reporte[clave]["origenes"][from_loc] = reporte[clave]["origenes"].get(from_loc, 0) + 1
            
        if to_loc:
            reporte[clave]["destinos"][to_loc] = reporte[clave]["destinos"].get(to_loc, 0) + 1

    # 5. Aplanar la estructura para devolver una lista limpia de diccionarios
    resultado_final = []
    for (fecha, user, turno), metricas in reporte.items():
        resultado_final.append({
            "Fecha Laboral": fecha,
            "User_ID": user,
            "Turno": turno,
            "Total_Load_Numbers": len(metricas["loads_unicos"]),
            "Detalle_From_Location": metricas["origenes"],
            "Detalle_To_Location": metricas["destinos"]
        })

    # Opcional: Ordenar por fecha, usuario y turno
    resultado_final.sort(key=lambda x: (x["Fecha Laboral"], x["User_ID"], x["Turno"]))

    return resultado_final


def mostrar_reporte_en_pantalla(lista_reporte):
    if not lista_reporte:
        print("No hay datos que mostrar.")
        return

    print(f"{'FECHA':<12} | {'USUARIO':<10} | {'TURNO':<15} | {'CARGAS':<6}")
    print("-" * 55)
    
    for r in lista_reporte:
        print(f"{r['Fecha Laboral']:<12} | {r['User_ID']:<10} | {r['Turno']:<15} | {r['Total_Load_Numbers']:<6}")
        
        # Mostrar desglose de ubicaciones con una pequeña sangría si existen
        if r['Detalle_From_Location']:
            print(f"   -> Orígenes: {r['Detalle_From_Location']}")
        if r['Detalle_To_Location']:
            print(f"   -> Destinos: {r['Detalle_To_Location']}")
        print("." * 55)
