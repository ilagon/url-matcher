#!/usr/bin/env python3

import pandas as pd
import re
import os
import argparse
import logging
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urlparse, unquote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"url_matcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('url_matcher')


class URLMatcher:
    """A class to match Live URLs with Staging URLs based on various matching strategies."""
    
    def __init__(self, csv_path, output_dir="./output", similarity_threshold=0.7):
        """Initialize the URLMatcher with the CSV file path and matching parameters.
        
        Args:
            csv_path (str): Path to the CSV file containing Live and Staging URLs
            output_dir (str): Directory to save output files
            similarity_threshold (float): Threshold for partial matching (0.0 to 1.0)
        """
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.similarity_threshold = similarity_threshold
        self.df = None
        self.working_df = None
        self.results = {
            "exact_matches": [],
            "partial_matches": [],
            "no_matches": []
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def load_data(self):
        """Load and prepare the CSV data for processing."""
        logger.info(f"Loading data from {self.csv_path}")
        try:
            # Read the CSV file
            self.df = pd.read_csv(self.csv_path)
            
            # Check if the expected columns exist
            if 'Live_URL' in self.df.columns and 'Staging_URL' in self.df.columns:
                # Columns are already correctly named
                pass
            elif len(self.df.columns) == 2:
                # Assume the first column is Live URL and the second is Staging URL
                self.df.columns = ['Live_URL', 'Staging_URL']
            else:
                raise ValueError("Could not identify Live and Staging URL columns. Expected 2 columns.")
            
            # Create a working copy
            self.working_df = self.df.copy()
            
            # Clean the URLs
            self.clean_urls()
            
            logger.info(f"Loaded {len(self.df)} rows of data")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def clean_urls(self):
        """Clean and standardize URLs in both columns."""
        logger.info("Cleaning URLs")
        
        # Function to clean individual URL
        def clean_url(url):
            if pd.isna(url) or not isinstance(url, str):
                return ""
            
            # Remove leading/trailing whitespace
            url = url.strip()
            
            # Ensure URL starts with http if it doesn't already
            if url and not url.startswith('http'):
                if url.startswith('/'):
                    url = 'http:/' + url  # Add http: to path-only URLs
                else:
                    url = 'http://' + url  # Add http:// to domain-only URLs
                
            # Remove duplicate slashes (but preserve http:// and https://)
            url = re.sub(r'(?<!:)/{2,}', '/', url)
            
            # URL decode
            url = unquote(url)
            
            return url
        
        # Apply cleaning to both URL columns
        self.working_df['Live_URL'] = self.working_df['Live_URL'].apply(clean_url)
        self.working_df['Staging_URL'] = self.working_df['Staging_URL'].apply(clean_url)
        
        # Remove rows where both URLs are empty
        self.working_df = self.working_df[(self.working_df['Live_URL'] != "") | 
                                         (self.working_df['Staging_URL'] != "")]
        
        logger.info(f"After cleaning, {len(self.working_df)} rows remain")
    
    def find_exact_matches(self):
        """Find exact matches between Live and Staging URLs."""
        logger.info("Finding exact matches")
        
        # Create a new column for match type
        self.working_df['Match_Type'] = 'No Match'
        
        # Step 1: Find rows where Live URL exactly matches Staging URL in the same row
        same_row_exact_matches = self.working_df[
            (self.working_df['Live_URL'] != "") & 
            (self.working_df['Staging_URL'] != "") & 
            (self.working_df['Live_URL'] == self.working_df['Staging_URL'])
        ]
        
        # Mark these as exact matches
        self.working_df.loc[same_row_exact_matches.index, 'Match_Type'] = 'Exact'
        
        # Step 2: Find exact matches across different rows
        # Get all unique Live URLs that don't already have exact matches
        unmatched_live_urls = self.working_df[
            (self.working_df['Live_URL'] != "") & 
            (self.working_df['Match_Type'] != 'Exact')
        ]['Live_URL'].unique()
        
        # Get all unique Staging URLs
        all_staging_urls = self.working_df[self.working_df['Staging_URL'] != ""]['Staging_URL'].unique()
        
        # Find cross-row exact matches
        cross_row_exact_matches = []
        for live_url in unmatched_live_urls:
            if live_url in all_staging_urls:
                # Find indices of rows with this Live URL
                live_indices = self.working_df[self.working_df['Live_URL'] == live_url].index
                
                # Mark as exact match
                self.working_df.loc[live_indices, 'Match_Type'] = 'Exact'
                
                # Add to cross-row exact matches
                cross_row_exact_matches.append({
                    'Live_URL': live_url,
                    'Staging_URL': live_url
                })
        
        # Combine all exact matches for results
        self.results['exact_matches'] = same_row_exact_matches[['Live_URL', 'Staging_URL']].to_dict('records') + cross_row_exact_matches
        
        # Create a new working dataframe without exact matches for further processing
        self.working_df_no_exact = self.working_df[self.working_df['Match_Type'] != 'Exact'].copy()
        
        total_exact_matches = len(same_row_exact_matches) + len(cross_row_exact_matches)
        logger.info(f"Found {total_exact_matches} exact matches ({len(same_row_exact_matches)} same-row, {len(cross_row_exact_matches)} cross-row)")
        return total_exact_matches
    
    def calculate_similarity(self, url1, url2):
        """Calculate similarity between two URLs using various methods.
        
        Args:
            url1 (str): First URL
            url2 (str): Second URL
            
        Returns:
            tuple: (similarity_score, match_type)
        """
        if not url1 or not url2:
            return 0, "None"
        
        # First check for exact match
        if url1 == url2:
            return 1.0, "Exact"
        
        # Method 1: Path-based matching
        # Split URLs into path components and compare
        path1 = urlparse(url1).path.strip('/').split('/')
        path2 = urlparse(url2).path.strip('/').split('/')
        
        # Calculate path overlap
        common_segments = set(path1).intersection(set(path2))
        if common_segments:
            path_similarity = len(common_segments) / max(len(path1), len(path2))
            if path_similarity > self.similarity_threshold:
                return path_similarity, "Partial - Path"
        
        # Method 2: Sequence matching using difflib
        sequence_similarity = SequenceMatcher(None, url1, url2).ratio()
        if sequence_similarity > self.similarity_threshold:
            return sequence_similarity, "Partial - Sequence"
        
        # Method 3: Check if one is a substring of the other
        if url1 in url2 or url2 in url1:
            substring_ratio = min(len(url1), len(url2)) / max(len(url1), len(url2))
            if substring_ratio > self.similarity_threshold:
                return substring_ratio, "Partial - Substring"
        
        return 0, "None"
    
    def find_partial_matches(self):
        """Find partial matches between Live and Staging URLs."""
        logger.info("Finding partial matches")
        
        # Get all Live URLs that don't have exact matches
        live_urls = self.working_df_no_exact[self.working_df_no_exact['Live_URL'] != ""]['Live_URL'].tolist()
        
        # Get all Staging URLs
        staging_urls = self.working_df[self.working_df['Staging_URL'] != ""]['Staging_URL'].tolist()
        
        partial_matches = []
        
        # For each Live URL without an exact match
        for live_url in live_urls:
            best_match = None
            best_score = 0
            best_match_type = "None"
            
            # Compare with each Staging URL
            for staging_url in staging_urls:
                score, match_type = self.calculate_similarity(live_url, staging_url)
                
                if score > best_score:
                    best_score = score
                    best_match = staging_url
                    best_match_type = match_type
            
            # If we found a good match
            if best_score > self.similarity_threshold:
                match = {
                    'Live_URL': live_url,
                    'Staging_URL': best_match,
                    'Similarity': best_score,
                    'Match_Type': best_match_type
                }
                partial_matches.append(match)
                
                # Update the match type in the working dataframe
                live_indices = self.working_df_no_exact[self.working_df_no_exact['Live_URL'] == live_url].index
                self.working_df.loc[live_indices, 'Match_Type'] = best_match_type
        
        # Store partial matches in results
        self.results['partial_matches'] = partial_matches
        
        logger.info(f"Found {len(partial_matches)} partial matches")
        return partial_matches
    
    def identify_unmatched_urls(self):
        """Identify URLs that have no matches."""
        logger.info("Identifying unmatched URLs")
        
        # Find Live URLs with no matches
        unmatched_live = self.working_df[
            (self.working_df['Live_URL'] != "") & 
            (self.working_df['Match_Type'] == 'No Match')
        ]['Live_URL'].tolist()
        
        # Find Staging URLs with no corresponding Live URL
        all_matched_staging = [m['Staging_URL'] for m in self.results['exact_matches']] + \
                             [m['Staging_URL'] for m in self.results['partial_matches']]
        
        unmatched_staging = [url for url in self.working_df['Staging_URL'].tolist() 
                           if url and url not in all_matched_staging]
        
        no_matches = {
            'unmatched_live': unmatched_live,
            'unmatched_staging': unmatched_staging
        }
        
        # Store unmatched URLs in results
        self.results['no_matches'] = no_matches
        
        logger.info(f"Found {len(unmatched_live)} unmatched Live URLs and {len(unmatched_staging)} unmatched Staging URLs")
        return no_matches
    
    def generate_report(self):
        """Generate a comprehensive report of the matching results."""
        logger.info("Generating report")
        
        # Create a timestamp for the output files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Create a CSV with all URLs and their match status
        output_df = self.df.copy()
        
        # Add match type column from working_df
        output_df['Match_Type'] = self.working_df['Match_Type']
        
        # Save to CSV
        output_csv_path = os.path.join(self.output_dir, f"url_matching_results_{timestamp}.csv")
        output_df.to_csv(output_csv_path, index=False)
        
        # 2. Create a summary report
        summary = {
            'total_urls': len(self.df),
            'exact_matches': len(self.results['exact_matches']),
            'partial_matches': len(self.results['partial_matches']),
            'unmatched_live': len(self.results['no_matches']['unmatched_live']),
            'unmatched_staging': len(self.results['no_matches']['unmatched_staging'])
        }
        
        # Calculate percentages
        total_live = sum(1 for url in self.df['Live_URL'] if url and not pd.isna(url))
        if total_live > 0:
            summary['exact_match_percentage'] = (summary['exact_matches'] / total_live) * 100
            summary['partial_match_percentage'] = (summary['partial_matches'] / total_live) * 100
            summary['unmatched_percentage'] = (summary['unmatched_live'] / total_live) * 100
        
        # Save summary to a text file
        summary_path = os.path.join(self.output_dir, f"url_matching_summary_{timestamp}.txt")
        
        with open(summary_path, 'w') as f:
            f.write("URL MATCHING SUMMARY\n")
            f.write("===================\n\n")
            f.write(f"Total URLs analyzed: {summary['total_urls']}\n")
            f.write(f"Exact matches: {summary['exact_matches']} ")
            if 'exact_match_percentage' in summary:
                f.write(f"({summary['exact_match_percentage']:.2f}% of Live URLs)\n")
            else:
                f.write("\n")
            
            f.write(f"Partial matches: {summary['partial_matches']} ")
            if 'partial_match_percentage' in summary:
                f.write(f"({summary['partial_match_percentage']:.2f}% of Live URLs)\n")
            else:
                f.write("\n")
            
            f.write(f"Unmatched Live URLs: {summary['unmatched_live']} ")
            if 'unmatched_percentage' in summary:
                f.write(f"({summary['unmatched_percentage']:.2f}% of Live URLs)\n")
            else:
                f.write("\n")
            
            f.write(f"Unmatched Staging URLs: {summary['unmatched_staging']}\n\n")
            
            # Add details about partial matches
            f.write("PARTIAL MATCHES BY TYPE\n")
            f.write("=====================\n\n")
            
            match_types = {}
            for match in self.results['partial_matches']:
                match_type = match['Match_Type']
                if match_type not in match_types:
                    match_types[match_type] = 0
                match_types[match_type] += 1
            
            for match_type, count in match_types.items():
                f.write(f"{match_type}: {count}\n")
        
        # 3. Create detailed reports for each category
        # Exact matches
        exact_path = os.path.join(self.output_dir, f"exact_matches_{timestamp}.csv")
        pd.DataFrame(self.results['exact_matches']).to_csv(exact_path, index=False)
        
        # Partial matches
        partial_path = os.path.join(self.output_dir, f"partial_matches_{timestamp}.csv")
        pd.DataFrame(self.results['partial_matches']).to_csv(partial_path, index=False)
        
        # Unmatched Live URLs
        unmatched_live_path = os.path.join(self.output_dir, f"unmatched_live_{timestamp}.csv")
        pd.DataFrame({'Live_URL': self.results['no_matches']['unmatched_live']}).to_csv(unmatched_live_path, index=False)
        
        # Unmatched Staging URLs
        unmatched_staging_path = os.path.join(self.output_dir, f"unmatched_staging_{timestamp}.csv")
        pd.DataFrame({'Staging_URL': self.results['no_matches']['unmatched_staging']}).to_csv(unmatched_staging_path, index=False)
        
        logger.info(f"Reports saved to {self.output_dir}")
        
        return {
            'summary': summary_path,
            'full_results': output_csv_path,
            'exact_matches': exact_path,
            'partial_matches': partial_path,
            'unmatched_live': unmatched_live_path,
            'unmatched_staging': unmatched_staging_path
        }
    
    def run(self):
        """Run the complete URL matching process."""
        logger.info("Starting URL matching process")
        
        # Step 1: Load and prepare data
        if not self.load_data():
            logger.error("Failed to load data. Exiting.")
            return False
        
        # Step 2: Find exact matches
        self.find_exact_matches()
        
        # Step 3: Find partial matches
        self.find_partial_matches()
        
        # Step 4: Identify unmatched URLs
        self.identify_unmatched_urls()
        
        # Step 5: Generate report
        report_paths = self.generate_report()
        
        logger.info("URL matching process completed successfully")
        logger.info(f"Summary report: {report_paths['summary']}")
        logger.info(f"Full results: {report_paths['full_results']}")
        
        return True


def main():
    """Main function to run the URL matcher from command line."""
    parser = argparse.ArgumentParser(description='Match Live URLs with Staging URLs')
    parser.add_argument('csv_file', help='Path to the CSV file containing URLs')
    parser.add_argument('--output-dir', '-o', default='./output', help='Directory to save output files')
    parser.add_argument('--threshold', '-t', type=float, default=0.7, 
                        help='Similarity threshold for partial matching (0.0 to 1.0)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create and run the URL matcher
    matcher = URLMatcher(
        csv_path=args.csv_file,
        output_dir=args.output_dir,
        similarity_threshold=args.threshold
    )
    
    success = matcher.run()
    
    if success:
        print("URL matching completed successfully. See logs for details.")
        return 0
    else:
        print("URL matching failed. See logs for details.")
        return 1


if __name__ == "__main__":
    main()
