import pandas as pd
from catboost import CatBoostRegressor, cv, Pool
from sklearn.metrics import root_mean_squared_error, make_scorer, mean_absolute_percentage_error
from sklearn.feature_selection import r_regression
from sklearn.model_selection import cross_validate, GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.linear_model import LinearRegression, ElasticNet, Lasso, Ridge
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures, OrdinalEncoder, OneHotEncoder, StandardScaler, RobustScaler
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
import pickle
import numpy as np

def train_model():

    df_1 = pd.read_json('app/DATASET_FINAL.json')

    df = df_1.copy()


    # Groupement des acteurs 1, 2, 3 , scénaristes, réalisateurs, et distributeurs qui font plus de 500k entrées 
    # + ajout d'un groupe "mid" entre 250k et 500k

    # Acteur 1
    df_actor_1 = df.groupby('actor_1')['weekly_entrances'].mean().reset_index()
    df_actor_1_mid = df_actor_1[(df_actor_1['weekly_entrances'] < 500001) & (df_actor_1['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_1 = df_actor_1[df_actor_1['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Acteur 2
    df_actor_2 = df.groupby('actor_2')['weekly_entrances'].mean().reset_index()
    df_actor_2_mid = df_actor_2[(df_actor_2['weekly_entrances'] < 500001) & (df_actor_2['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_2 = df_actor_2[df_actor_2['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Acteur 3
    df_actor_3 = df.groupby('actor_3')['weekly_entrances'].mean().reset_index()
    df_actor_3_mid = df_actor_3[(df_actor_3['weekly_entrances'] < 500001) & (df_actor_3['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_actor_3 = df_actor_3[df_actor_3['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Réalisateurs
    df_directors = df.groupby('directors')['weekly_entrances'].mean().reset_index()
    df_directors_mid = df_directors[(df_directors['weekly_entrances'] < 500001) & (df_directors['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_directors = df_directors[df_directors['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Scénaristes
    df_writer = df.groupby('writer')['weekly_entrances'].mean().reset_index()
    df_writer_mid = df_writer[(df_writer['weekly_entrances'] < 500001) & (df_writer['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_writer = df_writer[df_writer['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)

    # Distributeurs
    df_distribution = df.groupby('distribution')['weekly_entrances'].mean().reset_index()
    df_distribution_mid = df_distribution[(df_distribution['weekly_entrances'] < 500001) & (df_distribution['weekly_entrances'] > 250000)].sort_values(by='weekly_entrances', ascending=False)
    df_distribution = df_distribution[df_distribution['weekly_entrances'] > 500000].sort_values(by='weekly_entrances', ascending=False)


    # Création des colonnes "top" et "top_mid" pour les différents groupes

    df['top_actor_1'] = df['actor_1'].apply(lambda x: 1 if x in df_actor_1['actor_1'].to_list() else 0)
    df['top_actor_1_mid'] = df['actor_1'].apply(lambda x: 1 if x in df_actor_1_mid['actor_1'].to_list() else 0)

    df['top_actor_2'] = df['actor_2'].apply(lambda x: 1 if x in df_actor_2['actor_2'].to_list() else 0)
    df['top_actor_2_mid'] = df['actor_2'].apply(lambda x: 1 if x in df_actor_2_mid['actor_2'].to_list() else 0)

    df['top_actor_3'] = df['actor_3'].apply(lambda x: 1 if x in df_actor_3['actor_3'].to_list() else 0)
    df['top_actor_3_mid'] = df['actor_3'].apply(lambda x: 1 if x in df_actor_3_mid['actor_3'].to_list() else 0)

    df['top_director'] = df['directors'].apply(lambda x: 1 if x in df_directors['directors'].to_list() else 0)
    df['top_director_mid'] = df['directors'].apply(lambda x: 1 if x in df_directors_mid['directors'].to_list() else 0)

    df['top_writer'] = df['writer'].apply(lambda x: 1 if x in df_writer['writer'].to_list() else 0)
    df['top_writer_mid'] = df['writer'].apply(lambda x: 1 if x in df_writer_mid['writer'].to_list() else 0)

    df['top_distribution'] = df['distribution'].apply(lambda x: 1 if x in df_distribution['distribution'].to_list() else 0)
    df['top_distribution_mid'] = df['distribution'].apply(lambda x: 1 if x in df_distribution_mid['distribution'].to_list() else 0)


    df['top_pays'] = df.country.apply(lambda x : 1 if x in (['France','Etats-Unis','Grande-Bretagne']) else 0)

    df['released_date'] = pd.to_datetime(
        df['released_date'],
        format="%d/%m/%Y",
        errors='coerce'  # Optionnel : mettra NaT si une date est mal formée
    )

    df["summer"] = df["released_date"].apply(lambda x: 1 if ((x.month == 6 and x.day >= 21) or x.month in [7, 8] or (x.month == 9 and x.day < 22)) else 0)
    df["automn"] = df["released_date"].apply(lambda x: 1 if ((x.month == 9 and x.day >= 22) or x.month in [10, 11] or (x.month == 12 and x.day < 21)) else 0)
    df["winter"] = df["released_date"].apply(lambda x: 1 if ((x.month == 12 and x.day >= 21) or x.month in [1, 2] or (x.month == 3 and x.day < 20)) else 0)
    df["spring"] = df["released_date"].apply(lambda x: 1 if ((x.month == 3 and x.day >= 21) or x.month in [4, 5] or (x.month == 6 and x.day < 21)) else 0)

    df["is_covid"] = df["released_date"].apply(lambda x: 1 if (
        (x >= pd.to_datetime("2020-03-17") and x <= pd.to_datetime("2020-05-11")) or
        (x >= pd.to_datetime("2020-10-30") and x <= pd.to_datetime("2020-12-15")) or
        (x >= pd.to_datetime("2021-04-03") and x <= pd.to_datetime("2021-05-03"))
    ) else 0)
    df["post_streaming"] = df["released_date"].apply(lambda x: 1 if x >= pd.to_datetime("2014-09-15") else 0)

    df["summer_holidays"] = df["released_date"].apply(lambda x: 1 if x.month >= 7 or (x.month <= 9 and x.day < 10) else 0)

    df["christmas_period"] = df["released_date"].apply(lambda x: 1 if (x.month == 12 and x.day >= 20) or (x.month == 1 and x.day <= 5) else 0)

    df["is_award_season"] = df["released_date"].apply(lambda x: 1 if (x.month == 2 or (x.month == 3 and x.day <= 10)) else 0)


    features_of_interest = [
        'released_year',
        "country",
        'category',
        'classification',
        'duration_minutes', 
        "top_actor_1",
        "top_actor_2",
        "top_actor_3",
        "top_director",
        'top_writer',
        'top_distribution',
        "top_actor_1_mid",
        "top_actor_2_mid",
        "top_actor_3_mid",
        "top_director_mid",
        'top_writer_mid',
        'top_distribution_mid',
        'top_pays',
        'post_streaming',
        'summer_holidays',
        'christmas_period',
        'is_award_season',
    ]


    numerical_column = [
        'released_year',
        "duration_minutes",
    ]


    ordinal_column = [
        "top_actor_1",
        "top_actor_2",
        "top_actor_3",
        "top_director",
        'top_writer',
        "top_actor_1_mid",
        "top_actor_2_mid",
        "top_actor_3_mid",
        "top_director_mid",
        'top_writer_mid',
        'top_distribution_mid',
        'top_distribution',
        'top_pays',

        'post_streaming',
        'summer_holidays',
        'christmas_period',
        'is_award_season',
    ]

    categorical_column = [

        "country",
        'category',
        'classification',

    ]

    #
    target_name = "weekly_entrances"
    data, target, numerical_data,categorical_data = (
        df[features_of_interest],
        df[target_name],
        df[numerical_column],
        df[categorical_column]
    )

    X_train, X_test, y_train, y_test = train_test_split(data, target, shuffle=True, train_size=0.9, random_state=42, stratify = df['top_pays'])

    sample_weights = np.ones(len(y_train))
    success_mask = y_train > 200000
    sample_weights[success_mask] = 2

    preprocessor = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown='ignore'), categorical_column),
        ("numeric", RobustScaler(), numerical_column),
        ("ordinal", OrdinalEncoder(), ordinal_column)
        ],
        remainder="passthrough",
    )

    # catboost_model = make_pipeline(preprocessor,CatBoostRegressor(depth=4,iterations=300,l2_leaf_reg=1,learning_rate=0.07))
    catboost_model = make_pipeline(preprocessor,CatBoostRegressor())
    # catboost_model.fit(X_train,y_train)
    catboost_model.fit(X_train,y_train, catboostregressor__sample_weight=sample_weights)

    # Prédictions sur le test
    y_pred = catboost_model.predict(X_test)

    # Calcul des métriques
    rmse = root_mean_squared_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    errors = y_pred - y_test
    sum_errors = np.sum(errors)
    mean_errors = np.mean(errors)

    with open('app/model_new.pkl', 'wb') as f:
        pickle.dump(catboost_model,f)
    return rmse

if __name__ == "__main__" :
    train_model()

    
