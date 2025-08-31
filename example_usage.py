#!/usr/bin/env python3
"""
Example usage of the Alabama Autism Disparities Mapper

This script demonstrates how to use the mapper with different configurations
and shows various analysis options.
"""

from alabama_autism_disparities_mapper import AlabamaAutismDisparitiesMapper
import pandas as pd

def example_basic_analysis():
    """
    Example of basic analysis using default settings.
    """
    print("=== Basic Analysis Example ===")
    
    # Initialize mapper with default settings
    mapper = AlabamaAutismDisparitiesMapper()
    
    # Run complete analysis
    map_obj, analysis_df = mapper.run_analysis()
    
    # Display summary
    if not analysis_df.empty:
        print(f"Analysis completed for {len(analysis_df)} counties")
        print(f"Total providers found: {analysis_df['Provider_Count'].sum()}")
        
        # Show top 5 counties by provider count
        print("\nTop 5 counties by provider count:")
        top_counties = analysis_df.nlargest(5, 'Provider_Count')
        for _, row in top_counties.iterrows():
            print(f"  {row['County']}: {row['Provider_Count']} providers")

def example_custom_data_path():
    """
    Example using custom data file path.
    """
    print("\n=== Custom Data Path Example ===")
    
    # Initialize mapper with custom data path
    custom_mapper = AlabamaAutismDisparitiesMapper(
        data_path="path/to/your/autism_data.xlsx"
    )
    
    # Load and process data only
    autism_df = custom_mapper.load_autism_data()
    if not autism_df.empty:
        processed_df = custom_mapper.process_autism_data(autism_df)
        print(f"Processed {len(processed_df)} provider records")

def example_demographic_analysis():
    """
    Example focusing on demographic analysis.
    """
    print("\n=== Demographic Analysis Example ===")
    
    mapper = AlabamaAutismDisparitiesMapper()
    
    # Get demographic data only
    demographic_data = mapper.get_demographic_data()
    
    # Check what data is available
    for key, df in demographic_data.items():
        if not df.empty:
            print(f"{key.capitalize()} data: {len(df)} counties")
            if 'Population' in df.columns:
                print(f"  Total population: {df['Population'].sum():,}")

def example_map_creation():
    """
    Example of creating maps with custom settings.
    """
    print("\n=== Custom Map Creation Example ===")
    
    mapper = AlabamaAutismDisparitiesMapper()
    
    # Load data
    autism_df = mapper.load_autism_data()
    if autism_df.empty:
        print("No autism data available for mapping")
        return
    
    # Process data
    autism_df = mapper.process_autism_data(autism_df)
    
    # Get demographic data
    demographic_data = mapper.get_demographic_data()
    
    # Create map with custom settings
    map_obj = mapper.create_interactive_map(autism_df, demographic_data)
    
    # Save map with custom name
    map_obj.save('custom_alabama_autism_map.html')
    print("Custom map saved as 'custom_alabama_autism_map.html'")

def example_statistical_analysis():
    """
    Example of statistical analysis and correlation testing.
    """
    print("\n=== Statistical Analysis Example ===")
    
    mapper = AlabamaAutismDisparitiesMapper()
    
    # Load and process data
    autism_df = mapper.load_autism_data()
    if autism_df.empty:
        print("No autism data available for analysis")
        return
    
    autism_df = mapper.process_autism_data(autism_df)
    demographic_data = mapper.get_demographic_data()
    
    # Perform disparity analysis
    analysis_df = mapper.analyze_disparities(autism_df, demographic_data)
    
    if not analysis_df.empty:
        # Calculate correlations
        correlations = {}
        
        if 'Median_Income' in analysis_df.columns and 'Providers_per_100k' in analysis_df.columns:
            corr = analysis_df['Median_Income'].corr(analysis_df['Providers_per_100k'])
            correlations['Income vs Providers'] = corr
        
        if 'Black_Percentage' in analysis_df.columns and 'Providers_per_100k' in analysis_df.columns:
            corr = analysis_df['Black_Percentage'].corr(analysis_df['Providers_per_100k'])
            correlations['Black Population % vs Providers'] = corr
        
        if 'Population' in analysis_df.columns and 'Provider_Count' in analysis_df.columns:
            corr = analysis_df['Population'].corr(analysis_df['Provider_Count'])
            correlations['Population vs Provider Count'] = corr
        
        # Display correlations
        print("Correlation Analysis:")
        for variable, corr in correlations.items():
            print(f"  {variable}: {corr:.3f}")
        
        # Identify service gaps
        zero_provider_counties = analysis_df[analysis_df['Provider_Count'] == 0]
        if not zero_provider_counties.empty:
            print(f"\nCounties with zero providers ({len(zero_provider_counties)}):")
            for _, row in zero_provider_counties.iterrows():
                print(f"  - {row['County']}")

def main():
    """
    Run all examples.
    """
    print("Alabama Autism Disparities Mapper - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_analysis()
        example_demographic_analysis()
        example_map_creation()
        example_statistical_analysis()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have the required data files in the correct location.")

if __name__ == "__main__":
    main()
