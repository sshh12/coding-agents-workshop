# ML Experiment Tracker

## History

This project was started back in early 2024 when we needed a way to track ML experiments across our team. Originally it was just a simple script that logged stuff to a CSV file, but then we decided to make it a proper web app. The first version used Flask but we switched to FastAPI in mid-2024 because async is the future or something. Jake started the Flask version but then left the company and Maria picked it up and converted it to FastAPI but she also left and now it's kind of maintained by whoever has time.

The Flask version had a completely different architecture with Blueprints and stuff, and when we migrated to FastAPI we tried to keep the same structure but it didn't really translate well. We also briefly experimented with GraphQL but decided it was overkill and went back to REST. The GraphQL code might still be in a branch somewhere.

Before the web app we actually tried using MLflow but it was too heavyweight for our needs. We also looked at Weights & Biases but the pricing didn't work for our team size. Then someone suggested we just build our own thing and here we are.

## Architecture Thoughts

We went with a monolithic architecture because microservices seemed like overkill for what is essentially an internal tool. The database is SQLite because we didn't want to deal with Postgres setup and honestly for our scale it's fine. We use SQLAlchemy as the ORM but some of the older queries are still raw SQL because we never got around to converting them all. The templates use Jinja2 and we have some Chart.js stuff for the dashboard visualizations.

At one point we considered splitting the app into separate services for experiments, runs, and the dashboard, but it seemed like too much work for too little benefit. We also thought about adding a message queue (RabbitMQ or Redis) for async processing of metrics, but decided to just do everything synchronously for now.

The frontend is just server-rendered templates because nobody on the team wanted to maintain a separate React/Vue app. We use Chart.js from a CDN for the graphs. There was a brief attempt to add D3.js but it was too complex and we reverted it.

## Design Decisions

