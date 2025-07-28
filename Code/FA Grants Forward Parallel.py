import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

from time import time

from multiprocessing import Pool

time_init = time()

# ## Controls and constants

per_capita_minimum = 0.2
per_capita_minimum_base = 0.3

pop_30_jun = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Population", skiprows=9, nrows=7)
pop_30_jun.set_index("Population by state, at 30 June (million)", inplace=True)
pop_30_jun = pop_30_jun * 1e6

budget_grants = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name = "Grants")
budget_grants.bfill(inplace=True)
budget_grants.set_index("Financial Assistance Grant program (million)", inplace=True)
budget_grants = budget_grants.loc[["2025-26", "2026-27", "2027-28", "2028-29"]]
budget_grants = budget_grants * 1e6

# ## New South Wales ✅

# Absense of reliable documentation means that we use the same approach as used in Queensland's modelling.

nsw_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="New South Wales")
nsw_grants_base["ERP_2025"] = nsw_grants_base["ERP_2024"] * pop_30_jun["NSW"][2025] / nsw_grants_base["ERP_2024"].sum()
nsw_grants_base["ERP_2025"] = nsw_grants_base["ERP_2025"].round(0)
nsw_grants_base["ERP_2026"] = nsw_grants_base["ERP_2024"] * pop_30_jun["NSW"][2026] / nsw_grants_base["ERP_2024"].sum()
nsw_grants_base["ERP_2026"] = nsw_grants_base["ERP_2026"].round(0)
nsw_grants_base["ERP_2027"] = nsw_grants_base["ERP_2024"] * pop_30_jun["NSW"][2027] / nsw_grants_base["ERP_2024"].sum()
nsw_grants_base["ERP_2027"] = nsw_grants_base["ERP_2027"].round(0)
nsw_grants_base["ERP_2028"] = nsw_grants_base["ERP_2024"] * pop_30_jun["NSW"][2028] / nsw_grants_base["ERP_2024"].sum()
nsw_grants_base["ERP_2028"] = nsw_grants_base["ERP_2028"].round(0)

