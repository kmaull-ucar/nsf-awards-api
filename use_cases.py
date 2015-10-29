# -*- coding: utf-8 -*-
import json
import requests
import traceback
import pprint


DOI_ORG_URL    = "http://dx.doi.org/"
CR_SEARCH_URL  = "http://search.crossref.org/"
NSF_AWARDS_URL = "http://api.nsf.gov/services/v1/awards.json"


def use_case_01_get_publication_md_from_award_title(nsf_award_id):
    def get_citeproc_metadata(doi_url):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        r = requests.get(doi_url, headers=headers)

        if r.status_code == 200:
            # returned the converted JSON to a Python data structure
            return json.loads(r.text)

    def get_nsf_publication_titles(nsf_award_id):
        r = requests.get("{}?id={}&printFields=publicationResearch".format(NSF_AWARDS_URL, nsf_award_id))

        if r.status_code == 200:
            response = json.loads(r.text)
            award = response.get('response',{}).get("award", [])

            if award:
                papers = award[0].get('publicationResearch',{})
                if papers:
                    titles = [p.split('~')[TITLE_IDX] for p in papers]
                    return titles

    def get_dois_from_freeform_citations(free_form_citation_list):
        headers = {"Accept": "Content-Type: application/json"}
        r = requests.post("{}/links".format(CR_SEARCH_URL), data=json.dumps(free_form_citation_list), headers=headers)

        if r.status_code == 200:
            # returned the converted JSON to a Python data structure
            response = json.loads(r.text)

            if response['query_ok']:
                return response['results']

    TITLE_IDX = 1
    try:
        publication_titles = get_nsf_publication_titles(nsf_award_id)
        citation_results = get_dois_from_freeform_citations(publication_titles)

        for r in citation_results:
            if r['match']:
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(get_citeproc_metadata(r['doi']))
            else:
                print "No match found for : \n\t".format(r['text'])
            # break
    except:
        traceback.print_exc()

def main():
    use_case_01_get_publication_md_from_award_title(nsf_award_id = '0802290')

if __name__ == "__main__":
    main()
