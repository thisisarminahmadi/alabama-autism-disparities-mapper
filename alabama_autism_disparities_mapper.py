#!/usr/bin/env python3
"""
Alabama Autism Service Disparities Mapper

This script analyzes and visualizes disparities in autism service availability across Alabama counties.
It combines demographic data, socioeconomic indicators, and autism service provider locations to
create interactive maps showing service gaps and demographic correlations.


"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, Fullscreen
from geopy.geocoders import Nominatim
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class AlabamaAutismDisparitiesMapper:
    """
    A class to analyze and visualize autism service disparities in Alabama counties.
    """
    
    def __init__(self, data_path=None):
        """
        Initialize the mapper with data paths and configuration.
        
        Args:
            data_path (str): Path to the autism service provider data Excel file
        """
        self.data_path = data_path or "Updated_Scraped_autism_data_FromKelly_Feb18_2024.xlsx"
        self.geojson_path = "alabama-with-county-boundaries_1083.geojson"
        self.census_api_key = None  # Add your Census API key if needed
        
        # Alabama center coordinates
        self.alabama_center = [32.3182, -86.9023]
        
        # Census API endpoints
        self.census_base_url = "https://api.census.gov/data/2020/dec/pl"
        
    def load_autism_data(self):
        """
        Load autism service provider data from Excel file.
        
        Returns:
            pd.DataFrame: Autism service provider data
        """
        try:
            df = pd.read_excel(self.data_path)
            print(f"Loaded {len(df)} autism service provider records")
            return df
        except FileNotFoundError:
            print(f"Warning: Could not find {self.data_path}")
            print("Please ensure the data file is in the same directory as this script")
            return pd.DataFrame()
    
    def fetch_census_data(self, variable, state="01", county="*"):
        """
        Fetch data from US Census API for Alabama counties.
        
        Args:
            variable (str): Census variable to fetch
            state (str): State FIPS code (01 for Alabama)
            county (str): County FIPS code (* for all counties)
            
        Returns:
            pd.DataFrame: Census data
        """
        url = f"{self.census_base_url}?get={variable}&for=county:{county}&in=state:{state}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        except requests.RequestException as e:
            print(f"Error fetching census data: {e}")
            return pd.DataFrame()
    
    def get_demographic_data(self):
        """
        Fetch comprehensive demographic data for Alabama counties.
        
        Returns:
            dict: Dictionary containing various demographic DataFrames
        """
        print("Fetching demographic data from US Census API...")
        
        # Population data
        population_df = self.fetch_census_data("P1_001N")
        if not population_df.empty:
            population_df['County'] = population_df['NAME'].str.replace(', Alabama', '').str.replace(' County', '').str.strip()
            population_df['Population'] = pd.to_numeric(population_df['P1_001N'], errors='coerce')
        
        # Race/ethnicity data
        ethnicity_df = self.fetch_census_data("P1_004N")  # Black or African American alone
        if not ethnicity_df.empty:
            ethnicity_df['County'] = ethnicity_df['NAME'].str.replace(', Alabama', '').str.replace(' County', '').str.strip()
            ethnicity_df['Black_Population'] = pd.to_numeric(ethnicity_df['P1_004N'], errors='coerce')
        
        # Income data (from ACS)
        income_url = "https://api.census.gov/data/2020/acs/acs5?get=B19013_001E&for=county:*&in=state:01"
        try:
            response = requests.get(income_url)
            income_data = response.json()
            income_df = pd.DataFrame(income_data[1:], columns=income_data[0])
            income_df['County'] = income_df['NAME'].str.replace(', Alabama', '').str.replace(' County', '').str.strip()
            income_df['Median_Income'] = pd.to_numeric(income_df['B19013_001E'], errors='coerce')
        except:
            income_df = pd.DataFrame()
        
        return {
            'population': population_df,
            'ethnicity': ethnicity_df,
            'income': income_df
        }
    
    def process_autism_data(self, df):
        """
        Process and clean autism service provider data.
        
        Args:
            df (pd.DataFrame): Raw autism service provider data
            
        Returns:
            pd.DataFrame: Processed data with coordinates
        """
        if df.empty:
            return df
        
        # Clean county names
        if 'County' in df.columns:
            df['County'] = df['County'].str.replace(', Alabama', '').str.replace(' County', '').str.strip()
        
        # Add coordinates if not present
        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            df = self.geocode_providers(df)
        
        return df
    
    def geocode_providers(self, df):
        """
        Geocode provider addresses to get coordinates.
        
        Args:
            df (pd.DataFrame): Provider data with addresses
            
        Returns:
            pd.DataFrame: Data with added coordinates
        """
        geolocator = Nominatim(user_agent="alabama_autism_mapper")
        
        df['Latitude'] = np.nan
        df['Longitude'] = np.nan
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('Address', '')):
                try:
                    location = geolocator.geocode(f"{row['Address']}, Alabama, USA")
                    if location:
                        df.at[idx, 'Latitude'] = location.latitude
                        df.at[idx, 'Longitude'] = location.longitude
                except:
                    continue
        
        return df
    
    def create_interactive_map(self, autism_df, demographic_data):
        """
        Create an interactive map showing autism service disparities.
        
        Args:
            autism_df (pd.DataFrame): Processed autism service provider data
            demographic_data (dict): Demographic data for counties
            
        Returns:
            folium.Map: Interactive map
        """
        # Create base map
        base_map = folium.Map(
            location=self.alabama_center,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add Alabama county boundaries if GeoJSON file exists
        if Path(self.geojson_path).exists():
            try:
                with open(self.geojson_path, 'r') as f:
                    alabama_geojson = json.load(f)
                
                folium.GeoJson(
                    alabama_geojson,
                    name='Alabama Counties',
                    style_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.1
                    }
                ).add_to(base_map)
            except Exception as e:
                print(f"Warning: Could not load GeoJSON file: {e}")
        
        # Add autism service providers
        if not autism_df.empty and 'Latitude' in autism_df.columns:
            service_layer = folium.FeatureGroup(name='Autism Service Providers', overlay=True)
            
            for idx, row in autism_df.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    popup_text = f"""
                    <b>{row.get('Provider_Name', 'Unknown Provider')}</b><br>
                    Address: {row.get('Address', 'N/A')}<br>
                    County: {row.get('County', 'N/A')}<br>
                    Services: {row.get('Services', 'N/A')}
                    """
                    
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(service_layer)
            
            service_layer.add_to(base_map)
            
            # Add heatmap
            heat_data = []
            for idx, row in autism_df.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    heat_data.append([row['Latitude'], row['Longitude']])
            
            if heat_data:
                HeatMap(heat_data, name="Autism Service HeatMap").add_to(base_map)
        
        # Add demographic choropleth layers
        if demographic_data.get('population') is not None:
            self.add_choropleth_layer(base_map, demographic_data['population'], 
                                    'Population', 'Population', 'YlOrRd')
        
        if demographic_data.get('income') is not None:
            self.add_choropleth_layer(base_map, demographic_data['income'], 
                                    'Median Income', 'Median_Income', 'YlGnBu')
        
        # Add layer control
        folium.LayerControl().add_to(base_map)
        Fullscreen().add_to(base_map)
        
        return base_map
    
    def add_choropleth_layer(self, base_map, data_df, name, column, color_scheme):
        """
        Add a choropleth layer to the map.
        
        Args:
            base_map (folium.Map): Base map to add layer to
            data_df (pd.DataFrame): Data for the choropleth
            name (str): Layer name
            column (str): Column to use for coloring
            color_scheme (str): Color scheme for the choropleth
        """
        if Path(self.geojson_path).exists() and not data_df.empty:
            try:
                with open(self.geojson_path, 'r') as f:
                    geojson_data = json.load(f)
                
                # Prepare data for choropleth
                choropleth_data = {}
                for _, row in data_df.iterrows():
                    county_name = row['County']
                    value = row[column]
                    if pd.notna(value):
                        choropleth_data[county_name] = value
                
                folium.Choropleth(
                    geo_data=geojson_data,
                    name=name,
                    data=choropleth_data,
                    columns=['name', column],
                    key_on='feature.properties.name',
                    fill_color=color_scheme,
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name=name
                ).add_to(base_map)
            except Exception as e:
                print(f"Warning: Could not add {name} choropleth layer: {e}")
    
    def analyze_disparities(self, autism_df, demographic_data):
        """
        Analyze disparities in autism service availability.
        
        Args:
            autism_df (pd.DataFrame): Autism service provider data
            demographic_data (dict): Demographic data
            
        Returns:
            pd.DataFrame: Analysis results
        """
        if autism_df.empty:
            return pd.DataFrame()
        
        # Count providers by county
        county_counts = autism_df['County'].value_counts().reset_index()
        county_counts.columns = ['County', 'Provider_Count']
        
        # Merge with demographic data
        analysis_df = county_counts.copy()
        
        if demographic_data.get('population') is not None:
            analysis_df = analysis_df.merge(
                demographic_data['population'][['County', 'Population']], 
                on='County', how='left'
            )
            analysis_df['Providers_per_100k'] = (
                analysis_df['Provider_Count'] / analysis_df['Population'] * 100000
            )
        
        if demographic_data.get('income') is not None:
            analysis_df = analysis_df.merge(
                demographic_data['income'][['County', 'Median_Income']], 
                on='County', how='left'
            )
        
        if demographic_data.get('ethnicity') is not None:
            analysis_df = analysis_df.merge(
                demographic_data['ethnicity'][['County', 'Black_Population']], 
                on='County', how='left'
            )
            if 'Population' in analysis_df.columns:
                analysis_df['Black_Percentage'] = (
                    analysis_df['Black_Population'] / analysis_df['Population'] * 100
                )
        
        return analysis_df
    
    def create_analysis_plots(self, analysis_df):
        """
        Create analysis plots showing disparities.
        
        Args:
            analysis_df (pd.DataFrame): Analysis results
        """
        if analysis_df.empty:
            print("No data available for plotting")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Autism Service Disparities Analysis in Alabama', fontsize=16)
        
        # Providers per capita by county
        if 'Providers_per_100k' in analysis_df.columns:
            axes[0, 0].bar(range(len(analysis_df)), analysis_df['Providers_per_100k'])
            axes[0, 0].set_title('Providers per 100k Population by County')
            axes[0, 0].set_ylabel('Providers per 100k')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Income vs providers correlation
        if 'Median_Income' in analysis_df.columns and 'Providers_per_100k' in analysis_df.columns:
            axes[0, 1].scatter(analysis_df['Median_Income'], analysis_df['Providers_per_100k'])
            axes[0, 1].set_title('Median Income vs Providers per 100k')
            axes[0, 1].set_xlabel('Median Income ($)')
            axes[0, 1].set_ylabel('Providers per 100k')
        
        # Black population percentage vs providers
        if 'Black_Percentage' in analysis_df.columns and 'Providers_per_100k' in analysis_df.columns:
            axes[1, 0].scatter(analysis_df['Black_Percentage'], analysis_df['Providers_per_100k'])
            axes[1, 0].set_title('Black Population % vs Providers per 100k')
            axes[1, 0].set_xlabel('Black Population (%)')
            axes[1, 0].set_ylabel('Providers per 100k')
        
        # Population vs providers
        if 'Population' in analysis_df.columns and 'Provider_Count' in analysis_df.columns:
            axes[1, 1].scatter(analysis_df['Population'], analysis_df['Provider_Count'])
            axes[1, 1].set_title('Population vs Provider Count')
            axes[1, 1].set_xlabel('Population')
            axes[1, 1].set_ylabel('Provider Count')
        
        plt.tight_layout()
        plt.savefig('alabama_autism_disparities_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_results(self, analysis_df, map_obj):
        """
        Save analysis results and map.
        
        Args:
            analysis_df (pd.DataFrame): Analysis results
            map_obj (folium.Map): Interactive map
        """
        # Save analysis results
        if not analysis_df.empty:
            analysis_df.to_excel('alabama_autism_disparities_analysis.xlsx', index=False)
            print("Analysis results saved to 'alabama_autism_disparities_analysis.xlsx'")
        
        # Save map
        map_obj.save('alabama_autism_disparities_map.html')
        print("Interactive map saved to 'alabama_autism_disparities_map.html'")
    
    def run_analysis(self):
        """
        Run the complete analysis pipeline.
        """
        print("Starting Alabama Autism Service Disparities Analysis...")
        
        # Load data
        autism_df = self.load_autism_data()
        if autism_df.empty:
            print("No autism data found. Please ensure the data file is available.")
            return
        
        # Process autism data
        autism_df = self.process_autism_data(autism_df)
        
        # Get demographic data
        demographic_data = self.get_demographic_data()
        
        # Create interactive map
        map_obj = self.create_interactive_map(autism_df, demographic_data)
        
        # Analyze disparities
        analysis_df = self.analyze_disparities(autism_df, demographic_data)
        
        # Create plots
        self.create_analysis_plots(analysis_df)
        
        # Save results
        self.save_results(analysis_df, map_obj)
        
        print("Analysis complete!")
        return map_obj, analysis_df


def main():
    """
    Main function to run the analysis.
    """
    # Initialize the mapper
    mapper = AlabamaAutismDisparitiesMapper()
    
    # Run the analysis
    map_obj, analysis_df = mapper.run_analysis()
    
    # Display summary statistics
    if not analysis_df.empty:
        print("\nSummary Statistics:")
        print(f"Total counties analyzed: {len(analysis_df)}")
        print(f"Total providers: {analysis_df['Provider_Count'].sum()}")
        if 'Providers_per_100k' in analysis_df.columns:
            print(f"Average providers per 100k: {analysis_df['Providers_per_100k'].mean():.2f}")
            print(f"Counties with 0 providers: {(analysis_df['Provider_Count'] == 0).sum()}")


if __name__ == "__main__":
    main()
