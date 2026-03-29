"""
india_locations.py
==================
Comprehensive registry of Indian cities / district headquarters with
four climate / agricultural zone classifications per city.

Base fields
-----------
    state, state_code, city, district, lat, lon

Climate / zone metadata  (4 fields)
-------------------------------------
    koppen
        "Arid_West"           Rajasthan, Gujarat
        "Humid_Subtropical_N" UP, Bihar, Delhi, Haryana, MP, Punjab
        "Tropical_Wet_E"      WB, Odisha, Assam, NE states
        "Mountain_N"          HP, Uttarakhand, J&K, Ladakh, Sikkim
        "Tropical_WetDry_S"   Kerala, KA, TN, AP, TG, MH, Goa

    monsoon_zone
        "Early_SW"   June 1-10   Kerala, Goa, coastal KA, NE India
        "Central_SW" June 10-25  MH, MP, CG, Odisha, WB, AP, TG, int-KA
        "Late_SW"    June 25-Jul Bihar, Jharkhand, UP, Delhi, HR, PB, UK, HP
        "Arid_Late"  July+       Rajasthan, Gujarat (late onset + early retreat)
        "NE_Monsoon" Oct-Dec     Tamil Nadu, SE coast, Puducherry

    imd_zone
        ~20 simplified IMD meteorological subdivisions

    agri_zone
        "Kharif_Dom"     SW-monsoon single season (NE, Odisha, coastal)
        "Rabi_Dom"       Winter wheat belt (Punjab, Haryana, W-UP)
        "Kharif_Rabi"    Both seasons (AP, TG, MH, KA, MP, E-UP)
        "Year_Round"     Multi-crop perennial (Kerala, TN, Andaman)
        "Arid_Irrigated" Canal/drip irrigated (Rajasthan, Gujarat)
        "Mountain"       Subsistence / terrace farming
"""
from __future__ import annotations

