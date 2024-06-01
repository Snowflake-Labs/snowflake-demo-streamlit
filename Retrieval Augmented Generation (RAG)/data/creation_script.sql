-----------------------------------------------------
-- Create Database and Schema
-----------------------------------------------------
CREATE DATABASE SampleDatabase;
USE DATABASE SampleDatabase;
CREATE SCHEMA RAG_DEMO;
USE SCHEMA RAG_DEMO;
CREATE STAGE RAG_DEMO;

-----------------------------------------------------
-- Create Table
-----------------------------------------------------
CREATE OR REPLACE TABLE DOCS_CHUNKS_TABLE ( 
    RELATIVE_PATH VARCHAR(16777216), -- Relative path to the PDF file
    SIZE NUMBER(38,0), -- Size of the PDF
    FILE_URL VARCHAR(16777216), -- URL for the PDF
    SCOPED_FILE_URL VARCHAR(16777216), -- Scoped url (you can choose which one to keep depending on your use case)
    CHUNK VARCHAR(16777216), -- Piece of text
    CHUNK_VEC VECTOR(FLOAT, 768) 
);  -- Embedding using the VECTOR data type

CREATE OR REPLACE TABLE DOCS_SUMMARIES ( 
    DOC_NAME VARCHAR(),
    DOC_CONTENT VARCHAR()
);

-----------------------------------------------------
-- Create Functions
-----------------------------------------------------
CREATE OR REPLACE FUNCTION PDF_TEXT_CHUNKER(FILE_URL STRING)
RETURNS TABLE (CHUNK VARCHAR)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.9'
HANDLER = 'pdf_text_chunker'
PACKAGES = ('snowflake-snowpark-python','PyPDF2', 'langchain')
AS
$$
from snowflake.snowpark.types import StringType, StructField, StructType
from langchain.text_splitter import RecursiveCharacterTextSplitter
from snowflake.snowpark.files import SnowflakeFile
import PyPDF2, io
import logging
import pandas as pd

class pdf_text_chunker:

    def read_pdf(self, file_url: str) -> str:
    
        logger = logging.getLogger("udf_logger")
        logger.info(f"Opening file {file_url}")
    
        with SnowflakeFile.open(file_url, 'rb') as f:
            buffer = io.BytesIO(f.readall())
            
        reader = PyPDF2.PdfReader(buffer)   
        text = ""
        for page in reader.pages:
            try:
                text += page.extract_text().replace('\n', ' ').replace('\0', ' ')
            except:
                text = "Unable to Extract"
                logger.warn(f"Unable to extract from file {file_url}, page {page}")
        
        return text

    def process(self,file_url: str):

        text = self.read_pdf(file_url)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 4000,
            chunk_overlap  = 400,
            length_function = len
        )
    
        chunks = text_splitter.split_text(text)
        df = pd.DataFrame(chunks, columns=['chunks'])
        
        yield from df.itertuples(index=False, name=None)
$$;


CREATE OR REPLACE FUNCTION GET_PDF_CONTENT (FILE STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.8
PACKAGES = ('snowflake-snowpark-python','pypdf2')
HANDLER = 'read_file'
AS
$$
from io import BytesIO
from PyPDF2 import PdfFileReader
from snowflake.snowpark.files import SnowflakeFile


def read_file(file_path):
    pdf_content = ""
    with SnowflakeFile.open(file_path, "rb") as file:
        buffer = BytesIO(file.readall())
        pdf_reader = PdfFileReader(buffer)
        pdf_content = ""
        for page in pdf_reader.pages:
            pdf_content += page.extract_text()
    return pdf_content
$$;

CREATE OR REPLACE PROCEDURE GET_FILES_SUMMARIES()
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = 3.8
PACKAGES = ('snowflake-snowpark-python', 'pandas')
HANDLER='get_summaries'
EXECUTE AS CALLER
AS
$$
import pandas as pd


def get_summaries(session):
    file_list = session.sql("list @RAG_DEMO").collect()
    for file in file_list:
        file_name = file[0].split("/")[1]
        file_summary = (
            session.sql(
                f"""
                SELECT
                    SNOWFLAKE.CORTEX.SUMMARIZE(
                        SELECT
                            GET_PDF_CONTENT(
                                BUILD_SCOPED_FILE_URL(@RAG_DEMO, '{file_name}')
                            )
                    )
                """
            )
            .to_pandas()
            .iloc[0, 0]
        )
        session.sql(
            f"""
            INSERT INTO
                DOCS_SUMMARIES (DOC_NAME, DOC_CONTENT)
            VALUES
                ('{file_name}', '{file_summary}')
            """
        ).collect()

    return "SUCCESS"
$$;

-----------------------------------------------------
-- Insert from documents
-----------------------------------------------------
INSERT INTO
    DOCS_CHUNKS_TABLE (
        RELATIVE_PATH,
        SIZE,
        FILE_URL,
        SCOPED_FILE_URL,
        CHUNK,
        CHUNK_VEC
    )
SELECT
    RELATIVE_PATH,
    SIZE,
    FILE_URL,
    BUILD_SCOPED_FILE_URL(@RAG_DEMO, RELATIVE_PATH) AS SCOPED_FILE_URL,
    FUNC.CHUNK AS CHUNK,
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', CHUNK) AS CHUNK_VEC
FROM
    DIRECTORY(@RAG_DEMO),
    TABLE(
        PDF_TEXT_CHUNKER(BUILD_SCOPED_FILE_URL(@RAG_DEMO, RELATIVE_PATH))
    ) AS FUNC;

CALL GET_FILES_SUMMARIES();