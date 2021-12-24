import json
import pathlib
import logging
import requests
import smartcat
import magic

ID = "aeac194e-d2ec-4cf6-a1d8-2bc0afd25ced"
KEY = "1_zBR7Q3oYX5anSCWxIZoyvm2XY"
PROJECT_ID = "d23a5992-05a9-4676-a391-aa127877b8d9"
mime = magic.Magic(mime=True)


class SmartcatSession(requests.Session):
    def __init__(self, base_url):
        super(SmartcatSession, self).__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        return super(SmartcatSession, self).request(method, self.base_url + url, *args, **kwargs)


class Project(object):
    END_POINT = 'https://smartcat.ai'

    def __init__(self, account_id, api_key, project_id):
        self.project_id = project_id
        s = SmartcatSession(self.END_POINT)
        s.auth = (account_id, api_key)
        s.headers.update({'Accept': 'application/json'})
        self.session = s

    @property
    def details(self):
        r = self.session.get(f'/api/integration/v1/project/{self.project_id}')
        return json.loads(r.text)

    @property
    def docs(self):
        ret = {}
        for doc in self.details['documents']:
            name = doc['name']
            if name not in ret:
                ret[name] = []
            ret[name].append(doc)
        return ret

    def attach_doc(self, docs: dict):
        opened = []

        def file(name):
            fh = open(docs[name], 'rb')
            opened.append(fh)
            return pathlib.Path(docs[name]).name, fh, 'application/octetstream'

        curr_docs = self.docs
        new_files = {name: file(name) for name in docs.keys() if name not in curr_docs}

        try:
            if len(new_files):
                res = self.session.post('/api/integration/v1/project/document',
                                        params={"projectId": self.project_id},
                                        files=new_files)
                logging.info("uploaded new files")
                if not res.ok:
                    logging.warning(res.text)

            for doc_name in curr_docs:
                if doc_name not in docs:
                    continue
                for f in curr_docs[doc_name]:
                    res = self.session.put('/api/integration/v1/document/update',
                                           params={"documentId": f["id"]},
                                           files={"file": file(f['name'])})
                    logging.info(f'updated file: {f["name"]} {f["targetLanguage"]}')
                    if not res.ok:
                        logging.warning(res.text)
        finally:
            for f in opened:
                f.close()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    project = Project(ID, KEY, PROJECT_ID)
    project.attach_doc({"blueprint": "../strings/blueprints/template.pot"})
    # d = project.details
