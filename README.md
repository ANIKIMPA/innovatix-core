# Core

The `core` app is the central hub of our Django project, designed to encapsulate the fundamental functionalities essential for the operation of the entire website. It acts as a foundational template, enabling the seamless integration and reuse of common features across various components of the application. By centralizing critical functionalities in the `core` app, we ensure consistency, reduce redundancy, and maintain a DRY (Don't Repeat Yourself) codebase.

Detailed documentation is in the "docs" directory.

## Key Features

- **Reusable Components:** Contains a suite of reusable components, including base models, utilities, and template tags, which are essential for the development of other apps within the project.
- **Template Management:** Manages global templates and static files, providing a consistent look and feel across the website.
- **User Authentication:** Implements the foundational elements of user authentication and authorization, ensuring a secure and reliable user management system.
- **Common Utilities:** Houses a collection of utility functions and classes that are frequently used throughout the application, promoting code reusability and efficiency.
- **Settings and Configurations:** Centralizes important settings and configurations, making the application easily manageable and scalable.

## Required Settings

To ensure the proper functioning of the `core` app within your Django project, certain settings need to be configured:

- **Custom User Model:** If you are using the custom user model provided by `core`, update your `AUTH_USER_MODEL` in your project's `settings.py` as follows:

    ```python
    AUTH_USER_MODEL = "users.ProgramUser"
    ```

    This setting is essential for utilizing the custom user model implemented in the `core` app.

## Usage

The `core` app is designed to be intuitive and straightforward to use for developers. When creating new features or apps within the project, refer to the `core` app for reusable components and utilities. Ensure that any common functionality that could benefit other parts of the application is integrated into the `core` app to maintain consistency and avoid duplication.

## Contribution

As the backbone of our project, the `core` app is continuously evolving. Contributions that enhance its functionality, improve efficiency, or introduce beneficial features are always welcome. Please follow the project's contribution guidelines when proposing changes or additions to the `core` app.

## Quick start

1. Install the `core` app using pip:

    ```bash
    pip install git+https://github.com/ANIKIMPA/innovatix-core.git
    ```

2. Add "core" to your INSTALLED_APPS setting like this:

    ```python
    INSTALLED_APPS = [
        ...,
        "core",
    ]
    ```

3. Include the core URLconf in your project urls.py like this:

    ```python
    path("core/", include("core.urls")),
    ```

4. Update your project's `settings.py` with the required settings, especially the `AUTH_USER_MODEL`.

5. Run `python manage.py migrate` to create the core models.

6. Load the initial data to the database with `python manage.py loaddata initial.json`.

7. Start the development server and visit http://127.0.0.1:8000/admin/ to create core models (you'll need the Admin app enabled).
