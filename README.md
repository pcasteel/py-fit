# py-fit
A Python application to retrieve fitbit heartrate data in JSON format.

## Usage
```
usage: python py_fit.py [-h] [--start_time START_TIME] [--end_time END_TIME]
                 base_date detail_level output_file

positional arguments:
  base_date             Base date in yyyy-MM-dd format
  detail_level          Detail level with value of 1sec or 1min
  output_file           Path to output JSON file

optional arguments:
  -h, --help            show this help message and exit
  --start_time START_TIME
                        Start time in format HH:mm
  --end_time END_TIME   End time in format HH:mm
  ```
## Dependencies
The following python packages must be installed:
- cherrypy
- oauthlib

## Credentials
The `.fitbit` credentials file must have values for the `clientID` and `clientSecret` fields. These values come from registering an app at https://dev.fitbit.com/apps.