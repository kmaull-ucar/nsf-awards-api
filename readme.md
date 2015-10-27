# Overview

The NSF maintains an API for gathering information about the awards provided within their system.

This repo documents some of common use cases for the API.
 
## Use Case : Get publications associated with an NSF grant.

`input:` _an NSF award identifier_
`output:` _the list of papers associated with the input identifier_
 
 Using the awards endpoint and the `printFields` parameter set to `publicationResearch` we can make the call:
 
    http://api.nsf.gov/services/v1/awards.json?id={}&printFields=publicationResearch
    
 which will return something like :
 
    {
        "response": {
            "award": [
                {
                    "publicationResearch": [
                        "Burakowski, E. A., Ollinger, S.V., Lepine, L., Schaaf, C.B., Wang, Z., Dibb, J. E., Hollinger, D.Y., . . . Kim, D.H., Erb, A., Martin, M.~Spatial scaling of reflectance and surface albedo over a mixed-use, temperate forest landscape during snow-covered periods~Remote Sensing of the Environment~158~2015~465~",
                        "Hamilton, L~What people know~Environmental Studies and Sciences~5~2015~54~",
                        "Hamilton, L.C. &amp; Safford, T.G.~Environmental views from the coast: Public concern about local to global marine issues~Society and Natural Resources~28~2015~57~",
                        ...
                        ]
                }
        }
    }
    
### Parsing the publications out of the output response 
The publication segments (author, title, etc.) are separated by the `~` character.  At the moment, it appears the second segment is the title, though this may not be a steadfast rule or requirement.


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


### Using the Crossref Search service to get publication metadata
You can take a look at the [API documentation at Crossref](http://search.crossref.org/help/api), but using the free-form `/links` endpoint, you may get the DOI for a citation fragment (e.g. title).  From that, you can get the full metadata record using [Crossref's DOI metadata lookup service](http://www.crosscite.org/cn/).

The two methods here achieve that result quite nicely :

    def get_citeproc_metadata(doi_url):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        r = requests.get(doi_url, headers=headers)

        if r.status_code == 200:
            # returned the converted JSON to a Python data structure
            return json.loads(r.text)

    def get_dois_from_freeform_citations(free_form_citation_list):
        headers = {"Accept": "Content-Type: application/json"}
        r = requests.post("{}/links".format(CR_SEARCH_URL), data=json.dumps(free_form_citation_list), headers=headers)

        if r.status_code == 200:
            # returned the converted JSON to a Python data structure
            response = json.loads(r.text)

            if response['query_ok']:
                return response['results']

See the file [use_cases.py](https://github.com/kmaull-ucar/nsf-awards-api/blob/master/use_cases.py) for the following code fragment to do this work.
