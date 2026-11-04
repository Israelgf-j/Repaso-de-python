from datetime import datetime, timedelta


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


def obtener_zona(ubicacion):
    """
    Normaliza la ubicación y extrae su zona logística basada en prefijos.
    Si no coincide con ninguna, retorna ('OTRAS', ubicacion_normalizada)
    """
    if not ubicacion:
        return ("DESCONOCIDA", "DESCONOCIDA")
    
    # Limpieza estricta
    u = ubicacion.strip().upper()
    
    # 1. Racks
    if any(u.startswith(p) for p in ["A1", "A2", "B1", "C1", "G1", "F1", "F2", "E1", "E2", "D1"]):
        return ("RACK", u)
    # 2. Hand Off In (HOI y variaciones)
    if any(u.startswith(p) for p in ["HOI", "HO1", "HO0"]):
        return ("HOI", u)
    # 3. Hand Off Out (HOO)
    if u.startswith("HOO"):
        return ("HOO", u)
    # 4. Bahías de Recibo / Almacenamiento Temporal
    if any(u.startswith(p) for p in ["BRCST", "BLDST", "BLDSTG"]):
        return ("BAHIAS_RECIBO", u)
    # 5. Bahías de Embarques
    if any(u.startswith(p) for p in ["ASH", "AST"]):
        return ("BAHIAS_EMBARQUE", u)
    # 6. Líneas de Producción
    if u.startswith("STG"):
        return ("LINEAS_PROD", u)
    # 7. Líneas de Retrabajo
    if u.startswith("RECALL"):
        return ("RETRABAJO", u)
    # 8. Almacén de Charolas
    if any(u.startswith(p) for p in ["TRAY", "CRITICALTRAY"]):
        return ("CHAROLAS", u)
    # 9. Retornos de producción
    if u.startswith("RTN"):
        return ("RETORNOS", u)
    
    # Si no entra en ninguna categoría, conserva su nombre completo
    return ("OTRAS", u)


def determinar_turno_y_fecha(fecha_hora_str):
    """
    Calcula el turno y la fecha laboral real ajustando el desfase nocturno.
    Soporta formatos comunes de SQLite como 'YYYY-MM-DD HH:MM:SS'
    """
    dt = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
    hora = dt.time()
    
    # Valores por defecto
    fecha_laboral = dt.date()
    turno = ""
    
    if hora >= datetime.strptime("07:00:00", "%H:%M:%S").time() and hora < datetime.strptime("15:00:00", "%H:%M:%S").time():
        turno = "Matutino (07-15)"
    elif hora >= datetime.strptime("15:00:00", "%H:%M:%S").time() and hora < datetime.strptime("23:00:00", "%H:%M:%S").time():
        turno = "Vespertino (15-23)"
    else:
        turno = "Nocturno (23-07)"
        # Si está entre las 00:00 y las 06:59:59, pertenece al día laboral anterior
        if hora < datetime.strptime("07:00:00", "%H:%M:%S").time():
            fecha_laboral = (dt - timedelta(days=1)).date()
            
    return fecha_laboral.strftime("%Y-%m-%d"), turno


