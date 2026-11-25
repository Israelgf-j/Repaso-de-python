from datetime import datetime, timedelta
from itertools import chain

def resumen_productividad_por_usuario(datos):
    """
    Reconstruye movimientos productivos mediante secuencias consecutivas
    de load_number y genera contadores por fecha laboral, usuario y turno.

    Acepta cursores SQLite3, sqlite3.Row, diccionarios y tuplas
    cuando el cursor proporciona description.
    """

    # ---------------------------------------------------------
    # 1. Encabezados admitidos
    # ---------------------------------------------------------

    encabezados_requeridos = {
        "from_location",
        "to_location",
        "activity_code",
        "operation_code",
        "user_id",
        "item_number",
        "last_updated_date",
        "quantity",
        "load_number",
        "lot_number",
        "supplier_lot_number"
    }

    # ---------------------------------------------------------
    # 2. Familias de ubicaciones
    # ---------------------------------------------------------

    prefijos_ubicacion = [
        ("CRITICALTRAY", "CHAROLAS"),
        ("FINISH", "PRODUCCION"),
        ("BRCST", "RECIBO"),
        ("BLDST", "RECIBO"),
        ("RECALL", "RETRABAJO"),
        ("TRAY", "CHAROLAS"),
        ("HOI", "HOI"),
        ("HO0", "HO0"),
        ("HO1", "HO1"),
        ("HOO", "HOO"),
        ("HOS", "HOS"),
        ("ASH", "EMBARQUE"),
        ("AST", "EMBARQUE"),
        ("STG", "PRODUCCION"),
        ("RTN", "RETORNO"),
        ("A1", "RACK"),
        ("A2", "RACK"),
        ("B1", "RACK"),
        ("C1", "RACK"),
        ("G1", "RACK"),
        ("F1", "RACK"),
        ("F2", "RACK"),
        ("E1", "RACK"),
        ("E2", "RACK"),
        ("D1", "RACK")
    ]

    familias_logisticas = {"HOI", "HO0", "HO1", "HOO", "HOS", "RECIBO", "EMBARQUE", "PRODUCCION"}

    # ---------------------------------------------------------
    # 3. Reglas específicas de clasificación
    # ---------------------------------------------------------

    reglas_movimientos = {
        ("RACK", "RACK"): "RACK_A_RACK",
        ("RACK", "HOO"): "RACK_A_HOO",
        ("RACK", "RECIBO"): "RACK_A_RECIBO",
        ("RACK", "EMBARQUE"): "RACK_A_EMBARQUE",
        ("RACK", "HOI"): "RACK_A_HOI",
        ("HOI", "RACK"): "HOI_A_RACK",
        ("HOO", "RACK"): "HOO_A_RACK",
        ("HOO", "PRODUCCION"): "HOO_A_PRODUCCION",
        ("HOO", "EMBARQUE"): "HOO_A_EMBARQUE",
        ("RECIBO", "RACK"): "RECIBO_A_RACK",
        ("RECIBO", "HOI"): "RECIBO_A_HOI",
        ("RECIBO", "HO0"): "RECIBO_A_HO_SUPPLY",
        ("RECIBO", "HO1"): "RECIBO_A_HO_SUPPLY",
        ("RECIBO", "HOO"): "RECIBO_A_HOO",
        ("PRODUCCION", "HOI"): "PRODUCCION_A_WH",
        ("RETORNO", "HOI"): "PRODUCCION_A_WH",
        ("PRODUCCION", "HO0"): "PRODUCCION_A_SUPPLY",
        ("PRODUCCION", "HO1"): "PRODUCCION_A_SUPPLY"
    }

    nombres_categorias = [
        "RACK_A_RACK",
        "RACK_A_HOO",
        "RACK_A_RECIBO",
        "RACK_A_EMBARQUE",
        "RACK_A_HOI",
        "HOI_A_RACK",
        "HOO_A_RACK",
        "HOO_A_PRODUCCION",
        "HOO_A_EMBARQUE",
        "RECIBO_A_RACK",
        "RECIBO_A_HOI",
        "RECIBO_A_HOO",
        "RECIBO_A_HO_SUPPLY",
        "PRODUCCION_A_WH",
        "PRODUCCION_A_SUPPLY",
        "ENTRE_FAMILIAS_LOGISTICAS",
        "HOI_OTRAS",
        "HOO_OTRAS",
        "RECIBO_OTRAS",
        "MOVIMIENTOS_REPETIDOS",
        "OTROS_MOVIMIENTOS"
    ]

    # ---------------------------------------------------------
    # 4. Diagnósticos generales
    # ---------------------------------------------------------

    diagnosticos = {
        "filas_procesadas": 0,
        "filas_excluidas_activity_code": 0,
        "cargas_unicas": 0,
        "secuencias_identificadas": 0,
        "cambios_secuencia": 0,
        "secuencias_incompletas": 0,
        "cargas_sin_identificador": 0,
        "ubicaciones_desconocidas": 0,
        "cambios_usuario": 0,
        "cambios_fecha_turno": 0,
        "movimientos_productivos": 0,
        "movimientos_clasificados": 0,
        "movimientos_sin_categoria_especifica": 0,
        "registros_invalidos": 0
    }


    # ---------------------------------------------------------
    # 4.1. Actividades excluidas
    # ---------------------------------------------------------

    actividades_excluidas = {
        "Location Allocate to Empty Clear Automatic",
        "Cancel Pick",
        "Location Status Change"
        }

    # ---------------------------------------------------------
    # 5. Preparación del cursor y encabezados
    # ---------------------------------------------------------

    iterador = iter(datos)
    centinela = object()

    primera_fila = next(iterador, centinela)

    descripcion = getattr(datos, "description", None)

    if descripcion is not None:
        nombres_columnas = [columna[0] for columna in descripcion]

    elif primera_fila is not centinela and hasattr(primera_fila, "keys"):
        nombres_columnas = list(primera_fila.keys())

    elif isinstance(primera_fila, dict):
        nombres_columnas = list(primera_fila.keys())

    elif primera_fila is centinela:
        nombres_columnas = []

    else:
        raise ValueError(
            "Las tuplas necesitan un cursor con description."
        )

    # Normalizar nombres sin depender de su posición.

    mapa_columnas = {
        str(nombre).strip().lower().replace(" ", "_"): nombre
        for nombre in nombres_columnas
    }

    faltantes = encabezados_requeridos - set(mapa_columnas)

    if faltantes:
        raise ValueError(
            f"Faltan encabezados requeridos: {sorted(faltantes)}"
        )

    indices_columnas = {
        nombre: nombres_columnas.index(mapa_columnas[nombre])
        for nombre in encabezados_requeridos
    }

    # ---------------------------------------------------------
    # 6. Estructuras de acumulación
    # ---------------------------------------------------------

    grupos = {}
    cargas_registradas = set()

    secuencia = None

    # ---------------------------------------------------------
    # 7. Procesamiento de una sola pasada
    # ---------------------------------------------------------

    if primera_fila is centinela:
        filas = iter((centinela,))
    else:
        filas = chain(
            (primera_fila,),
            iterador,
            (centinela,)
        )

    for fila in filas:

        es_fin = fila is centinela

        if not es_fin:
            diagnosticos["filas_procesadas"] += 1

            # Obtener valores sin depender del orden.

            valores = {}

            for nombre in encabezados_requeridos:
                columna = mapa_columnas[nombre]

                if isinstance(fila, dict):
                    valor = fila[columna]

                elif hasattr(fila, "keys"):
                    valor = fila[columna]

                else:
                    valor = fila[indices_columnas[nombre]]

                valores[nombre] = valor

            
            # -------------------------------------------------
            # 7.1 Ignorar actividades no productivas
            # -------------------------------------------------

            if (
                valores["activity_code"] is not None and str(valores["activity_code"]).strip() in actividades_excluidas
            ):
                diagnosticos["filas_excluidas_activity_code"] += 1
                continue

            load_actual = valores["load_number"]

            if load_actual is None or not str(load_actual).strip():
                load_actual = None
                diagnosticos["cargas_sin_identificador"] += 1
                diagnosticos["registros_invalidos"] += 1

            else:
                load_actual = str(load_actual).strip()

            # ----------------------------------
            # Obtencion del usuario actual
            # ----------------------------------

            usuario_actual = valores["user_id"]

            if usuario_actual is None or not str(usuario_actual).strip():
                usuario_actual = "(SIN USUARIO)"
            else:
                usuario_actual = str(usuario_actual).strip()

        else:
            load_actual = None

        # -----------------------------------------------------
        # 8. Detectar el final de una secuencia
        # -----------------------------------------------------

        if secuencia is not None and (load_actual != secuencia["load_number"] or usuario_actual != secuencia["usuario"]):

            if not es_fin:
                diagnosticos["cambios_secuencia"] += 1

            # Registrar cambios detectados dentro de la secuencia.

            if secuencia["cambio_usuario"]:
                diagnosticos["cambios_usuario"] += 1

            if secuencia["cambio_fecha_turno"]:
                diagnosticos["cambios_fecha_turno"] += 1

            origen = secuencia["origen"]
            destino = secuencia["destino"]

            # -------------------------------------------------
            # 9. Validar el movimiento
            # -------------------------------------------------

            movimiento_valido = (
                origen is not None
                and destino is not None
                and secuencia["fecha_valida"]
            )

            if not movimiento_valido:
                diagnosticos["secuencias_incompletas"] += 1

            # La secuencia se asigna al primer registro.

            if secuencia["fecha_laboral"] is not None:

                clave_grupo = (
                    secuencia["fecha_laboral"],
                    secuencia["usuario"],
                    secuencia["turno"]
                )

                if clave_grupo not in grupos:
                    grupos[clave_grupo] = {
                        "cargas_unicas": 0,
                        "movimientos_productivos": 0,
                        "categorias": {
                            categoria: 0
                            for categoria in nombres_categorias
                        },
                        "detalle_ubicaciones": {},
                        "detalle_por_categoria": {
                            categoria: {}
                            for categoria in nombres_categorias
                        }
                    }

                grupo = grupos[clave_grupo]

                # Una carga por secuencia, incluso si su ID reaparece.

                grupo["cargas_unicas"] += 1

                # -------------------------------------------------
                # 10. Clasificar solamente movimientos válidos
                # -------------------------------------------------

                if movimiento_valido:

                    # Determinar familias.

                    familia_origen = next(
                        (
                            familia
                            for prefijo, familia in prefijos_ubicacion
                            if origen.startswith(prefijo)
                        ),
                        "OTRAS"
                    )

                    familia_destino = next(
                        (
                            familia
                            for prefijo, familia in prefijos_ubicacion
                            if destino.startswith(prefijo)
                        ),
                        "OTRAS"
                    )

                    # Clasificación exclusiva.

                    par_familias = (
                        familia_origen,
                        familia_destino
                    )

                    if par_familias in reglas_movimientos:

                        categoria = reglas_movimientos[par_familias]

                    elif (
                        familia_origen == familia_destino
                        and (
                            familia_origen in familias_logisticas
                            or familia_origen == "RETORNO"
                        )
                    ):

                        categoria = "MOVIMIENTOS_REPETIDOS"

                    elif (
                        familia_origen in familias_logisticas
                        and familia_destino in familias_logisticas
                    ):

                        categoria = "ENTRE_FAMILIAS_LOGISTICAS"

                    elif familia_origen == "HOI":

                        categoria = "HOI_OTRAS"

                    elif familia_origen == "HOO":

                        categoria = "HOO_OTRAS"

                    elif familia_origen == "RECIBO":

                        categoria = "RECIBO_OTRAS"

                    else:

                        categoria = "OTROS_MOVIMIENTOS"

                    # -------------------------------------------------
                    # 11. Actualizar contadores
                    # -------------------------------------------------

                    grupo["movimientos_productivos"] += 1
                    grupo["categorias"][categoria] += 1

                    diagnosticos["movimientos_productivos"] += 1
                    diagnosticos["movimientos_clasificados"] += 1

                    # Guardar detalle de ubicaciones por categoría.

                    detalle_categoria = grupo["detalle_por_categoria"][categoria]
                    clave_detalle = (origen, destino)
                    detalle_categoria[clave_detalle] = (detalle_categoria.get(clave_detalle, 0) + 1)

                    if categoria == "OTROS_MOVIMIENTOS":
                        diagnosticos[
                            "movimientos_sin_categoria_especifica"
                        ] += 1

                    # Contabilizar ubicaciones desconocidas.

                    if familia_origen == "OTRAS":
                        diagnosticos["ubicaciones_desconocidas"] += 1

                    if familia_destino == "OTRAS":
                        diagnosticos["ubicaciones_desconocidas"] += 1

                    # Detalle por ubicación completa.

                    clave_detalle = (origen, destino)

                    detalle = grupo["detalle_ubicaciones"]

                    detalle[clave_detalle] = (
                        detalle.get(clave_detalle, 0) + 1
                    )

                    ultimo_destino = secuencia["destino"]
                    ultimo_load = secuencia["load_number"]

            # La secuencia anterior ya fue procesada.
            secuencia = None

        # El centinela permite finalizar la última secuencia.

        if es_fin:
            break

        # -----------------------------------------------------
        # 12. Ignorar filas sin identificador
        # -----------------------------------------------------

        if load_actual is None:
            continue

        # -----------------------------------------------------
        # 13. Iniciar una nueva secuencia
        # -----------------------------------------------------

        if secuencia is None:

            diagnosticos["secuencias_identificadas"] += 1

            cargas_registradas.add(load_actual)

            # Fecha inicial.

            try:
                fecha_hora = datetime.strptime(
                    str(valores["last_updated_date"]).strip(),
                    "%Y-%m-%d %H:%M:%S"
                )

                fecha_valida = True

            except (ValueError, TypeError, AttributeError):
                fecha_hora = None
                fecha_valida = False

                diagnosticos["registros_invalidos"] += 1

            fecha_laboral = None
            turno = None

            if fecha_valida:

                hora = fecha_hora.hour

                if hora < 7:
                    fecha_laboral = (
                        fecha_hora.date()
                        - timedelta(days=1)
                    ).strftime("%Y-%m-%d")

                    turno = "23:00-07:00"

                elif hora < 15:
                    fecha_laboral = fecha_hora.strftime("%Y-%m-%d")
                    turno = "07:00-15:00"

                elif hora < 23:
                    fecha_laboral = fecha_hora.strftime("%Y-%m-%d")
                    turno = "15:00-23:00"

                else:
                    fecha_laboral = fecha_hora.strftime("%Y-%m-%d")
                    turno = "23:00-07:00"

            usuario = valores["user_id"]

            if usuario is None or not str(usuario).strip():
                usuario = "(SIN USUARIO)"
            else:
                usuario = str(usuario).strip()

            origen = valores["from_location"]


            # Si es una continuación de la misma carga,
            # utilizar el último destino de la secuencia anterior.
            if (
                secuencia is None
                and 'ultimo_destino' in locals()
                and ultimo_destino is not None
            ):
                if load_actual == ultimo_load:
                    origen = ultimo_destino


            if origen is not None:
                origen = str(origen).strip().upper() or None

            destino = valores["to_location"]

            if destino is not None:
                destino = str(destino).strip().upper() or None

            secuencia = {
                "load_number": load_actual,
                "origen": origen,
                "destino": destino,
                "fecha_laboral": fecha_laboral,
                "usuario": usuario,
                "turno": turno,
                "fecha_valida": fecha_valida,
                "cambio_usuario": False,
                "cambio_fecha_turno": False
            }

            continue

        # -----------------------------------------------------
        # 14. Continuar una secuencia existente
        # -----------------------------------------------------

        usuario_actual = valores["user_id"]

        if usuario_actual is None or not str(usuario_actual).strip():
            usuario_actual = "(SIN USUARIO)"
        else:
            usuario_actual = str(usuario_actual).strip()

        if usuario_actual != secuencia["usuario"]:
            secuencia["cambio_usuario"] = True

        # El destino siempre se actualiza.
        # El origen permanece siendo el de la primera fila.

        destino = valores["to_location"]

        if destino is not None:
            destino = str(destino).strip().upper() or None

        secuencia["destino"] = destino

        # Detectar cambios de fecha laboral o turno.

        try:
            fecha_actual = datetime.strptime(
                str(valores["last_updated_date"]).strip(),
                "%Y-%m-%d %H:%M:%S"
            )

            hora = fecha_actual.hour

            if hora < 7:
                fecha_actual_laboral = (
                    fecha_actual.date()
                    - timedelta(days=1)
                ).strftime("%Y-%m-%d")

                turno_actual = "23:00-07:00"

            elif hora < 15:
                fecha_actual_laboral = fecha_actual.strftime("%Y-%m-%d")
                turno_actual = "07:00-15:00"

            elif hora < 23:
                fecha_actual_laboral = fecha_actual.strftime("%Y-%m-%d")
                turno_actual = "15:00-23:00"

            else:
                fecha_actual_laboral = fecha_actual.strftime("%Y-%m-%d")
                turno_actual = "23:00-07:00"

            if (
                fecha_actual_laboral != secuencia["fecha_laboral"]
                or turno_actual != secuencia["turno"]
            ):
                secuencia["cambio_fecha_turno"] = True

        except (ValueError, TypeError, AttributeError):

            secuencia["fecha_valida"] = False
            diagnosticos["registros_invalidos"] += 1

    # ---------------------------------------------------------
    # 15. Construir resultados
    # ---------------------------------------------------------

    diagnosticos["cargas_unicas"] = len(cargas_registradas)

    lista_reportes = []

    for clave, grupo in sorted(grupos.items()):

        fecha, usuario, turno = clave

        lista_reportes.append({
            "fecha_laboral": fecha,
            "usuario": usuario,
            "turno": turno,
            "cargas_unicas": grupo["cargas_unicas"],
            "movimientos_productivos": grupo["movimientos_productivos"],
            "categorias": grupo["categorias"],
            "detalle_ubicaciones": grupo["detalle_ubicaciones"],
            "detalle_por_categoria": grupo["detalle_por_categoria"]
        })

    # ---------------------------------------------------------
    # 16. Diagnóstico general
    # ---------------------------------------------------------

    print("\n========== DIAGNÓSTICO DE PRODUCTIVIDAD ==========")

    for indicador, cantidad in diagnosticos.items():
        print(f"{indicador:42}: {cantidad}")

    print("==================================================\n")

    return {
        "diagnosticos": diagnosticos,
        "reportes": lista_reportes
    }


