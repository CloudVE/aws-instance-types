# AWS Instance Types by Availability Zone
## (Auto-Updated Helper for CloudBridge)
This repository uses the AWS Pricing API through CloudBridge (https://github.com/cloudve/cloudbridge) to determine what Instance Types are available in each availability zone, and extracts information about the instance types from the [ec2instances.info's JSON file](https://raw.githubusercontent.com/powdahound/ec2instances.info/master/www/instances.json).

This repository auto-updates daily, in two halves, through Travis CI CRON jobs.

CloudBridge (https://github.com/cloudve/cloudbridge) is a Python library, developped by members of the Galaxy Project community (https://galaxyproject.org), that provides a consistent layer of abstraction over different Infrastructure-as-a-Service cloud providers, reducing or eliminating the need to write conditional code for each cloud. CloudBridge v2 currently supports AWS, Azure, GCP, and OpenStack, providing a standardized and easily extendable library to manage resources on any of those providers. This library is meant to be used for the AWS VMTypes service in CloudBridge.

## Contributing
Community contributions for any part of the project are welcome. If you have a completely new idea or would like to bounce your idea before moving forward with the implementation, feel free to create an issue to start a discussion. Contributions should come in the form of a pull request.
