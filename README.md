# nhs-uk-reviews

This repo is to implement automatic moderation of reviews submitted to NHS.UK.

Detailed documentation about methodology and purpose [can be found at this link](https://nhsd-confluence.digital.nhs.uk/display/DAT/DS_233%3A+NHS.UK+Reviews+2), which can only be accessed by NHS England staff. This README deals instead with some practicalities of the repo itself. Details about the models themselves can be found in the `model_cards` folder in the root of this repo.

## Requirements

For local dev work, run

```bash
conda create --name reviews python=3.8
conda activate reviews
pip install -r requirements.txt
```

Note that `requirements.txt` is the same file used by the docker image in deployment. Note that this is not sufficient to for the repo tests to pass - see the secrets explanation below.

## Secrets

The app relies on making a series of api calls to function. The URLS and keys for these are treated as environment variables, and the values they take vary between hosting environments in production, and also between these and local dev work. For information on this, [see the information on this page](https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?pageId=725553065).

## Data

**NOTE: In this public version of this repo, the data folder has been redacted in its entirety.**

The data folder contains seven csv files that are used as look-up tables for post-processing steps that take place in the flask app.

- `acroynm-list.csv` To cross check against any all-caps words found
- `def-names.csv` A list of words that are definite names and should be caught by the names rule
- `non-names.csv` A list of words that are not names and should not be caught by the names rule
- `descriptions-adjectives.csv` A list of adjectives that are not allowed in combination with a noun from descriptions-nouns.csv
- `descriptions-nouns.csv` A list of nouns that are not allowed in combination with an adjective from descriptions-adjectives.csv
- `profanity-list-hard.csv` A list of prohibited strong language
- `profanity-list-soft.csv` A list of strong language that may or may not be permitted depending on context

There is also a json file `AutomodApiTests.postman_collection.json` used for testing purposes. See the acceptance tests for more info.

## Modules

The modules folder is where we keep the code for each of our rules. This is where calls are made to the machine learning models and post-processing steps are carried out. Each rule and it's associated file(s) is below:

- All Caps Rule: `allcaps.py`
- Email Rule: `email_rule.py`
- URL Rule: `url_rule.py`
- Soft Profanity Rule: `profanity_soft.py`
- Hard Profanity Rule: `profanity_hard.py`
- Descriptions Rule: `descriptor_rule.py`
- Names Rule: `names_rule.py` and `names_helpers.py`
- Complaint Rule: `complaint_rule.py`
- Not An Experience Rule: `not_experience_rule.py`
- Safeguarding Rule: `safeguarding_rule.py`

## Tests

`python -m pytest` (this will catch any potential path issues with pytest as opposed to just `pytest`).
Note that this runs the unit tests stored in the `tests/` folder. There is a test for each module, to check that the rules are behaving as expected. There is also a test for the HardRules function defined in `src/hardrules.py`, to check that the rules can run in combination. Fabricated reviews for use in these tests are found in the `tests/test_data/` folder.

## Local Deployment / Testing

Use `python src/app.py` for local flask app.

To query the app, use the automoderator route. Typically this will mean directing queries to

`http://localhost:8080/automoderator`

The JSON structure for a query is as follows:

```json
{
  "organisation-name": "an organisation (GP surgery or hospital etc)",
  "request-id": "abc",
  "request": [
    {
      "id": "title",
      "text": "title of the review"
    },
    {
      "id": "body",
      "text": "Main text of the review"
    }
  ]
}
```

## Workflow for updates

Please run `black` and `isort` before each pr.

All development work should treat the latest `ds_improvements_x` branch as master. This is because it's NHSE policy that the code deployed to production must reflect the `master` branch - since we don't want a release on every PR, we use this workflow. When ready for a release, merge `ds_improvements_x` into `master` in consultation with the non data-science devs on the project. For more information on this process, [see the documentation on this page](https://nhsd-confluence.digital.nhs.uk/display/DAT/DS_233%3A+How+to+do+a+release+on+the+Flask+app).

## Code: explanations by section

### app.py

This is the main application file where the Flask application is created and configured. It contains a single route, used for for automoderating reviews: the `automoderator/` route. This will apply each of the automoderation rules to the input data, and return a dictionary flagging which rules the input breaks. To see the format required for input requests to this route, see the section above on Local Deployment / Testing.

### azure-pipeline.yml and pipeline-templates/

This azure-pipeline.yml file outlines a CI/CD pipeline for automating tests, builds, and deployments via Azure Pipelines, targeting multiple environments (dev, int, stag, prod). This runs automatically on merges to `master`, but you can also run it manually - [the url for this stuff is here](https://dev.azure.com/nhsuk/nhsuk.moderation-api/_build?definitionId=1059). Here's an image of a run:
![alt text](readme_images/pipeline_run.png)

Key stages include:

- **Test**: This runs Runs unit tests on the codebase. It fetches secrets from the `dev` keyvault, builds an image with the codebase, and runs pytest. Note that this is distinct from the test suite which is run in the acceptance tests section, explained below.

- **Build**: Creates and pushes a Docker image to a registry.

- **Deployment**: Sequentially deploys to each hosting environment (dev, int, stag, prod). This uses the `deploy-to-env.yml` file in `pipeline-templates/`.

The Docker files in the project root are used to build the image which gets deployed to the different hosting environments.

- **Acceptance Tests**: Executes post-deployment tests to verify application functionality in each environment. See the section in this README on acceptance tests for more detail. This stage calls on the `run-acceptance-tests.yml` file in the `pipeline-templates/` folder.

### Acceptance tests

These serve a different role to the unit tests.
**Unit Tests**: Test functions individually, in a standalone way.
**Acceptance Tests**: Builds a hosted version of the app, and then queries it with queries which simulate how it would be used in deployment.

These are very very important. It would be perfectly possible to build a repo in which all of the functions work fine, but when we deploy the app none of them are called correctly, or something. The acceptance tests help us check the final product is doing what we expect.

These form an important part of the deployment pipeline - a build should not be promoted to a given environment unless it has passed the acceptance tests on the previous level.

In this repo we have two sets of acceptance tests. These correspond to different tasks in the `run-acceptance-tests.yml` file.

The first of these was created early on in the project and doesn't do very much. It installs newman (a commandline version of postman), and submits a query - the query is contained in `src/data/AutomodApiTests.postman_collection.json`. I advise against spending much time on this - and definitely against trying to interpret the json. If needed, import the json into postman to interpret it.

The second set of acceptance tests installs pytest, and then runs the tests written in `src/acceptance_tests/acceptance_tests.py`.
These submit a set of queries - one for each rule, and have expected results. This allows us to leverage the nice properties of pytest. The URL which needs to be queried, and the key which is needed as well, are both fetched from environment variables which are passed to the image running the pytest. Just to be clear: the image running pytest is, in this case, **not** the same as the image deployed to the hosting environment. In the case of the unit tests, it **is** the same image.

### Files for SSH

**sshd_config**: This configuration is for a server's SSH service. This is basically for debugging purposes - it's often very useful to be able to directly interact with a deployed image. This SSH allows for this interaction. Note that this SSH is **not** required for the actual functionality of the Flask app.

**`startup.sh`**: This script prepares and starts both a secure SSH service and the Flask app. It also exposes all the environment variables to the SSH service, which was needed for a particular debugging stage. This means that if you SSH into the service, you can `echo` the environment variables, to check that they've been fetched from the keyvault and inserted in the correct way.

## Contact

Please send all enquiries to [datascience@nhs.net](mailto:datascience@nhs.net)

## License

This codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is © Crown copyright and available under the terms of the Open Government 3.0 licence.