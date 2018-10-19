#!/opt/splunk/bin/python
"""
Use urlscan.io to pivot off an IOC and present in Splunk.
"""

import requests
import validators


def process_iocs(provided_iocs):
    """Return data formatted for Splunk from urlscan.io."""
    splunk_table = []

    for provided_ioc in set(provided_iocs):
        if validators.domain(provided_ioc) or validators.ipv4(provided_ioc) or \
           validators.md5(provided_ioc) or validators.sha256(provided_ioc):
            api    = 'https://urlscan.io/api/v1/search/?size=10000&q='
            uagent = 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
            resp   = requests.get('{}{}'.format(api, provided_ioc),
                                  headers={"User-Agent": uagent})
            ioc_dicts = rename_dicts(resp.json()["results"])
            
            for ioc_dict in ioc_dicts:
                splunk_table.append(ioc_dict)
        else:
            invalid_ioc = invalid_dict(provided_ioc)
            splunk_table.append(invalid_ioc)
    return splunk_table

def rename_dicts(results):
    """Rename the keys in of the returned dictionaries from urlscan.io API."""
    ioc_dicts = []

    for result in results:
        page                 = result["page"]
        new_page             = {}
        new_page["URL"]      = page.get("url", "")
        new_page["Domain"]   = page.get("domain", "")
        new_page["IP"]       = page.get("ip", "")
        new_page["PTR"]      = page.get("ptr", "")
        new_page["Server"]   = page.get("server", "")
        new_page["City"]     = page.get("city", "")
        new_page["Country"]  = page.get("country", "")
        new_page["ASN"]      = page.get("asn", "")
        new_page["ASN Name"] = page.get("asnname", "")

        if 'files' not in result.keys():
            download = {}
            download["Filename"]  = ""
            download["File Size"] = ""
            download["MIME Type"] = ""
            download["SHA256"]    = ""
            download["Invalid"]   = ""
            ioc_dict              = merge_dict(new_page, download)
            
            ioc_dicts.append(ioc_dict)
        else:
            files_dict = result["files"]

            for dl_file in files_dict:
                download = {}
                download["Filename"]  = dl_file.get("filename", "")
                download["File Size"] = dl_file.get("filesize", "")
                download["MIME Type"] = dl_file.get("mimeType", "")
                download["SHA256"]    = dl_file.get("sha256", "")
                download["Invalid"]   = ""
                ioc_dict              = merge_dict(new_page, download)
                
                ioc_dicts.append(ioc_dict)
    return ioc_dicts

def merge_dict(page, download):
    """Return a dictionary containing both page and download data."""
    merged_dict = {}
    merged_dict.update(page)
    merged_dict.update(download)
    return merged_dict

def invalid_dict(provided_ioc):
    """Return a dictionary for the invalid IOC."""
    invalid_ioc = {}
    invalid_ioc["URL"]       = ""
    invalid_ioc["Domain"]    = ""
    invalid_ioc["IP"]        = ""
    invalid_ioc["PTR"]       = ""
    invalid_ioc["Server"]    = ""
    invalid_ioc["City"]      = ""
    invalid_ioc["Country"]   = ""
    invalid_ioc["ASN"]       = ""
    invalid_ioc["ASN Name"]  = ""
    invalid_ioc["Filename"]  = ""
    invalid_ioc["File Size"] = ""
    invalid_ioc["SHA256"]    = ""
    invalid_ioc["MIME Type"] = ""
    invalid_ioc["Invalid"]   = provided_ioc
    return invalid_ioc
