# This script downloads list of urls
# Copy urls and they will be downloaded to current working directory
# Optionally folder(s) can be passed as argument and urls will be downloaded to nested folder
# In case of failure the report will be generated (with url and status_code)
import os
import sys
import requests
import pyperclip
from shutil import copyfile

# list of not-downloaded files
def status_report(url, status):
    report_file = '_du_errors_report.csv'
    if not os.path.exists(report_file):
        rf = open(report_file, 'w')
        rf.write('url,status_code\n')
        rf.close()
    print('Error {}: {}'.format(status, url))
    with open(report_file, 'a') as rf:
        rf.write('"{}","{}"\n'.format(url, status))
    rf.close()

def proper_name(arg):
    forbidden_chars = (':', '*', '?', '"', '<', '>', '|', '%20')
    for fc in forbidden_chars:
        arg = arg.replace(fc, '-')
    return arg

# download html page
def download_page(url, filename):
    # Headers for faking user browsing
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    # Skip files already downloaded
    if os.path.isfile(filename):
        print('Skipped: ', filename)
        return
    # Copy local files
    if 'C:' in url or 'Z:' in url:
        copyfile(url.replace('file:///', ''), filename)
        print('Copied: ', filename)
        return
    # Download pages
    try:
        res = requests.get(url, headers=headers)
        status_code, res_content = res.status_code, res.content
    except:
        status_code, res_content = 'unknown error', ''
    if status_code != 200:
        status_report(url, status_code)
        return
    if res_content:
        with open(filename, 'wb') as f:
            f.write(res_content)
            print('Downloaded: ', filename)

def create_directory(args):
    if not args:
        return
    if isinstance(args, str):
        args = [args]
    if not isinstance(args, list):
        return
    directory = proper_name(os.path.sep.join(args))
    if not directory.strip():
        return
    if not os.path.exists(directory):
        print('Creating directory: {}'.format(directory))
        os.makedirs(directory)
    return directory

def get_urls(folder=None):
    # Get urls from clipboard
    urls = set([o.strip().replace('\\', '/') for o in pyperclip.paste().splitlines() if o.strip() and ('/' in o or '\\' in o)])
    print(len(urls), 'urls in clipboard')
    if not urls:
        pass
    if folder:
        folder = create_directory(folder)
    # Fire in the hole
    for url in urls:
        if '\t' in url:
            filename,url = url.split('\t')
            # switch url with filename if filename is in second column
            if '/' in filename:
                filename,url = url,filename
        else:
            filename = url.rstrip('/').split('/')[-1]
            if '=' in filename:
                filename = filename.split('=')[-1]
        filename = proper_name(filename)
        if folder:
            filename = os.path.join(folder, filename)
        download_page(url, filename)

if __name__ == '__main__':
    get_urls(sys.argv[1:])
