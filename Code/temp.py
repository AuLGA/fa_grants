import pandas as pd
import openpyxl as pxl
import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

per_capita_minimum = 0.3
per_capita_minimum_base = 0.3

pop_30_jun = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Population", skiprows=9, nrows=7)

pop_30_jun.set_index("Population by state, at 30 June (million)", inplace=True)

pop_30_jun = pop_30_jun * 1e6

budget_grants = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name = "Grants")

budget_grants.bfill(inplace=True)

budget_grants.set_index("Financial Assistance Grant program (million)", inplace=True)

budget_grants = budget_grants.loc[["2025-26", "2026-27", "2027-28", "2028-29"]]

budget_grants = budget_grants * 1e6

qld_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Queensland")

qld_grants_base["ERP_2025"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2025] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2025"] = qld_grants_base["ERP_2025"].round(0)

qld_grants_base["ERP_2026"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2026] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2026"] = qld_grants_base["ERP_2026"].round(0)

qld_grants_base["ERP_2027"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2027] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2027"] = qld_grants_base["ERP_2027"].round(0)

qld_grants_base["ERP_2028"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2028] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2028"] = qld_grants_base["ERP_2028"].round(0)

queensland_master_sim = pd.DataFrame()

#for i in range(1000):
qld_grants = qld_grants_base.copy()

i = 0

qld_grants["UID"] = qld_grants["LGA"].str.replace(" ", "").replace("-", "") + str(i+1)

#for year in range(2025, 2029):
year = 2025

prev_year = year - 1

min_per_capita_grant = budget_grants["QLD"][f"{year}-{(year+1)%1000}"] / qld_grants[f"ERP_{year}"].sum() * per_capita_minimum

min_grant = qld_grants[f"ERP_{year}"] * min_per_capita_grant

min_per_capita_grant_base = budget_grants["QLD"][f"{year}-{(year+1)%1000}"] / qld_grants[f"ERP_{year}"].sum() * per_capita_minimum_base

min_grant_base = qld_grants[f"ERP_{year}"] * min_per_capita_grant_base

non_min = qld_grants[f"ERP_{year}"] <= 80000

qld_grants[f"Scaled Gap_{year}"] = (qld_grants[f"Scaled Gap_{year-1}"] * np.random.normal(1, 0.1, size=qld_grants.shape[0])) * non_min
qld_grants[f"Scaled Gap_{year}"] = qld_grants[f"Scaled Gap_{year}"]/qld_grants[f"Scaled Gap_{year}"].sum()

# New case

raw_alloc = qld_grants[f"Scaled Gap_{year}"] * (budget_grants["QLD"][f"{year}-{(year+1)%1000}"] - min_grant.sum())

qld_grants[f"Grant_{year}"] = min_grant + raw_alloc

# Base case

raw_alloc = qld_grants[f"Scaled Gap_{year}"] * (budget_grants["QLD"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())

qld_grants[f"Grant_base_{year}"] = min_grant_base + raw_alloc

    
    #queensland_master_sim = pd.concat([queensland_master_sim, qld_grants])

#queensland_master_sim.to_csv("../Data/Output/south_australia.csv")