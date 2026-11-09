import anthropic
c = anthropic.Anthropic()
r = c.messages.create(model="claude-fable-5-2", max_tokens=100, messages=[])
s = c.messages.create(model="claude-opus-5-5", effort="max", max_tokens=100, messages=[])
