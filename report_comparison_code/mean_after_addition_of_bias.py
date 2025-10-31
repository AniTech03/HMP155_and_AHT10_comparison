# *********** Compare AHT10 and HMP Data + Error Visualization ***********
import pandas as pd
import matplotlib.pyplot as plt
import os

# ================= USER SETTINGS =================
AHT10_folder = r"C:\Users\anike\OneDrive\Desktop\IITG project\AC model\Heat flow Simulation\HMP_AHT10_Compare\AHT10_data"
HMP_folder   = r"C:\Users\anike\OneDrive\Desktop\IITG project\AC model\Heat flow Simulation\HMP_AHT10_Compare\HMP_data"


days = ["2025-10-23","2025-10-24","2025-10-25", "2025-10-26", "2025-10-27", "2025-10-28", "2025-10-29"]  # List of days available

# ================= READ & MERGE =================
def load_aht10(day):
    path = os.path.join(AHT10_folder, f"humidity_log_{day}.csv")
    df = pd.read_csv(path)
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.rename(columns={'Tin': 'Tin_AHT10', 'RHin': 'RHin_AHT10'})
    df = df[['Time', 'Tin_AHT10', 'RHin_AHT10']]
    return df

def load_hmp(day):
    path = os.path.join(HMP_folder, f"HMP_{day}.csv")
    df = pd.read_csv(path)
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.rename(columns={'Tin': 'Tin_HMP', 'RHin': 'RHin_HMP'})
    df = df[['DateTime', 'Tin_HMP', 'RHin_HMP']]
    df = df.rename(columns={'DateTime': 'Time'})
    return df

# Load and concatenate both days
aht10_all = pd.concat([load_aht10(day) for day in days])
hmp_all = pd.concat([load_hmp(day) for day in days])

# Round timestamps to nearest minute for alignment
aht10_all['Time_rounded'] = aht10_all['Time'].dt.floor('min')
hmp_all['Time_rounded'] = hmp_all['Time'].dt.floor('min')

# Merge based on rounded time
merged = pd.merge(aht10_all, hmp_all, on='Time_rounded', how='inner')
merged = merged.sort_values(by='Time_rounded')

# ================= COMPUTE ERRORS =================
merged['Tin_Error'] = merged['Tin_HMP'] - merged['Tin_AHT10']
merged['RHin_Error'] = merged['RHin_HMP'] - merged['RHin_AHT10']

av_Terr = merged['Tin_Error'].mean()
av_RHerr = merged['RHin_Error'].mean()
std_Terr = merged['Tin_Error'].std()
std_RHerr = merged['RHin_Error'].std()
print("Tin error avg = ",av_Terr, "     SD = ", std_Terr)
print("RHin error avg = ",av_RHerr, "       SD = ", std_RHerr)

merged['Tin_AHT10'] = merged['Tin_AHT10'] + 0.36482638888888896
merged['RHin_AHT10'] = merged['RHin_AHT10'] + (-2.485659722222222)
merged['Tin_Error'] = merged['Tin_HMP'] - merged['Tin_AHT10']
merged['RHin_Error'] = merged['RHin_HMP'] - merged['RHin_AHT10']

av_Terr = merged['Tin_Error'].mean()
av_RHerr = merged['RHin_Error'].mean()
std_Terr = merged['Tin_Error'].std()
std_RHerr = merged['RHin_Error'].std()
print("After adding bias:")
print("Tin error avg = ",av_Terr, "     SD = ", std_Terr)
print("RHin error avg = ",av_RHerr, "       SD = ", std_RHerr)
# ================= PLOT =================
fig, axs = plt.subplots(2, 1, figsize=(13, 7), sharex=True)

# -------- Temperature Plot --------
ax1 = axs[0]
# Sort by time just to be sure
merged = merged.sort_values('Time_rounded')

# Break the line when time jumps too much (e.g. > 2 minutes)
time_diff = merged['Time_rounded'].diff().dt.total_seconds()
merged.loc[time_diff > 120, ['Tin_AHT10', 'Tin_HMP', 'RHin_AHT10', 'RHin_HMP']] = float('nan')

ax1.plot(merged['Time_rounded'], merged['Tin_AHT10'], label='AHT10 Tin', color='red', linewidth=1.5)
ax1.plot(merged['Time_rounded'], merged['Tin_HMP'], label='HMP Tin', color='blue', linewidth=1.5)
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('AHT10 vs HMP Comparison with Error')
ax1.grid(True)
ax1.legend(loc='upper left')

# Add error bars on right axis
ax1b = ax1.twinx()
ax1b.bar(merged['Time_rounded'], merged['Tin_Error'], width=0.0005, color='gray', alpha=0.4, label='Tin Error')
ax1b.set_ylabel('Tin Error (°C)')
ax1b.legend(loc='upper right')

# -------- Humidity Plot --------
ax2 = axs[1]
ax2.plot(merged['Time_rounded'], merged['RHin_AHT10'], label='AHT10 RH', color='orange', linewidth=1.5)
ax2.plot(merged['Time_rounded'], merged['RHin_HMP'], label='HMP RH', color='green', linewidth=1.5)
ax2.set_ylabel('Relative Humidity (%)')
ax2.set_xlabel('Time')
ax2.grid(True)
ax2.legend(loc='upper left')

# Add RH error bars on right axis
ax2b = ax2.twinx()
ax2b.bar(merged['Time_rounded'], merged['RHin_Error'], width=0.0005, color='gray', alpha=0.4, label='RH Error')
ax2b.set_ylabel('RH Error (%)')
ax2b.legend(loc='upper right')

plt.tight_layout()
plt.show()


# ================= SAVE MERGED FILE =================
merged.to_csv("AHT10_HMP_Merged_with_Error_23th_26th_oct.csv", index=False)
print("✅ Merged data with errors saved as 'AHT10_HMP_Merged_with_Error_25th_26th_oct.csv'")

# Mean and SD data:
