import datetime

import altair as alt
import pandas as pd
import streamlit as st

def initialize_state():
    """Initializes the session state with an empty, structured DataFrame."""
    if "df" not in st.session_state:
        # Define the structure of the DataFrame
        columns = ["ID", "Category", "Update", "Status", "Priority", "Date Logged"]
        st.session_state.df = pd.DataFrame(columns=columns)
        # Set specific data types for columns to ensure consistency
        st.session_state.df = st.session_state.df.astype({
            "ID": str,
            "Category": str,
            "Update": str,
            "Status": str,
            "Priority": str,
            "Date Logged": "datetime64[ns]"
        })

def display_header():
    """Displays the header and introduction of the Streamlit app."""
    st.title("📈 Business Operations Tracker")
    st.write(
        """
        This app provides a centralized dashboard to track real-time updates across
        different business functions. Log new updates, edit existing ones, and visualize progress.
        """
    )

def display_add_update_form():
    """Displays the form to add a new business update."""
    st.header("Log a New Update")
    
    categories = [
        "Lead Contacted", "Client Payment Received", "Client Feedback", 
        "Software Update", "App Update", "Digital Marketing Update", 
        "Mixing and Mastering Update", "Operations Update", "Utilities Update", 
        "Resource Purchase", "Legal Update", "UI/UX Update", "Custom"
    ]

    with st.form("add_update_form", clear_on_submit=True):
        category_selection = st.selectbox("Category", categories)
        
        custom_category = ""
        if category_selection == "Custom":
            custom_category = st.text_input("Enter Custom Category Name")

        update_description = st.text_area("Update Description")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        submitted = st.form_submit_button("Submit")

        if submitted and update_description:
            final_category = custom_category if category_selection == "Custom" and custom_category else category_selection
            
            if final_category == "Custom":
                st.warning("Please enter a name for the custom category.")
                return

            # Generate new ID safely
            if st.session_state.df.empty:
                new_id_num = 1001
            else:
                last_id_num = int(st.session_state.df['ID'].str.replace('UPDATE-', '').max())
                new_id_num = last_id_num + 1
            new_update_id = f"UPDATE-{new_id_num}"
            
            df_new = pd.DataFrame([{
                "ID": new_update_id,
                "Category": final_category,
                "Update": update_description,
                "Status": "Not Started",
                "Priority": priority,
                "Date Logged": pd.to_datetime(datetime.date.today()),
            }])

            st.session_state.df = pd.concat([df_new, st.session_state.df], ignore_index=True)
            st.success("Update logged successfully!")
        elif submitted:
            st.warning("Please provide an update description before submitting.")

def display_existing_updates():
    """Displays the existing updates in an editable data editor."""
    st.header("Activity Log")
    st.write(f"Total Updates: `{len(st.session_state.df)}`")

    if st.session_state.df.empty:
        st.info("No updates have been logged yet. Use the form above to add your first update.")
        return

    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", help="Task status", options=["Not Started", "In Progress", "Completed", "On Hold"], required=True
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority", help="Priority", options=["High", "Medium", "Low"], required=True
            ),
            "Date Logged": st.column_config.DateColumn("Date Logged", format="YYYY-MM-DD"),
            "Update": st.column_config.TextColumn("Update")
        },
        disabled=["ID", "Category", "Date Logged"],
    )
    # Update the session state with the edited data
    if edited_df is not None:
        st.session_state.df = edited_df


def display_statistics(df: pd.DataFrame):
    """Displays statistics and charts based on the update data."""
    st.header("Dashboard")
    
    if df.empty:
        st.info("The dashboard will populate with charts and metrics once you log an update.")
        return

    # Metrics
    num_completed = len(df[df["Status"] == "Completed"])
    num_in_progress = len(df[df["Status"] == "In Progress"])
    num_not_started = len(df[df["Status"] == "Not Started"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Completed", num_completed)
    col2.metric("In Progress", num_in_progress)
    col3.metric("Not Started", num_not_started)

    st.divider()

    # Charts
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("##### Updates by Category")
        category_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Category:N", sort='-y', title="Category"),
            y=alt.Y("count():Q", title="Number of Updates"),
            color=alt.Color("Category:N", legend=None)
        ).properties(height=350)
        st.altair_chart(category_chart, use_container_width=True, theme="streamlit")
        
    with col2:
        st.write("##### Status Distribution")
        status_chart = alt.Chart(df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Status", aggregate="count"),
            color=alt.Color(field="Status", type="nominal", scale=alt.Scale(
                domain=['Completed', 'In Progress', 'Not Started', 'On Hold'],
                range=['#2E8B57', '#FFA500', '#FF4B4B', '#808080']
            )),
        ).properties(height=350).configure_legend(orient="bottom", titlePadding=5)
        st.altair_chart(status_chart, use_container_width=True, theme="streamlit")

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Business Operations Tracker", page_icon="📈", layout="wide")

    initialize_state()
    display_header()
    display_add_update_form()
    display_existing_updates()
    display_statistics(st.session_state.df)

if __name__ == '__main__':
    main()