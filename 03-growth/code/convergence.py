import wbgapi as wb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os
from pathlib import Path

# 1. Configuration
indicator = 'NY.GDP.PCAP.KD' 
start_year = 1960
end_year = 2023 
output_path = Path(__file__).resolve().parents[1] / "slides" / "figures"

# 16:9 Aspect Ratio
FRAME_WIDTH = 16
FRAME_HEIGHT = 9

def get_convergence_data(ids):
    if not ids: return pd.DataFrame()
    try:
        df = wb.data.DataFrame(indicator, ids, time=[start_year, end_year], labels=True)
        df.columns = ['Country', 'y_start', 'y_end']
        df = df.dropna(subset=['y_start', 'y_end'])
        df['growth_rate'] = (np.log(df['y_end']) - np.log(df['y_start'])) / (end_year - start_year) * 100
        return df
    except:
        return pd.DataFrame()

# 2. Extract Data
all_ids = [row['id'] for row in wb.economy.list() if row.get('aggregate') == False]
try:
    oecd_ids = list(wb.region.members('OED'))
except:
    oecd_ids = list(set(row['economy'] for row in wb.data.fetch(indicator, economy='OED', time=end_year)))

df_oecd = get_convergence_data(oecd_ids)
df_world = get_convergence_data(all_ids)

# 3. Mega-Font Plot Function
def save_mega_font_plot(df, title, filename, country_font=14, is_world=False):
    plt.figure(figsize=(FRAME_WIDTH, FRAME_HEIGHT))
    
    # Heavier dots and thicker line for high-vis
    ax = sns.regplot(data=df, x='y_start', y='growth_rate', 
                     ci=None, 
                     scatter_kws={'alpha':0.6, 's':120, 'color':'#2c3e50'}, 
                     line_kws={'color':'#e74c3c', 'lw':5})
    
    # AXIS TICKS: Size 18
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.tick_params(axis='both', which='major', labelsize=18)
    
    # TITLES AND LABELS: Size 32 and 22
    plt.title(f'{title} Convergence ({start_year}-{end_year})', fontsize=32, fontweight='bold', pad=30)
    plt.xlabel(f'Real GDP per Capita in {start_year} (Constant 2015 US$)', fontsize=22, fontweight='semibold', labelpad=15)
    plt.ylabel('Avg. Annual Growth Rate (%)', fontsize=22, fontweight='semibold', labelpad=15)
    
    plt.grid(True, ls="--", alpha=0.4)
    
    # COUNTRY LABELS
    x_range = df['y_start'].max() - df['y_start'].min()
    offset = x_range * 0.012  
    
    for i in range(df.shape[0]):
        plt.text(df.y_start.iloc[i] + offset, df.growth_rate.iloc[i], 
                 df.Country.iloc[i], fontsize=country_font, alpha=0.9, 
                 fontweight='medium', verticalalignment='center')

    # SOURCE NOTE: Size 14
    source_text = f"Source: World Bank WDI. Growth = avg. annual log change."
    plt.figtext(0.1, 0.04, source_text, ha='left', fontsize=14, style='italic', color='#333333')

    # Adjust layout to prevent clipping
    plt.subplots_adjust(bottom=0.18, top=0.88, left=0.1, right=0.92)

    # Save
    full_path = os.path.join(output_path, filename)
    plt.savefig(full_path, dpi=300)
    print(f"Saved Mega-Plot: {full_path}")
    plt.show()

# Execute
# For the World plot, 10pt is the limit before it becomes a wall of black ink
save_mega_font_plot(df_oecd, 'OECD', 'convergence_oecd.png', country_font=14)
save_mega_font_plot(df_world, 'World', 'convergence_world.png', country_font=9)