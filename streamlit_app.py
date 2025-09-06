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

def display_csv_uploader():
    """Displays a file uploader to load data from a CSV file with duplicate checking."""
    with st.expander("Upload or Merge Data from CSV"):
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV with columns: ID, Category, Update, Status, Priority, Date Logged (YYYY-MM-DD)"
        )
        if uploaded_file is not None:
            try:
                # Read and validate the uploaded CSV
                uploaded_df = pd.read_csv(uploaded_file)
                
                expected_columns = {
                    "ID": str, "Category": str, "Update": str,
                    "Status": str, "Priority": str, "Date Logged": "datetime64[ns]"
                }
                
                if not all(col in uploaded_df.columns for col in expected_columns):
                    st.error("The uploaded CSV is missing one or more required columns. "
                             "Please ensure it has: ID, Category, Update, Status, Priority, Date Logged.")
                    return
                
                # Enforce correct data types
                uploaded_df = uploaded_df.astype({k: v for k, v in expected_columns.items() if k != "Date Logged"})
                uploaded_df["Date Logged"] = pd.to_datetime(uploaded_df["Date Logged"])

                # --- Conditional Import Logic ---
                if st.session_state.df.empty:
                    # Case 1: No existing data. Load the entire CSV.
                    st.session_state.df = uploaded_df
                    st.success(f"Successfully uploaded and loaded {len(uploaded_df)} updates from the CSV!")
                    st.rerun() # Rerun because state has changed
                else:
                    # Case 2: Existing data is present. Check for duplicates based on 'ID'.
                    existing_ids = st.session_state.df['ID'].tolist()
                    
                    # Filter for new tickets (IDs not in the existing dataframe)
                    new_tickets_df = uploaded_df[~uploaded_df['ID'].isin(existing_ids)]
                    num_new = len(new_tickets_df)
                    num_duplicates = len(uploaded_df) - num_new

                    # Append only the new, non-duplicate tickets
                    if num_new > 0:
                        st.session_state.df = pd.concat([st.session_state.df, new_tickets_df], ignore_index=True)
                        st.success(f"Successfully imported {num_new} new updates.")
                        st.rerun() # Rerun because state has changed
                    
                   
            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")


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
            if st.session_state.df.empty or st.session_state.df['ID'].str.replace('UPDATE-', '').str.isnumeric().sum() == 0:
                 new_id_num = 1001
            else:
                 # Filter out non-numeric IDs before finding the max
                 numeric_ids = pd.to_numeric(st.session_state.df['ID'].str.replace('UPDATE-', ''), errors='coerce').dropna()
                 if numeric_ids.empty:
                     new_id_num = 1001
                 else:
                     last_id_num = int(numeric_ids.max())
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

    # Make a copy of the dataframe for editing
    df_to_edit = st.session_state.df.copy()
    df_to_edit['Date Logged'] = pd.to_datetime(df_to_edit['Date Logged'])

    edited_df = st.data_editor(
        df_to_edit,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", help="Task status", options=["Not Started", "In Progress", "Completed", "On Hold"], required=True
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority", help="Priority", options=["High", "Medium", "Low"], required=True
            ),
            "Date Logged": st.column_config.DateColumn("Date Logged", format="YYYY-MM-DD", disabled=True),
            "Update": st.column_config.TextColumn("Update"),
            "ID": st.column_config.TextColumn("ID", disabled=True),
            "Category": st.column_config.TextColumn("Category", disabled=True),
        },
    )
    
    # Check if the user has made any changes in the data editor.
    # This prevents the editor's old state from overwriting the new CSV data.
    if not st.session_state.df.equals(edited_df):
        # If there are changes, update the session state and rerun the app to reflect them.
        st.session_state.df = edited_df
        st.rerun()


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
            theta=alt.Theta(field="Status", type="nominal", aggregate="count"),
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
    display_csv_uploader()
    display_add_update_form()
    display_existing_updates()
    display_statistics(st.session_state.df)

if __name__ == '__main__':
    main()