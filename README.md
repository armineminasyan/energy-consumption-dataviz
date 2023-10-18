> :warning: **This code is from 2017**: it might use deprecated APIs!

# Abstract

Understanding energy consumption patterns is vital in an industry, that of the distribution of electrical energy, which is very much limited by infrastructural capacity.
The electric network must be sized by considering the "worst-case" utilisation scenario: the network cannot collapse if there is a sudden surge in demand.
However, serving users during periods of peak demand is very expensive and reduces the network's capability of absorbing systemic demand variations.

For these reasons, there has been a big push to understand the demand patterns of different commercial and residential users in the last years to predict when the demand will be higher.
By appropriate pricing, the operator can shift some of the load from periods of high demand to periods of low demand, thereby balancing the load on the network.

Using an open big dataset of hourly measurements of electric consumption over one year, we will try to derive demand patterns which can be used as input for pricing strategies.
The data refers to users in the United States over the year 2004 and is available on the [OpenEI website](https://openei.org/datasets/dataset/commercial-and-residential-hourly-load-profiles-for-all-tmy3-locations-in-the-united-states).

# Files

The file `Analysis.ipynb` contains the main Jupyter notebook.
A clean version of the OpenEI data is in file `energy-consumption.csv.tar.bz2` (remember to deflate this file before running the notebook).
The script to clean the data is in `clean-data.rb`.
Timezone data for the cities in the dataset is kept in `timezone.csv`; this file is used as a cache in the notebook to avoid calling Google's geolocation API.

# License

The workbook is released under the GPL v3.0 license.
The original dataset was released under the CC0 1.0 license.
This work has been inspired by a [blog post](https://medium.com/startup-grind/i-reverse-engineered-a-500m-artificial-intelligence-company-in-one-week-heres-the-full-story-d067cef99e1c) by Gianluca Mauro.
