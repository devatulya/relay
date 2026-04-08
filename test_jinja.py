from jinja2 import Template
print(Template("const LB = '{{', RB = '}}';").render())
