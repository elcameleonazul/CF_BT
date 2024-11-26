import streamlit as st
import pandas as pd
import os
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
from streamlit_extras.let_it_rain import rain

# Fonction pour charger toutes les startlists
def load_startlists(directory):
    startlists = {}
    for file in os.listdir(directory):
        if file.endswith(".pkl"):
            course_name = os.path.splitext(file)[0]  # Nom de la course (sans extension)
            startlists[course_name] = pd.read_pickle(os.path.join(directory, file))
    return startlists

# Charger les données
startlist_dir = "./Race/"
startlists = load_startlists(startlist_dir)

col1, col2,col3 = st.columns(3)

# Sélectionner une course
st.title("Cycling Fantasy : Make the best team 🪄 📊")
st.text("")
st.text("")
st.text("")
with col2 :

    st.image("./A2L_photo.jpg")
    st.text("Make with ♥️ by De Lie Bulls")

st.text("")
st.text("")
selected_course = st.selectbox("Select a race :", list(startlists.keys()))

# Afficher la startlist de la course sélectionnée
startlist = startlists[selected_course]
st.write(f"Startlist for {selected_course} :")
st.dataframe(startlist,hide_index=True)

# Gestion des sélections
st.write("**Make your pronostic for the top20 :**")
selected_riders = []
for i in range(1, 21):
    available_riders = startlist[~startlist["Rider"].isin(selected_riders)]["Rider"]
    rider = st.selectbox(f"Position {i} :", available_riders, key=f"pos_{i}")
    if rider:
        selected_riders.append(rider)
copmlete=st.checkbox("Selection completed !")
if copmlete :
    def rain_emoji() :
        rain(
            emoji='🐂',
            font_size=30,
            falling_speed=7,
            animation_length=3
        )
    # Afficher les pronostics
    if len(selected_riders) == 20:
        rain_emoji()

    selected_df= startlist
    for i,rider in enumerate(selected_riders) :
        selected_df.loc[selected_df['Rider']==rider,'Rank']=i
    selected_df=selected_df.sort_values(by='Rank')
    selected_df=selected_df.drop(columns='Rank').reset_index(drop=True)



    def PL(selected_df):
        points_grille = [60, 35, 30, 26, 23, 20, 18, 16, 14, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        points_grille = points_grille + [0] * (len(selected_df) - len(points_grille))
        
        # Convertir les colonnes nécessaires en numérique
        selected_df['Price'] = pd.to_numeric(selected_df['Price'], errors='coerce')
        
        # Création du problème de maximisation
        prob = LpProblem("Meilleure_Equipe", LpMaximize)
        
        # Variables de décision
        x = LpVariable.dicts("Coureur", selected_df['Rider'], cat='Binary')
        
        # Fonction objectif : maximiser les points
        prob += lpSum([x[coureur] * points_grille[i] for i, coureur in enumerate(selected_df['Rider']) if i < len(points_grille)])
        
        # Contraintes
        # 1. Prix total doit être inférieur ou égal à 5000
        prob += lpSum([x[coureur] * selected_df['Price'].iloc[i] for i, coureur in enumerate(selected_df['Rider'])]) <= 5000
        
        # 2. Nombre total de coureurs doit être égal à 9
        prob += lpSum([x[coureur] for coureur in selected_df['Rider']]) == 9
        
        # Résolution du problème
        prob.solve()
        list_selected=[v.name for v in prob.variables() if v.varValue == 1]
        list_selected=[nom.replace('Coureur_', '').replace('_', ' ') for nom in list_selected]
        selected_coureurs_df = selected_df[selected_df['Rider'].isin(list_selected)]
        result = []
        for pos in list(selected_coureurs_df.index):
            if pos < len(points_grille):
                result.append(points_grille[pos])
        
        # Calcul des totaux
        total_price = selected_coureurs_df['Price'].sum()
        total_points = sum(result)


        return selected_coureurs_df, total_price, total_points

    df, total_price, total_points = PL(selected_df)

    st.header("Your best team 🏆")
    st.dataframe(df, hide_index=True)
    st.text(f"total price : {total_price}")
    st.text(f"total points : {total_points}")
st.text("")
st.text('')
st.image("./CF.jpg")
st.text("All data from https://cyclingfantasy.cc/ 🙇‍♂️")