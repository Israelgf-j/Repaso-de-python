from datetime import datetime, timedelta, time


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
    
    u = str(ubicacion).strip().upper()
    
    # Mapeo de prefijos a sus respectivas zonas logísticas
    MAPEO_PREFIJOS = {
        ("A1", "A2", "B1", "C1", "G1", "F1", "F2", "E1", "E2", "D1"): "RACK",
        ("HOI", "HO1", "HO0"): "HOI",
        ("HOO",): "HOO",
        ("BRCST", "BLDST", "BLDSTG"): "BAHIAS_RECIBO",
        ("ASH", "AST"): "BAHIAS_EMBARQUE",
        ("STG",): "LINEAS_PROD",
        ("RECALL",): "RETRABAJO",
        ("TRAY", "CRITICALTRAY"): "CHAROLAS",
        ("RTN",): "RETORNOS"
    }
    
    # Busca si la ubicación comienza con alguno de los prefijos de las tuplas
    for prefijos, zona in MAPEO_PREFIJOS.items():
        if u.startswith(prefijos):
            return (zona, u)
            
    return ("OTRAS", u)


def determinar_turno_y_fecha(fecha_hora_str):
    """
    Calcula el turno y la fecha laboral real ajustando el desfase nocturno.
    Soporta formatos comunes de SQLite como 'YYYY-MM-DD HH:MM:SS'
    """
    try:
        dt = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "FECHA_INVALIDA", "TURNO_INVALIDO"
        
    hora = dt.time()
    fecha_laboral = dt.date()
    
    # Simplificación: Comparamos directamente contra objetos time predefinidos
    if time(7, 0) <= hora < time(15, 0):
        turno = "Matutino (07-15)"
    elif time(15, 0) <= hora < time(23, 0):
        turno = "Vespertino (15-23)"
    else:
        turno = "Nocturno (23-07)"
        # Si son entre las 00:00 y las 06:59:59, pertenece al día laboral anterior
        if hora < time(7, 0):
            fecha_laboral -= timedelta(days=1)
            
    return fecha_laboral.strftime("%Y-%m-%d"), turno


