import re
from termcolor import colored

def pretty_prompt(qns):
    out = {}

    for q in qns:
        prompt = q['message'] + ': '
        if q.get('type') == 'confirm':
            q['default'] = 'Y'
            prompt += colored('(Y/n) ', 'grey')
        elif q.get('type') == 'list':
            for n, choice in enumerate(q['choices']):
                print '%d. %s' % (n+1, choice['name'].title())
            q['validate'] = lambda x: x.isdigit() and int(x) <= len(q['choices'])
            q['default'] = '1'
        elif q.get('default'):
            prompt += colored('(%s) ' % q['default'], 'grey')

        while True:
            value = raw_input(prompt)
            if not value: value = q['default']
            if 'validate' in q and not q['validate'](value):
                continue
            break

        if q.get('type') == 'confirm':
            out[q['name']] = re.match('^y(es)?$(?i)', value)
            value = 'Yes' if out[q['name']] else 'No'
        elif q.get('type') == 'list':
            choice = q['choices'][int(value)-1]
            out[q['name']] = choice['value']
            value = '%s (%s)' % (value, choice['name'].title())
        else:
            out[q['name']] = value

        print "\033[1A%s: %s%s" % (
            q['message'], colored(value, 'blue'),
            ' ' * max(len(value), len(q['default'])+3)
        )

    return out
