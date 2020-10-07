#!/usr/bin/python

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
  return [format_author(people[a['personId']]) for a in paper['authors']]

def miniconf_paper(paper, sessions, people):
  authors = get_authors(paper, people)

  result = {
    'UID': str(paper['id']),
    'title': paper['title'],
    'sessions': sessions.get(paper['id']) or [],
    'abstract': paper['abstract'],
    'keywords': paper['keywords'],
    'authors': authors
  }

  return result

def convert_content(content, sessions, people, type_ids):
  return [miniconf_paper(c, sessions, people) for c in content if c['typeId'] in type_ids]

def get_typeid(prog, tname):
  for info in prog['contentTypes']:
    if info['name'] == tname:
      return info['id']

if __name__ == '__main__':
  import sys
  import argparse
  import json

  DEFAULT_TYPES=['Paper', 'Posters', 'Demos']

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
  type_ids = frozenset([get_typeid(prog, t) for t in args.types])
  converted = convert_content(content, sessions, people, type_ids)

  with (open(outname, 'w') if outname else sys.stdout) as fp:
    json.dump(converted, fp)
    print('', file=fp)
