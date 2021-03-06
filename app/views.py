import os

from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView

from app.forms import HomeForm
from app.backend.extraction import get_phenotypes, get_probable_diagnoses

# Class-Based Views
class HomeView(TemplateView):
    template_name = os.path.join(settings.TEMPLATE_BASE_DIR, 'home.html')

    def get(self,request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    def post(self,request):
        # Fills the form out with the data that was recieved.
        form = HomeForm(request.POST)

        if form.is_valid():
            # Clean to ensure there's no breakers/sql injection/hackery nonsense.
            text = form.cleaned_data['post']
            # Extract phenotypes from user input.
            input_phenotypes = get_phenotypes(text.lower())
            # Once I take in the data, I don't want to see it in the input bar.
            # anymore, but I can show it below.
            form = HomeForm()
            results = get_probable_diagnoses(input_phenotypes)
        args = {'form': form, 'text': text, 'results' : results, 'results_empty' : (len(results)==0)}
        return render(request, self.template_name, args)
