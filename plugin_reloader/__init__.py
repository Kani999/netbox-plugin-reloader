"""
NetBox Plugin Reloader - Dynamically reload NetBox plugins without server restart.
"""

from netbox.plugins import PluginConfig
from .version import __version__, __description__


class PluginReloaderConfig(PluginConfig):
    """
    Configuration for the Plugin Reloader NetBox plugin.

    This plugin allows NetBox to dynamically reload plugin models and form fields
    that might have been missed during the initial application startup.
    """

    name = "netbox_plugin_reloader"
    verbose_name = "Plugin Reloader"
    description = __description__
    version = __version__
    base_url = "netbox-plugin-reloader"

    # Plugin configuration
    default_settings = {}
    required_settings = []

    # NetBox version compatibility
    min_version = "4.2.0"
    max_version = "4.2.99"

    def ready(self):
        """
        Plugin initialization logic executed when Django loads the application.

        This method handles the dynamic registration of plugin models and
        refreshes form fields to ensure all plugins are properly loaded.
        """
        # Initialize parent plugin functionality
        super().ready()

        # Import dependencies
        from core.models import ObjectType
        from django.apps import apps
        from django.conf import settings
        from django.utils.translation import gettext_lazy as _
        from extras.forms.model_forms import CustomFieldForm
        from netbox.models.features import FEATURES_MAP, register_models
        from netbox.registry import registry
        from utilities.forms.fields import ContentTypeMultipleChoiceField

        # Step 1: Register any plugin models missed during initial application startup
        self._register_missing_plugin_models(
            plugin_list=settings.PLUGINS,
            app_registry=apps,
            netbox_registry=registry,
            feature_mixins_map=FEATURES_MAP,
            model_register_function=register_models,
        )

        # Step 2: Ensure form fields for plugins are properly initialized
        self._refresh_custom_field_form(
            form_class=CustomFieldForm,
            field_class=ContentTypeMultipleChoiceField,
            object_type_class=ObjectType,
            translation_function=_,
        )

    def _register_missing_plugin_models(
        self,
        plugin_list,
        app_registry,
        netbox_registry,
        feature_mixins_map,
        model_register_function,
    ):
        """
        Register plugin models that weren't properly registered during application startup.

        This method scans all enabled plugins, identifies models that haven't been
        registered in NetBox's feature registry, and registers them.

        Args:
            plugin_list: List of enabled plugin names from settings
            app_registry: Django application registry
            netbox_registry: NetBox's internal registry for tracking features
            feature_mixins_map: Dictionary mapping feature names to mixin classes
            model_register_function: Function used to register models with NetBox
        """
        unregistered_models = []

        # For each enabled plugin
        for plugin_name in plugin_list:
            try:
                # Get the Django app configuration for this plugin
                plugin_app_config = app_registry.get_app_config(plugin_name)
                app_label = plugin_app_config.label

                # Check each model in the plugin
                for model_class in plugin_app_config.get_models():
                    model_name = model_class._meta.model_name

                    # Only register models that aren't already in the registry
                    if not self._is_model_registered(
                        app_label=app_label,
                        model_name=model_name,
                        registry=netbox_registry,
                        feature_mixins_map=feature_mixins_map,
                    ):
                        unregistered_models.append(model_class)

            except Exception as e:
                # Safely handle errors with specific plugins
                print(f"Error processing plugin {plugin_name}: {e}")

        # Register the collected models if any were found
        if unregistered_models:
            model_register_function(*unregistered_models)
            print(f"Plugin Reloader: Registered {len(unregistered_models)} previously missed models")

    def _is_model_registered(self, app_label, model_name, registry, feature_mixins_map):
        """
        Check if a model is already registered in any NetBox feature registry.

        Args:
            app_label: Django application label (e.g., 'dcim', 'ipam')
            model_name: Model name without the app label
            registry: NetBox registry containing feature registrations
            feature_mixins_map: Dictionary mapping feature names to mixin classes

        Returns:
            bool: True if model is registered in any feature, False otherwise
        """
        # Check each available feature registry
        for feature_name in feature_mixins_map.keys():
            feature_registry = registry["model_features"][feature_name]

            # If the app_label exists and the model is registered under it
            if app_label in feature_registry and model_name in feature_registry[app_label]:
                return True

        # Model not found in any feature registry
        return False

    def _refresh_custom_field_form(self, form_class, field_class, object_type_class, translation_function):
        """
        Refresh form field definitions for custom fields.

        This ensures that plugin models are properly included in form field choices
        after they've been registered.

        Args:
            form_class: The CustomFieldForm class to update
            field_class: Field class to use for the object_types field
            object_type_class: The ObjectType model class
            translation_function: Function for internationalizing strings
        """
        # Create a field that includes all models with custom_fields feature
        object_types_field = field_class(
            label=translation_function("Object types"),
            queryset=object_type_class.objects.with_feature("custom_fields"),
            help_text=translation_function("The type(s) of object that have this custom field"),
        )

        # Update the form definition
        form_class.base_fields["object_types"] = object_types_field


# Plugin configuration object
config = PluginReloaderConfig