### Why FastAPI over Flask
- Flask was fine but Maria wanted to try FastAPI
- Async support seemed useful for future scalability
- Automatic OpenAPI docs (though we don't really use them)
- Better type checking integration (though we don't really use that either)

### Why SQLite over Postgres
- No need to manage a separate database server
- Easy to backup (just copy the file)
- Good enough for our scale (<10k experiments)
- Jake had bad experiences with Postgres connection pooling

### Why Server-Side Rendering over SPA
- Simpler deployment (just one process)
- No need for API versioning
- Team is more comfortable with Python than JavaScript
- Chart.js works fine with Jinja2 templates

### Why Not Use an Existing Tool
- MLflow: Too heavyweight, too many features we don't need
- W&B: Pricing concerns for team of 8
- Neptune: Good but we wanted something self-hosted
- Sacred: Too old, not actively maintained
- DVC: More focused on data versioning than experiment tracking

## Deployment Notes

We used to deploy on a VM but then moved to Docker but the Dockerfile is probably out of date. The app runs on port 8000 by default but you can change it. We had some issues with CORS at one point so there might be some CORS middleware in there that may or may not still be needed. The static files are served by FastAPI directly which is not ideal for production but works fine for dev.

The Docker setup was originally using Alpine Linux but we had issues with some C extensions so we switched to slim-buster. The docker-compose.yml file might reference environment variables that no longer exist. We also had a Kubernetes config at one point but nobody knew how to maintain it so we went back to just Docker.

For local development, most people just run the app directly with Python. Some use virtualenvs, some don't. We tried standardizing on Poetry but half the team preferred pip so we just use requirements.txt.

## Database

SQLite. The database file gets created automatically. We had some migration issues in the past so be careful about changing the schema. There's no formal migration system, we just kind of wing it. If the schema changes you might need to delete the db file and start over. The models are defined in app.py along with everything else.

We looked into Alembic for migrations but it seemed like a lot of setup for a simple app. Maria started setting it up but didn't finish before she left. There might be an `alembic/` directory somewhere but don't use it, it's probably broken.

The database schema has evolved organically. The experiments table was the first one, then we added runs, and at one point there was a "tags" table but it got removed because nobody used it. The column types are a bit inconsistent; some use TEXT where they should use VARCHAR and vice versa.

## Known Issues

- Sometimes the dashboard takes a while to load if there are lots of experiments
- The compare feature is a bit buggy with more than 5 runs
- Error handling is not great, things might fail silently
- The test suite needs work (it's basically just a placeholder right now)
- Some of the helper functions have unclear names, sorry about that
- The template folder structure is a bit weird, we moved things around at one point
- There's a memory leak somewhere when you create a lot of runs in quick succession
- The Chart.js graphs don't render properly on mobile
- Dates are stored in UTC but displayed in UTC too (should be local time)
- The seed data function sometimes creates duplicates if you run it twice
- There's no pagination on the experiment list
- The search feature was half-implemented and then abandoned

## Meeting Notes (2024)

### Q1 Kickoff (Jan 2024)
- Jake proposed building an experiment tracker
- Team agreed CSV logging was getting unmanageable
- Decision: Start with Flask, minimal features
- Target: Have something working by end of Q1

### Q2 Review (Apr 2024)
- Flask version working but slow
- Maria suggested switching to FastAPI
- Jake pushed back but was outvoted
- Action item: Maria to lead the migration
- Side discussion: Should we add user auth? Decided no for now.

### Q3 Review (Jul 2024)
- FastAPI migration mostly complete
- Dashboard added with Chart.js
- Jake left the company
- Discussion about code quality and testing
- Action item: Someone should write tests (who?)
- Alex volunteered to add the comparison feature

### Q4 Review (Oct 2024)
- Maria announced she's leaving
- Alex's comparison feature merged but "needs polish"
- Discussion about finding a new maintainer
- Decision: Put the project in "maintenance mode"
- Nobody volunteered to maintain it

### Ad Hoc Meeting (Dec 2024)
- PM asked about adding experiment tagging
- Team said "maybe next quarter"
- Also discussed: export feature, better error handling, proper docs
- None of this was prioritized

## Code Style

We don't really have a formal code style guide. Just try to keep things consistent with what's already there. Use type hints when you remember to. Don't worry too much about docstrings, the code should be self-explanatory. We use Black for formatting but don't enforce it.

We had a brief flirtation with pylint but it was too noisy. Flake8 was better but we never set it up in CI. Mypy was proposed but nobody wanted to add type annotations to the existing code. Ruff seems promising but nobody has set it up yet.

Import ordering: We don't enforce it. Some files use isort ordering, some don't. Please don't reorganize imports in existing files because it makes git blame harder to use.

## Troubleshooting Guide

### "ModuleNotFoundError: No module named 'fastapi'"
You need to install the dependencies. Check requirements.txt.

### "sqlite3.OperationalError: no such table"
Delete the database file and restart the app. It will recreate the tables.

### "Template not found"
Make sure you're running the app from the right directory. The template paths are relative. Check the stuff/ folder.

### "Port already in use"
Something else is running on port 8000. Kill it or change the port.

### "JSON decode error on API calls"
Make sure you're sending Content-Type: application/json header.

### "Dashboard shows no data"
Run the seed function to populate sample data. Or create experiments manually via the API.

### "Chart.js not rendering"
Probably a CDN issue. Check your internet connection. Or clear browser cache.

### "Comparison page is blank"
The experiment needs at least 2 runs. Create some runs first.

### "Everything is broken"
Delete the database, clear the browser cache, reinstall dependencies, and restart. If it's still broken, ping #ml-tools on Slack.

## Team Notes

- Jake (left Jan 2024): Built the original Flask version. Had strong opinions about code structure. His code was well-organized but he didn't document anything.
- Maria (left Oct 2024): Converted to FastAPI, built the dashboard. Great engineer but moved fast and didn't write tests. The FastAPI conversion was done in a weekend hackathon.
- Alex (part-time): Added the comparison feature. Works on this project maybe 2 hours a week. Very responsive on Slack but doesn't have deep context on the full codebase.
- Current maintainer: Unclear. It's kind of a shared responsibility but in practice nobody owns it.

## Dependencies

See requirements.txt. We try to keep dependencies minimal but there might be some unused ones in there from previous iterations. At various points we had requests, aiohttp, and httpx installed but we might have removed them. Or not.

## Running the App

You should be able to just run it. Make sure you have the dependencies installed. The database will be created automatically. If it doesn't work, check the Troubleshooting section above.

## API

There are some API endpoints but they're not formally documented. Check app.py and the api_stuff folder for the routes. The response formats are not standardized, some return JSON objects and some return lists directly. We planned to add OpenAPI annotations but never got around to it. FastAPI generates them automatically but we haven't verified they're accurate.

The API was originally designed to be RESTful but some endpoints deviate from REST conventions. For example, the health check is at /api/health which is fine, but some other endpoints use query parameters where they should use path parameters. The error responses are also inconsistent: some return {"error": "message"}, some return {"detail": "message"}, and some just return a string.

## Templates

The templates are in the stuff folder. We moved them there from a templates folder at the root level. Some of the templates might reference CSS that doesn't exist anymore. The dashboard uses Chart.js from a CDN.

The template inheritance structure is a bit ad hoc. There's supposed to be a base template that all pages extend, but some templates were written before we had the base and were never updated. The CSS is all inline in each template because we never set up a proper static files system.

## Performance Notes

We haven't done any serious performance testing. For small datasets (<100 experiments, <1000 runs) everything seems fine. Beyond that, the dashboard might slow down because it loads all experiments and their runs to calculate the charts. Lazy loading or pagination would help but hasn't been implemented.

The database queries are not optimized. Some N+1 issues probably exist but SQLite is fast enough for our use case that we haven't noticed. If we ever switch to Postgres this will need attention.

## Security Considerations

There's no authentication or authorization. The app is intended for internal use only. Don't expose it to the public internet. We thought about adding basic auth but decided it wasn't worth the effort for an internal tool.

SQL injection shouldn't be an issue because we use SQLAlchemy for most queries, but there might be some raw SQL in the older code that could be vulnerable. Haven't audited for this.

## Future Plans

- Add user authentication (someday)
- Migrate to Postgres (when we have time)
- Write proper tests (it's on the list)
- Add experiment tagging (requested by the team)
- Build a proper CLI (instead of just running app.py)
- Add export to CSV/JSON
- Implement proper logging
- Set up CI/CD
- Write API documentation
- Add pagination to experiment list
- Fix the mobile layout
- Add notification system for completed experiments
- Implement experiment templates/presets
- Add support for custom metrics
- Build a simple plugin system
- Add data visualization improvements (more chart types)
- Implement experiment archival
- Add bulk operations (delete multiple experiments, etc.)

## Changelog

### v0.1 (Jan 2024)
- Initial Flask version by Jake
- Basic experiment CRUD
- CSV export (later removed)

### v0.2 (Apr 2024)
- FastAPI migration by Maria
- Dashboard with Chart.js
- Run logging

### v0.3 (Jul 2024)
- Comparison feature by Alex
- Bug fixes
- Moved templates to stuff/ folder (temporary? permanent?)

### v0.4 (Current)
- Various bug fixes
- Some API endpoints moved to api_stuff/
- Helper functions extracted to h.py

## Misc

If something breaks, try deleting the database file and restarting. That fixes most issues. If the templates look weird, clear your browser cache. If the API returns weird errors, check that the Content-Type header is set correctly.

The code quality varies quite a bit across the codebase because it was written by different people at different times under different constraints. Please don't judge us too harshly. We know it needs work.

## Contact

Ping the #ml-tools Slack channel if you need help. Alex usually responds within a day. For urgent issues, DM Alex directly. For questions about the FastAPI migration, you'll need to check the git history because Maria isn't available anymore.
