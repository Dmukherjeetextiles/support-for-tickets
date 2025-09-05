# 📈 Business Operations Tracker

A professional and versatile Streamlit app to create, manage, and visualize real-time updates for various business operations. This tool is designed to be a central hub for tracking progress across different departments and projects.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://support-tickets-template.streamlit.app/)

![Screenshot of the Business Operations Tracker](https://storage.googleapis.com/static.streamlit.io/screenshots/support-tickets-template.png)

## ✨ Features

- **Starts Clean**: The app boots up with a blank slate, ready for your data.
- **Log Updates**: A simple form to submit new updates with a description, category, and priority level.
- **Custom Categories**: In addition to predefined categories, you can add your own custom ones.
- **Interactive Dashboard**: An interactive table displays all existing updates. You can edit the status and priority directly in the table.
- **Dynamic Statistics**: Key metrics and charts that populate in real-time as you log and edit data.
- **Data Persistence**: Utilizes Streamlit's session state to persist data across app reruns.

## 🗂️ Categories include

- Lead Contacted
- Client Payment Received
- Client Feedback
- Software/App Update
- Digital Marketing Update
- And many more, plus custom entries!

## 🚀 How to run it on your own machine

1.  **Prerequisites**
    - Python 3.8+
    - An environment manager like `venv` or `conda`.

2.  **Clone the repository**
    ```bash
    git clone https://github.com/Dmukherjeetextiles/support-for-tickets.git
    cd support-for-tickets
    ```

3.  **Set up a virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

4.  **Install the requirements**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the app**
    ```bash
    streamlit run streamlit_app.py
    ```

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or new features, feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.