def resumen_productividad_por_usuario(datos):
    """
    Procesa las filas de SQLite, reconstruye los movimientos cronológicos de pallets,
    clasifica las actividades logísticas y agrupa los resultados sin saturar la memoria.
    """
    if not datos:
        return {}
    
    # 1. Validar y garantizar orden cronológico ascendente basándonos en la columna de fecha (asumiendo índice 1)
    # Estructura supuesta: [load_number (0), fecha_hora (1), from_location (2), to_location (3), user_id (4)]
    primera_fecha = datos[0][1]
    ultima_fecha = datos[-1][1]
    
    if primera_fecha > ultima_fecha:
        datos = datos[::-1] # Inversión rápida en memoria si venía descendente
        
    # 2. Reconstrucción de movimientos reales mediante Single-Pass Streaming
    movimientos_consolidados = []
    
    actual_load = None
    origen_inicial = None
    destino_final = None
    fecha_hora_mov = None
    usuario_mov = None
    
    for fila in datos:
        load_num, fecha_hora, from_loc, to_loc, user_id = fila
        
        if load_num != actual_load:
            # Si ya había una carga procesándose, cerramos su ciclo y guardamos el movimiento terminado
            if actual_load is not None:
                movimientos_consolidados.append({
                    'load_number': actual_load,
                    'from_loc': origen_inicial,
                    'to_loc': destino_final,
                    'fecha_hora': fecha_hora_mov,
                    'user_id': usuario_mov
                })
            # Inicializamos la nueva secuencia de la carga entrante
            actual_load = load_num
            origen_inicial = from_loc
            fecha_hora_mov = fecha_hora
            usuario_mov = user_id
        
        # El destino final se actualiza de manera constante en cada fila intermedia de la misma carga
        destino_final = to_loc
        
    # Guardar el último movimiento remanente al salir del ciclo
    if actual_load is not None:
        movimientos_consolidados.append({
            'load_number': actual_load,
            'from_loc': origen_inicial,
            'to_loc': destino_final,
            'fecha_hora': fecha_hora_mov,
            'user_id': usuario_mov
        })
        
    # 3. Clasificación logística y Agrupación en Reporte Compacto
    reporte = {}
    
    for mov in movimientos_consolidados:
        f_laboral, turno = determinar_turno_y_fecha(mov['fecha_hora'])
        user_id = mov['user_id']
        load_num = mov['load_number']
        
        # Clave primaria de agrupación
        clave_grupo = (f_laboral, user_id, turno)
        
        if clave_grupo not in reporte:
            reporte[clave_grupo] = {
                'cargas_vistas': set(), # Estructura intermedia temporal para contar cargas únicas reales
                'cargas_unicas_count': 0,
                'total_movimientos_productivos': 0,
                'rack_a_rack': 0,
                'hoi_a_rack': 0,
                'hoo_a_rack': 0,
                'hoo_a_stg': 0,
                'hoo_a_ast_ash': 0,
                'bahias_a_rack': 0,
                'bahias_a_hoi': 0,
                'bahias_a_hoo': 0,
                'entre_hoi_hoo_bahias': 0,
                'hoi_a_otras': 0,
                'hoo_a_otras': 0,
                'brcst_a_otras': 0,
                'movimientos_repetidos': 0,
                'detalles_combinaciones': {} # (origen, destino): cantidad
            }
            
        grupo = reporte[clave_grupo]
        grupo['cargas_vistas'].add(load_num)
        
        # Identificar zonas semánticas
        zona_orig, orig_full = obtener_zona(mov['from_loc'])
        zona_dest, dest_full = obtener_zona(mov['to_loc'])
        
        # Filtrado preventivo: si viene sin información válida, ignorar
        if zona_orig == "DESCONOCIDA" or zona_dest == "DESCONOCIDA":
            continue
            
        es_movimiento_productivo = False
        categoria_metrica = None
        
        # Lógica de asignación mutuamente excluyente
        
        # Control de Movimientos Repetidos (Misma zona exacta inicial y final)
        if orig_full == dest_full:
            categoria_metrica = 'movimientos_repetidos'
            es_movimiento_productivo = True
            
        # A. Rack a Rack
        elif zona_orig == "RACK" and zona_dest == "RACK":
            categoria_metrica = 'rack_a_rack'
            es_movimiento_productivo = True
            
        # B. HOI -> Rack
        elif zona_orig == "HOI" and zona_dest == "RACK":
            categoria_metrica = 'hoi_a_rack'
            es_movimiento_productivo = True
            
        # C. HOO -> Rack
        elif zona_orig == "HOO" and zona_dest == "RACK":
            categoria_metrica = 'hoo_a_rack'
            es_movimiento_productivo = True
            
        # D. Bahías hacia Rack
        elif zona_orig == "BAHIAS_RECIBO" and zona_dest == "RACK":
            categoria_metrica = 'bahias_a_rack'
            es_movimiento_productivo = True
            
        # E. Movimientos entre HOI, HOO, Líneas y Bahías
        elif zona_orig == "HOO" and zona_dest == "LINEAS_PROD":
            categoria_metrica = 'hoo_a_stg'
            es_movimiento_productivo = True
            
        elif zona_orig == "HOO" and zona_dest == "BAHIAS_EMBARQUE":
            categoria_metrica = 'hoo_a_ast_ash'
            es_movimiento_productivo = True
            
        elif zona_orig == "BAHIAS_RECIBO" and zona_dest == "HOI":
            categoria_metrica = 'bahias_a_hoi'
            es_movimiento_productivo = True
            
        elif zona_orig == "BAHIAS_RECIBO" and zona_dest == "HOO":
            categoria_metrica = 'bahias_a_hoo'
            es_movimiento_productivo = True
            
        elif zona_orig in ["HOI", "HOO", "BAHIAS_RECIBO"] and zona_dest in ["HOI", "HOO", "BAHIAS_RECIBO"]:
            categoria_metrica = 'entre_hoi_hoo_bahias'
            es_movimiento_productivo = True
            
        # F, G, H. Flujos dirigidos hacia OTRAS ubicaciones fuera de los flujos críticos
        elif zona_orig == "HOI" and zona_dest not in ["RACK", "HOO", "BAHIAS_EMBARQUE", "LINEAS_PROD", "BAHIAS_RECIBO"]:
            categoria_metrica = 'hoi_a_otras'
            es_movimiento_productivo = True
            
        elif zona_orig == "HOO" and zona_dest not in ["RACK", "HOI", "BAHIAS_EMBARQUE", "LINEAS_PROD", "BAHIAS_RECIBO"]:
            categoria_metrica = 'hoo_a_otras'
            es_movimiento_productivo = True
            
        elif zona_orig == "BAHIAS_RECIBO" and zona_dest not in ["RACK", "HOI", "HOO", "BAHIAS_EMBARQUE", "LINEAS_PROD"]:
            categoria_metrica = 'brcst_a_otras'
            es_movimiento_productivo = True
            
        # I. Combinaciones no contempladas por las reglas de negocio
        else:
            # No se suma a ninguna métrica ni se cuenta como movimiento productivo
            pass

        # Aplicación de conteos si la regla fue válida
        if es_movimiento_productivo:
            grupo['total_movimientos_productivos'] += 1
            if categoria_metrica:
                grupo[categoria_metrica] += 1
            
            # Consolidar el par origen-destino sin registrar datos individuales del pallet
            comb = (orig_full, dest_full)
            grupo['detalles_combinaciones'][comb] = grupo['detalles_combinaciones'].get(comb, 0) + 1

        # Limpieza final: convertir sets temporales a enteros nativos para aligerar la estructura de salida
        for clave, data in reporte.items():
            data['cargas_unicas_count'] = len(data['cargas_vistas'])
            del data['cargas_vistas']
        
        return reporte


