"""
NetBox Plugin Reloader - Dynamically reload NetBox plugins without server restart.
"""

from netbox.plugins import PluginConfig

from netbox_plugin_reloader.version import __version__


class NetboxPluginReloaderConfig(PluginConfig):
    """
    Configuration for the Plugin Reloader NetBox plugin.

    This plugin allows NetBox to dynamically reload plugin models and form fields
    that might have been missed during the initial application startup.
    """

    name = "netbox_plugin_reloader"
    verbose_name = "Plugin Reloader"
    description = "Dynamically reload NetBox plugins without server restart"
    version = __version__
    base_url = "netbox-plugin-reloader"
    min_version = "4.3.0"
    max_version = "4.3.99"

    def ready(self):
        """
        Plugin initialization logic executed when Django loads the application.
        """
        super().ready()

        from core.models import ObjectType
        from django.apps import apps
        from django.conf import settings
        from django.utils.translation import gettext_lazy as _
        from extras.forms.model_forms import CustomFieldForm, TagForm
        from netbox.models.features import FEATURES_MAP, register_models
        from netbox.registry import registry
        from utilities.forms.fields import ContentTypeMultipleChoiceField

        # Register missing plugin models
        self._register_missing_plugin_models(settings.PLUGINS, apps, registry, FEATURES_MAP, register_models)

        # Refresh form fields
        self._refresh_form_field(CustomFieldForm, "custom_fields", ObjectType, ContentTypeMultipleChoiceField, _)
        self._refresh_form_field(TagForm, "tags", ObjectType, ContentTypeMultipleChoiceField, _)

    def _register_missing_plugin_models(
        self, plugin_list, app_registry, netbox_registry, feature_mixins_map, model_register_function
    ):
        """Register plugin models that weren't properly registered during application startup."""
        unregistered_models = []

        for plugin_name in plugin_list:
            try:
                plugin_app_config = app_registry.get_app_config(plugin_name)
                app_label = plugin_app_config.label

                for model_class in plugin_app_config.get_models():
                    model_name = model_class._meta.model_name
                    if not self._is_model_registered(app_label, model_name, netbox_registry, feature_mixins_map):
                        unregistered_models.append(model_class)

            except Exception as e:
                print(f"Error processing plugin {plugin_name}: {e}")

        if unregistered_models:
            model_register_function(*unregistered_models)
            print(f"Plugin Reloader: Registered {len(unregistered_models)} previously missed models")

    def _is_model_registered(self, app_label, model_name, registry, feature_mixins_map):
        """Check if a model is already registered in any NetBox feature registry."""
        return any(
            app_label in registry["model_features"][feature_name]
            and model_name in registry["model_features"][feature_name][app_label]
            for feature_name in feature_mixins_map.keys()
        )

    def _refresh_form_field(self, form_class, feature_name, object_type_class, field_class, translation_function):
        """Refresh form field definitions to include newly registered models."""
        field_labels = {
            "custom_fields": ("Object types", "The type(s) of object that have this custom field"),
            "tags": ("Object types", "The type(s) of object that can have this tag"),
        }

        label, help_text = field_labels[feature_name]

        object_types_field = field_class(
            label=translation_function(label),
            queryset=object_type_class.objects.with_feature(feature_name),
            help_text=translation_function(help_text),
        )

        form_class.base_fields["object_types"] = object_types_field


# Plugin configuration object
config = NetboxPluginReloaderConfig
