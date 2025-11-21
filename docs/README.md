# WhichMovie App - Technical Documentation

Complete technical guide to understanding the whichmovie_app Django application.

## Table of Contents

1. **[Platform Overview](./01_platform_overview.md)** ✅ - What is whichmovie_app and what does it do
2. **[Django Basics](./02_django_basics.md)** ✅ - Core Django concepts (MVT, apps, project structure)
3. **[Entry Point](./03_entry_point.md)** ✅ - What happens when you run `python manage.py runserver`
4. **[URL Routing](./04_url_routing.md)** ✅ - How URLs are matched and routed to views
5. **[Views](./05_views.md)** ✅ - Request handlers and response generation
6. **[Models](./06_models.md)** ✅ - Database layer and data structures
7. **[Templates](./07_templates.md)** - HTML rendering and frontend
8. **[Forms](./08_forms.md)** - User input handling
9. **[Admin Interface](./09_admin.md)** - Django admin for data management
10. **[Middleware](./10_middleware.md)** - Request/response processing pipeline
11. **[Static Files & Media](./11_static_media.md)** - CSS, JavaScript, file uploads
12. **[Authentication & Permissions](./12_auth.md)** - User login and access control
13. **[Signals](./13_signals.md)** - Event system for model lifecycle
14. **[Management Commands](./14_management_commands.md)** - Custom CLI commands
15. **[Dramatiq Tasks](./15_dramatiq_tasks.md)** ✅ - Background job scheduler
16. **[Testing](./16_testing.md)** - Test framework and strategies
17. **[Settings & Configuration](./17_settings.md)** - Configuration management
18. **[Error Handling](./18_error_handling.md)** - Exception handling and logging
19. **[Data Flow Architecture](./19_data_flow.md)** ✅ - Complete data flow from YouTube → Database → Display
20. **[API Clients](./20_api_clients.md)** - YouTube, TMDB, and base client patterns

## Quick Start

Each document follows this structure:
- **What it is** - Basic explanation
- **How it works** - Step-by-step walkthrough
- **In this project** - Specific implementation in whichmovie_app
- **Example** - Real code examples
- **Diagram** - Visual representation

---

Last updated: November 2025