def mostrar_reporte_en_pantalla(lista_reporte):
    """
    Presenta los resultados de productividad.
    No procesa ni modifica los registros originales.
    """

    if not lista_reporte or not lista_reporte.get("reportes"):
        print("No existen movimientos para mostrar.")
        return

    nombres = {
        "RACK_A_RACK": "Rack → Rack",
        "RACK_A_HOO": "Rack → HOO",
        "RACK_A_RECIBO": "Rack → Recibo",
        "RACK_A_EMBARQUE": "Rack → EMBARQUE",
        "RACK_A_HOI": "Rack → HOI",
        "HOI_A_RACK": "HOI → Rack",
        "HOO_A_RACK": "HOO → Rack",
        "HOO_A_PRODUCCION": "HOO → PRODUCCION",
        "HOO_A_EMBARQUE": "HOO → ASH/AST",
        "RECIBO_A_RACK": "Recibo → Rack",
        "RECIBO_A_HOI": "Recibo → HOI/HO0/HO1",
        "RECIBO_A_HOO": "Recibo → HOO",
        "RECIBO_A_HO_SUPPLY": "Recibo → HO0/HO1",

        # De FINISH a Supply
        "PRODUCCION_A_SUPPLY": "PRODUCCION → HO0/HO1",
        # De RTN a Warehouse
        "PRODUCCION_A_WH": "PRODUCCION → HOI",

        "ENTRE_FAMILIAS_LOGISTICAS": "Entre familias logísticas",
        "HOI_OTRAS": "HOI → otras ubicaciones",
        "HOO_OTRAS": "HOO → otras ubicaciones",
        "RECIBO_OTRAS": "Recibo → otras ubicaciones",
        "MOVIMIENTOS_REPETIDOS": "Movimientos repetidos",
        "OTROS_MOVIMIENTOS": "Otros movimientos"
    }

    reportes = lista_reporte["reportes"]

    fecha_actual = None

    print("\n" + "=" * 65)
    print("             REPORTE DE PRODUCTIVIDAD LOGÍSTICA")
    print("=" * 65)

    for reporte in reportes:

        if reporte["fecha_laboral"] != fecha_actual:

            fecha_actual = reporte["fecha_laboral"]

            print(f"\n\nFECHA LABORAL: {fecha_actual}")
            print("-" * 65)

        print(f"\nUsuario : {reporte['usuario']}")
        print(f"Turno   : {reporte['turno']}")

        print(f"Cargas / secuencias : {reporte['cargas_unicas']}")
        print(
            f"Movimientos productivos: "
            f"{reporte['movimientos_productivos']}"
        )

        print("\nCLASIFICACIÓN DE MOVIMIENTOS")

        for categoria, nombre in nombres.items():
            
            cantidad = reporte["categorias"].get(categoria, 0)

            if cantidad > 0:
                
                if categoria == "ENTRE_FAMILIAS_LOGISTICAS":
                    print(f"  {nombre:35}: {cantidad:>6} - HOO2 a HO03, HOI1 a HOI2, RTN01 a RTNMOL")
                    continue
                
                print(f"  {nombre:35}: {cantidad:>6}")




        # Impresion de otros movimientos.
        otros = reporte["detalle_por_categoria"]["OTROS_MOVIMIENTOS"]

        if otros:

            print("\nFecha:", reporte["fecha_laboral"])
            print("Usuario:", reporte["usuario"])
            print("Turno:", reporte["turno"])

            print("\nOTROS MOVIMIENTOS:")

            for (origen, destino), cantidad in otros.items():

                print(
                    f"{origen} -> {destino}: {cantidad}"
                )

        #break