def resumen_productividad_por_usuario(datos, encabezados_recibidos):
    print(f"[DIAGNÓSTICO] Filas recibidas de la BD: {len(datos)}")
        
    """
    Procesa las filas de SQLite mapeando dinámicamente las columnas según los 
    encabezados recibidos. Reconstruye movimientos cronológicos y clasifica actividades.
    """
    if not datos or not encabezados_recibidos:
        return {}
    
    # --- MAPEADO DINÁMICO DE ENCABEZADOS ---
    try:
        indices = {nom: encabezados_recibidos.index(nom) for nom in ["Load Number", "Last Updated Date", "From Location", "To Location", "User ID"]}
    except ValueError as e:
        raise ValueError(f"Falta un encabezado obligatorio en los datos: {e}")
    
    idx_load, idx_fecha = indices["Load Number"], indices["Last Updated Date"]
    idx_from, idx_to, idx_user = indices["From Location"], indices["To Location"], indices["User ID"]
    limite_indice = max(indices.values())
    
    # 1. Dirección cronológica de los datos
    if len(datos) > 1 and datos[0][idx_fecha] and datos[-1][idx_fecha]:
        if datos[0][idx_fecha] > datos[-1][idx_fecha]:
            datos = datos[::-1]
        
    # 2. Reconstrucción de movimientos reales mediante Single-Pass Streaming
    movimientos_consolidados = []
    actual_load = None
    origen_inicial = destino_final = fecha_hora_mov = usuario_mov = None
    
    for fila in datos:
        if len(fila) <= limite_indice:
            continue
            
        load_num, fecha_hora, from_loc, to_loc, user_id = fila[idx_load], fila[idx_fecha], fila[idx_from], fila[idx_to], fila[idx_user]
        
        if load_num != actual_load:
            if actual_load is not None:
                movimientos_consolidados.append({
                    'load_number': actual_load, 'from_loc': origen_inicial,
                    'to_loc': destino_final, 'fecha_hora': fecha_hora_mov, 'user_id': usuario_mov
                })
            actual_load, origen_inicial, fecha_hora_mov, usuario_mov = load_num, from_loc, fecha_hora, user_id
        
        destino_final = to_loc
        
    if actual_load is not None:
        movimientos_consolidados.append({
            'load_number': actual_load, 'from_loc': origen_inicial,
            'to_loc': destino_final, 'fecha_hora': fecha_hora_mov, 'user_id': usuario_mov
        })
    print(f"[DIAGNÓSTICO] Movimientos consolidados tras Single-Pass: {len(movimientos_consolidados)}")
    

    # 3. Clasificación logística y Agrupación en Reporte Compacto
    reporte = {}
    set_transito = {"HOI", "HOO", "BAHIAS_RECIBO"}
    
    for mov in movimientos_consolidados:
        if not mov['fecha_hora']:
            continue
            
        f_laboral, turno = determinar_turno_y_fecha(mov['fecha_hora'])
        if f_laboral == "FECHA_INVALIDA":
            continue
            
        user_id, load_num = mov['user_id'], mov['load_number']
        clave_grupo = (f_laboral, user_id, turno)
        
        if clave_grupo not in reporte:
            reporte[clave_grupo] = {
                'cargas_vistas': set(), 'cargas_unicas_count': 0, 'total_movimientos_productivos': 0,
                'rack_a_rack': 0, 'hoi_a_rack': 0, 'hoo_a_rack': 0, 'hoo_a_stg': 0, 'hoo_a_ast_ash': 0,
                'bahias_a_rack': 0, 'bahias_a_hoi': 0, 'bahias_a_hoo': 0, 'entre_hoi_hoo_bahias': 0,
                'hoi_a_otras': 0, 'hoo_a_otras': 0, 'brcst_a_otras': 0, 'movimientos_repetidos': 0,
                'detalles_combinaciones': {}
            }
            
        grupo = reporte[clave_grupo]
        grupo['cargas_vistas'].add(load_num)
        
        zona_orig, orig_full = obtener_zona(mov['from_loc'])
        zona_dest, dest_full = obtener_zona(mov['to_loc'])
        
        if zona_orig == "DESCONOCIDA" or zona_dest == "DESCONOCIDA":
            continue
            
        # --- MATRIZ DE ASIGNACIÓN LOGÍSTICA SIMPLIFICADA ---
        categoria_metrica = None
        
        if orig_full == dest_full:
            categoria_metrica = 'movimientos_repetidos'
        elif zona_orig == "RACK" and zona_dest == "RACK":
            categoria_metrica = 'rack_a_rack'
        elif zona_dest == "RACK":
            mapeo_a_rack = {"HOI": "hoi_a_rack", "HOO": "hoo_a_rack", "BAHIAS_RECIBO": "bahias_a_rack"}
            categoria_metrica = mapeo_a_rack.get(zona_orig)
        elif zona_orig == "HOO":
            mapeo_desde_hoo = {"LINEAS_PROD": "hoo_a_stg", "BAHIAS_EMBARQUE": "hoo_a_ast_ash", "OTRAS": "hoo_a_otras"}
            categoria_metrica = mapeo_desde_hoo.get(zona_dest)
        elif zona_orig == "BAHIAS_RECIBO":
            mapeo_desde_bahias = {"HOI": "bahias_a_hoi", "HOO": "bahias_a_hoo", "OTRAS": "brcst_a_otras"}
            categoria_metrica = mapeo_desde_bahias.get(zona_dest)
        elif zona_orig in set_transito and zona_dest in set_transito:
            categoria_metrica = 'entre_hoi_hoo_bahias'
        elif zona_orig == "HOI" and zona_dest == "OTRAS":
            categoria_metrica = 'hoi_a_otras'

        if categoria_metrica:
            grupo[categoria_metrica] += 1
            grupo['total_movimientos_productivos'] += 1
            
        comb = (zona_orig, zona_dest)
        grupo['detalles_combinaciones'][comb] = grupo['detalles_combinaciones'].get(comb, 0) + 1

    for grupo in reporte.values():
        grupo['cargas_unicas_count'] = len(grupo['cargas_vistas'])
        grupo.pop('cargas_vistas', None)

    print(f"[DIAGNÓSTICO] Grupos creados en el reporte final: {len(reporte)}")
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

    # Mapeo ordenado de las claves del diccionario a sus textos descriptivos
    ETIQUETAS_METRICAS = [
        ('rack_a_rack',           '   |- Almacenamiento Rack a Rack:                  '),
        ('hoi_a_rack',            '   |- Traslados desde HOI -> Rack:                '),
        ('hoo_a_rack',            '   |- Traslados desde HOO -> Rack:                '),
        ('bahias_a_rack',         '   |- Bahías (BRCST/BLD) -> Rack:                 '),
        ('hoo_a_stg',             '   |- Surtido a Líneas (HOO -> STG):              '),
        ('hoo_a_ast_ash',         '   |- Despacho a Embarques (HOO -> AST/ASH):      '),
        ('entre_hoi_hoo_bahias',  '   |- Interconexiones Internas (HOI/HOO/Bahías):  '),
        ('bahias_a_hoi',          '   |- Bahías -> Entrada HOI:                      '),
        ('bahias_a_hoo',          '   |- Bahías -> Salida HOO:                       '),
        ('hoi_a_otras',           '   |- Flujos HOI -> Otras Ubicaciones:            '),
        ('hoo_a_otras',           '   |- Flujos HOO -> Otras Ubicaciones:            '),
        ('brcst_a_otras',         '   |- Flujos Bahías -> Otras Ubicaciones:         '),
        ('movimientos_repetidos', '   |- Movimientos Repetidos (Misma Ubicación):    '),
    ]

    for (fecha, usuario, turno), datos in lista_reporte.items():
        print(f"\n[ FECHA LABORAL: {fecha} ]  [ TURNO: {turno} ]  [ USUARIO: {usuario} ]")
        print("-" * 80)
        print(f" * Total de Cargas Únicas (Pallets identificados): {datos['cargas_unicas_count']}")
        print(f" * Total de Movimientos Productivos Contemplados: {datos['total_movimientos_productivos']}")
        
        # Iteración dinámica sobre las métricas logísticas
        for clave_metrica, prefijo_texto in ETIQUETAS_METRICAS:
            print(f"{prefijo_texto}{datos[clave_metrica]}")
        
        # Sección de desgloses de combinaciones físicas
        if datos['detalles_combinaciones']:
            print("\n     Detalle de Combinaciones Geográficas (Origen -> Destino):")
            for (orig, dest), total in sorted(datos['detalles_combinaciones'].items()):
                print(f"       • {orig} → {dest} : {total} mov(s).")
        else:
            print("\n     No se registraron detalles de combinación para este bloque.")
            
        print("." * 80)
        
    print("\n" + "=" * 80)
