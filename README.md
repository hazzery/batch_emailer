# daily_email_report

daily_email_report is a simple email automation tool.
It is used to send out an email to a mailing list once a day.

## Configuration

All configuration of daily_email_report is specified in `config.toml`.
The config file contains the following options:

#### email
 - `sender` - Who the email is addressed from.
 - `mailing_list` - Filepath to the mailing list.
 - `subject` - The subject of the email.
 - `email_content` - Filepath to a document containing the email's body.
 - `attachments` - List of filepaths to attach to the email.

#### server
 - `hostname` - The hostname of the SMTP server.
 - `port_number` - The port number the SMTP server is running on.

####
 - `schedule_time` - The time of day for the email to be scheduled.

## How to run

To run daily_email_report execute the following command.
```bash
python3 -m daily_email_report
```
This will run in your terminal perpetually, sending the email out daily,
until stopped manually.
