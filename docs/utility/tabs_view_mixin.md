# TabsViewMixin [+](/app/mixins.py)

This is a simple Mixin to display Tab navigation on your TemplateView or any View class that inherits this class.
The navigation tabs are the navigation that is displayed on top of your template container.

## Methods

### get_current_tabs
This method is meant to be overridden and return an array to be with tuples. The first element of the tuple will be the text of the tab and the second will be the url, those 2 are mandatory.
The 3rd is and optional variable that can be set to None to be omitted and displays a warning symbol.
Finally, the 4th variable is to set the tab to active with a boolean, if None or unset the tab will be active if the path equals the url.
Data can be passed to the method with the `get_context_data` kwargs at the super of your view.

### get_back_url
Method that returns the url that will be updated to the context with the name `back`.
