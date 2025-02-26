# -*- coding: utf-8 -*-
"""R2D2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rXzVo79jOkynLh_5FCl2_Wz1Pyt_t7pV
"""
"""
!pip install pdfplumber
!pip install openpyxl
!pip install camelot-py[cv]
!pip install tabula-py
!pip install pdfplumber
!pip install pandas
!pip install pytesseract
!pip install pdf2image
!pip install ChatOpenAI
!pip install langchain
!pip install openai
!pip install pypdf
!pip install xlsxwriter
!pip install python-dotenv
!pip install fuzzywuzzy
"""
import os
import os
import re
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

# Cargar variables del .env
load_dotenv()

# Definir el modelo LLM
api_key = os.getenv("API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

# Crear un prompt para procesar tablas (ajustado)
prompt = PromptTemplate(
    input_variables=["pdf_content"],
    template=(
        "Extrae los siguientes datos del texto del PDF para cada residuo encontrado, y organízalos en una lista de pares clave-valor, separados por comas. Separa cada residuo con un punto y coma (;).\n"
        "n_folio, Establecimiento, Razon Social, Rut titular, Realizado por, Fecha declaracion, Residuo, Cantidad, tipo tratamiento, Destino\n"
        "El texto es:\n{pdf_content}\n"
        "Solo devuelve la lista de pares clave-valor, sin texto adicional."
    )
)

# Crear una cadena LangChain
chain = LLMChain(llm=llm, prompt=prompt)

# Directorio de entrada y salida
pdf_directory = "on"
output_file = "output.xlsx"

# Lista para almacenar los DataFrames
data_list = []

# Procesar PDFs en el directorio
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        filepath = os.path.join(pdf_directory, filename)

        print(f" Procesando archivo: {filename}")

        try:
            # Cargar y leer el PDF
            loader = PyPDFLoader(filepath)
            documents = loader.load()
            pdf_text = " ".join([doc.page_content for doc in documents])

            # Ejecutar el modelo en el contenido del PDF
            response = chain.run(pdf_content=pdf_text)

            # Procesar la respuesta del modelo (ajustado)
            try:
                # Separar los datos de cada residuo
                residuos = response.strip().split(";")
                for residuo in residuos:
                    # Extraer pares clave-valor usando expresiones regulares
                    pairs = re.findall(r"([\w\s]+):\s*([\w\s\d\-\./]+)", residuo)
                    if pairs:
                        data = {key.strip(): value.strip() for key, value in pairs}
                        data_list.append(data)
            except Exception as e:
                print(f"❌ Error al procesar la respuesta del modelo: {e}")
                continue

            print(f"✅ Datos extraídos de: {filename}")

        except Exception as e:
            print(f"❌ Error al procesar {filename}: {e}")

# Crear DataFrame de pandas
df_final = pd.DataFrame(data_list)
df_final.dropna(axis=1, how="all", inplace=True)

# Guardar en Excel
try:
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Datos", index=False)

    # Aplicar formato de tabla en Excel
    wb = load_workbook(output_file)
    ws = wb["Datos"]
    table = Table(displayName="Table_Datos", ref=ws.dimensions)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    table.tableStyleInfo = style
    ws.add_table(table)
    wb.save(output_file)

    print(f"✅ Archivo Excel guardado como {output_file}")
except Exception as e:
    print(f"❌ Error al guardar el archivo Excel: {e}")