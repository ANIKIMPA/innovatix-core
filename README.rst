=====
Core
=====

The `core` app is the central hub of our Django project, designed to encapsulate the fundamental functionalities essential for the operation of the entire website. It acts as a foundational template, enabling the seamless integration and reuse of common features across various components of the application. By centralizing critical functionalities in the `core` app, we ensure consistency, reduce redundancy, and maintain a DRY (Don't Repeat Yourself) codebase.

Detailed documentation is in the "docs" directory.


Key Features
------------

- **Reusable Components:** Contains a suite of reusable components, including base models, utilities, and template tags, which are essential for the development of other apps within the project.
- **Template Management:** Manages global templates and static files, providing a consistent look and feel across the website.
- **User Authentication:** Implements the foundational elements of user authentication and authorization, ensuring a secure and reliable user management system.
- **Common Utilities:** Houses a collection of utility functions and classes that are frequently used throughout the application, promoting code reusability and efficiency.
- **Settings and Configurations:** Centralizes important settings and configurations, making the application easily manageable and scalable.


Usage
-----

The `core` app is designed to be intuitive and straightforward to use for developers. When creating new features or apps within the project, refer to the `core` app for reusable components and utilities. Ensure that any common functionality that could benefit other parts of the application is integrated into the `core` app to maintain consistency and avoid duplication.


Contribution
------------

As the backbone of our project, the `core` app is continuously evolving. Contributions that enhance its functionality, improve efficiency, or introduce beneficial features are always welcome. Please follow the project's contribution guidelines when proposing changes or additions to the `core` app.


Quick start
-----------

1. Add "core" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "core",
    ]

2. Include the core URLconf in your project urls.py like this::

    path("core/", include("core.urls")),

3. Run ``python manage.py migrate`` to create the core models.

4. Start the development server and visit http://127.0.0.1:8000/admin/ to create core models (you'll need the Admin app enabled).
