from django import template

register = template.Library()

BREADCRUMB_MAP = {
    "helpdesk:dashboard": [
        ("Dashboard", "helpdesk:dashboard"),
    ],
    "helpdesk:zgloszenie_detail": [
        ("Dashboard", "helpdesk:dashboard"),
        ("Zgłoszenia", "helpdesk:dashboard"),  # lista zgłoszeń jest na dashboardzie
        # "#ID" dokładamy niżej jako leaf_label
    ],
}


@register.inclusion_tag("partials/breadcrumb.html", takes_context=True)
def render_breadcrumb(context, leaf_label=None):
    request = context.get("request")
    if not request or not hasattr(request, "resolver_match"):
        items = [("Dashboard", "helpdesk:dashboard")]
    else:
        view_name = request.resolver_match.view_name
        items = BREADCRUMB_MAP.get(
            view_name,
            [("Dashboard", "helpdesk:dashboard")],
        )

    if leaf_label:
        items = items + [(leaf_label, None)]

    return {"items": items}
