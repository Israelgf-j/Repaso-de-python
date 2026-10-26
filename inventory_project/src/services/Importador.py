def crear_tabla_capacidad(cursor):

    #_, claves_csv_bd = ManejoCSV.leer_CSV(self.RUTA_CSV
    cursor.execute("DROP TABLE IF EXISTS inventario_capacidad;")
    query = """
        CREATE TABLE inventario_capacidad (
        building_id TEXT,
        item_number TEXT,
        description TEXT,
        unit_quantity REAL,
        stocking_unit_of_measure TEXT,
        lot_number TEXT,
        inventory_status TEXT,
        storage_location TEXT,
        load_number TEXT,
        fifo_date TEXT,
        last_move_date TEXT,
        supplier_lot_number TEXT,
        display_unit_quantity TEXT,
        area TEXT,
        manufactured_date TEXT,
        received_date TEXT);     
    """

    print("\n\tTabla 'inventario_capacidad' creada exitosamente.")
    
    return cursor.execute(query)


def crear_tabla_productividad(cursor):

    cursor.execute("DROP TABLE IF EXISTS inventario_productividad;")

    query = """
        CREATE TABLE inventario_productividad (
        from_location TEXT,
        to_location TEXT,
        activity_code TEXT,
        operation_code TEXT,
        user_id TEXT,
        item_number TEXT,
        last_updated_date TEXT,
        quantity REAL,
        load_number TEXT,
        lot_number TEXT,
        supplier_lot_number TEXT);
        """
    
    print("\n\tTabla 'inventario_productividad' creada exitosamente.")
    
    return cursor.execute(query)

