# Overview

The [NSF maintains an Awards API](http://www.research.gov/common/webapi/awardapisearch-v1.htm) for gathering information about the awards provided within their system.

This repo documents some of common use cases for their API.
 
## Use Case #1: Get publications associated with an NSF grant.

`input:` _an NSF award identifier_
`output:` _the list of papers (metadata) associated with the input identifier_
 
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
You can take a look at the [API documentation at Crossref](http://search.crossref.org/help/api), by using the free-form `/links` endpoint, you may get the DOI for a citation fragment (e.g. title).  From that, you can get the full metadata record using [Crossref's DOI metadata lookup service](http://www.crosscite.org/cn/).

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

### Example output from use case
With the input grant ID = `0802290`, we can see the output from the first publication returned (the others are suppressed from the output).


    {   u'DOI': u'10.1016/j.dsr2.2012.02.002',
        u'ISSN': [u'0967-0645'],
        u'URL': u'http://dx.doi.org/10.1016/j.dsr2.2012.02.002',
        u'alternative-id': [u'S0967064512000069'],
        u'author': [   {   u'affiliation': [],
                           u'family': u'Cooper',
                           u'given': u'L.W.'},
                       {   u'affiliation': [],
                           u'family': u'Janout',
                           u'given': u'M.A.'},
                       {   u'affiliation': [],
                           u'family': u'Frey',
                           u'given': u'K.E.'},
                       {   u'affiliation': [],
                           u'family': u'Pirtle-Levy',
                           u'given': u'R.'},
                       {   u'affiliation': [],
                           u'family': u'Guarinello',
                           u'given': u'M.L.'},
                       {   u'affiliation': [],
                           u'family': u'Grebmeier',
                           u'given': u'J.M.'},
                       {   u'affiliation': [],
                           u'family': u'Lovvorn',
                           u'given': u'J.R.'}],
        u'container-title': u'Deep Sea Research Part II: Topical Studies in Oceanography',
        u'created': {   u'date-parts': [[2012, 2, 8]],
                        u'date-time': u'2012-02-08T10:37:30Z',
                        u'timestamp': 1328697450000L},
        u'deposited': {   u'date-parts': [[2015, 2, 14]],
                          u'date-time': u'2015-02-14T05:00:00Z',
                          u'timestamp': 1423890000000L},
        u'indexed': {   u'date-parts': [[2015, 9, 26]],
                        u'date-time': u'2015-09-26T20:25:32Z',
                        u'timestamp': 1443299132580L},
        u'issued': {   u'date-parts': [[2012, 6]]},
        u'link': [   {   u'URL': u'http://api.elsevier.com/content/article/PII:S0967064512000069?httpAccept=text/xml',
                         u'content-type': u'text/xml',
                         u'content-version': u'vor',
                         u'intended-application': u'text-mining'},
                     {   u'URL': u'http://api.elsevier.com/content/article/PII:S0967064512000069?httpAccept=text/plain',
                         u'content-type': u'text/plain',
                         u'content-version': u'vor',
                         u'intended-application': u'text-mining'}],
        u'member': u'http://id.crossref.org/member/78',
        u'page': u'141-162',
        u'prefix': u'http://id.crossref.org/prefix/10.1016',
        u'publisher': u'Elsevier BV',
        u'reference-count': 38,
        u'score': 1.0,
        u'source': u'CrossRef',
        u'subtitle': [],
        u'title': u'The relationship between sea ice break-up, water mass variation, chlorophyll biomass, and sedimentation in the northern Bering Sea',
        u'type': u'journal-article',
        u'volume': u'65-70'}
        ...
 
## Use Case #2 : Get award amounts by organization.

This seems to be a core use case that the API was designed for.  Head over to the [uc02_nsf_awards.ipynb](data-explorations/usecase02_nsf_awards.ipynb) to see what can be done.
