"""
Run the following to generate the initial migration after setting DATABASE_URL:

alembic revision --autogenerate -m "create employers / employees / quotes tables"

Then apply:

alembic upgrade head
"""
