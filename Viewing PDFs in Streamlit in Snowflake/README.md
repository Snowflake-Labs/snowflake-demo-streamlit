![](../shared_assets/sis-header.jpeg)

# Viewing PDFs in Streamlit in Snowflake
This app demonstrates how to read a PDF file from a stage and have it render as an image in Streamlit

## Prerequisites

### Create a stage with Directory Tables enabled

> Note: To create an internal stage, you must use a role that is granted or inherits the necessary privileges. For details, see [Access control requirements](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html#label-create-stage-privileges) for [CREATE STAGE](https://docs.snowflake.com/en/sql-reference/sql/create-stage).

To use Snowsight to create a named internal stage, do the following:
1. Sign in to Snowsight.
2. In the navigation menu, select **Create** » **Stage** » **Snowflake Managed**.
3. In the **Create Stage** dialog, enter a **Stage Name**.
4. Select the database and schema where you want to create the stage.
5. Leave the Directory table enabled. 
    > Directory tables let you see files on the stage, but require a warehouse and thus incur a cost. You can choose to deselect this option for now and enable a directory table later.
6. Under **Encyrption**, select **Server-side entryption** for all files on your stage. For details, see [encryption for internal stages](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html#label-create-stage-internalstageparams).
    > Note: You can’t change the encryption type after you create the stage.
    >
    >To enable data access, use server-side encryption. Otherwise, staged files are client-side encrypted by default and unreadable when downloaded. For more information, see [Server-side encryption for unstructured data access](https://docs.snowflake.com/en/user-guide/unstructured-intro.html#label-file-url-server-side-encryption).
7. Complete the fields to describe your stage. For more information, see [CREATE STAGE](https://docs.snowflake.com/en/sql-reference/sql/create-stage).
8. Select **Create**.

For the lastest instruction, visit: https://docs.snowflake.com/en/user-guide/data-load-local-file-system-stage-ui#creating-a-stage

Alternatively, you can run the following SQL
```sql
CREATE STAGE mystage
   DIRECTORY = (ENABLE = TRUE);
```

### Adding sample data  

Upload files onto a named internal stage using the Snowsight Web Interface
> Note: The maximum file size is 250 MB.
>
> To upload files onto an internal stage, you must use a role that is granted or inherits the USAGE privilege on the database and schema and the WRITE privilege on the stage. For more information, see [Stage privileges](https://docs.snowflake.com/en/user-guide/security-access-control-privileges.html#label-access-control-privileges-stage).

To upload files onto your stage, do the following:
1. Sign in to Snowsight.
2. Select **Data** » **Add Data**.
3. On the **Add Data** page, select **Load files into a Stage**.
4. In the **Upload Your Files** dialog that appears, select the files that you want to upload. You can upload multiple files at the same time.
    > There are sample PDFs in the `pdfs` folder
5. Select the database schema in which you created the stage, then select the stage.
6. Optionally, select or create a path where you want to save your files within the stage.
7. Select **Upload**.

For the lastest instruction, visit: https://docs.snowflake.com/en/user-guide/data-load-local-file-system-stage-ui#uploading-files-onto-a-stage



### Add Python Packages

Make sure to add the `pypdfium2` package.