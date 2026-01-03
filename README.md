# Cricsheet_Data_Analysis

## Problem Statement

The goal of this project is to extract, transform, and analyze structured cricket match data from Cricsheet across different formats—Test, ODI, T20, and IPL. The raw data is available in JSON format and needs to be converted into structured tabular data for efficient storage, analysis, and visualization. This project focuses on building a data pipeline that converts JSON files into SQL tables, performs performance analysis using SQL queries, and visualizes insights through Power BI and a Streamlit web app.

---

## Project Objectives

Download and parse cricket match data in JSON format from Cricsheet.
- Transform the raw JSON files into structured Pandas DataFrames.
- Store the processed data in a MySQL relational database using SQLAlchemy and PyMySQL.
- Design and create separate tables for each match format (Test, ODI, T20, IPL).
- Write and execute 20+ SQL queries to derive key insights on player and team performance.
- Build an interactive Power BI dashboard to visualize match statistics and trends.
- Develop a Streamlit web application to dynamically display SQL query insights and metrics.

---

## Technologies Used

- Data Source         : Cricsheet (JSON Format)
- Programming Language: Python
- Data Processing     : Pandas, JSON
- Database            : MySQL, PyMySQL, SQLAlchemy
- Data Visualization  : Power BI
- Web Application     : Streamlit
- Development Tools   : VS Code, Jupyter Notebook

---

## Streamlit Dashboard Screenshots

![screenshot1](screenshots/streamlit_ss1.png)

![screenshot2](screenshots/streamlit_ss2.png)

---

## Power BI Dashboard

- [Click here to view the Power Bi Dashboard](https://app.powerbi.com/view?r=eyJrIjoiOGZmYzdjMjYtYWIyNi00M2MxLWE4OTgtODA1ODNjNzRiNzllIiwidCI6ImNiNmMxMjcwLWVjNmItNDI1Mi1iNzcwLWFkMDQ1NDQxOTgzZCJ9)

### Power BI Dashboard Screenshots

| HOME | IPL | ODI |
|--------|--------|--------|
| <img src="screenshots/Powerbi_home.png" width="300"/> | <img src="screenshots/Powerbi_ipl.png" width="300"/> | <img src="screenshots/Powerbi_odi.png" width="300"/> |

| T20 | TEST |
|--------|--------|
| <img src="screenshots/Powerbi_t20.png" width="300"/> | <img src="screenshots/Powerbi_test.png" width="300"/> |

---