INDIA_LOCATIONS: list[dict] = [
    # ── Andhra Pradesh ───────────────────────────────────────────────────────
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Amaravati",         "district": "Guntur",           "lat": 16.5731, "lon": 80.3575, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Visakhapatnam",     "district": "Visakhapatnam",    "lat": 17.6868, "lon": 83.2185, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Vijayawada",        "district": "Krishna",          "lat": 16.5062, "lon": 80.6480, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Tirupati",          "district": "Tirupati",         "lat": 13.6288, "lon": 79.4192, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Rayalaseema",          "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Guntur",            "district": "Guntur",           "lat": 16.3067, "lon": 80.4365, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Nellore",           "district": "SPSR Nellore",     "lat": 14.4426, "lon": 79.9865, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Kurnool",           "district": "Kurnool",          "lat": 15.8281, "lon": 78.0373, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Rayalaseema",          "agri_zone": "Kharif_Rabi"},
    {"state": "Andhra Pradesh",    "state_code": "AP", "city": "Kakinada",          "district": "East Godavari",    "lat": 16.9891, "lon": 82.2475, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Coastal_AP",           "agri_zone": "Kharif_Rabi"},
    # ── Arunachal Pradesh ────────────────────────────────────────────────────
    {"state": "Arunachal Pradesh", "state_code": "AR", "city": "Itanagar",          "district": "Papum Pare",       "lat": 27.0844, "lon": 93.6053, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Arunachal Pradesh", "state_code": "AR", "city": "Naharlagun",        "district": "Papum Pare",       "lat": 27.1019, "lon": 93.6954, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    # ── Assam ────────────────────────────────────────────────────────────────
    {"state": "Assam",             "state_code": "AS", "city": "Guwahati",          "district": "Kamrup Metro",     "lat": 26.1445, "lon": 91.7362, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Assam",             "state_code": "AS", "city": "Silchar",           "district": "Cachar",           "lat": 24.8333, "lon": 92.7789, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Assam",             "state_code": "AS", "city": "Dibrugarh",         "district": "Dibrugarh",        "lat": 27.4728, "lon": 94.9120, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Assam",             "state_code": "AS", "city": "Jorhat",            "district": "Jorhat",           "lat": 26.7509, "lon": 94.2037, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Assam",             "state_code": "AS", "city": "Nagaon",            "district": "Nagaon",           "lat": 26.3465, "lon": 92.6862, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    # ── Bihar ────────────────────────────────────────────────────────────────
    {"state": "Bihar",             "state_code": "BR", "city": "Patna",             "district": "Patna",            "lat": 25.5941, "lon": 85.1376, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Bihar",             "state_code": "BR", "city": "Gaya",              "district": "Gaya",             "lat": 24.7955, "lon": 84.9994, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Bihar",             "state_code": "BR", "city": "Bhagalpur",         "district": "Bhagalpur",        "lat": 25.2425, "lon": 86.9842, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Bihar",             "state_code": "BR", "city": "Muzaffarpur",       "district": "Muzaffarpur",      "lat": 26.1209, "lon": 85.3647, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Bihar",             "state_code": "BR", "city": "Darbhanga",         "district": "Darbhanga",        "lat": 26.1542, "lon": 85.8918, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Bihar",             "state_code": "BR", "city": "Purnia",            "district": "Purnia",           "lat": 25.7771, "lon": 87.4753, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    # ── Chhattisgarh ─────────────────────────────────────────────────────────
    {"state": "Chhattisgarh",      "state_code": "CG", "city": "Raipur",            "district": "Raipur",           "lat": 21.2514, "lon": 81.6296, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Chhattisgarh",         "agri_zone": "Kharif_Dom"},
    {"state": "Chhattisgarh",      "state_code": "CG", "city": "Bilaspur",          "district": "Bilaspur",         "lat": 22.0796, "lon": 82.1391, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Chhattisgarh",         "agri_zone": "Kharif_Dom"},
    {"state": "Chhattisgarh",      "state_code": "CG", "city": "Korba",             "district": "Korba",            "lat": 22.3595, "lon": 82.7501, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Chhattisgarh",         "agri_zone": "Kharif_Dom"},
    {"state": "Chhattisgarh",      "state_code": "CG", "city": "Jagdalpur",         "district": "Bastar",           "lat": 19.0728, "lon": 82.0195, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Chhattisgarh",         "agri_zone": "Kharif_Dom"},
    # ── Goa ──────────────────────────────────────────────────────────────────
    {"state": "Goa",               "state_code": "GA", "city": "Panaji",            "district": "North Goa",        "lat": 15.4909, "lon": 73.8278, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Dom"},
    {"state": "Goa",               "state_code": "GA", "city": "Margao",            "district": "South Goa",        "lat": 15.2993, "lon": 73.9862, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Dom"},
    # ── Gujarat ──────────────────────────────────────────────────────────────
    {"state": "Gujarat",           "state_code": "GJ", "city": "Gandhinagar",       "district": "Gandhinagar",      "lat": 23.2156, "lon": 72.6369, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Ahmedabad",         "district": "Ahmedabad",        "lat": 23.0225, "lon": 72.5714, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Surat",             "district": "Surat",            "lat": 21.1702, "lon": 72.8311, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Vadodara",          "district": "Vadodara",         "lat": 22.3072, "lon": 73.1812, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Rajkot",            "district": "Rajkot",           "lat": 22.3039, "lon": 70.8022, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Bhavnagar",         "district": "Bhavnagar",        "lat": 21.7645, "lon": 72.1519, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Jamnagar",          "district": "Jamnagar",         "lat": 22.4707, "lon": 70.0577, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    {"state": "Gujarat",           "state_code": "GJ", "city": "Junagadh",          "district": "Junagadh",         "lat": 21.5222, "lon": 70.4579, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Gujarat_Saurashtra",   "agri_zone": "Arid_Irrigated"},
    # ── Haryana ──────────────────────────────────────────────────────────────
    {"state": "Haryana",           "state_code": "HR", "city": "Gurugram",          "district": "Gurugram",         "lat": 28.4595, "lon": 77.0266, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Faridabad",         "district": "Faridabad",        "lat": 28.4089, "lon": 77.3178, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Rohtak",            "district": "Rohtak",           "lat": 28.8955, "lon": 76.6066, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Ambala",            "district": "Ambala",           "lat": 30.3782, "lon": 76.7767, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Hisar",             "district": "Hisar",            "lat": 29.1492, "lon": 75.7217, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Karnal",            "district": "Karnal",           "lat": 29.6857, "lon": 76.9905, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Panipat",           "district": "Panipat",          "lat": 29.3909, "lon": 76.9635, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Haryana",           "state_code": "HR", "city": "Sonipat",           "district": "Sonipat",          "lat": 28.9945, "lon": 77.0198, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    # ── Himachal Pradesh ─────────────────────────────────────────────────────
    {"state": "Himachal Pradesh",  "state_code": "HP", "city": "Shimla",            "district": "Shimla",           "lat": 31.1048, "lon": 77.1734, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Himachal Pradesh",  "state_code": "HP", "city": "Dharamsala",        "district": "Kangra",           "lat": 32.2190, "lon": 76.3234, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Himachal Pradesh",  "state_code": "HP", "city": "Mandi",             "district": "Mandi",            "lat": 31.7083, "lon": 76.9318, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Himachal Pradesh",  "state_code": "HP", "city": "Manali",            "district": "Kullu",            "lat": 32.2396, "lon": 77.1887, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    # ── Jharkhand ────────────────────────────────────────────────────────────
    {"state": "Jharkhand",         "state_code": "JH", "city": "Ranchi",            "district": "Ranchi",           "lat": 23.3441, "lon": 85.3096, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Jharkhand",         "state_code": "JH", "city": "Jamshedpur",        "district": "East Singhbhum",   "lat": 22.8046, "lon": 86.2029, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Jharkhand",         "state_code": "JH", "city": "Dhanbad",           "district": "Dhanbad",          "lat": 23.7957, "lon": 86.4304, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Jharkhand",         "state_code": "JH", "city": "Bokaro",            "district": "Bokaro",           "lat": 23.6693, "lon": 86.1511, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    {"state": "Jharkhand",         "state_code": "JH", "city": "Hazaribagh",        "district": "Hazaribagh",       "lat": 23.9925, "lon": 85.3637, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Bihar_Jharkhand",      "agri_zone": "Kharif_Rabi"},
    # ── Karnataka ────────────────────────────────────────────────────────────
    {"state": "Karnataka",         "state_code": "KA", "city": "Bengaluru",         "district": "Bengaluru Urban",  "lat": 12.9716, "lon": 77.5946, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Mysuru",            "district": "Mysuru",           "lat": 12.2958, "lon": 76.6394, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Mangaluru",         "district": "Dakshina Kannada", "lat": 12.9141, "lon": 74.8560, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Coastal_Karnataka",    "agri_zone": "Kharif_Dom"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Hubballi",          "district": "Dharwad",          "lat": 15.3647, "lon": 75.1240, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Belagavi",          "district": "Belagavi",         "lat": 15.8497, "lon": 74.4977, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Davanagere",        "district": "Davanagere",       "lat": 14.4644, "lon": 75.9218, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Ballari",           "district": "Ballari",          "lat": 15.1394, "lon": 76.9214, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    {"state": "Karnataka",         "state_code": "KA", "city": "Kalaburagi",        "district": "Kalaburagi",       "lat": 17.3297, "lon": 76.8343, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Interior_Karnataka",   "agri_zone": "Kharif_Rabi"},
    # ── Kerala ───────────────────────────────────────────────────────────────
    {"state": "Kerala",            "state_code": "KL", "city": "Thiruvananthapuram","district":"Thiruvananthapuram", "lat":  8.5241, "lon": 76.9366, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Kochi",             "district": "Ernakulam",        "lat":  9.9312, "lon": 76.2673, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Kozhikode",         "district": "Kozhikode",        "lat": 11.2588, "lon": 75.7804, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Thrissur",          "district": "Thrissur",         "lat": 10.5276, "lon": 76.2144, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Kollam",            "district": "Kollam",           "lat":  8.8932, "lon": 76.6141, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Palakkad",          "district": "Palakkad",         "lat": 10.7867, "lon": 76.6548, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Malappuram",        "district": "Malappuram",       "lat": 11.0510, "lon": 76.0711, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    {"state": "Kerala",            "state_code": "KL", "city": "Kannur",            "district": "Kannur",           "lat": 11.8745, "lon": 75.3704, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Kerala",               "agri_zone": "Year_Round"},
    # ── Madhya Pradesh ───────────────────────────────────────────────────────
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Bhopal",            "district": "Bhopal",           "lat": 23.2599, "lon": 77.4126, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Indore",            "district": "Indore",           "lat": 22.7196, "lon": 75.8577, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Jabalpur",          "district": "Jabalpur",         "lat": 23.1815, "lon": 79.9864, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Gwalior",           "district": "Gwalior",          "lat": 26.2183, "lon": 78.1828, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Ujjain",            "district": "Ujjain",           "lat": 23.1793, "lon": 75.7849, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Sagar",             "district": "Sagar",            "lat": 23.8388, "lon": 78.7378, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Rewa",              "district": "Rewa",             "lat": 24.5362, "lon": 81.3032, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Madhya Pradesh",    "state_code": "MP", "city": "Ratlam",            "district": "Ratlam",           "lat": 23.3315, "lon": 75.0367, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Central_SW",  "imd_zone": "MP",                   "agri_zone": "Kharif_Rabi"},
    # ── Maharashtra ──────────────────────────────────────────────────────────
    {"state": "Maharashtra",       "state_code": "MH", "city": "Mumbai",            "district": "Mumbai City",      "lat": 19.0760, "lon": 72.8777, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Pune",              "district": "Pune",             "lat": 18.5204, "lon": 73.8567, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Nagpur",            "district": "Nagpur",           "lat": 21.1458, "lon": 79.0882, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Vidarbha",             "agri_zone": "Kharif_Dom"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Nashik",            "district": "Nashik",           "lat": 19.9975, "lon": 73.7898, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Aurangabad",        "district": "Aurangabad",       "lat": 19.8762, "lon": 75.3433, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Solapur",           "district": "Solapur",          "lat": 17.6805, "lon": 75.9064, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Kolhapur",          "district": "Kolhapur",         "lat": 16.7050, "lon": 74.2433, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Amravati",          "district": "Amravati",         "lat": 20.9320, "lon": 77.7523, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Vidarbha",             "agri_zone": "Kharif_Dom"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Nanded",            "district": "Nanded",           "lat": 19.1383, "lon": 77.3210, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Maharashtra_Interior", "agri_zone": "Kharif_Rabi"},
    {"state": "Maharashtra",       "state_code": "MH", "city": "Thane",             "district": "Thane",            "lat": 19.2183, "lon": 72.9781, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Rabi"},
    # ── Manipur / Meghalaya / Mizoram / Nagaland ─────────────────────────────
    {"state": "Manipur",           "state_code": "MN", "city": "Imphal",            "district": "Imphal West",      "lat": 24.8170, "lon": 93.9368, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Meghalaya",         "state_code": "ML", "city": "Shillong",          "district": "East Khasi Hills", "lat": 25.5788, "lon": 91.8933, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Meghalaya",         "state_code": "ML", "city": "Tura",              "district": "West Garo Hills",  "lat": 25.5153, "lon": 90.2148, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Mizoram",           "state_code": "MZ", "city": "Aizawl",            "district": "Aizawl",           "lat": 23.7271, "lon": 92.7176, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Nagaland",          "state_code": "NL", "city": "Kohima",            "district": "Kohima",           "lat": 25.6751, "lon": 94.1086, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    {"state": "Nagaland",          "state_code": "NL", "city": "Dimapur",           "district": "Dimapur",          "lat": 25.9110, "lon": 93.7267, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    # ── Odisha ───────────────────────────────────────────────────────────────
    {"state": "Odisha",            "state_code": "OD", "city": "Bhubaneswar",       "district": "Khordha",          "lat": 20.2961, "lon": 85.8245, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Cuttack",           "district": "Cuttack",          "lat": 20.4625, "lon": 85.8828, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Berhampur",         "district": "Ganjam",           "lat": 19.3149, "lon": 84.7941, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Sambalpur",         "district": "Sambalpur",        "lat": 21.4669, "lon": 83.9756, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Rourkela",          "district": "Sundargarh",       "lat": 22.2604, "lon": 84.8536, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Puri",              "district": "Puri",             "lat": 19.8135, "lon": 85.8312, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    {"state": "Odisha",            "state_code": "OD", "city": "Balasore",          "district": "Balasore",         "lat": 21.4927, "lon": 86.9347, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "Odisha",               "agri_zone": "Kharif_Dom"},
    # ── Punjab ───────────────────────────────────────────────────────────────
    {"state": "Punjab",            "state_code": "PB", "city": "Ludhiana",          "district": "Ludhiana",         "lat": 30.9010, "lon": 75.8573, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Punjab",            "state_code": "PB", "city": "Amritsar",          "district": "Amritsar",         "lat": 31.6340, "lon": 74.8723, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Punjab",            "state_code": "PB", "city": "Jalandhar",         "district": "Jalandhar",        "lat": 31.3260, "lon": 75.5762, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Punjab",            "state_code": "PB", "city": "Patiala",           "district": "Patiala",          "lat": 30.3398, "lon": 76.3869, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Punjab",            "state_code": "PB", "city": "Bathinda",          "district": "Bathinda",         "lat": 30.2110, "lon": 74.9455, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Punjab",            "state_code": "PB", "city": "Mohali",            "district": "SAS Nagar",        "lat": 30.7046, "lon": 76.7179, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    # ── Rajasthan ────────────────────────────────────────────────────────────
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Jaipur",            "district": "Jaipur",           "lat": 26.9124, "lon": 75.7873, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Jodhpur",           "district": "Jodhpur",          "lat": 26.2389, "lon": 73.0243, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Udaipur",           "district": "Udaipur",          "lat": 24.5854, "lon": 73.7125, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Kota",              "district": "Kota",             "lat": 25.2138, "lon": 75.8648, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Bikaner",           "district": "Bikaner",          "lat": 28.0229, "lon": 73.3119, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Ajmer",             "district": "Ajmer",            "lat": 26.4499, "lon": 74.6399, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Alwar",             "district": "Alwar",            "lat": 27.5530, "lon": 76.6346, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    {"state": "Rajasthan",         "state_code": "RJ", "city": "Sikar",             "district": "Sikar",            "lat": 27.6094, "lon": 75.1399, "koppen": "Arid_West",           "monsoon_zone": "Arid_Late",   "imd_zone": "Rajasthan",            "agri_zone": "Arid_Irrigated"},
    # ── Sikkim ───────────────────────────────────────────────────────────────
    {"state": "Sikkim",            "state_code": "SK", "city": "Gangtok",           "district": "East Sikkim",      "lat": 27.3314, "lon": 88.6138, "koppen": "Mountain_N",          "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Mountain"},
    # ── Tamil Nadu ───────────────────────────────────────────────────────────
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Chennai",           "district": "Chennai",          "lat": 13.0827, "lon": 80.2707, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Coimbatore",        "district": "Coimbatore",       "lat": 11.0168, "lon": 76.9558, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Madurai",           "district": "Madurai",          "lat":  9.9252, "lon": 78.1198, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Tiruchirappalli",   "district": "Tiruchirappalli",  "lat": 10.7905, "lon": 78.7047, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Salem",             "district": "Salem",            "lat": 11.6643, "lon": 78.1460, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Tirunelveli",       "district": "Tirunelveli",      "lat":  8.7139, "lon": 77.7567, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Vellore",           "district": "Vellore",          "lat": 12.9165, "lon": 79.1325, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Erode",             "district": "Erode",            "lat": 11.3410, "lon": 77.7172, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    {"state": "Tamil Nadu",        "state_code": "TN", "city": "Tiruppur",          "district": "Tiruppur",         "lat": 11.1085, "lon": 77.3411, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
    # ── Telangana ────────────────────────────────────────────────────────────
    {"state": "Telangana",         "state_code": "TG", "city": "Hyderabad",         "district": "Hyderabad",        "lat": 17.3850, "lon": 78.4867, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Telangana",            "agri_zone": "Kharif_Rabi"},
    {"state": "Telangana",         "state_code": "TG", "city": "Warangal",          "district": "Warangal Urban",   "lat": 17.9784, "lon": 79.5941, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Telangana",            "agri_zone": "Kharif_Rabi"},
    {"state": "Telangana",         "state_code": "TG", "city": "Nizamabad",         "district": "Nizamabad",        "lat": 18.6725, "lon": 78.0941, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Telangana",            "agri_zone": "Kharif_Rabi"},
    {"state": "Telangana",         "state_code": "TG", "city": "Karimnagar",        "district": "Karimnagar",       "lat": 18.4386, "lon": 79.1288, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Telangana",            "agri_zone": "Kharif_Rabi"},
    {"state": "Telangana",         "state_code": "TG", "city": "Khammam",           "district": "Khammam",          "lat": 17.2473, "lon": 80.1514, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Central_SW",  "imd_zone": "Telangana",            "agri_zone": "Kharif_Rabi"},
    # ── Tripura ──────────────────────────────────────────────────────────────
    {"state": "Tripura",           "state_code": "TR", "city": "Agartala",          "district": "West Tripura",     "lat": 23.8315, "lon": 91.2868, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "NE_India",             "agri_zone": "Kharif_Dom"},
    # ── Uttar Pradesh ────────────────────────────────────────────────────────
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Lucknow",           "district": "Lucknow",          "lat": 26.8467, "lon": 80.9462, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Agra",              "district": "Agra",             "lat": 27.1767, "lon": 78.0081, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Kanpur",            "district": "Kanpur Nagar",     "lat": 26.4499, "lon": 80.3319, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Varanasi",          "district": "Varanasi",         "lat": 25.3176, "lon": 82.9739, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Prayagraj",         "district": "Prayagraj",        "lat": 25.4358, "lon": 81.8463, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Meerut",            "district": "Meerut",           "lat": 28.9845, "lon": 77.7064, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Bareilly",          "district": "Bareilly",         "lat": 28.3670, "lon": 79.4304, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Gorakhpur",         "district": "Gorakhpur",        "lat": 26.7606, "lon": 83.3732, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Aligarh",           "district": "Aligarh",          "lat": 27.8974, "lon": 78.0880, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Moradabad",         "district": "Moradabad",        "lat": 28.8386, "lon": 78.7733, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Saharanpur",        "district": "Saharanpur",       "lat": 29.9680, "lon": 77.5510, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Jhansi",            "district": "Jhansi",           "lat": 25.4484, "lon": 78.5685, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Kharif_Rabi"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Mathura",           "district": "Mathura",          "lat": 27.4924, "lon": 77.6737, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    {"state": "Uttar Pradesh",     "state_code": "UP", "city": "Noida",             "district": "Gautam Budh Nagar","lat": 28.5355, "lon": 77.3910, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "UP",                   "agri_zone": "Rabi_Dom"},
    # ── Uttarakhand ──────────────────────────────────────────────────────────
    {"state": "Uttarakhand",       "state_code": "UK", "city": "Dehradun",          "district": "Dehradun",         "lat": 30.3165, "lon": 78.0322, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Uttarakhand",       "state_code": "UK", "city": "Haridwar",          "district": "Haridwar",         "lat": 29.9457, "lon": 78.1642, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Uttarakhand",       "state_code": "UK", "city": "Nainital",          "district": "Nainital",         "lat": 29.3803, "lon": 79.4636, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    {"state": "Uttarakhand",       "state_code": "UK", "city": "Roorkee",           "district": "Haridwar",         "lat": 29.8543, "lon": 77.8880, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "Uttarakhand_HP",       "agri_zone": "Mountain"},
    # ── West Bengal ──────────────────────────────────────────────────────────
    {"state": "West Bengal",       "state_code": "WB", "city": "Kolkata",           "district": "Kolkata",          "lat": 22.5726, "lon": 88.3639, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Howrah",            "district": "Howrah",           "lat": 22.5958, "lon": 88.2636, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Durgapur",          "district": "Paschim Bardhaman","lat": 23.5204, "lon": 87.3119, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Asansol",           "district": "Paschim Bardhaman","lat": 23.6833, "lon": 86.9833, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Siliguri",          "district": "Darjeeling",       "lat": 26.7271, "lon": 88.3953, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Malda",             "district": "Malda",            "lat": 25.0107, "lon": 88.1439, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Central_SW",  "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    {"state": "West Bengal",       "state_code": "WB", "city": "Jalpaiguri",        "district": "Jalpaiguri",       "lat": 26.5449, "lon": 88.7179, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "West_Bengal",          "agri_zone": "Kharif_Dom"},
    # ── Union Territories ────────────────────────────────────────────────────
    {"state": "Delhi",             "state_code": "DL", "city": "New Delhi",         "district": "New Delhi",        "lat": 28.6139, "lon": 77.2090, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Chandigarh",        "state_code": "CH", "city": "Chandigarh",        "district": "Chandigarh",       "lat": 30.7333, "lon": 76.7794, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "Haryana_Delhi_Punjab", "agri_zone": "Rabi_Dom"},
    {"state": "Jammu & Kashmir",   "state_code": "JK", "city": "Srinagar",          "district": "Srinagar",         "lat": 34.0837, "lon": 74.7973, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "JK_Ladakh",            "agri_zone": "Mountain"},
    {"state": "Jammu & Kashmir",   "state_code": "JK", "city": "Jammu",             "district": "Jammu",            "lat": 32.7266, "lon": 74.8570, "koppen": "Humid_Subtropical_N", "monsoon_zone": "Late_SW",     "imd_zone": "JK_Ladakh",            "agri_zone": "Mountain"},
    {"state": "Ladakh",            "state_code": "LA", "city": "Leh",               "district": "Leh",              "lat": 34.1526, "lon": 77.5771, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "JK_Ladakh",            "agri_zone": "Mountain"},
    {"state": "Ladakh",            "state_code": "LA", "city": "Kargil",            "district": "Kargil",           "lat": 34.5539, "lon": 76.1349, "koppen": "Mountain_N",          "monsoon_zone": "Late_SW",     "imd_zone": "JK_Ladakh",            "agri_zone": "Mountain"},
    {"state": "Andaman & Nicobar", "state_code": "AN", "city": "Port Blair",        "district": "South Andaman",    "lat": 11.6234, "lon": 92.7265, "koppen": "Tropical_Wet_E",      "monsoon_zone": "Early_SW",    "imd_zone": "Andaman_Nicobar",      "agri_zone": "Year_Round"},
    {"state": "Lakshadweep",       "state_code": "LD", "city": "Kavaratti",         "district": "Lakshadweep",      "lat": 10.5626, "lon": 72.6369, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Lakshadweep",          "agri_zone": "Year_Round"},
    {"state": "Dadra & NH / D&D",  "state_code": "DN", "city": "Daman",             "district": "Daman",            "lat": 20.3974, "lon": 72.8328, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Rabi"},
    {"state": "Dadra & NH / D&D",  "state_code": "DN", "city": "Silvassa",          "district": "Dadra & NH",       "lat": 20.2667, "lon": 73.0167, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "Early_SW",    "imd_zone": "Konkan_Goa",           "agri_zone": "Kharif_Rabi"},
    {"state": "Puducherry",        "state_code": "PY", "city": "Puducherry",        "district": "Puducherry",       "lat": 11.9416, "lon": 79.8083, "koppen": "Tropical_WetDry_S",   "monsoon_zone": "NE_Monsoon",  "imd_zone": "Tamil_Nadu_Puducherry","agri_zone": "Year_Round"},
]

# Monsoon onset / withdrawal windows (day-of-year) per monsoon_zone
MONSOON_ONSET_WINDOW: dict[str, tuple[int, int]] = {
    "Early_SW":   (152, 165),   # June 1–14
    "Central_SW": (162, 180),   # June 11–29
    "Late_SW":    (176, 196),   # June 25–July 15
    "Arid_Late":  (185, 210),   # July 4–29
    "NE_Monsoon": (274, 335),   # Oct 1–Dec 1
}

MONSOON_WITHDRAWAL_WINDOW: dict[str, tuple[int, int]] = {
    "Early_SW":   (274, 305),
    "Central_SW": (274, 290),
    "Late_SW":    (258, 274),
    "Arid_Late":  (244, 265),
    "NE_Monsoon": (335, 365),
}

# ── Helper functions ──────────────────────────────────────────────────────────

def get_locations_by_state(state: str)   -> list[dict]: return [l for l in INDIA_LOCATIONS if l["state"].lower()        == state.lower()]
def get_locations_by_koppen(zone: str)   -> list[dict]: return [l for l in INDIA_LOCATIONS if l["koppen"]               == zone]
def get_locations_by_monsoon(zone: str)  -> list[dict]: return [l for l in INDIA_LOCATIONS if l["monsoon_zone"]         == zone]
def get_locations_by_imd(zone: str)      -> list[dict]: return [l for l in INDIA_LOCATIONS if l["imd_zone"]             == zone]
def get_locations_by_agri(zone: str)     -> list[dict]: return [l for l in INDIA_LOCATIONS if l["agri_zone"]            == zone]
def get_all_states()                     -> list[str]:  return sorted({l["state"] for l in INDIA_LOCATIONS})
def city_slug(loc: dict)                 -> str:        return loc["city"].lower().replace(" ", "_").replace("/", "_").replace(",", "")

def get_zone_summary(zone_field: str = "koppen") -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for loc in INDIA_LOCATIONS:
        out.setdefault(loc.get(zone_field, "Unknown"), []).append(loc["city"])
    return out

def as_dataframe():
    import pandas as pd
    return pd.DataFrame(INDIA_LOCATIONS)


if __name__ == "__main__":
    print(f"Total : {len(INDIA_LOCATIONS)}  |  States/UTs : {len(get_all_states())}")
    for field, label in [("koppen","Köppen"), ("monsoon_zone","Monsoon"),
                          ("imd_zone","IMD"), ("agri_zone","Agri")]:
        print(f"\n{label} zones:")
        for zone, cities in sorted(get_zone_summary(field).items()):
            print(f"  {zone:<35} {len(cities):>3} cities")
