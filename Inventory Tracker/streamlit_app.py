from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import altair as alt
import pandas as pd
import streamlit as st

# -------------------------------
# Connection and page settings
# -------------------------------
session: Session = get_active_session()
st.set_page_config(layout="wide")


# -------------------------------
# Utils
# -------------------------------
def load_product_data() -> pd.DataFrame:
    """Loads the inventory data from the database."""

    data = session.sql(
        """SELECT
               ID,
               IMAGE,
               ITEM_NAME,
               PRICE,
               UNITS_SOLD,
               UNITS_LEFT,
               COST_PRICE,
               REORDER_POINT,
               DESCRIPTION
           FROM
               INVENTORY;"""
    ).toPandas()

    data.rename(
        columns={
            "ID": "ID",
            "IMAGE": "Image",
            "ITEM_NAME": "Item Name",
            "PRICE": "Price",
            "UNITS_SOLD": "Units Sold",
            "UNITS_LEFT": "Units Left",
            "COST_PRICE": "Cost Price",
            "REORDER_POINT": "Reorder Point",
            "DESCRIPTION": "Description",
        },
        inplace=True,
    )

    return data


def update_product_data(dataframe, changes) -> None:
    """Updates the inventory data in the database."""

    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]

        for i, delta in deltas.items():
            row_value = dataframe.iloc[i].to_dict()
            row_value.update(delta)
            try:
                session.sql(
                    f"""
                    UPDATE
                        INVENTORY
                    SET
                        ITEM_NAME = '{row_value['Item Name']}',
                        PRICE = {row_value['Price']},
                        UNITS_SOLD = {row_value['Units Sold']},
                        UNITS_LEFT = {row_value['Units Left']},
                        COST_PRICE = {row_value['Cost Price']},
                        REORDER_POINT = {row_value['Reorder Point']},
                        DESCRIPTION = '{row_value['Description']}',
                        IMAGE = '{row_value['Image']}'
                    WHERE
                        ID = {row_value['ID']}
                    """
                ).collect()
                st.toast("Data have being updated!")
            except:
                st.toast("Something went wrong while updating the data, try again.")

    if changes["added_rows"]:
        try:
            for row_value in changes["added_rows"]:
                session.sql(
                    f"""
                            INSERT INTO
                                INVENTORY (
                                    ITEM_NAME,
                                    PRICE,
                                    UNITS_SOLD,
                                    UNITS_LEFT,
                                    COST_PRICE,
                                    REORDER_POINT,
                                    DESCRIPTION
                                )
                            VALUES
                                (
                                    '{row_value['Item Name']}',
                                    {row_value['Price']},
                                    {row_value['Units Sold']},
                                    {row_value['Units Left']},
                                    {row_value['Cost Price']},
                                    {row_value['Reorder Point']},
                                    '{row_value['Description']}'
                                )
                            """
                ).collect()
            st.toast("Data have being added!")
        except:
            st.toast("Something went wrong while adding the data, try again.")

    if changes["deleted_rows"]:
        try:
            for row_value in changes["deleted_rows"]:
                session.sql(
                    f"""
                    DELETE FROM
                        INVENTORY
                    WHERE
                        ID = {dataframe.iloc[row_value]['ID']}
                    """
                ).collect()
            st.toast("Data have being delete!")
        except:
            st.toast("Something went wrong while deleting the data, try again.")


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.
# -----------------------------------------------------------------------------

st.title("Inventory Tracker 📊")
st.write("This page reads and writes directly from/to our inventory database.")
st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """,
    icon="ℹ️"
)

product_data = load_product_data()
edited_product_data = st.data_editor(
    product_data,
    disabled=["ID"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "Cost Price": st.column_config.NumberColumn(format="$%.2f"),
        "Image": st.column_config.ImageColumn(),
    },
    key="inventory_table",
    use_container_width=True,
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="secondary",
    disabled=not has_uncommitted_changes,
    on_click=update_product_data,
    args=(product_data, st.session_state.inventory_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts
# -----------------------------------------------------------------------------

st.subheader("Units left", divider="green")

need_to_reorder = product_data[
    product_data["Units Left"] < product_data["Reorder Point"]
].loc[:, "Item Name"]

if len(need_to_reorder) > 0:
    items = "\n".join(f"* {name}" for name in need_to_reorder)
    st.warning(f"We're running dangerously low on the items below:\n {items}")

st.altair_chart(
    alt.Chart(product_data)
    .mark_bar(orient="horizontal", color="#52c234")
    .encode(
        x="Units Left",
        y="Item Name",
    )
    + alt.Chart(product_data)
    .mark_point(
        shape="diamond",
        filled=True,
        size=50,
        color="#061700",
        opacity=1,
    )
    .encode(
        x="Reorder Point",
        y="Item Name",
    ),
    use_container_width=True,
)

st.caption("NOTE: The :diamonds: location shows the reorder point.")

st.subheader("Best sellers", divider="green")

st.altair_chart(
    alt.Chart(product_data)
    .mark_bar(orient="horizontal", color="#1D976C")
    .encode(
        x="Units Sold",
        y=alt.Y("Item Name").sort("-x"),
    ),
    use_container_width=True,
)
