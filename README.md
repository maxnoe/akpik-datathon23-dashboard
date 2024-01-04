# Dashboard / Submission System for AKPIK Datathon

This is a small flask app that was used in the [first AKPIK Datathon](https://www.dpg-physik.de/vereinigungen/fachuebergreifend/ak/akpik/akpik-datathon).

The task was to select training samples from a tainted dataset for use with a fixed model architecture. 
The scoring was done by:

* Training the model on the training indices provided by the participants
* Applying the model to test data
* Computing accuracy of the predictions

The flask web interface
* can administer teams, which authenticate via a token.
* handles the team submissions
* shows the current leaderboar

a celery background worker scores the submissions.
