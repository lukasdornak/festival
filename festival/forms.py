from django import forms
from . import models


class PhotoAdminForm(forms.ModelForm):
    cropped = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        fields = ['original', 'description', 'year', 'order']
        model = models.Photo


class GalleryAdminForm(forms.ModelForm):
    photo_list = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=False, label='fotky')

    class Meta:
        fields = ['photo_list']
        model = models.Year
