from django.template.base import Node, token_kwargs, TemplateSyntaxError

from django import template

register = template.Library()

class TenantNode(template.Node):
    def __init__(self, nodelist, tenant_var):
        self.tenant_var = tenant_var
        self.nodelist = nodelist

    def render(self, context):
        tenant = context.get(self.tenant_var, None)
        if tenant:
            with tenant:
                output = self.nodelist.render(context)
                return output
        output = self.nodelist.render(context)
        return output

@register.tag('tenant')
def do_tenant(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]
    extra_context = token_kwargs(remaining_bits, parser, support_legacy=True)

    nodelist = parser.parse(('endtenant',))
    parser.delete_first_token()
    return TenantNode(nodelist, tenant_var=remaining_bits[0])