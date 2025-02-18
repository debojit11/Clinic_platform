from django import forms
from .models import Patient, MedicalRecord

class PatientDetailsForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['age', 'gender', 'contact', 'medical_history']

    # Adding fields for User model data
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            # Populate the form fields with data from the related User model
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        # Save changes to the Patient model
        patient = super().save(commit=False)
        
        # Save the user-related fields (first_name, last_name, email) to the User model
        user = patient.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            patient.save()

        return patient


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'doctor_notes']