from django.db import models
import uuid
import os
from django.conf import settings


class URLMatcherJob(models.Model):
    """Model to track URL matcher job status and results."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    csv_file = models.FileField(upload_to='csv_uploads/')
    similarity_threshold = models.FloatField(default=0.7)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Result paths
    summary_file = models.CharField(max_length=255, blank=True, null=True)
    results_file = models.CharField(max_length=255, blank=True, null=True)
    exact_matches_file = models.CharField(max_length=255, blank=True, null=True)
    partial_matches_file = models.CharField(max_length=255, blank=True, null=True)
    unmatched_live_file = models.CharField(max_length=255, blank=True, null=True)
    unmatched_staging_file = models.CharField(max_length=255, blank=True, null=True)
    
    # Statistics
    total_urls = models.IntegerField(default=0)
    exact_matches = models.IntegerField(default=0)
    partial_matches = models.IntegerField(default=0)
    unmatched_live = models.IntegerField(default=0)
    unmatched_staging = models.IntegerField(default=0)
    
    def __str__(self):
        return f"URL Matcher Job {self.id} - {self.status}"
    
    def get_output_dir(self):
        """Get the output directory for this job's results."""
        job_output_dir = os.path.join(settings.URL_MATCHER_OUTPUT_DIR, str(self.id))
        if not os.path.exists(job_output_dir):
            os.makedirs(job_output_dir)
        return job_output_dir
    
    def get_summary_content(self):
        """Get the content of the summary file."""
        if self.summary_file and os.path.exists(self.summary_file):
            with open(self.summary_file, 'r') as f:
                return f.read()
        return None
