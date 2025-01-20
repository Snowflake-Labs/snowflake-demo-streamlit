# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pypdfium2 as pdfium
import pandas as pd

st.set_page_config(
    layout="wide"
)

st.title('Viewing PDFs in Streamlit in Snowflake')

# Get the current credentials
session = get_active_session()

def get_stages():
    stages = session.sql("SHOW STAGES").collect()
    # Format as a Pandas DataFrame before returning
    return pd.DataFrame(stages)

# Get files from directory table
def get_files(db, schema, stage):
   session.sql(f"""ALTER STAGE "{db}"."{schema}"."{stage}" REFRESH""").collect()
   return session.sql(
       f"""SELECT * FROM DIRECTORY('@"{db}"."{schema}"."{stage}"') 
       WHERE RELATIVE_PATH ILIKE '%.pdf' ORDER BY RELATIVE_PATH ASC"""
   ).to_pandas()

df = get_stages()
df = df[df['directory_enabled']=='Y']

# Create the dropdowns to select the db, schema, and stage
stage_containers = st.columns(3)
with stage_containers[0]:  
    db = st.selectbox('Database', df['database_name'].dropna().unique().tolist())

with stage_containers[1]:  
    schema = st.selectbox('Schema', df['schema_name'].dropna().unique().tolist())
    
with stage_containers[2]:  
    stage = st.selectbox('Stage', df['name'].dropna().unique().tolist())

st.caption("Not seeing your stage? Make sure directory tables is enabled")


df = get_files(db, schema, stage)
if(len(df) == 0):
    st.info('No PDFs found in this stage')
    st.stop()

with st.expander('Show full data', expanded=False):
    st.dataframe(df)

pdf_selector_cols = st.columns([3,1])
with pdf_selector_cols[0]:
    # Drop down to select a PDF
    selected_pdf = st.selectbox('Choose PDF', df['RELATIVE_PATH'])


# Get the selected PDF
session.file.get(f"""@"{db}"."{schema}"."{stage}"/{selected_pdf}""", f"/tmp")

with open(f"/tmp/{selected_pdf}", "rb") as pdf_file:
    st.download_button(
        label='Download PDF', 
        data=pdf_file,
        file_name=f"{selected_pdf}",
        mime="application/pdf")

with pdf_selector_cols[1]:
    zoom_scale = st.selectbox('Zoom', [0.5,0.75,1,2,3,4], 2)

# Display the PDF
pdf = pdfium.PdfDocument(f"/tmp/{selected_pdf}")

# Iterate through the pages
for page_num in range(len(pdf)):
    # Render the page
    bitmap = pdf[page_num].render(
        scale = zoom_scale, 
        rotation = 0, # no additional rotation
        # ... further rendering options https://pypdfium2.readthedocs.io/en/stable/python_api.html#pypdfium2._helpers.page.PdfPage.render
    )
    pil_image = bitmap.to_pil()
    st.image(pil_image)