def mostrar_reporte_en_pantalla_consolidado(lista_reporte):
    """
    Presenta el reporte de productividad agrupado por fecha y turno.

    Filas: categorías de movimientos.
    Columnas: usuarios del turno.
    Cada turno tiene su propia tabla.
    No modifica los registros originales.
    """

    if not lista_reporte or not lista_reporte.get("reportes"):
        print("No existen movimientos para mostrar.")
        return

    from tabulate import tabulate
    import shutil

    nombres = {
        "RACK_A_RACK": "Rack-Rack",
        "RACK_A_HOO": "Rack-HOO",
        "RACK_A_RECIBO": "Rack-Recibo",
        "RACK_A_EMBARQUE": "Rack-Emb",
        "RACK_A_HOI": "Rack-HOI",
        "HOI_A_RACK": "HOI-Rack",
        "HOO_A_RACK": "HOO-Rack",
        "HOO_A_PRODUCCION": "HOO-STG",
        "HOO_A_EMBARQUE": "HOO-ASH/AST",
        "RECIBO_A_RACK": "Rec-Rack",
        "RECIBO_A_HOI": "Rec-HOI",
        "RECIBO_A_HOO": "Rec-HOO",
        "RECIBO_A_HO_SUPPLY": "Rec-Supply",
        "PRODUCCION_A_SUPPLY": "Prod-Supply",
        "PRODUCCION_A_WH": "Prod-HOI",
        "ENTRE_FAMILIAS_LOGISTICAS": "Entre familias",
        "HOI_OTRAS": "HOI-Otras",
        "HOO_OTRAS": "HOO-Otras",
        "RECIBO_OTRAS": "Rec-Otras",
        "MOVIMIENTOS_REPETIDOS": "Repetidos",
        "OTROS_MOVIMIENTOS": "Otros"
    }

    reportes = lista_reporte["reportes"]

    fechas = {}

    for reporte in reportes:
        fecha = reporte["fecha_laboral"]
        turno = reporte["turno"]

        fechas.setdefault(fecha, {})
        fechas[fecha].setdefault(turno, [])

        fechas[fecha][turno].append(reporte)

    ancho_pantalla = shutil.get_terminal_size((120, 30)).columns

    print("\n" + "=" * min(ancho_pantalla, 100))
    print("       REPORTE GENERAL DE PRODUCTIVIDAD")
    print("=" * min(ancho_pantalla, 100))

    for fecha, turnos in fechas.items():

        print(f"\nFECHA LABORAL: {fecha}")
        print("=" * min(ancho_pantalla, 100))

        for turno, registros in turnos.items():

            print(f"\nTURNO: {turno}")
            print("-" * min(ancho_pantalla, 100))

            # Usuarios sin mostrar el turno en el encabezado
            usuarios = [r["usuario"] for r in registros]

            ancho_categoria = 18
            ancho_usuario = 9

            max_columnas = max(
                1,
                (ancho_pantalla - ancho_categoria - 8) // ancho_usuario
            )

            filas = []

            for categoria, nombre in nombres.items():

                cantidades = [
                    r["categorias"].get(categoria, 0)
                    for r in registros
                ]

                # Ocultar categorías sin movimientos
                if not any(cantidades):
                    continue

                filas.append([nombre] + cantidades + [sum(cantidades)])

            # Resumen de cargas
            filas.append(
                ["CARGAS"] +
                [r["cargas_unicas"] for r in registros] +
                [sum(r["cargas_unicas"] for r in registros)]
            )

            # Resumen de movimientos productivos
            filas.append(
                ["MOV. PRODUCTIVOS"] +
                [r["movimientos_productivos"] for r in registros] +
                [sum(r["movimientos_productivos"] for r in registros)]
            )

            # Mostrar usuarios en grupos según el ancho de pantalla
            for inicio in range(0, len(usuarios), max_columnas):

                fin = inicio + max_columnas

                encabezados = (["CATEGORÍA"] + usuarios[inicio:fin] + ["TOTAL"])

                filas_grupo = []

                for fila in filas:
                    valores = fila[1 + inicio:1 + fin]

                    filas_grupo.append(
                        [fila[0]] + valores + [sum(valores)]
                    )

                print(
                    tabulate(
                        filas_grupo,
                        headers=encabezados,
                        tablefmt="simple",
                        numalign="right",
                        stralign="left"
                    )
                )

                if fin < len(usuarios):
                    print("\n--- SIGUIENTES USUARIOS ---\n")

            print()

    print("=" * min(ancho_pantalla, 100))