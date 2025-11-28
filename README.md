# COVID-19 Dashboard

A collection of COVID-19 data visualization tools built with Python.

## Project Structure

- **`app.py`** - Dash/Plotly interactive dashboard with selectable chart styles
- **`bokeh_app.py`** - Bokeh server-based visualization 
- **`prepare_owid_covid.py`** - Data preparation script that downloads and cleans OWID COVID-19 data
- **`covid_19_clean_complete.csv`** - Sample/source COVID-19 dataset

## Features

- Interactive charts with multiple visualization styles (line, scatter, bar, area, histogram, box)
- Country selection filtering
- Real-time data updates
- Support for multiple COVID-19 metrics:
  - Total cases and new cases
  - Total deaths and new deaths
  - Recovered and active cases
  - Vaccination data (where available)

## Requirements

Python 3.7+ with the following packages:
- pandas
- dash
- plotly
- bokeh
- requests

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd covid_dashboard_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Dash Dashboard
```bash
python app.py
```
Then open your browser to `http://localhost:8050`

### Run the Bokeh Dashboard
```bash
bokeh serve bokeh_app.py
```

### Prepare/Update Data
```bash
python prepare_owid_covid.py
```
This downloads the latest OWID COVID-19 data, cleans it, and generates processed CSV files in the `covid_output/` directory.

## Data Sources

- **Our World in Data (OWID)** - Comprehensive COVID-19 dataset
- **Kaggle COVID-19 Dataset** - Sample data format

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