def mostrar_reporte_en_pantalla(lista_reporte):
    """
    Imprime en la terminal el reporte consolidado de forma legible y estructurada,
    evitando la sobrecarga visual mediante desgloses limpios y agrupados.
    """
    if not lista_reporte:
        print(">>> No hay registros para mostrar en el reporte. <<<")
        return

    print("=" * 80)
    print(f"{'REPORTE DE PRODUCTIVIDAD Y RENDIMIENTO LOGÍSTICO':^80}")
    print("=" * 80)

    for clave, datos in lista_reporte.items():
        fecha, usuario, turno = clave
        
        print(f"\n[ FECHA LABORAL: {fecha} ]  [ TURNO: {turno} ]  [ USUARIO: {usuario} ]")
        print("-" * 80)
        print(f" * Total de Cargas Únicas (Pallets identificados): {datos['cargas_unicas_count']}")
        print(f" * Total de Movimientos Productivos Contemplados: {datos['total_movimientos_productivos']}")
        print(f"   |- Almacenamiento Rack a Rack:                  {datos['rack_a_rack']}")
        print(f"   |- Traslados desde HOI -> Rack:                {datos['hoi_a_rack']}")
        print(f"   |- Traslados desde HOO -> Rack:                {datos['hoo_a_rack']}")
        print(f"   |- Bahías (BRCST/BLD) -> Rack:                 {datos['bahias_a_rack']}")
        print(f"   |- Surtido a Líneas (HOO -> STG):              {datos['hoo_a_stg']}")
        print(f"   |- Despacho a Embarques (HOO -> AST/ASH):      {datos['hoo_a_ast_ash']}")
        print(f"   |- Interconexiones Internas (HOI/HOO/Bahías):  {datos['entre_hoi_hoo_bahias']}")
        print(f"   |- Bahías -> Entrada HOI:                      {datos['bahias_a_hoi']}")
        print(f"   |- Bahías -> Salida HOO:                       {datos['bahias_a_hoo']}")
        print(f"   |- Flujos HOI -> Otras Ubicaciones:            {datos['hoi_a_otras']}")
        print(f"   |- Flujos HOO -> Otras Ubicaciones:            {datos['hoo_a_otras']}")
        print(f"   |- Flujos Bahías -> Otras Ubicaciones:         {datos['brcst_a_otras']}")
        print(f"   |- Movimientos Repetidos (Misma Ubicación):    {datos['movimientos_repetidos']}")
        
        # Sección de desgloses de combinaciones físicas
        if datos['detalles_combinaciones']:
            print(f"\n     Detalle de Combinaciones Geográficas (Origen -> Destino):")
            for (orig, dest), total in sorted(datos['detalles_combinaciones'].items()):
                print(f"       • {orig} → {dest} : {total} mov(s).")
        else:
            print(f"\n     No se registraron detalles de combinación para este bloque.")
            
        print("." * 80)
    print("\n" + "=" * 80)
