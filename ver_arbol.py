import os

# Lista de carpetas a excluir
EXCLUIR = {'venv', '.git', '__pycache__'}

def mostrar_arbol(directorio, prefijo=""):
    try:
        contenido = sorted(os.listdir(directorio))
    except PermissionError:
        return  # Evita errores con carpetas protegidas

    for i, nombre in enumerate(contenido):
        if nombre in EXCLUIR:
            continue

        ruta = os.path.join(directorio, nombre)
        es_ultimo = i == len(contenido) - 1
        conector = "└── " if es_ultimo else "├── "
        print(prefijo + conector + nombre)
        if os.path.isdir(ruta):
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            mostrar_arbol(ruta, nuevo_prefijo)

if __name__ == "__main__":
    carpeta_raiz = "."  # O por ejemplo: "gestion_pedidos"
    print("📁 Estructura del proyecto (sin carpetas excluidas):\n")
    mostrar_arbol(carpeta_raiz)
