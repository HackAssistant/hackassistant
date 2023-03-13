# OverwriteOnlyModelFormMixin [+](/app/mixins.py)

I have a model that is being shared across many forms. An ugly side effect of this was that if I ever forgot to ensure that the HTML rendered contained *exactly* the fields defined in the form, django would overwrite the values.

Here’s a mixin that you can add to any ModelForm which will only update values.

Note that this still allows users to update a model field explicitly with a blank.

[Source](https://yuji.wordpress.com/2013/03/12/django-prevent-modelform-from-updating-values-if-user-did-not-submit-them/)
