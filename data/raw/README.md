
# Heat Exchanger Parametric Study Dataset

This dataset was generated from a parametric simulation of a heat exchanger using DWSIM. It contains both original and noisy values for 10 key process variables, making it suitable for regression, surrogate modeling, and optimization studies.

## 📄 Dataset Description

The dataset has 10,000 rows and 20 columns:
- 10 columns with original simulation data.
- 10 columns with Gaussian noise added to simulate measurement errors.

| Column Name                                               | Description                                               | Units      |
|-----------------------------------------------------------|-----------------------------------------------------------|------------|
| hot_inlet_temperature_k                                   | Hot stream inlet temperature                              | K          |
| cold_inlet_mass_flow_kg_s                                 | Cold stream inlet mass flow rate                          | kg/s       |
| hot_outlet_temperature_k                                  | Hot stream outlet temperature                             | K          |
| cold_outlet_temperature_k                                 | Cold stream outlet temperature                            | K          |
| hx_1_heat_load_kw                                         | Heat load of heat exchanger HX-1                          | kW         |
| hot_outlet_pressure_pa                                    | Hot stream outlet pressure                                | Pa         |
| cold_outlet_pressure_pa                                   | Cold stream outlet pressure                               | Pa         |
| hot_outlet_mass_flow_kg_s                                 | Hot stream outlet mass flow rate                          | kg/s       |
| cold_outlet_mass_flow_kg_s                                | Cold stream outlet mass flow rate                         | kg/s       |
| hx_1_logarithmic_mean_temperature_difference_lmtd_k       | Logarithmic Mean Temperature Difference for HX-1          | K          |
| *_noisy                                                   | Corresponding noisy values for each of the above variables|            |

## 📦 Files Included
- `heat_exchanger_dataset.csv`: Cleaned dataset with original and noisy data.
- `README.md`: Dataset documentation.
- `LICENSE.txt`: MIT License.

## 📊 Example Applications
- Surrogate model development for heat exchanger behavior.
- Training machine learning models with noise robustness.
- Process optimization studies.

## 🔖 License
This dataset is released under the MIT License.
