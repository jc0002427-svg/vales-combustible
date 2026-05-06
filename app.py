def extraer_datos(texto):
    texto = texto.upper().replace("\n", " ")

    # 🔹 Vale (más flexible)
    vale = re.search(r'(NO|N°|N0)[\s.:]*?(\d{3,})', texto)
    vale = vale.group(2) if vale else ""

    # 🔹 Fecha (varios formatos)
    fecha = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', texto)
    fecha = fecha.group(1) if fecha else ""

    # 🔹 Valor (más robusto)
    valores = re.findall(r'\d{2,3}[.,]?\d{3}', texto)
    valor = ""
    if valores:
        # tomar el mayor (normalmente es el total)
        valor = max(valores, key=lambda x: int(x.replace(".", "").replace(",", "")))

    # 🔹 Combustible
    if "ACPM" in texto:
        combustible = "ACPM (Diesel)"
    else:
        combustible = "Gasolina Motor"

    # 🔹 Placa
    placa_match = re.search(r'[A-Z]{3}\s?\d{3}', texto)
    placa = placa_match.group(0) if placa_match else "MAQUINARIA"

    # 🔹 Lógica negocio
    if placa == "MAQUINARIA":
        destino = "Maquinaria"
        cantidad = 3
        obs = "Maquinaria GUADAÑA"
    else:
        destino = "Vehículo"
        cantidad = 1
        obs = ""

    return {
        "N° Vale": vale,
        "Fecha": fecha,
        "Placa / Equipo": placa,
        "Tipo de Combustible": combustible,
        "Cantidad": cantidad,
        "Valor Total ($)": valor,
        "Destino": destino,
        "Observaciones": obs
    }
