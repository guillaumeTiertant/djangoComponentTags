from django import template
from django.utils.safestring import mark_safe

from component_tags.arguments import Argument, Flag, KeywordArgument
from component_tags.core import registry

register = template.Library()

@register.simple_tag(name="dependencies")
def component_dependencies_tag():
    registry_component = registry._registry
    registry_component = { k: v for k, v in registry_component.items() }
    registry.clear()
    unique_component_classes = set(registry_component.values())

    out = []
    for component_class in unique_component_classes:
        import_static_files = component_class.render_dependencies()
        for import_static_file in import_static_files:
            if not import_static_file in out:
                out.append(import_static_file)
    out.sort()
    return mark_safe("\n".join(out) + "\n")