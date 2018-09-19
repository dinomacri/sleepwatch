# sleepwatch
An application which checks PLEX for its status (users currently viewing media on Plex) during "offline hours" and takes action by shutting down the target PC if parameters are met. This application can be configured to wake the server if the PLEX server is unavailable when not in offline hours

## Requirements
* [Python](https://www.python.org/downloads/)
* pip (included with Python >= 3.4)

## Installation
To install ``sleepwatch`` clone the repository.

``git clone https://github.com/dinomacri/sleepwatch``

Install the necessary python libraries.

``pip install -r requirements.txt``

Execute the script

``python sleepwatch.py``

## Configuration

A sample configuration is included in ``config.sample``.

Create a copy of the config and make your adjustments.

``cp config.sample config`` 
