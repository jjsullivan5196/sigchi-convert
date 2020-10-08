#!/usr/bin/python
import re

COPY_FIELDS = ['title', 'abstract', 'keywords', 'doi']
AFFL_PUNCT = r'[.,:;-|]'

def scase(s):
  return '_'.join([w.lower() for w in s.split(' ')])

def session_table(prog):
  table = {}

  for session in prog['sessions']:
    for cid in session['contentIds']:
      table[cid] = table.get(cid) or []
      table[cid].append(str(session['id']))

  return table

def people_table(prog):
  table = {}

  for person in prog['people']:
    table[person['id']] = person

  return table

def format_author(a):
  return f"{a['firstName']} {a['middleInitial'] + ' ' if a['middleInitial'] else ''}{a['lastName']}"

def get_authors(paper, people):
  authors = []
  affiliation = {}

  for a in paper['authors']:
    authors.append(format_author(people[a['personId']]))
    affiliation.update({
      re.sub(AFFL_PUNCT, '', af['institution'].strip().casefold()): af['institution'].strip()
      for af in a['affiliations']
    })

  return {
    'affiliations': list(affiliation.values()),
    'authors': authors
  }

def miniconf_paper(paper, sequence, track, sessions, people):
  result = {
    'UID': str(paper['id']),
    'sequence': str(sequence),
    'track': track,
    'sessions': sessions.get(paper['id']) or [],
    **get_authors(paper, people),
    **{
      k: paper[k]
      for k in iter(paper)
      if k in COPY_FIELDS
    }
  }

  if 'qaLink' in paper:
    result['qa'] = paper['qaLink']['url']

  if 'broadcastLink' in paper:
    result['broadcast'] = paper['broadcastLink']['url']

  if 'videos' in paper:
    for link in paper['videos']:
      result[scase(link['type'])] = link['url']

  return result

def convert_content(content, sessions, people, type_ids):
  return [
    miniconf_paper(c, i, type_ids[c['typeId']], sessions, people)
    for i, c in enumerate(content, start = 1)
    if c['typeId'] in type_ids
  ]

def get_typeid(prog, tname):
  for info in prog['contentTypes']:
    if info['name'] == tname:
      return info['id']

if __name__ == '__main__':
  import sys
  import argparse
  import json

  DEFAULT_TYPES=['Paper', 'Posters', 'Demos', 'SIC', 'DC']

  parser = argparse.ArgumentParser(description='Convert SIGCHI program content to miniconf papers format')
  parser.add_argument('--types', dest='types', metavar='TS', type=str,
                      nargs='+', default=DEFAULT_TYPES,
                      help=f'types of content to be converted (one or more of {json.dumps(DEFAULT_TYPES)})')
  parser.add_argument('--prog', dest='prog', type=str, default=None,
                      help='json file containing the program (standard input if not given)')
  parser.add_argument('--out', dest='out', type=str, default=None,
                      help='location of output json for miniconf (standard output if not given)')

  args = parser.parse_args()
  fname = args.prog
  outname = args.out

  with (open(fname, 'r') if fname else sys.stdin) as fp:
    prog = json.load(fp)

  content = prog['contents']
  sessions = session_table(prog)
  people = people_table(prog)
  type_ids = {get_typeid(prog, t): t for t in args.types}
  converted = convert_content(content, sessions, people, type_ids)

  with (open(outname, 'w') if outname else sys.stdout) as fp:
    json.dump(converted, fp)
    print('', file=fp)
