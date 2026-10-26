def total_inventario(cursor, tabla):

    query = f"SELECT COUNT(*) FROM {tabla}"

    cursor.execute(query)

    return cursor.fetchone()[0]


def mostrar_datos_tabla(cursor, tabla):
        
        query = f"""
            SELECT *
            FROM {tabla}
            ORDER BY last_move_date
            LIMIT 10
            """
        
        cursor.execute(query)

        return cursor.fetchall()


def reporte_24hrs(cursor, tabla):
    """
    Retorna registros filtrados por ubicaciones específicas (HO, AST, ASH, BRC, BLD) 
    y cuya fecha de último movimiento sea estrictamente anterior al día de hoy.
    """
    print()
    print("-" * 20, "Ejecutando consulta del reporte de 24 horas...\n")
    
    query = f"""
    SELECT load_number, item_number, unit_quantity, storage_location, supplier_lot_number, lot_number, last_move_date,
    -- 🌟 CORRECCIÓN: Compara puras fechas (substrae los días reales sin importar la hora)
    CAST(julianday(date('now', 'localtime')) - julianday(date(last_move_date)) AS INTEGER) AS dias_perdido 
    FROM {tabla}
    WHERE ( 
        storage_location LIKE 'WHKILL%' OR
        storage_location LIKE 'HOI%' OR
        storage_location LIKE 'BRC%' OR 
        storage_location LIKE 'BLD%' OR
        storage_location LIKE 'HO0%' OR
        storage_location LIKE 'HO1%' OR
        storage_location LIKE 'AST%' OR
        storage_location LIKE 'ASH%' 
    ) 
    -- 🌟 FILTRO SEGURO: Asegura que solo traiga días estrictamente anteriores (Ayer o antes)
    AND date(last_move_date) < date('now', 'localtime') 
    ORDER BY dias_perdido DESC;
    """
        
    cursor.execute(query)

    return cursor.fetchall()


def reporte_capacidad(cursor, tabla):
    """
    Retorna registros filtrados por ubicaciones específicas (B10, B11, B12, B13, B14, C10, C11, C12, C13, C14, D10, D11, D12, D13, D14, HOI, BRC, BLD, A1, A2 AST, ASH, HO1, HO0)
    """
    print("\n\tEjecutando consulta del reporte de capacidad...")
    
    query = f"""
    SELECT  building_id, item_number, description, unit_quantity, stocking_unit_of_measure, lot_number, inventory_status,storage_location, load_number, fifo_date
    FROM {tabla}
    WHERE (
        -- Simplificación para patrones como B10, B11..., C10..., D10...
        (SUBSTR(storage_location, 1, 3) IN (
            'B10', 'B11', 'B12', 'B13', 'B14', 
            'C10', 'C11', 'C12', 'C13', 'C14', 
            'D10', 'D11', 'D12', 'D13', 'D14', 
            'HOI', 'BRC', 'BLD', 'HO1', 'HO0', 'AST', 'ASH'
        ))
        -- Simplificación para patrones más cortos de 2 caracteres
        OR (SUBSTR(storage_location, 1, 2) IN ('A1', 'A2'))
    );
    -- ORDER BY storage_location DESC;
    """

    cursor.execute(query)

    return cursor.fetchall()