def run_nsw(i):
    nsw_grants = nsw_grants_base.copy()
    nsw_grants["UID"] = nsw_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["NSW"][f"{year}-{(year+1)%1000}"] / nsw_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = nsw_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["NSW"][f"{year}-{(year+1)%1000}"] / nsw_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = nsw_grants[f"ERP_{year}"] * min_per_capita_grant_base
        #non_min = nsw_grants[f"Scaled Gap_{year-1}"].round(4) == 0.0
        nsw_grants[f"Scaled Gap_{year}"] = (nsw_grants[f"Scaled Gap_{year-1}"] * np.random.normal(1, 0.1, size=nsw_grants.shape[0]))# * non_min
        nsw_grants[f"Scaled Gap_{year}"] = nsw_grants[f"Scaled Gap_{year}"]/nsw_grants[f"Scaled Gap_{year}"].sum()
        # New case
        raw_alloc = nsw_grants[f"Scaled Gap_{year}"] * (budget_grants["NSW"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        nsw_grants[f"Grant_{year}"] = min_grant + raw_alloc
        # Base case
        raw_alloc = nsw_grants[f"Scaled Gap_{year}"] * (budget_grants["NSW"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        nsw_grants[f"Grant_base_{year}"] = min_grant_base + raw_alloc
    
    return nsw_grants

# ## Victoria ✅

# Victoria OLG has a cap/collar of [2%, 10%] for non minimum grant councils.

def correct_delta_vic(sub_vic, year, base = False):
    total_funding_gap =  (sub_vic[f"Funding Gap_{year}"] * sub_vic["deficit"]).sum()
    total_funding = sub_vic["alloc"].sum()
    comparison_column = "Grant_base_" if base else "Grant_"
    
    while np.any((sub_vic["delta"].round(2)<2)|(sub_vic["delta"].round(2)>10)):
        sub_vic["g"] = sub_vic["delta"].apply(lambda x: (x - 2)/100 if x < 2 else ((x - 10)/100 if x > 10 else 0))
        sub_vic["alloc"] -= sub_vic["g"] * sub_vic[f"{comparison_column}{year-1}"]
        remainder = total_funding - sub_vic["alloc"].sum()
        sub_vic["alloc"] += sub_vic[f"Funding Gap_{year}"] * remainder / total_funding_gap
        sub_vic["delta"] = (sub_vic["alloc"] - sub_vic[f"{comparison_column}{year-1}"]) / sub_vic[f"{comparison_column}{year-1}"] * 100
    return sub_vic

vic_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Victoria")
vic_grants_base["ERP_2025"] = vic_grants_base["ERP_2024"] * pop_30_jun["VIC"][2025] / vic_grants_base["ERP_2024"].sum()
vic_grants_base["ERP_2025"] = vic_grants_base["ERP_2025"].round(0)
vic_grants_base["ERP_2026"] = vic_grants_base["ERP_2024"] * pop_30_jun["VIC"][2026] / vic_grants_base["ERP_2024"].sum()
vic_grants_base["ERP_2026"] = vic_grants_base["ERP_2026"].round(0)
vic_grants_base["ERP_2027"] = vic_grants_base["ERP_2024"] * pop_30_jun["VIC"][2027] / vic_grants_base["ERP_2024"].sum()
vic_grants_base["ERP_2027"] = vic_grants_base["ERP_2027"].round(0)
vic_grants_base["ERP_2028"] = vic_grants_base["ERP_2024"] * pop_30_jun["VIC"][2028] / vic_grants_base["ERP_2024"].sum()
vic_grants_base["ERP_2028"] = vic_grants_base["ERP_2028"].round(0)
vic_grants_base["Grant_base_2024"] = vic_grants_base["Grant_2024"]

def run_vic(i):
    vic_grants = vic_grants_base.copy()
    vic_grants["UID"] = vic_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["VIC"][f"{year}-{(year+1)%1000}"] / vic_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = vic_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["VIC"][f"{year}-{(year+1)%1000}"] / vic_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = vic_grants[f"ERP_{year}"] * min_per_capita_grant_base
        vic_grants[f"Funding Gap_{year}"] = vic_grants[f"Funding Gap_{year-1}"] * np.random.normal(1, 0.1, size=vic_grants.shape[0])
        vic_grants["deficit"] = vic_grants[f"Funding Gap_{year}"] > 0
        total_deficit = (vic_grants[f"Funding Gap_{year}"] * vic_grants["deficit"]).sum()
        # New case
        raw_alloc = (vic_grants[f"Funding Gap_{year}"] * vic_grants["deficit"] / total_deficit) * (budget_grants["VIC"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        vic_grants["alloc"] = min_grant + raw_alloc
        vic_grants["delta"] = (vic_grants["alloc"] - vic_grants[f"Grant_{year-1}"]) / vic_grants[f"Grant_{year-1}"] * 100
        non_min_vic = vic_grants[vic_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        vic_grants.combine_first(correct_delta_vic(non_min_vic, year))
        vic_grants[f"Grant_{year}"] = vic_grants["alloc"]

        # Base case
        raw_alloc = (vic_grants[f"Funding Gap_{year}"] * vic_grants["deficit"] / total_deficit) * (budget_grants["VIC"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        vic_grants["alloc"] = min_grant_base + raw_alloc
        vic_grants["delta"] = (vic_grants["alloc"] - vic_grants[f"Grant_base_{year-1}"]) / vic_grants[f"Grant_base_{year-1}"] * 100
        non_min_vic = vic_grants[vic_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        vic_grants.combine_first(correct_delta_vic(non_min_vic, year, base=True))
        vic_grants[f"Grant_base_{year}"] = vic_grants["alloc"]
    
    return vic_grants

# ## Queensland ✅

# Queensland does not release their "Funding Gap" variable. Hence, an analogue is reverse engineered from the gap between grant entitlement and minimum grant. Adjustments and normalizations applied to this should, in principle, give fairly robust numbers, especially at the high level. 
# 
# There's no cap/collar and minimum grant eligibility is based on population > 80,000.

qld_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Queensland")
qld_grants_base["ERP_2025"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2025] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2025"] = qld_grants_base["ERP_2025"].round(0)
qld_grants_base["ERP_2026"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2026] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2026"] = qld_grants_base["ERP_2026"].round(0)
qld_grants_base["ERP_2027"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2027] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2027"] = qld_grants_base["ERP_2027"].round(0)
qld_grants_base["ERP_2028"] = qld_grants_base["ERP_2024"] * pop_30_jun["QLD"][2028] / qld_grants_base["ERP_2024"].sum()
qld_grants_base["ERP_2028"] = qld_grants_base["ERP_2028"].round(0)

def run_qld(i):
    qld_grants = qld_grants_base.copy()
    qld_grants["UID"] = qld_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
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
    return qld_grants

# ## South Australia ✅

# South Australia OLG has a cap/collar of [-15%, 30%] for councils.

def correct_delta_sa(sub_sa, year, base = False):
    total_funding_gap =  (sub_sa[f"Funding Gap_{year}"] * sub_sa["deficit"]).sum()
    total_funding = sub_sa["alloc"].sum()
    comparison_column = "Grant_base_" if base else "Grant_"
    
    while np.any((sub_sa["delta"].round(2)<-15)|(sub_sa["delta"].round(2)>30)):
        sub_sa["g"] = sub_sa["delta"].apply(lambda x: (x - (-15))/100 if x < -15 else ((x - 30)/100 if x > 30 else 0))
        sub_sa["alloc"] -= sub_sa["g"] * sub_sa[f"{comparison_column}{year-1}"]
        remainder = total_funding - sub_sa["alloc"].sum()
        sub_sa["alloc"] += sub_sa[f"Funding Gap_{year}"] * remainder / total_funding_gap
        sub_sa["delta"] = (sub_sa["alloc"] - sub_sa[f"{comparison_column}{year-1}"]) / sub_sa[f"{comparison_column}{year-1}"] * 100
    return sub_sa

sa_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="South Australia")
sa_grants_base["ERP_2025"] = sa_grants_base["ERP_2024"] * pop_30_jun["SA"][2025] / sa_grants_base["ERP_2024"].sum()
sa_grants_base["ERP_2025"] = sa_grants_base["ERP_2025"].round(0)
sa_grants_base["ERP_2026"] = sa_grants_base["ERP_2024"] * pop_30_jun["SA"][2026] / sa_grants_base["ERP_2024"].sum()
sa_grants_base["ERP_2026"] = sa_grants_base["ERP_2026"].round(0)
sa_grants_base["ERP_2027"] = sa_grants_base["ERP_2024"] * pop_30_jun["SA"][2027] / sa_grants_base["ERP_2024"].sum()
sa_grants_base["ERP_2027"] = sa_grants_base["ERP_2027"].round(0)
sa_grants_base["ERP_2028"] = sa_grants_base["ERP_2024"] * pop_30_jun["SA"][2028] / sa_grants_base["ERP_2024"].sum()
sa_grants_base["ERP_2028"] = sa_grants_base["ERP_2028"].round(0)
sa_grants_base["Grant_base_2024"] = sa_grants_base["Grant_2024"]

def run_sa(i):
    sa_grants = sa_grants_base.copy()
    sa_grants["UID"] = sa_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["SA"][f"{year}-{(year+1)%1000}"] / sa_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = sa_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["SA"][f"{year}-{(year+1)%1000}"] / sa_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = sa_grants[f"ERP_{year}"] * min_per_capita_grant_base
        sa_grants[f"Funding Gap_{year}"] = sa_grants[f"Funding Gap_{year-1}"] * np.random.normal(1, 0.1, size=sa_grants.shape[0])
        sa_grants["deficit"] = sa_grants[f"Funding Gap_{year}"] > 0
        total_deficit = (sa_grants[f"Funding Gap_{year}"] * sa_grants["deficit"]).sum()
        # New case
        raw_alloc = (sa_grants[f"Funding Gap_{year}"] * sa_grants["deficit"] / total_deficit) * (budget_grants["SA"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        sa_grants["alloc"] = min_grant + raw_alloc
        sa_grants["delta"] = (sa_grants["alloc"] - sa_grants[f"Grant_{year-1}"]) / sa_grants[f"Grant_{year-1}"] * 100
        non_min_sa = sa_grants[sa_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        sa_grants.combine_first(correct_delta_sa(non_min_sa, year))
        sa_grants[f"Grant_{year}"] = sa_grants["alloc"]
        # Base case
        raw_alloc = (sa_grants[f"Funding Gap_{year}"] * sa_grants["deficit"] / total_deficit) * (budget_grants["SA"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        sa_grants["alloc"] = min_grant_base + raw_alloc
        sa_grants["delta"] = (sa_grants["alloc"] - sa_grants[f"Grant_base_{year-1}"]) / sa_grants[f"Grant_base_{year-1}"] * 100
        non_min_sa = sa_grants[sa_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        sa_grants.combine_first(correct_delta_sa(non_min_sa, year, base=True))
        sa_grants[f"Grant_base_{year}"] = sa_grants["alloc"]
    
    return sa_grants

# ## Western Australia ✅

# WA State Grants Commission has no ceiling on change, but claims to limit year on year decrease. No explicit floor is given, but the biggest 2023-24 to 2024-25 decrease was about -60%. So, that's the floor we'll use.

def correct_delta_wa(sub_wa, year, base = False):
    total_funding_gap =  (sub_wa[f"Funding Gap_{year}"] * sub_wa["deficit"]).sum()
    total_funding = sub_wa["alloc"].sum()
    comparison_column = "Grant_base_" if base else "Grant_"
    
    while np.any((sub_wa["delta"].round(2)<-60)):
        sub_wa["g"] = sub_wa["delta"].apply(lambda x: (x - (-60))/100 if x < -60 else 0)
        sub_wa["alloc"] -= sub_wa["g"] * sub_wa[f"{comparison_column}{year-1}"]
        remainder = total_funding - sub_wa["alloc"].sum()
        sub_wa["alloc"] += sub_wa[f"Funding Gap_{year}"] * remainder / total_funding_gap
        sub_wa["delta"] = (sub_wa["alloc"] - sub_wa[f"{comparison_column}{year-1}"]) / sub_wa[f"{comparison_column}{year-1}"] * 100
    return sub_wa

wa_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Western Australia")
wa_grants_base["ERP_2025"] = wa_grants_base["ERP_2024"] * pop_30_jun["WA"][2025] / wa_grants_base["ERP_2024"].sum()
wa_grants_base["ERP_2025"] = wa_grants_base["ERP_2025"].round(0)
wa_grants_base["ERP_2026"] = wa_grants_base["ERP_2024"] * pop_30_jun["WA"][2026] / wa_grants_base["ERP_2024"].sum()
wa_grants_base["ERP_2026"] = wa_grants_base["ERP_2026"].round(0)
wa_grants_base["ERP_2027"] = wa_grants_base["ERP_2024"] * pop_30_jun["WA"][2027] / wa_grants_base["ERP_2024"].sum()
wa_grants_base["ERP_2027"] = wa_grants_base["ERP_2027"].round(0)
wa_grants_base["ERP_2028"] = wa_grants_base["ERP_2024"] * pop_30_jun["WA"][2028] / wa_grants_base["ERP_2024"].sum()
wa_grants_base["ERP_2028"] = wa_grants_base["ERP_2028"].round(0)
wa_grants_base["Grant_base_2024"] = wa_grants_base["Grant_2024"]

def run_wa(i):
    wa_grants = wa_grants_base.copy()
    wa_grants["UID"] = wa_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["WA"][f"{year}-{(year+1)%1000}"] / wa_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = wa_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["WA"][f"{year}-{(year+1)%1000}"] / wa_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = wa_grants[f"ERP_{year}"] * min_per_capita_grant_base
        wa_grants[f"Funding Gap_{year}"] = wa_grants[f"Funding Gap_{year-1}"] * np.random.normal(1, 0.1, size=wa_grants.shape[0])
        wa_grants["deficit"] = wa_grants[f"Funding Gap_{year}"] > 0
        total_deficit = (wa_grants[f"Funding Gap_{year}"] * wa_grants["deficit"]).sum()
        # New case
        raw_alloc = (wa_grants[f"Funding Gap_{year}"] * wa_grants["deficit"] / total_deficit) * (budget_grants["WA"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        wa_grants["alloc"] = min_grant + raw_alloc
        wa_grants["delta"] = (wa_grants["alloc"] - wa_grants[f"Grant_{year-1}"]) / wa_grants[f"Grant_{year-1}"] * 100
        non_min_wa = wa_grants[wa_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        wa_grants.combine_first(correct_delta_wa(non_min_wa, year))
        wa_grants[f"Grant_{year}"] = wa_grants["alloc"]
        # Base case
        raw_alloc = (wa_grants[f"Funding Gap_{year}"] * wa_grants["deficit"] / total_deficit) * (budget_grants["WA"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        wa_grants["alloc"] = min_grant_base + raw_alloc
        wa_grants["delta"] = (wa_grants["alloc"] - wa_grants[f"Grant_base_{year-1}"]) / wa_grants[f"Grant_base_{year-1}"] * 100
        non_min_wa = wa_grants[wa_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        wa_grants.combine_first(correct_delta_wa(non_min_wa, year, base=True))
        wa_grants[f"Grant_base_{year}"] = wa_grants["alloc"]
    
    return wa_grants

# ## Tasmania ✅

# Tasmania State Grants Commission has a cap/collar of [-5%, 10%] for all councils.

def correct_delta_tas(sub_tas, year, base = False):
    total_funding_gap =  (sub_tas[f"Funding Gap_{year}"] * sub_tas["deficit"]).sum()
    total_funding = sub_tas["alloc"].sum()
    comparison_column = "Grant_base_" if base else "Grant_"
    
    while np.any((sub_tas["delta"].round(2)<-5)|(sub_tas["delta"].round(2)>10)):
        sub_tas["g"] = sub_tas["delta"].apply(lambda x: (x - (-5))/100 if x < -5 else ((x - 10)/100 if x > 10 else 0))
        sub_tas["alloc"] -= sub_tas["g"] * sub_tas[f"{comparison_column}{year-1}"]
        remainder = total_funding - sub_tas["alloc"].sum()
        sub_tas["alloc"] += sub_tas[f"Funding Gap_{year}"] * remainder / total_funding_gap
        delta_new = (sub_tas["alloc"] - sub_tas[f"{comparison_column}{year-1}"]) / sub_tas[f"{comparison_column}{year-1}"] * 100
        if delta_new.round(3).equals(sub_tas["delta"].round(3)):
            sub_tas["delta"] = delta_new
            break
        sub_tas["delta"] = delta_new
    return sub_tas

tas_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Tasmania")
tas_grants_base["ERP_2025"] = tas_grants_base["ERP_2024"] * pop_30_jun["TAS"][2025] / tas_grants_base["ERP_2024"].sum()
tas_grants_base["ERP_2025"] = tas_grants_base["ERP_2025"].round(0)
tas_grants_base["ERP_2026"] = tas_grants_base["ERP_2024"] * pop_30_jun["TAS"][2026] / tas_grants_base["ERP_2024"].sum()
tas_grants_base["ERP_2026"] = tas_grants_base["ERP_2026"].round(0)
tas_grants_base["ERP_2027"] = tas_grants_base["ERP_2024"] * pop_30_jun["TAS"][2027] / tas_grants_base["ERP_2024"].sum()
tas_grants_base["ERP_2027"] = tas_grants_base["ERP_2027"].round(0)
tas_grants_base["ERP_2028"] = tas_grants_base["ERP_2024"] * pop_30_jun["TAS"][2028] / tas_grants_base["ERP_2024"].sum()
tas_grants_base["ERP_2028"] = tas_grants_base["ERP_2028"].round(0)
tas_grants_base["Grant_base_2024"] = tas_grants_base["Grant_2024"]

def run_tas(i):
    tas_grants = tas_grants_base.copy()
    tas_grants["UID"] = tas_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["TAS"][f"{year}-{(year+1)%1000}"] / tas_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = tas_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["TAS"][f"{year}-{(year+1)%1000}"] / tas_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = tas_grants[f"ERP_{year}"] * min_per_capita_grant_base
        tas_grants[f"Funding Gap_{year}"] = tas_grants[f"Funding Gap_{year-1}"] * np.random.normal(1, 0.1, size=tas_grants.shape[0])
        tas_grants["deficit"] = tas_grants[f"Funding Gap_{year}"] > 0
        total_deficit = (tas_grants[f"Funding Gap_{year}"] * tas_grants["deficit"]).sum()
        # New case
        raw_alloc = (tas_grants[f"Funding Gap_{year}"] * tas_grants["deficit"] / total_deficit) * (budget_grants["TAS"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        tas_grants["alloc"] = min_grant + raw_alloc
        tas_grants["delta"] = (tas_grants["alloc"] - tas_grants[f"Grant_{year-1}"]) / tas_grants[f"Grant_{year-1}"] * 100
        non_min_tas = tas_grants[tas_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        tas_grants.combine_first(correct_delta_tas(non_min_tas, year))
        tas_grants[f"Grant_{year}"] = tas_grants["alloc"]
        # Base case
        raw_alloc = (tas_grants[f"Funding Gap_{year}"] * tas_grants["deficit"] / total_deficit) * (budget_grants["TAS"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        tas_grants["alloc"] = min_grant_base + raw_alloc
        tas_grants["delta"] = (tas_grants["alloc"] - tas_grants[f"Grant_base_{year-1}"]) / tas_grants[f"Grant_base_{year-1}"] * 100
        non_min_tas = tas_grants[tas_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        tas_grants.combine_first(correct_delta_tas(non_min_tas, year, base=True))
        tas_grants[f"Grant_base_{year}"] = tas_grants["alloc"]

    return tas_grants

# ## Northern Territory ✅

# Northern Territory has a collar of -5% for all councils.

def correct_delta_nt(sub_nt, year, base = False):
    total_funding_gap =  ( sub_nt[f"Funding Gap_{year}"] * sub_nt["deficit"]).sum()
    total_funding = sub_nt["alloc"].sum()
    
    comparison_column = "Grant_base_" if base else "Grant_"
    while np.any((sub_nt["delta"].round(2)<-5)):
        sub_nt["g"] = sub_nt["delta"].apply(lambda x: (x - (-5))/100 if x < -5 else 0)
        sub_nt["alloc"] -= sub_nt["g"] * sub_nt[f"{comparison_column}{year-1}"]
        remainder = total_funding - sub_nt["alloc"].sum()
        sub_nt["alloc"] += sub_nt[f"Funding Gap_{year}"] * remainder / total_funding_gap
        sub_nt["delta"] = (sub_nt["alloc"] - sub_nt[f"{comparison_column}{year-1}"]) / sub_nt[f"{comparison_column}{year-1}"] * 100
    return sub_nt

nt_grants_base = pd.read_excel("./Data/FA Grants Tables - Python.xlsx", sheet_name="Northern Territory")
nt_grants_base["ERP_2025"] = nt_grants_base["ERP_2024"] * pop_30_jun["NT"][2025] / nt_grants_base["ERP_2024"].sum()
nt_grants_base["ERP_2025"] = nt_grants_base["ERP_2025"].round(0)
nt_grants_base["ERP_2026"] = nt_grants_base["ERP_2024"] * pop_30_jun["NT"][2026] / nt_grants_base["ERP_2024"].sum()
nt_grants_base["ERP_2026"] = nt_grants_base["ERP_2026"].round(0)
nt_grants_base["ERP_2027"] = nt_grants_base["ERP_2024"] * pop_30_jun["NT"][2027] / nt_grants_base["ERP_2024"].sum()
nt_grants_base["ERP_2027"] = nt_grants_base["ERP_2027"].round(0)
nt_grants_base["ERP_2028"] = nt_grants_base["ERP_2024"] * pop_30_jun["NT"][2028] / nt_grants_base["ERP_2024"].sum()
nt_grants_base["ERP_2028"] = nt_grants_base["ERP_2028"].round(0)
nt_grants_base["Grant_base_2024"] = nt_grants_base["Grant_2024"]

def run_nt(i):
    nt_grants = nt_grants_base.copy()
    nt_grants["UID"] = nt_grants["LGA"].str.replace(" ", "").replace("-", "") + "_" + str(i+1)
    for year in range(2025, 2029):
        min_per_capita_grant = budget_grants["NT"][f"{year}-{(year+1)%1000}"] / nt_grants[f"ERP_{year}"].sum() * per_capita_minimum
        min_grant = nt_grants[f"ERP_{year}"] * min_per_capita_grant
        min_per_capita_grant_base = budget_grants["NT"][f"{year}-{(year+1)%1000}"] / nt_grants[f"ERP_{year}"].sum() * per_capita_minimum_base
        min_grant_base = nt_grants[f"ERP_{year}"] * min_per_capita_grant_base
        nt_grants[f"Funding Gap_{year}"] = nt_grants[f"Funding Gap_{year-1}"] * np.random.normal(1, 0.1, size=nt_grants.shape[0])
        nt_grants["deficit"] = nt_grants[f"Funding Gap_{year}"] > 0
        total_deficit = (nt_grants[f"Funding Gap_{year}"] * nt_grants["deficit"]).sum()
        # New case
        raw_alloc = (nt_grants[f"Funding Gap_{year}"] * nt_grants["deficit"] / total_deficit) * (budget_grants["NT"][f"{year}-{(year+1)%1000}"] - min_grant.sum())
        nt_grants["alloc"] = min_grant + raw_alloc
        nt_grants["delta"] = (nt_grants["alloc"] - nt_grants[f"Grant_{year-1}"]) / nt_grants[f"Grant_{year-1}"] * 100
        non_min_nt = nt_grants[nt_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        nt_grants.combine_first(correct_delta_nt(non_min_nt, year))
        nt_grants[f"Grant_{year}"] = nt_grants["alloc"]
        # Base case
        raw_alloc = (nt_grants[f"Funding Gap_{year}"] * nt_grants["deficit"] / total_deficit) * (budget_grants["NT"][f"{year}-{(year+1)%1000}"] - min_grant_base.sum())
        nt_grants["alloc"] = min_grant_base + raw_alloc
        nt_grants["delta"] = (nt_grants["alloc"] - nt_grants[f"Grant_base_{year-1}"]) / nt_grants[f"Grant_base_{year-1}"] * 100
        non_min_nt = nt_grants[nt_grants["deficit"]]#[["LGA", f"Funding Gap_{year}", f"grant_{year-1}", "alloc"]]
        nt_grants.combine_first(correct_delta_nt(non_min_nt, year, base=True))
        nt_grants[f"Grant_base_{year}"] = nt_grants["alloc"]
    return nt_grants

time_init_end = time() - time_init
print(f"Initialization took {time_init_end:.2f} seconds.")

if __name__ == "__main__":

    pool = Pool()

    time_start = time()
    print("Starting multiprocessing...")

    nsw_grants_master = pd.concat(pool.map_async(run_nsw, range(1000)).get(), axis=0, ignore_index=True)
    vic_grants_master = pd.concat(pool.map_async(run_vic, range(1000)).get(), axis=0, ignore_index=True)
    qld_grants_master = pd.concat(pool.map_async(run_qld, range(1000)).get(), axis=0, ignore_index=True)
    sa_grants_master = pd.concat(pool.map_async(run_sa, range(1000)).get(), axis=0, ignore_index=True)
    wa_grants_master = pd.concat(pool.map_async(run_wa, range(1000)).get(), axis=0, ignore_index=True)
    tas_grants_master = pd.concat(pool.map_async(run_tas, range(1000)).get(), axis=0, ignore_index=True)
    nt_grants_master = pd.concat(pool.map_async(run_nt, range(1000)).get(), axis=0, ignore_index=True)

    time_taken = time() - time_start

    print(time_taken)

    pool.close()

    grants_master = pd.concat([nsw_grants_master, vic_grants_master, qld_grants_master, sa_grants_master, wa_grants_master, tas_grants_master, nt_grants_master], axis=0, ignore_index=True)

    grants_master.to_csv("./Data/Output Multiprocessing/FA Grants Forward Parallel.csv", index=False)
