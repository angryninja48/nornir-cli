from drivers.templates import Templates

y = Templates()
a = y.render_config(template_name='interfaces')


print(a['csr01'].result)
print(a['csr02'].result)
