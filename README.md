# Alabama Autism Service Disparities Mapper

## Overview

This repository contains the code and analysis for mapping autism service disparities across Alabama counties. The project analyzes the geographic distribution of autism service providers in relation to demographic and socioeconomic factors to identify service gaps and disparities.

## Research Context

This analysis was conducted as part of a study examining disparities in autism service availability across Alabama counties. The research investigates how factors such as income, race/ethnicity, and population density correlate with the availability of autism services, with implications for healthcare access and policy.

## Features

- **Interactive Mapping**: Creates interactive maps showing autism service provider locations with heatmaps
- **Demographic Analysis**: Integrates US Census data for population, income, and racial/ethnic composition
- **Disparity Analysis**: Analyzes correlations between service availability and demographic factors
- **Visualization**: Generates statistical plots and choropleth maps
- **Data Export**: Saves analysis results in Excel format and interactive maps in HTML

## Files Description

- `alabama_autism_disparities_mapper.py`: Main analysis script
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file
- `Updated_Scraped_autism_data_FromKelly_Feb18_2024.xlsx`: Autism service provider data (not included in repo)
- `alabama-with-county-boundaries_1083.geojson`: Alabama county boundaries GeoJSON file (not included in repo)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/[your-username]/alabama-autism-disparities-mapper.git
cd alabama-autism-disparities-mapper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have the required data files:
   - `Updated_Scraped_autism_data_FromKelly_Feb18_2024.xlsx` (autism service provider data)
   - `alabama-with-county-boundaries_1083.geojson` (Alabama county boundaries)

## Usage

### Basic Usage

Run the complete analysis:

```bash
python alabama_autism_disparities_mapper.py
```

### Programmatic Usage

```python
from alabama_autism_disparities_mapper import AlabamaAutismDisparitiesMapper

# Initialize the mapper
mapper = AlabamaAutismDisparitiesMapper()

# Run the analysis
map_obj, analysis_df = mapper.run_analysis()

# Access results
print(analysis_df.head())
```

## Data Sources

### Autism Service Provider Data
- Source: Scraped from various autism service directories
- Format: Excel file with provider information including names, addresses, counties, and services
- Date: February 18, 2024

### Demographic Data
- Source: US Census Bureau API
- Datasets: 2020 Decennial Census (population, race/ethnicity) and 2020 American Community Survey (income)
- Geographic Level: County-level data for Alabama

### Geographic Data
- Source: Alabama county boundaries GeoJSON file
- Purpose: County boundary visualization and choropleth mapping

## Output Files

The script generates several output files:

1. **`alabama_autism_disparities_map.html`**: Interactive map showing:
   - Autism service provider locations (red markers)
   - Service density heatmap
   - County boundaries
   - Demographic choropleth layers (population, income)

2. **`alabama_autism_disparities_analysis.xlsx`**: Analysis results including:
   - Provider counts by county
   - Providers per 100,000 population
   - Demographic correlations
   - Statistical summaries

3. **`alabama_autism_disparities_analysis.png`**: Statistical plots showing:
   - Providers per capita by county
   - Income vs. service availability correlation
   - Racial/ethnic composition vs. service availability
   - Population vs. provider count relationship

## Key Findings

The analysis reveals several important patterns in autism service distribution across Alabama:

1. **Geographic Concentration**: Services are concentrated in urban areas, leaving rural counties underserved
2. **Socioeconomic Disparities**: Higher-income counties tend to have more service providers per capita
3. **Racial Disparities**: Counties with higher percentages of Black residents often have fewer service providers
4. **Service Gaps**: Multiple counties have zero autism service providers

## Methodology

### Data Processing
1. **Provider Data**: Clean and geocode autism service provider addresses
2. **Census Integration**: Fetch and merge demographic data from US Census API
3. **Spatial Analysis**: Calculate provider density and demographic correlations

### Statistical Analysis
- Provider density per 100,000 population by county
- Correlation analysis between service availability and demographic factors
- Geographic visualization of disparities

### Visualization
- Interactive maps using Folium
- Choropleth maps for demographic data
- Statistical plots using Matplotlib and Seaborn

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **folium**: Interactive mapping
- **geopy**: Geocoding addresses
- **requests**: API data fetching
- **matplotlib**: Statistical plotting
- **seaborn**: Enhanced statistical visualizations
- **openpyxl**: Excel file handling

## Citation

If you use this code in your research, please cite:

```
[Your Name]. (2024). Alabama Autism Service Disparities Mapper. 
PLOS ONE. https://github.com/[your-username]/alabama-autism-disparities-mapper
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

This repository is associated with a PLOS ONE publication. For questions or issues related to the research, please contact the corresponding author.

## Acknowledgments

- US Census Bureau for demographic data
- Autism service providers and directories for service information
- OpenStreetMap for geographic data
- The research team and participants

## Contact

For questions about this analysis or the associated research, please contact:
- Email: [your-email]
- Institution: [your-institution]

## Version History

- v1.0.0: Initial release for PLOS ONE publication
  - Complete analysis pipeline
  - Interactive mapping functionality
  - Statistical analysis and visualization
