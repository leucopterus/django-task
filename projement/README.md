# Projement - simple project management tool

## Project overview

Projement is a simplified tool for project managers. Project managers can have an overview of all the projects in a company.
This includes estimated and actual hours spent on *design*, *development* and *testing*.

### Setup

Use `Python 3` for back-end.

All the requirements are described in `requirements.txt`. Make sure to add all your back-end requirements there as well!

Initial requirements include:

- [Django](https://docs.djangoproject.com/en/2.2/) as the base framework
- [django-crispy-forms](http://django-crispy-forms.readthedocs.io/en/latest/) for easier form layouts
- [markdown](http://pythonhosted.org/Markdown/siteindex.html) for rendering markdown in HTML

The application uses SQLite for the database by default. You can change the database backend, but make sure to document it somehow, if needed!

Migrate the database before the first run:

    python manage.py migrate

Create a superuser:

    python manage.py createsuperuser

Load initial data for projects:

    python manage.py loaddata projects/fixtures/initial.json

### Running the application

    python manage.py runserver

The application should be visible at `127.0.0.1:8000` after that.

## Assignment

- **Make sure to read through the whole assignment before you start writing your solutions.**
  **The last tasks might be more complicated than the first ones and, depending on the implementation, they might be related to each other.**
- Please use the best practices known to you to make the commits and manage branches in the repository.
- If you have any issues or questions about the task, mark them as TODOs in comments and figure out the best solution yourself.
- With bigger issues you can also ask us via e-mail or phone, but it might take some time until we respond.

##### When you have finished, create a Pull Request in GitHub containing the entire solution, and request for a review from the owner of the repository.

#### 1. Fix project ordering on the dashboard

Currently, the projects on the dashboard are ordered by start date. The project managers want to see them in a different order.

**As a result of this task:**

- Projects on the dashboard must be ordered by end date descendingly.
- Projects that have not ended yet, must be shown first.

#### 2. Improve the admin for project detail view

Currently, in the administration interface, it is possible to filter the projects by company name, but not the company instance in the database.
But project managers want to filter out projects of one specific company, even if there are multiple companies with the same name.

**As a result of this task:**

- In the admin interface, it must be possible to filter projects by actual companies in the database.

#### 3. Actual hours need to be decimals

Currently, all the actual hours (design, development, testing) for the `Project` model are integers.
Project managers want to have more precision - they need to be changed to decimals.

**As a result of this task:**

- The actual hours fields must be `DecimalField`s.
- The actual hours must be in the range of `0 <= x < 10000` and have 2 decimal places.
- All other changes necessary to keep the application running, must be made (e.g. migrations).

#### 4. Incremental changes

When two people edit the same project at the same time, and both want to increase the actual development hours by 10, they end up with faulty results.

For example, if the actual development hours are currently 25 in a project, and two developers begin 
editing the form simultaneously, then both have an initial value of 25 in the form.
They both did 10 hours of work, and thus insert 35 as the development hours.

After both have submitted the form, the actual development hours stored in the database are 35, 
even though both developers did 10 hours of work and the resulting value should be 45 (25+10+10).

**As a result of this task:**

- Instead of entering the total amount of actual hours, the user only has to enter the additional amount of development, design and testing hours that they have spent since last update.
- It must be possible for two users to enter their additional hours simultaneously, with both entries taken into account.

#### 5. Design and implement the history of changes

Currently, all the users can edit the actual hours of a project and no history of the changes is left behind. 
This way, the project managers cannot know, who has worked on the project and how much work they did.

**As a result of this task:**

- Every change to any of the actual hours fields must be logged and stored in the database.
- The data about which user and when did the changes, must be stored.
- Information about the initial value, change delta and resulting value for any changed field must be easily accessible.
- If the user changes multiple fields at the same time (e.g. both design and development), then this should be recognizable as one change.
- If none of the actual hours changed, no changes or logs should be created.
- The data that was entered before implementing this feature must not be lost.
- In the future, the changes should be easily viewable and filterable. You don't need to display this information anywhere at the moment.
- All previously implemented features must keep working.

#### 6. Add tags to the projects

Project managers want to have an easy way to add small bits of information to projects. For this, we need to implement tags.

**As a result of this task:**

- It must be possible to create, read, update and delete tags.
- Tag length is limited to 16 characters.
- Tags must be easily editable in the admin.
- It must be possible to add tags to a project. Each project can have `0...*` tags attached to it.
- Tags must be shared between projects.
- Tags for one project must be easily editable in the admin.
- The data about when a tag was attached to a project, must be stored.
- It is not required to display the tags on the dashboard or in the edit form (however it would not be a bad thing). 

#### 7. Excel

Project managers sometimes need to do some calculations with the data, so they want to download an Excel file.

**As a result of this task:**

- It must be possible to download a simple summary of projects in `.xls` format.
- The summary can have the same content as the table in the dashboard.
- It must be easy for the project manager to download the Excel file.

#### 8. Fix and write tests

Project managers don't like it, when the new features don't work as expected or even worse, when they break existing functionality. 
We need to make sure everything works as requested.

**As a result of this task:**

- All existing tests run successfully.
- All added functionality is covered with tests that pass.

#### 9. Improve the code (optional)

Project managers always value the opinion of developers. If you have any ideas on how to improve Projement - 
either on the architectural side, back-end implementation, code quality or developer experience - please 
write them down, e.g. as TODO-s in README.md, and implement them in case you find the time.  
