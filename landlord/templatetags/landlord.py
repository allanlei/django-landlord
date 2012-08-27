from django.template.base import Node, token_kwargs, TemplateSyntaxError

from django import template

register = template.Library()


@register.tag('with_tenant')
def do_with(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]
    extra_context = token_kwargs(remaining_bits, parser, support_legacy=True)


#     if not extra_context:
#         raise TemplateSyntaxError("%r expected at least one variable "
#                                   "assignment" % bits[0])
#     if remaining_bits:
#         raise TemplateSyntaxError("%r received an invalid token: %r" %
#                                   (bits[0], remaining_bits[0]))
#     nodelist = parser.parse(('endwith_tenant',))
#     parser.delete_first_token()

    nodelist = parser.parse(('endwith_tenant',))
    parser.delete_first_token()
    # print 'bits', bits
    # print 'remaining', remaining_bits
    # print 'extra', extra_context
    return WithNode(nodelist, tenant_var=remaining_bits[0])

class WithNode(template.Node):
    def __init__(self, nodelist, tenant_var):
        self.tenant_var = tenant_var
        self.nodelist = nodelist

    def render(self, context):
        tenant = context.get(self.tenant_var, None)       #residence.get(...) if var is String
        if tenant:
            with tenant:
                output = self.nodelist.render(context)
                return output
        output = self.nodelist.render(context)
        return output


# class WithNode(Node):
#     def __init__(self, var, name, nodelist, extra_context=None):
#         self.nodelist = nodelist
#         # var and name are legacy attributes, being left in case they are used
#         # by third-party subclasses of this Node.
#         self.extra_context = extra_context or {}
#         if name:
#             self.extra_context[name] = var

#     def __repr__(self):
#         return "<WithNode>"

#     def render(self, context):
#         values = dict([(key, val.resolve(context)) for key, val in
#                            self.extra_context.iteritems()])
#         context.update(values)

#         tenant = values.get('tenant', None)
#         if tenant:  
#             with tenant:
#                 output = self.nodelist.render(context)
#         else:
#             output = self.nodelist.render(context)
#         context.pop()
#         return output

# @register.tag('with_tenant')
# def do_with(parser, token):
#     bits = token.split_contents()
#     remaining_bits = bits[1:]
#     extra_context = token_kwargs(remaining_bits, parser, support_legacy=True)
#     print remaining_bits, extra_context
#     if not extra_context:
#         raise TemplateSyntaxError("%r expected at least one variable "
#                                   "assignment" % bits[0])
#     if remaining_bits:
#         raise TemplateSyntaxError("%r received an invalid token: %r" %
#                                   (bits[0], remaining_bits[0]))
#     nodelist = parser.parse(('endwith_tenant',))
#     parser.delete_first_token()
#     return WithNode(None, None, nodelist, extra_context=extra_context)
