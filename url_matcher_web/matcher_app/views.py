import os
import pandas as pd
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .forms import CSVUploadForm
from .models import URLMatcherJob
from .tasks import process_url_matcher_job


@ensure_csrf_cookie
@csrf_exempt
def upload_csv(request):
    """View for uploading CSV files for URL matching."""
    # Ensure CSRF cookie is set for all requests
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new job
            job = URLMatcherJob(
                csv_file=request.FILES['csv_file'],
                similarity_threshold=form.cleaned_data['similarity_threshold']
            )
            job.save()
            
            # Process the job in a background thread
            thread = threading.Thread(target=process_url_matcher_job, args=(job,))
            thread.daemon = True
            thread.start()
            
            # Redirect to results page
            return redirect(reverse('matcher_app:results', kwargs={'job_id': job.id}))
    else:
        form = CSVUploadForm()
    
    return render(request, 'matcher_app/upload.html', {'form': form})


def results(request, job_id):
    """View for displaying URL matcher results."""
    job = get_object_or_404(URLMatcherJob, id=job_id)
    
    # Check if the job is still processing
    if job.status == 'pending' or job.status == 'processing':
        return render(request, 'matcher_app/processing.html', {'job': job})
    
    # Check if the job failed
    if job.status == 'failed':
        return render(request, 'matcher_app/error.html', {'job': job})
    
    # Load the results data
    results_data = {
        'job': job,
        'summary': job.get_summary_content(),
    }
    
    # Load exact matches
    if job.exact_matches_file and os.path.exists(job.exact_matches_file):
        exact_matches_df = pd.read_csv(job.exact_matches_file)
        results_data['exact_matches'] = exact_matches_df.to_dict('records')
    
    # Load partial matches
    if job.partial_matches_file and os.path.exists(job.partial_matches_file):
        partial_matches_df = pd.read_csv(job.partial_matches_file)
        results_data['partial_matches'] = partial_matches_df.to_dict('records')
    
    return render(request, 'matcher_app/results.html', results_data)


def check_job_status(request, job_id):
    """AJAX endpoint to check job status."""
    try:
        job = URLMatcherJob.objects.get(id=job_id)
        return JsonResponse({
            'status': job.status,
            'redirect': reverse('matcher_app:results', kwargs={'job_id': job.id}) if job.status == 'completed' else None
        })
    except URLMatcherJob.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)
