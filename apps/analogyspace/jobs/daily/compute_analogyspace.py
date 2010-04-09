from django_extensions.management.jobs import DailyJob
from analogyspace.analysis import run_analogy_space_lang
from django.conf import settings

class Job(DailyJob):
    help = "Compute and store the AnalogySpace tensors and SVDs"

    def execute(self):
        # Configure logging
        import logging
        logging.basicConfig(level=logging.DEBUG)

        for lang in settings.SVD_LANGUAGES:
            run_analogy_space_lang(lang)
