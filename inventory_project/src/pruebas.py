# Lista original de encabezados
encabezados = [
    "From Location", "To Location", "Activity Code", "Operation Code", 
    "User ID", "Item Number", "Last Updated Date", "Quantity", 
    "Load Number", "Lot Number", "Supplier Lot Number"
]

# Creación automática del diccionario vaciando los espacios por "_" y pasando a minúsculas
diccionario_automatico = {encabezado.lower().replace(" ", "_"): encabezado for encabezado in encabezados}

print(diccionario_automatico)

mapeo_encabezados = {clave.strip().lower().replace(" ", "_"): clave for clave in encabezados}

mapeo_productividad = {'from_location': 'From Location', 'to_location': 'To Location', 'activity_code': 'Activity Code', 'operation_code': 'Operation Code', 'user_id': 'User ID', 'item_number': 'Item Number', 'last_updated_date': 'Last Updated Date', 'quantity': 'Quantity', 'load_number': 'Load Number', 'lot_number': 'Lot Number', 'supplier_lot_number': 'Supplier Lot Number'}