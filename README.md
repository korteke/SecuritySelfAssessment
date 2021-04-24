# Security Self Assessment

This repository contains some basic tooling to provide metrics for an
Application Security Program in an organization that develops software
either for internal use or for public release in any form.

* a web application written on the Tornadoweb framework that can present configurable forms
* a form definition for a Security Self Assessment questionnaire
* another form definition to evaluate SaaS contracts

## Note

You need to be able to read Python code (and write a bit) (or have
someone do that) to configure this to run in your own environment.

# Background

The author has created and is currently managing an Application
Security Program at [Sanoma Media
Finland](https://www.sanoma.fi/en/). Although there's an abundance of
open references on application security, simple tooling to collect
maturity metrics in an easily usable form in a larger organization
don't really exist (or didn't exist when this project was originally
conceived). The program code in this repository is a simple web
application that can render forms defined in JSON files, collect
filled forms in a database, and compute simple scores based on the
answers. The two supplied forms can be used to assess the security
maturity level of software projects or SaaS integrations in an
organization. The forms are based on Sanoma use cases.

The code in this repository is written in Python on top of the awesome
[Tornadoweb](https://www.tornadoweb.org/en/stable/) framework. Design
goals were simplicity and a minimal number of dependencies, therefore
HTML rendering is implemented inline in a true 90s fashion (don't
judge me, I'm just not at all interested in user interfaces).

This repository is not a plug and play solution unless you are
prepared to run this on a manually set up or self hosted
environment. The code can be run "locally" on a *nix host that has
Python, tornadoweb, and mysql running. Alternatively a Dockerfile and
docker-compose.yml file are provided. For deployment in a cloud
environment, you need to figure the deployment out yourself.

The code and the two supplied forms are provided for public use
courtesy of Sanoma Media Finland. Sharing is caring <3

# Usage

## Authentication

Due to the original use case of this software (Sanoma internal use),
the codebase currently assumes it's being used in an environment where
[Active Directory Federation
Services](https://docs.microsoft.com/en-us/windows-server/identity/active-directory-federation-services)
is being used to provide user authentication. The ADFS authentication
is implemented using [this
project](https://github.com/oh6hay/tornadoadfsoauth2), originally
created as part of this project but recently extracted into its own
repository. The ADFS configuration is supplied by environment
variables, see `sample-env.sh`. If you don't have ADFS, you need to
implement another way to authenticate your users. Pull requests are
welcome!

## Environment

Create a configuration file based on the `sample-env.sh` file. It
provides Mysql connection details and ADFS configuration details (see
above on authentication). 

## Docker

The easiest way to run this is to use the provided Docker and
docker-compose files. Make sure you have docker and docker-compose
installed and then just `make run`.

## Development

Assuming you develop on a Debian/Ubuntu based box, install mysql
server and then

```
pip3 install PyJWT tornado cryptography mysql-connector tornadoadfsoauth2
```


# How to contribute

The following contributions would be welcome:

* different authentication methods (eg. standalone, or other oauth2
  providers)
* form definitions for your appsec requirements! (suitably anonymized)

# Contact

ossi d0t vaananen @t gmail d0+ com

