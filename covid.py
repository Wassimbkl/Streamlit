import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(file):
    try:
        df = pd.read_csv(file, sep=";")  # Ajout du séparateur correct
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

    df.columns = df.columns.str.strip()

    required_columns = ["province", "country", "latitude", "longitude", "date", "confirmed", "deaths", "recovered"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.warning(f"⚠️ Colonnes manquantes dans {file} : {missing_columns}")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce')

    return df

# Chargement des données
file = "covid_data_global.csv"
df = load_data(file)

if df is not None:
    st.title("Tableau de bord COVID-19")

    case_type = st.selectbox("Sélectionnez le type de données", ["Cas Confirmés", "Décès", "Guérisons"])

    case_column_map = {
        "Cas Confirmés": "confirmed",
        "Décès": "deaths",
        "Guérisons": "recovered"
    }

    if "country" in df.columns:
        countries = df["country"].dropna().unique()
        selected_countries = st.multiselect("Choisissez un ou plusieurs pays", countries)

       

        country_data = df[df["country"].isin(selected_countries)]
        
        if country_data.empty:
            st.warning("")
        elif "date" in df.columns:
            country_data["Month"] = country_data["date"].dt.to_period("M")
            monthly_data = country_data.groupby(["Month", "country"])[case_column_map[case_type]].sum().reset_index()
            monthly_data["Month"] = monthly_data["Month"].astype(str)

            st.write("📊 Aperçu des données traitées :", monthly_data.head())

            fig = px.line(
                monthly_data, 
                x="Month", 
                y=case_column_map[case_type], 
                color="country",
                title=f"{case_type} - Comparaison entre pays", 
                markers=True
            )
            st.plotly_chart(fig)
        else:
            st.error("❌ La colonne 'date' est absente, impossible de générer le graphique.")
    else:
        st.error("❌ La colonne 'country' est absente, impossible d'afficher les données par pays.")
