import os
import sys
import pandas as pd
import logging
import traceback
from django.conf import settings

# Add the parent directory to sys.path to import the matcher module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from matcher import URLMatcher

logger = logging.getLogger(__name__)

def process_url_matcher_job(job):
    """
    Process a URL matcher job in the background.
    
    Args:
        job: URLMatcherJob instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    from .models import URLMatcherJob
    
    try:
        # Update job status
        job.status = 'processing'
        job.save()
        
        # Get the file path
        csv_file_path = job.csv_file.path
        
        # Get output directory
        output_dir = job.get_output_dir()
        
        # Create and run the URL matcher
        matcher = URLMatcher(
            csv_path=csv_file_path,
            output_dir=output_dir,
            similarity_threshold=job.similarity_threshold
        )
        
        success = matcher.run()
        
        if success:
            # Update job with results
            job.status = 'completed'
            
            # Get the latest report files (most recent by timestamp)
            report_files = {}
            for file in os.listdir(output_dir):
                if file.startswith('url_matching_summary_'):
                    report_files['summary'] = os.path.join(output_dir, file)
                elif file.startswith('url_matching_results_'):
                    report_files['results'] = os.path.join(output_dir, file)
                elif file.startswith('exact_matches_'):
                    report_files['exact_matches'] = os.path.join(output_dir, file)
                elif file.startswith('partial_matches_'):
                    report_files['partial_matches'] = os.path.join(output_dir, file)
                elif file.startswith('unmatched_live_'):
                    report_files['unmatched_live'] = os.path.join(output_dir, file)
                elif file.startswith('unmatched_staging_'):
                    report_files['unmatched_staging'] = os.path.join(output_dir, file)
            
            # Update job with file paths
            job.summary_file = report_files.get('summary', '')
            job.results_file = report_files.get('results', '')
            job.exact_matches_file = report_files.get('exact_matches', '')
            job.partial_matches_file = report_files.get('partial_matches', '')
            job.unmatched_live_file = report_files.get('unmatched_live', '')
            job.unmatched_staging_file = report_files.get('unmatched_staging', '')
            
            # Update statistics
            if job.summary_file and os.path.exists(job.summary_file):
                # Parse the summary file to extract statistics
                with open(job.summary_file, 'r') as f:
                    summary_content = f.read()
                    
                    # Extract statistics from summary content
                    for line in summary_content.split('\n'):
                        if 'Total URLs analyzed:' in line:
                            job.total_urls = int(line.split(':')[1].strip())
                        elif 'Exact matches:' in line:
                            job.exact_matches = int(line.split(':')[1].strip().split(' ')[0])
                        elif 'Partial matches:' in line:
                            job.partial_matches = int(line.split(':')[1].strip().split(' ')[0])
                        elif 'Unmatched Live URLs:' in line:
                            job.unmatched_live = int(line.split(':')[1].strip().split(' ')[0])
                        elif 'Unmatched Staging URLs:' in line:
                            job.unmatched_staging = int(line.split(':')[1].strip().split(' ')[0])
            
            job.save()
            return True
        else:
            job.status = 'failed'
            job.error_message = 'URL matcher failed to run successfully'
            job.save()
            return False
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing URL matcher job: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Update job status
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        
        return False
