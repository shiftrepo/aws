#!/usr/bin/env python3
"""
Generate a sample patent classification trend chart
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configure plot settings
plt.rcParams['figure.figsize'] = (12, 8)
plt.style.use('ggplot')

def generate_sample_chart():
    """Generate a sample chart showing patent application trends over time by classification"""
    
    # Create sample data
    years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
    
    # Patent classification categories with English names
    categories = {
        'B60': 'Vehicles',
        'G06F': 'Electric Digital Data', 
        'G06N': 'AI/Machine Learning',
        'H01': 'Electric Elements',
        'H04': 'Electric Communication',
        'F02': 'Combustion Engines',
        'G01': 'Measuring/Testing',
        'B01': 'Phys/Chem Processes',
        'H02': 'Electric Power',
        'C02': 'Water Treatment'
    }
    
    # Generate synthetic data
    np.random.seed(42)  # For reproducibility
    
    # Create data with specific trends
    data = {
        'B60': [65, 72, 81, 93, 87, 95, 103, 118, 110, 98],  # Vehicles - strong throughout, peaking in 2022
        'G06F': [25, 31, 42, 38, 47, 55, 68, 72, 79, 85],    # Digital data - steady increase
        'G06N': [8, 12, 17, 22, 35, 45, 58, 67, 78, 83],     # AI - rapid growth
        'H01': [31, 36, 33, 39, 45, 52, 57, 65, 71, 75],     # Electric elements - steady growth
        'H04': [22, 27, 25, 32, 36, 41, 45, 53, 61, 70],     # Communication - increasing
        'F02': [45, 53, 62, 67, 61, 58, 52, 48, 43, 37],     # Combustion engines - decreasing
        'G01': [28, 31, 35, 33, 37, 38, 41, 43, 42, 45],     # Measuring - stable
        'B01': [15, 18, 22, 25, 23, 28, 29, 31, 33, 35],     # Chemical processes - slight increase
        'H02': [19, 23, 27, 31, 35, 42, 48, 53, 58, 62],     # Electric power - growing
        'C02': [12, 14, 15, 16, 17, 19, 22, 24, 26, 29],     # Water treatment - slight increase
    }
    
    # Create DataFrame
    df = pd.DataFrame(data, index=years)
    
    # Sort columns by total count to make the chart more readable
    column_sums = df.sum()
    sorted_columns = column_sums.sort_values(ascending=False).index
    df = df[sorted_columns]
    
    # Create the stacked bar chart
    ax = df.plot(kind='bar', stacked=True, figsize=(14, 8))
    
    # Set labels and title
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Applications', fontsize=12)
    ax.set_title('Patent Applications by Classification: Toyota', fontsize=14)
    
    # Replace column names with descriptive names
    plt.legend([categories[col] for col in df.columns], 
              title='IPC Classification', 
              bbox_to_anchor=(1.05, 1), 
              loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    output_path = 'sample_output/sample_classification_trend.png'
    plt.savefig(output_path)
    print(f"Sample chart saved as {output_path}")
    
    return output_path

if __name__ == "__main__":
    # Create the sample_output directory if it doesn't exist
    import os
    os.makedirs('sample_output', exist_ok=True)
    
    # Generate the chart
    generate_sample_chart()
